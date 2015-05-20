import os
from fabric.api import env, run, cd, prefix
from fabcommon import deploy


env.repository = 'my_repository'


def django_pre_activate_task(releases_path, version):
    with cd(os.path.join(releases_path, version)):
        # create local_settings.py file if not there
        run('cd config') + \
            ' && if [ ! -f settings_local.py ]; then ' + \
            'cp '+ env.local_settings + ' settings_local.py; fi')
        with prefix('source venv/bin/activate'):
            run('./manage.py collectstatic --noinput')
            run('./manage.py syncdb --noinput')
            run('./manage.py migrate')

env.pre_activate_task = django_pre_activate_task


def prod():
    env.hosts = ['127.0.0.1']
    env.base_path = '/www/my_project'
    env.local_settings = 'settings_prod.py'


def stage():
    env.hosts = ['127.0.0.1']
    env.base_path = '/www/my_project_stage'
    env.local_settings = 'settings_stage.py'


