"""Run after full UE5.5 editor startup in the included isolated project.
Creates one gold triangle layer using engine-native authoring APIs.
"""
import json
from pathlib import Path
import unreal as u

ROOT = Path(__file__).resolve().parent
DEST = '/Game/TriangleLine'
lib = u.MaterialEditingLibrary
assets = u.AssetToolsHelpers.get_asset_tools()
report = {'engine': u.SystemLibrary.get_engine_version(), 'input_results': [], 'assets': {}}
assert report['engine'].startswith('5.5.'), report['engine']

def fresh(name, cls, factory):
    path = DEST + '/' + name
    if u.EditorAssetLibrary.does_asset_exist(path):
        raise RuntimeError('Asset already exists; use a new trial project instead of overwriting: ' + path)
    obj = assets.create_asset(name, DEST, cls, factory)
    if not obj:
        raise RuntimeError('Could not create ' + path)
    return obj

task = u.AssetImportTask()
task.filename = str(ROOT / 'SourceAssets/T_TriangleLine.png')
task.destination_path = DEST
task.destination_name = 'T_TriangleLine'
task.automated = True
task.save = True
task.replace_existing = False
assets.import_asset_tasks([task])
texture = u.load_asset(DEST + '/T_TriangleLine')
assert texture
texture.set_editor_property('srgb', False)
texture.set_editor_property('compression_settings', u.TextureCompressionSettings.TC_MASKS)

