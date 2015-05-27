from __future__ import with_statement
"""
Fabcommon is a reusable deployment script in fabric
Copyright (c) 2015, Miguel Marcos.
License: MIT (see LICENSE for details)
"""

__author__ = 'Miguel Marcos'
__version__ = '0.9.0'
__license__ = 'MIT'

import os
import re
from fabric.api import local, settings, abort, env, run, cd, prefix
from fabric.contrib.console import confirm

# default settings
env.repository_type = 'git'
# can be 'release' - new virtualenv for every release, 'project' - one 
#virtualenv for all releases or None - no virtualenv.
env.venv_scope = 'project' 

def sort_versions(versions, reverse=False): 
    # small hack to ensure final versions come after pre-releases
    versions = [version + 'z' for version in versions]
    convert = lambda text: int(text) if text.isdigit() else text.lower() 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)] 
    versions = sorted(versions, key=alphanum_key)
    # remove hack after sorting
    versions = [version[:-1] for version in versions]
    if reverse:
        versions.reverse()
    return versions

def verify_or_increase_version(version_pre_release, message):
    '''
    If version is a recognized keyword it increments the version number by 
    looking into the tag list, picking up the highest version that conforms to 
    the semver.org spec, and increasing the correct level according to the 
    pattern: major.minor.patch[-alpha.n|beta.n|rc.n]
    Possible keywords are: major|minor|patch|release[-]alpha|beta|rc
    alpha, beta and rc versions can only be created together with a new version
    or on top of an existing pre-release, so major-beta is possible but beta is 
    only possible if an alpha pre-release or a beta pre-release already exists
    on the latest version. 
    release is not possible to combine with alpha, beta or rc keywords. This
    keyword will remove the pre-release label and will keep the version number. 
    If version is not a keyword and it exists in the tag list, then version is 
    returned without any changes.
    If version is not a keyword and is not in the tag list, an Exception is 
    raised 
    '''
    # get all tags into a list
    tags = local('git tag -l "*.*.*"', capture=True).split()
    
    # if it's an existing version, then just return it
    if version_pre_release in tags:
        return version_pre_release
    
    # otherwise it's assumed to be a keyword to increase the version number
    version_pre_release = version_pre_release.split('-')
    if len(version_pre_release) == 2 and \
       version_pre_release[0] in ('major', 'minor', 'patch') and \
       version_pre_release[1] in ('alpha', 'beta', 'rc'):
        version, pre_release = version_pre_release
    elif len(version_pre_release) == 1:
        if version_pre_release[0] in ('alpha', 'beta', 'rc'):
            version = ''
            pre_release = version_pre_release[0]
        elif version_pre_release[0] in ('major', 'minor', 'patch', 'release'):
            version = version_pre_release[0]
            pre_release = ''
        else:
            raise Exception('Version does not exist or invalid keyword')
    else:
        raise Exception('Version does not exist or invalid keyword')
    
    if not tags:
        tags = ['0.0.0']
    # do a natural sort with descending order 
    tags = sort_versions(tags, reverse=True)

    # look for the first semver.org compatible version
    version_pattern = re.compile('(\d+)\.(\d+)\.(\d+)(-[^\+]+)?(\+.+)?')
    for tag in tags:
        version_match = version_pattern.match(tag)
        new_version = []
        new_pre_release = []
        if version_match:
            # create array with major, minor and patch numbers
            if version == 'major':
                new_version = [str(int(version_match.group(1)) + 1), '0', '0']
            elif version == 'minor':
                new_version = [version_match.group(1), 
                               str(int(version_match.group(2)) + 1), '0']
            elif version == 'patch':
                new_version = [version_match.group(1), version_match.group(2),
                               str(int(version_match.group(3)) + 1)]
            elif version == 'release' and not version_match.group(4):
                    raise Exception('There is already a final release, use ' +\
                                    'major|minor|patch[-]alpha|beta|rc instead')
            else:
                new_version = [(version_match.group(1)), 
                               (version_match.group(2)),
                               (version_match.group(3))]
            
            # pre_release is optional, it is only possible to create a new
            # pre-release if a final version does not exist yet (one without a
            # pre-release appended), an alpha version cannot be
            # created/increased if a beta or rc version exists and a beta
            # version cannot be created/increased if an rc version exists.
            if pre_release:
                previous_pre_release = version_match.group(4)
                if version:
                    new_pre_release = [pre_release, '1']
                elif previous_pre_release:
                    previous_pre_release = previous_pre_release[1:].split('.')
                    if previous_pre_release[0] == pre_release:
                        new_pre_release = [pre_release, \
                                          str(int(previous_pre_release[1]) + 1)]
                    elif previous_pre_release[0] == 'alpha' and \
                            pre_release in ('beta', 'rc'):
                            new_pre_release = [pre_release, '1']
                    elif previous_pre_release[0] in ('alpha', 'beta') and \
                            pre_release == 'rc':
                            new_pre_release = [pre_release, '1']
                    else:
                        raise Exception('Unable to increase pre-release')

            increased_version = ('.'.join(new_version) + '-' + '.'.\
                                 join(new_pre_release)).rstrip('-')
            local('git tag -a {0} -m \'{1}\''.format(increased_version, 
                                                     message))
            local('git push --quiet --tags')
            return increased_version
    return None
    

