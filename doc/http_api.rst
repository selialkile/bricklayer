Creating projects
-----------------

:method: POST
:endpoint: /project/:project_name

Parameters
++++++++++

:name: Project name
:version: Initial version (will be incremented by each git commit or hudson git tag)
:git_url: Repository URL to watch
:branch: Branch to follow
:build_cmd: Command within your project that generate binaries or prepare your project to be installed
:install_cmd: A command within your project that install the generated binaries
:repo_url: A ftp package repository that your package will be uploaded
:repo_user: ftp user for this repository
:repo_passwd: ftp user password for the repository


Payload failure case
++++++++++++++++++++

::

  {"status": "fail"}



Payload success case
++++++++++++++++++++

::

  {"status": "ok"}



Info for a project
------------------

:method: GET
:endpoint: /project/:project_name


Delete a project
----------------

:method: DELETE
:endpoint: /project/:project_name


Schedule a build for a given branch
-----------------------------------

:method: POST
:endpoint: /project/:project_name

Parameters
++++++++++

:branch: Inform the branch that will schedule a build


Get builds
----------

:method: GET
:endpoint: /build/:project_name


Get logs
--------

Return the logfile for the given build number

:method: GET
:endpoint: /log/:project_name/:build_number


Clear cache
-----------

Clear the project cache

:method: DELETE
:endpoint: /cache/:project_name


Managing groups
---------------

Create a group

:method: POST
:endpoint: /group

Parameters
++++++++++

:name: The group name
:repo_addr: The package repository URL
:repo_user: The package repository user
:repo_passwd: The package repository password
