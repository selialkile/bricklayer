import sys
import os
import subprocess
import time
import ConfigParser
import shutil
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.append(os.path.dirname(__file__))

import pystache
import git

from twisted.internet import threads, reactor, defer
from config import BrickConfig
from projects import Projects

from rpm_builder import RpmBuilder
from deb_builder import DebBuilder
from dreque import Dreque

config = BrickConfig()
redis_server = config.get('redis', 'redis-server')
log_file = config.get('log', 'file')

queue = Dreque(redis_server)

logging.basicConfig(filename=log_file, level=logging.DEBUG)
log = logging.getLogger('builder')

@defer.inlineCallbacks
def build_project(kargs):
    builder = Builder(kargs['project'])
    kargs.pop('project')
    yield builder.build_project(**kargs)

class Builder:
    def __init__(self, project):
        self.workspace = BrickConfig().get('workspace', 'dir')
        self.project = Projects(project)
        self.templates_dir = BrickConfig().get('workspace', 'template_dir')
        self.git = git.Git(self.project)
        self.workdir = self.git.workdir
        self.build_system = BrickConfig().get('build', 'system')

        if self.build_system == 'rpm':
            self.package_builder = RpmBuilder(self)
        elif self.build_system == 'deb':
            self.package_builder = DebBuilder(self)

        if self.build_system == 'rpm':
            self.mod_install_cmd = self.project.install_cmd.replace(
                'BUILDROOT', '%{buildroot}'
            )
        elif self.build_system == 'deb' or self.build_system == None:
            self.mod_install_cmd = self.project.install_cmd.replace(
                'BUILDROOT', 'debian/tmp'
            )

        if not os.path.isdir(self.workspace):
            os.makedirs(self.workspace)

        if not os.path.isdir(os.path.join(self.workspace, 'log')):
            os.makedirs(os.path.join(self.workspace, 'log'))

        self.stdout = None
        self.stderr = self.stdout

    def _exec(self, cmd, *args, **kwargs):
        return subprocess.Popen(cmd, *args, **kwargs)

    def build_project(self, branch=None, release=None, version=None):
        if not self.project.is_building():
            self.project.start_building()
            try:
                self.oldworkdir = self.workdir
                if not os.path.isdir("%s-%s" % (self.workdir, release)):
                    shutil.copytree(self.workdir, "%s-%s" % (self.workdir, release))
                self.workdir = "%s-%s" % (self.workdir, release)

                os.chdir(self.workdir)
                self.git.workdir = self.workdir
                self.git.pull()
                self.git.checkout_branch(branch)

                if release == 'experimental':
                    self.git.checkout_branch(branch)
                    self.package_builder.build(branch, release)
                    self.package_builder.upload(branch)
                else:
                    self.project.last_tag(release, self.git.last_tag(release))
                    self.git.checkout_tag(self.project.last_tag(release))
                    self.package_builder.build(branch, self.project.last_tag(release))
                    self.package_builder.upload(release)
                self.git.checkout_branch('master')
                
                self.workdir = self.oldworkdir

            except Exception, e:
                log.exception("build failed: %s" % repr(e))
            finally:
                self.project.stop_building()

