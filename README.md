# fabcommon
Reusable deployment script in fabric.

Fabcommon executes a number of tasks needed to deploy a typical web project in a 
Linux environment. It ws originally used to deploy Django projects, but the
current version should be able to deploy any kind of python web project.

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


Each project release will be stored in the releases directory and named as the project tag being deployed.
A symlink is then created in the root of the project to the src directory of the deployed tag.
A tag is usually a version number, but it can really be anything.
A logs, media and venv directories are also created if they don't already exist.

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


 

   