# fabcommon
Reusable deployment script in fabric.

Fabcommon executes a number of tasks needed to deploy a typical python based 
web project in a Linux environment. It was originally used to deploy Django 
projects, but the current version should be able to deploy any kind of python 
web project.

It assumes, by default, that projects have the following structure:

	{project_name}/
	   src/
	      requirements.txt
		  crontab.txt
	   ...

and will create a deploy with the following structure:

	{web_projects}/
	   {project_name}/
	      releases/
		     v1.0.0/
			 v1.0.1/
			 v1.0.2-beta/
			 ...
		  logs/
		     ...
		  media/
		     ...
		  src -> releases/{version}/src
		  venv/
		     ...

Each project release will be stored in the `releases` directory and named as the project tag being deployed.
A symlink is then created in the root of the project to the `src` directory of the deployed tag.
A tag is usually a version number, but it can really be anything.
A `logs`, `media` and `venv` directories are also created if they don't already exist.

In addition to creating the above layout it:

- optionally creates a version tag for the current commit or deploys 
  and existing tag to a git repository.
- creates a virtualenv and installs the needed dependencies from a requirements
  file. A new virtualenv can be created within every release or on the root of
  the project and updated with every deploy (default is project). 
- updates the crontab if it finds a crontab.txt file and update_cron is set to 
  True (default is False)
- runs additional user defined tasks
- limits the number of deploys in the relases directory to the last 10.


##Usage:

**Install fabcommon**

	sudo pip install git+https://github.com/mmarcos/fabcommon.git#egg=fabcommon

**Create a fabfile.py in your project**

in the file import deploy from fabcommon:

	from fabric.api import env, run, cd, prefix
	from fabcommon import deploy


setup the repository url for the project:

	env.repository = 'git+git://my_repository'

optionally create a function for additional tasks, for example:

	def django_pre_activate_task(releases_path, version):
	    with cd(os.path.join(releases_path, version)):
	        # create local_settings.py file if not there
	        run('cd src/config' + \
	            ' && if [ ! -f settings_local.py ]; then ' + \
	            'cp '+ env.local_settings + ' settings_local.py; fi')
	        with prefix('source ' + os.path.join(env.base_path, 'venv/bin/activate')):
	            run('src/manage.py collectstatic --noinput')
	            run('src/manage.py migrate')

add the newly created function to env:

	env.pre_activate_task = django_pre_activate_task

setup the different deploy environments, for example prodution or staging: 

	def production():
	    env.hosts = ['127.0.0.1', '127.0.0.2']
	    env.base_path = '/www/my_project'
	    env.local_settings = 'settings_prod.py'


	def staging():
	    env.hosts = ['127.0.0.3']
	    env.base_path = '/www/my_project_stage'
	    env.local_settings = 'settings_stage.py'

**Deploy:**
	
	fab staging deploy:{tag}
	

## Versioning

When deploying instead of first creating a tag, it is possible to tell fabcommon
to create a tag representing a new version. This is done by checking
the existing tags that are recognized as a version number and create a new one that
increments the highest version found.
The new version tag will be applied to the local commit in the active branch.

**Basic versioning:**

Version number follows the semanthic versioning convention, there are three
levels of decimal numbers: {major}.{minor}.{patch}
For example, version 1.2.3 has a major version of 1, a minor version of 2 and 
patch version 3.
Tagging a new version is a matter of using the keywords major, minor, or patch 
instead of a tag name, for example:

	fab staging deploy:minor

if the previous version was 1.2.3, then this deploy would create version 1.3.0



 

   