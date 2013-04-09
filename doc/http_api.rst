==============
HTTP Interface
==============

This exposes data via a REST interface.


Resources
=========

/project/:project_name
----------------------

Method: ``POST``
~~~~~~~~~~~~~~~~

Creates a new project with the given :project_name

:name:        Project name
:version:     Initial version (will be incremented by each git commit or hudson git tag)
:git_url:     Repository URL to watch
:branch:      Branch to follow
:build_cmd:   Command within your project that generate binaries or prepare your project to be installed
:install_cmd: A command within your project that install the generated binaries
:repo_url:    A FTP package repository that your package will be uploaded
:repo_user:   FTP user for this repository
:repo_passwd: FTP user password for the repository


/project/:project_name
----------------------

Method: ``GET``
~~~~~~~~~~~~~~~

Retrieve the project's information.



/project/:project_name
----------------------

Method: ``DELETE``
~~~~~~~~~~~~~~~~~~

Delete a project


/project/:project_name
----------------------

Method: ``POST``
~~~~~~~~~~~~~~~~

Schedule a build for a given branch

:branch: Inform the branch that will schedule a build


/build/:project_name
--------------------

Method: ``GET``
~~~~~~~~~~~~~~~

Get builds for a given project



/log/:project_name/:build_number
--------------------------------

Method: ``GET``
~~~~~~~~~~~~~~~

Return the logfile for the given build number


/cache/:project_name
--------------------

Method: ``DELETE``
~~~~~~~~~~~~~~~~~~

Clear the project cache


/group
------

Method: ``POST``
~~~~~~~~~~~~~~~~

Create a group

:name: The group name
:repo_addr: The package repository URL
:repo_user: The package repository user
:repo_passwd: The package repository password



Default return for PUT and DELETE requests
==========================================

Payload failure case
--------------------

::

  {"status": "fail"}



Payload success case
--------------------

::

  {"status": "ok"}