def deploy(version, message='', update_cron=False):
    releases_path = os.path.join(env.base_path, 'releases')
    # if no specific version number is specified we will increment the current 
    # one based on how big the changes are.
    
    version = verify_or_increase_version(version, message)
    # create a releases directory if one doesn't exist
    run('mkdir -p ' + releases_path)
    with cd(releases_path):
        # export the source code to the build directory if not already there
        run('if [ ! -d ' + version + ' ]; then ' + \
            'git clone ' + env.repository + ' ' + version +\
            ' && cd ' + version + ' && git checkout -b tags/' + version +\
            ' && rm -rf .git; fi')
        if env.venv_scope == 'release':
            # setup virtualenv and install dependencies, if not already there
            run('cd ' + version + ' && if [ ! -d venv ]; then ' +\
                'virtualenv venv ' +\
                '&& source venv/bin/activate ' +\
                '&& pip install -qr src/requirements.txt; fi')
    
    if env.venv_scope == 'release':
        # add a symlink to venv
        run('rm -rf ' + os.path.join(env.base_path, 'venv'))
        run('ln -sfn ' + os.path.join(releases_path, version, 'venv') + ' ' +\
            os.path.join(env.base_path, 'venv'))
    elif env.venv_scope == 'project':
        with cd(env.base_path):
            run('if [ ! -d venv ]; then ' +\
                'rm -rf venv ' +\
                '&& virtualenv venv; fi ' +\
                '&& source venv/bin/activate ' +\
                '&& pip install -qr ' + os.path.join(releases_path, version, \
                                                     'src/requirements.txt'))       
    
    # create a logs and media dirs if they do not exist
    run('mkdir -p ' + os.path.join(env.base_path, 'logs'))
    run('mkdir -p ' + os.path.join(env.base_path, 'media'))
    # add a symlink to the media folder
    run('rm -rf ' + os.path.join(releases_path, version, 'media') +\
        ' && ln -s '+ os.path.join(env.base_path, 'media') + ' ' +\
        os.path.join(releases_path, version, 'media'))
    
    if env.pre_activate_task:
        env.pre_activate_task(releases_path, version)
        
    # update the crontab if crontab.txt exists and update_cron is True
    # the crontab can have a template variable {{ project_dir }} that will
    # be replace with the current 
    if update_cron:
        with cd(os.path.join(releases_path, version)):
            run('if [ -f crontab.txt ]; then ' + \
                'crontab -r && cat crontab.txt | ' + \
                'sed -e \'s,{{ project_dir }},\'$PWD\',\' | crontab; fi')
 
    # activate the build
    run('ln -sfn ' + os.path.join(releases_path, version, 'src') + ' ' +\
        os.path.join(env.base_path, 'src'))
    
    # only keep the 10 most recent releases
    with cd(releases_path):
        run('ls -t | sed \'s,\\(.*\\),"\\1",\' | tail -n+10 | xargs rm -rf')
        