mat = fresh('M_TriangleGold', u.Material, u.MaterialFactoryNew())
mat.set_editor_property('blend_mode', u.BlendMode.BLEND_ADDITIVE)
mat.set_editor_property('shading_model', u.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property('two_sided', True)
mat.set_editor_property('used_with_niagara_sprites', True)

def node(cls, x, y):
    return lib.create_material_expression(mat, cls, x, y)
def connect(a, output, b, input_name):
    assert lib.connect_material_expressions(a, output, b, input_name), (a, output, b, input_name)
def custom_input(name):
    value = u.CustomInput()
    value.set_editor_property('input_name', name)
    return value
def scalar(name, value, x, y):
    n = node(u.MaterialExpressionScalarParameter, x, y)
    n.set_editor_property('parameter_name', name)
    n.set_editor_property('default_value', value)
    return n

sample = node(u.MaterialExpressionTextureSampleParameter2D, -800, -100)
sample.set_editor_property('parameter_name', 'ShapeMask')
sample.set_editor_property('texture', texture)
sample.set_editor_property('sampler_type', u.MaterialSamplerType.SAMPLERTYPE_MASKS)
tint = node(u.MaterialExpressionVectorParameter, -800, 150)
tint.set_editor_property('parameter_name', 'GoldColor')
tint.set_editor_property('default_value', u.LinearColor(1.0, 0.48, 0.06, 1.0))
glow = scalar('GlowStrength', 8.0, -800, 330)
opacity = scalar('Visibility', 1.0, -800, 500)
fade_in = scalar('FadeInFraction', 0.1, -800, 680)
fade_out = scalar('FadeOutFraction', 0.15, -800, 820)
age = node(u.MaterialExpressionParticleRelativeTime, -800, 980)
fade = node(u.MaterialExpressionCustom, -420, 650)
fade.set_editor_property('code', 'return saturate(Age / max(FadeIn, 0.0001)) * saturate((1.0 - Age) / max(FadeOut, 0.0001));')
fade.set_editor_property('output_type', u.CustomMaterialOutputType.CMOT_FLOAT1)
fade.set_editor_property('inputs', [custom_input('Age'), custom_input('FadeIn'), custom_input('FadeOut')])
connect(age, '', fade, 'Age')
connect(fade_in, '', fade, 'FadeIn')
connect(fade_out, '', fade, 'FadeOut')
prev = sample
prev_pin = 'R'
for other, x, y in [(tint, -400, -80), (glow, -170, -80), (fade, 40, -80), (opacity, 250, -80)]:
    mul = node(u.MaterialExpressionMultiply, x, y)
    connect(prev, prev_pin, mul, 'A')
    connect(other, '', mul, 'B')
    prev, prev_pin = mul, ''
assert lib.connect_material_property(prev, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
one = node(u.MaterialExpressionConstant, 250, 240)
one.set_editor_property('r', 1.0)
assert lib.connect_material_property(one, '', u.MaterialProperty.MP_OPACITY)
lib.layout_material_expressions(mat)
lib.recompile_material(mat)
mi = fresh('MI_TriangleGold', u.MaterialInstanceConstant, u.MaterialInstanceConstantFactoryNew())
lib.set_material_instance_parent(mi, mat)
lib.update_material_instance(mi)

fx = u.FXConverterUtilitiesLibrary
system = fresh('NS_TriangleLine', u.NiagaraSystem, u.NiagaraSystemFactoryNew())
ctx = fx.create_system_conversion_context(system)
emitter = ctx.add_empty_emitter('GoldTriangle')
emitter.set_sim_target(u.NiagaraSimTarget.CPU_SIM)
emitter.set_local_space(True)

def module(name, path, category, version=(1, 0)):
    return emitter.find_or_add_module_script(name, u.CreateScriptContextArgs(fx.create_asset_data(path), list(version)), category)
def set_input(script, name, value, enable_override=False):
    ok = script.set_parameter(name, value, enable_override, enable_override)
    report['input_results'].append({'parameter': name, 'accepted': bool(ok)})
    assert ok, 'Module input not accepted: ' + name

state = module('EmitterState', '/Niagara/Modules/Emitter/EmitterState.EmitterState', u.ScriptExecutionCategory.EMITTER_UPDATE)
set_input(state, 'Life Cycle Mode', fx.create_script_input_enum('/Niagara/Enums/ENiagaraEmitterLifeCycleMode.ENiagaraEmitterLifeCycleMode', 'Self'))
set_input(state, 'Loop Behavior', fx.create_script_input_enum('/Niagara/Enums/ENiagara_EmitterStateOptions.ENiagara_EmitterStateOptions', 'Once'))
set_input(state, 'Inactive Response', fx.create_script_input_enum('/Niagara/Enums/ENiagaraInactiveMode.ENiagaraInactiveMode', 'Complete (Let Particles Finish then Kill Emitter)'))
set_input(state, 'Loop Duration', fx.create_script_input_float(2.0))
burst = module('SpawnOne', '/Niagara/Modules/Emitter/SpawnBurst_Instantaneous.SpawnBurst_Instantaneous', u.ScriptExecutionCategory.EMITTER_UPDATE)
set_input(burst, 'Spawn Count', fx.create_script_input_int(1))
set_input(burst, 'Spawn Time', fx.create_script_input_float(0.0))
initialize = module('InitializeParticle', '/Niagara/Modules/Spawn/Initialization/V2/InitializeParticle.InitializeParticle', u.ScriptExecutionCategory.PARTICLE_SPAWN)
set_input(initialize, 'Lifetime', fx.create_script_input_float(2.0))
set_input(initialize, 'Sprite Size Mode', fx.create_script_input_enum('/Niagara/Enums/ENiagara_SizeScaleMode.ENiagara_SizeScaleMode', 'Non-Uniform'))
set_input(initialize, 'Sprite Size', fx.create_script_input_vec2(u.Vector2D(300.0, 300.0)), True)
module('ParticleState', '/Niagara/Modules/Update/Lifetime/ParticleState.ParticleState', u.ScriptExecutionCategory.PARTICLE_UPDATE, (1, 1))
emitter.set_parameter_directly('Particles.SpriteFacing', fx.create_script_input_vector(u.Vector(0.0, 0.0, 1.0)), u.ScriptExecutionCategory.PARTICLE_SPAWN)
emitter.set_parameter_directly('Particles.SpriteAlignment', fx.create_script_input_vector(u.Vector(1.0, 0.0, 0.0)), u.ScriptExecutionCategory.PARTICLE_SPAWN)
renderer = u.NiagaraSpriteRendererProperties()
renderer.set_editor_property('material', mi)
renderer.set_editor_property('facing_mode', u.NiagaraSpriteFacingMode.CUSTOM_FACING_VECTOR)
renderer.set_editor_property('alignment', u.NiagaraSpriteAlignment.CUSTOM_ALIGNMENT)
emitter.add_renderer('TriangleSprite', renderer)
ctx.finalize()
for asset in [texture, mat, mi, system]:
    assert u.EditorAssetLibrary.save_loaded_asset(asset, False), 'Could not save: ' + asset.get_path_name()
    report['assets'][asset.get_name()] = asset.get_path_name()
ctx.cleanup()

# A neutral checker floor makes empty areas and additive blending visible.
floor_mat = fresh('M_TrialFloor', u.Material, u.MaterialFactoryNew())
floor_mat.set_editor_property('shading_model', u.MaterialShadingModel.MSM_UNLIT)
floor_uv = lib.create_material_expression(floor_mat, u.MaterialExpressionTextureCoordinate, -450, 0)
floor_pattern = lib.create_material_expression(floor_mat, u.MaterialExpressionCustom, -180, 0)
floor_pattern.set_editor_property('code', 'float2 p=floor(UV*20.0); float v=fmod(p.x+p.y,2.0); return lerp(float3(0.015,0.019,0.025),float3(0.03,0.037,0.047),v);')
floor_pattern.set_editor_property('output_type', u.CustomMaterialOutputType.CMOT_FLOAT3)
floor_pattern.set_editor_property('inputs', [custom_input('UV')])
assert lib.connect_material_expressions(floor_uv, '', floor_pattern, 'UV')
assert lib.connect_material_property(floor_pattern, '', u.MaterialProperty.MP_EMISSIVE_COLOR)
lib.recompile_material(floor_mat)
assert u.EditorAssetLibrary.save_loaded_asset(floor_mat, False)

level_path = DEST + '/L_TriangleTrial'
level = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert level.new_level(level_path)
actors = u.get_editor_subsystem(u.EditorActorSubsystem)
floor = actors.spawn_actor_from_class(u.StaticMeshActor, u.Vector(0, 0, -5))
floor.set_actor_label('Background checker floor')
floor.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Plane'))
floor.static_mesh_component.set_material(0, floor_mat)
floor.set_actor_scale3d(u.Vector(12, 12, 1))
effect = actors.spawn_actor_from_class(u.NiagaraActor, u.Vector(0, 0, 0))
effect.set_actor_label('GoldTriangle_OneParticle')
effect.get_component_by_class(u.NiagaraComponent).set_asset(system)
camera_pos = u.Vector(420, -500, 500)
camera = actors.spawn_actor_from_class(u.CineCameraActor, camera_pos, u.MathLibrary.find_look_at_rotation(camera_pos, u.Vector(0, 0, 0)))
camera.set_actor_label('TrialCamera')
camera.set_editor_property('auto_activate_for_player', u.AutoReceiveInput.PLAYER0)
camera.get_cine_camera_component().set_editor_property('current_focal_length', 38.0)
sequence = fresh('LS_TriangleTrial', u.LevelSequence, u.LevelSequenceFactoryNew())
sequence.set_display_rate(u.FrameRate(30, 1))
sequence.set_playback_start(0)
sequence.set_playback_end(96)
binding = sequence.add_possessable(camera)
cut = sequence.add_track(u.MovieSceneCameraCutTrack).add_section()
cut.set_range(-30, 96)
bid = u.MovieSceneObjectBindingID()
bid.set_editor_property('guid', binding.get_id())
cut.set_camera_binding_id(bid)
effect_binding = sequence.add_possessable(effect.get_component_by_class(u.NiagaraComponent))
life = effect_binding.add_track(u.MovieSceneNiagaraSystemTrack).add_section()
life.set_range(0, 96)
life.set_editor_property('age_update_mode', u.NiagaraAgeUpdateMode.DESIRED_AGE)
life.set_editor_property('section_evaluate_behavior', u.NiagaraSystemSpawnSectionEvaluateBehavior.NONE)
life.set_editor_property('section_end_behavior', u.NiagaraSystemSpawnSectionEndBehavior.DEACTIVATE)
assert u.EditorAssetLibrary.save_loaded_asset(sequence, False)
assert level.save_current_level()
report['assets']['L_TriangleTrial'] = level_path
report['assets']['LS_TriangleTrial'] = sequence.get_path_name()
report['parameters'] = {'spawn_count': 1, 'spawn_time_seconds': 0, 'lifetime_seconds': 2, 'size_cm': [300, 300], 'fade_in_seconds': 0.2, 'hold_seconds': 1.5, 'fade_out_seconds': 0.3, 'motion': 'stationary horizontal plane', 'color_linear': [1.0, 0.48, 0.06], 'glow': 8.0}
(ROOT / 'build-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
u.log('TRIANGLE_BUILD_COMPLETE=' + str(ROOT / 'build-report.json'))
u.SystemLibrary.quit_editor()
