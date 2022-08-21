import os

BASE_FOLDER = os.environ.get('JOB_ORCHESTRATION_WORKSPACE')

config_source_location = os.path.join(BASE_FOLDER,'ConfigSources')
config_ready_location = os.path.join(BASE_FOLDER,'ConfigsToRun')
config_completed_location = os.path.join(BASE_FOLDER,'ConfigsCompleted')
config_failed_location = os.path.join(BASE_FOLDER,'ConfigsFailed')
output_location = os.path.join(BASE_FOLDER,'Output')
misc_location = os.path.join(BASE_FOLDER,'Misc')
workers_registration_path = os.path.join(misc_location, "workers.yaml")
config_yaml = "config.yaml"
max_error_count = 3