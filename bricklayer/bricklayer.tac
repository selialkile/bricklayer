import sys
import os
import logging
sys.path.append('.')

import bricklayer
sys.path.append(os.path.dirname(bricklayer.__file__))
sys.path.append(os.path.join(os.path.dirname(bricklayer.__file__), 'utils'))

import pystache

from twisted.application import internet, service
from twisted.internet import protocol, task, threads, reactor
from twisted.protocols import basic
from twisted.python import log

from builder import Builder, build_project
from projects import Projects
from git import Git
from config import BrickConfig
from rest import restApp
from dreque import Dreque, DrequeWorker


class BricklayerFactory(protocol.ServerFactory):
    protocol = basic.LineReceiver()

    def __init__(self):
        self.sched_projects()
    
    def send_job(self, project_name, branch, release, version):
        log.msg('sched build: %s [%s:%s]' % (project_name, release, version))
        brickconfig = BrickConfig()
        queue = Dreque(brickconfig.get('redis', 'redis-server'))
        queue.enqueue('build', 'builder.build_project', {
            'project': project_name, 
            'branch': branch, 
            'release': release, 
            'version': version,
            })

    def sched_builder(self):
        for project in Projects.get_all():
            try:
                if project.is_building():
                    log.msg("project %s still building, skip" % project.name)
                    continue
                branch = "master"
                git = Git(project)
                if os.path.isdir(git.workdir):
                    git.checkout_branch(branch)
                    git.pull()
                else:
                    git.clone(branch)

                for remote_branch in git.branches(remote=True):
                    git.checkout_remote_branch(remote_branch.replace('origin/', ''))

                for release in ('stable', 'testing', 'unstable'):
                    if project.last_tag(release) != git.last_tag(release):
                        try:
                            _, version = git.last_tag(release).split('_')
                            log.msg("new %s tag, building version: %s" % (release, version))
                            d = threads.deferToThread(self.send_job, project.name, branch, release, version)
                        except Exception, e:
                            log.msg("tag not parsed: %s:%s" % (project.name, git.last_tag(release)))
                
                if int(project.experimental) == 1:
                    for branch in project.branches():
                        git.checkout_remote_branch(branch)
                        git.checkout_branch(branch)
                        git.pull()
                        if project.last_commit(branch) != git.last_commit(branch):
                            project.last_commit(branch, git.last_commit(branch))
                            d = threads.deferToThread(self.send_job, project.name, branch, 'experimental', None)

                        git.checkout_branch("master")

            except Exception, e:
                log.msg("Something went really wrong: %s" % repr(e))
                

    def sched_projects(self):
        sched_task = task.LoopingCall(self.sched_builder)
        sched_task.start(10.0)

brickconfig = BrickConfig()
unix_socket = brickconfig.get('server', 'unix')

bricklayer = service.MultiService()

factory = BricklayerFactory()
brickService = internet.UNIXServer(unix_socket, factory)

brickService.setServiceParent(bricklayer)

application = service.Application("Bricklayer")
bricklayer.setServiceParent(application)
