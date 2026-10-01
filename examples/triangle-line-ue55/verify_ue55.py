"""Reload saved native assets and check actual CPU Niagara particle data."""
import json
import time
from pathlib import Path
import unreal as u
ROOT=Path(__file__).resolve().parent
report={'engine':u.SystemLibrary.get_engine_version(),'assets':{},'samples':[]}
for name in ['T_TriangleLine','M_TriangleGold','MI_TriangleGold','NS_TriangleLine','M_TrialFloor','L_TriangleTrial','LS_TriangleTrial']:
    asset=u.load_asset('/Game/TriangleLine/'+name)
    assert asset, name
    report['assets'][name]=asset.get_path_name()
texture=u.load_asset('/Game/TriangleLine/T_TriangleLine')
material=u.load_asset('/Game/TriangleLine/M_TriangleGold')
report['material']={'texture_srgb':texture.get_editor_property('srgb'),'texture_compression':str(texture.get_editor_property('compression_settings')),'blend_mode':str(material.get_editor_property('blend_mode')),'shading_model':str(material.get_editor_property('shading_model')),'scalar_parameters':{n:u.MaterialEditingLibrary.get_material_default_scalar_parameter_value(material,n) for n in ['GlowStrength','Visibility','FadeInFraction','FadeOutFraction']}}
level=u.get_editor_subsystem(u.LevelEditorSubsystem)
assert level.load_level('/Game/TriangleLine/L_TriangleTrial')
actor=next(a for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors() if isinstance(a,u.NiagaraActor))
comp=actor.get_component_by_class(u.NiagaraComponent)
sim_cache=u.NiagaraSimCacheFunctionLibrary.create_niagara_sim_cache(comp)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.SystemLibrary.execute_console_command(world,'fx.Niagara.ForceWaitForCompilationOnActivate 1')
u.EditorPythonScripting.set_keep_python_script_alive(True)
start=time.perf_counter()
def verify_tick(delta):
    if time.perf_counter()-start < 3:
        return
    u.unregister_slate_post_tick_callback(callback)
    try:
        comp.set_force_solo(True)
        # The editor may already be playing the placed actor. Clear that instance
        # before measuring a fresh trigger; Activate(reset) alone can keep old particles.
        comp.reinitialize_system()
        comp.set_component_tick_enabled(False)
        assert comp.is_active(), 'System did not activate after compile and world initialization'
        for i in range(66):
            comp.advance_simulation(1,1/30)
            if i in [0,2,5,29,50,56,59,60,64,65]:
                cache=u.NiagaraSimCacheFunctionLibrary.capture_niagara_sim_cache_immediate(sim_cache,u.NiagaraSimCacheCreateParameters(),comp)
                row={'seconds':round((i+1)/30,6),'active':comp.is_active(),'captured':bool(cache)}
                if cache:
                    names=cache.get_emitter_names()
                    assert len(names)==1, names
                    row['particle_count']=len(cache.read_position_attribute('Position',names[0],True,0))
                    row['age']=[float(x) for x in cache.read_float_attribute('Age',names[0],0)]
                    row['lifetime']=[float(x) for x in cache.read_float_attribute('Lifetime',names[0],0)]
                    row['sprite_size_cm']=[[v.x,v.y] for v in cache.read_vector2_attribute('SpriteSize',names[0],0)]
                report['samples'].append(row)
        assert all(s['particle_count']==1 for s in report['samples'] if s['seconds']<2), report['samples']
        assert all(abs(s['lifetime'][0]-2)<0.001 and s['sprite_size_cm'][0]==[300,300] for s in report['samples'] if s['seconds']<2), report['samples']
        assert all(not s['active'] or s.get('particle_count')==0 for s in report['samples'] if s['seconds']>2.1), report['samples']
        report['passed']=True
    except Exception as exc:
        report['passed']=False
        report['error']=str(exc)
        u.log_error(str(exc))
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    u.SystemLibrary.quit_editor()
callback=u.register_slate_post_tick_callback(verify_tick)
