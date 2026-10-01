"""Render real UE frames through Movie Render Queue after editor startup."""
from pathlib import Path
import json
import unreal as u
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'Preview/frames'
OUT.mkdir(parents=True,exist_ok=True)
u.EditorPythonScripting.set_keep_python_script_alive(True)
world=u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
u.SystemLibrary.execute_console_command(world,'fx.Niagara.ForceWaitForCompilationOnActivate 1')
subsystem=u.get_editor_subsystem(u.MoviePipelineQueueSubsystem)
queue=subsystem.get_queue()
queue.delete_all_jobs()
job=queue.allocate_new_job(u.MoviePipelineExecutorJob)
job.job_name='Gold triangle only'
job.map=u.SoftObjectPath('/Game/TriangleLine/L_TriangleTrial.L_TriangleTrial')
job.sequence=u.SoftObjectPath('/Game/TriangleLine/LS_TriangleTrial.LS_TriangleTrial')
config=job.get_configuration()
output=config.find_or_add_setting_by_class(u.MoviePipelineOutputSetting)
output.output_directory=u.DirectoryPath(str(OUT))
output.file_name_format='triangle_{frame_number}'
output.output_resolution=u.IntPoint(1280,720)
output.use_custom_frame_rate=True
output.output_frame_rate=u.FrameRate(30,1)
output.override_existing_output=True
config.find_or_add_setting_by_class(u.MoviePipelineImageSequenceOutput_PNG)
config.find_or_add_setting_by_class(u.MoviePipelineDeferredPassBase)
aa=config.find_or_add_setting_by_class(u.MoviePipelineAntiAliasingSetting)
aa.spatial_sample_count=1
aa.temporal_sample_count=1
aa.engine_warm_up_count=32
aa.render_warm_up_count=8
aa.use_camera_cut_for_warm_up=False
aa.render_warm_up_frames=True
camera_setting=config.find_or_add_setting_by_class(u.MoviePipelineCameraSetting)
camera_setting.shutter_timing=u.MoviePipelineShutterTiming.FRAME_OPEN
executor=u.MoviePipelinePIEExecutor()
u.get_default_object(u.MoviePipelinePIEExecutorSettings).set_editor_property('initial_delay_frame_count',60)
def finished(executor,success):
    (ROOT/'Preview/render-report.json').write_text(json.dumps({'engine':u.SystemLibrary.get_engine_version(),'success':bool(success),'frames':len(list(OUT.glob('*.png'))),'method':'native UE Movie Render Queue, PNG output, 30fps, 1280x720'},indent=2),encoding='utf-8')
    u.SystemLibrary.quit_editor()
def failed(executor,pipeline,is_fatal,text):
    u.log_error(str(text))
executor.on_executor_finished_delegate.add_callable_unique(finished)
executor.on_executor_errored_delegate.add_callable_unique(failed)
subsystem.render_queue_with_executor_instance(executor)
