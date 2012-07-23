import os
import sys
import shutil
import time
import re
import logging as log
import subprocess
import ftplib
import tarfile
import pystache

from projects import Projects
from config import BrickConfig
from build_info import BuildInfo

from git import Git
from glob import glob
from types import *

class BuilderRpm():

    def __init__(self, builder):
        self.builder = builder
        self.project = self.builder.project
        self.distribution = None
        self.version = None

    def dos2unix(self, file):
        f = open(file, 'r').readlines()
        new_file = open(file, "w+")
        match = re.compile('\r\n')
        for line in f:
            new_file.write(match.sub('\n', line))
        new_file.close()

    def build(self, branch, last_tag=None):
        templates_dir = os.path.join(self.builder.templates_dir, 'rpm')
        rpm_dir = os.path.join(self.builder.workdir, 'redhat')
        spec_filename = os.path.join(rpm_dir, 'SPECS', "%s.spec" % self.project.name)

        self.build_info = BuildInfo(self.project.name)
        logfile = os.path.join(self.builder.workspace, 'log', '%s.%s.log' % (self.project.name, self.build_info.build_id))
        self.build_info.log(logfile)
        self.stdout = open(logfile, 'a+')
        self.stderr = self.stdout

        if last_tag != None and last_tag.startswith('stable'):
            self.project.version('stable', last_tag.split('_')[1])
            self.build_info.version(self.project.version('stable'))
            self.version = self.project.version('stable')
            self.distribution = 'stable'

        elif last_tag != None and last_tag.startswith('testing'):
            self.project.version('testing', last_tag.split('_')[1])
            self.build_info.version(self.project.version('testing'))
            self.version = self.project.version('testing')
            self.distribution = 'testing'

        elif last_tag != None and last_tag.startswith('unstable'):
            self.project.version('unstable', last_tag.split('_')[1])
            self.build_info.version(self.project.version('unstable'))
            self.version = self.project.version('unstable')
            self.distribution = 'unstable'

        else:
            """
            otherwise it should change the distribution to unstable
            """
            if self.project.version(branch):
                version_list = self.project.version(branch).split('.')
                version_list[len(version_list) - 1] = str(int(version_list[len(version_list) - 1]) + 1)
                self.project.version(branch, '.'.join(version_list))
                self.build_info.version(self.project.version(branch))
                self.version = self.project.version(branch)
                self.distribution = 'experimental'

        dir_prefix = "%s-%s" % (self.project.name, self.version)

        for dir in ('SOURCES', 'SPECS', 'RPMS', 'SRPMS', 'BUILD', 'TMP'):
            if os.path.isdir(os.path.join(rpm_dir, dir)):
                shutil.rmtree(os.path.join(rpm_dir, dir))
            os.makedirs(os.path.join(rpm_dir, dir))

        build_dir = os.path.join(rpm_dir, 'TMP', self.project.name)
        os.makedirs(build_dir)

        if os.path.isdir(os.path.join(rpm_dir, dir_prefix)):
            shutil.rmtree(os.path.join(rpm_dir, dir_prefix))
        os.makedirs(os.path.join(rpm_dir, dir_prefix))

        subprocess.call(["cp -rP `ls -a | grep -Ev '\.$|\.\.$|debian$|redhat$'` %s" %
            os.path.join(rpm_dir, dir_prefix)],
            cwd=self.builder.workdir,
            shell=True
        )

        cur_dir = os.getcwd()
        os.chdir(rpm_dir)

        source_file = os.path.join(rpm_dir, 'SOURCES', '%s.tar.gz' % dir_prefix)
        tar = tarfile.open(source_file, 'w:gz')
        tar.add(dir_prefix)
        tar.close()
        shutil.rmtree(dir_prefix)
        os.chdir(cur_dir)

        if self.project.install_prefix is None:
            self.project.install_prefix = 'opt'

        if not self.project.install_cmd:

            self.project.install_cmd = 'cp -r \`ls -a | grep -Ev "\.$|\.\.$|debian$"\` %s/%s/%s' % (
                    build_dir,
                    self.project.install_prefix,
                    self.project.name
                )

        template_data = {
                'name': self.project.name,
                'version': self.version,
                'build_dir': build_dir,
                'build_cmd': self.project.build_cmd,
                'install_cmd': self.builder.mod_install_cmd,
                'username': self.project.username,
                'email': self.project.email,
                'date': time.strftime("%a %h %d %Y"),
                'git_url': self.project.git_url,
                'source': source_file,
            }

        rvm_rc = os.path.join(self.builder.workdir, '.rvmrc')
        rvm_rc_example = rvm_rc +  ".example"
        has_rvm = False

        environment = None

        if os.path.isfile(rvm_rc):
            has_rvm = True
        elif os.path.isfile(rvm_rc_example):
            has_rvm = True
            rvm_rc = rvm_rc_example

        if has_rvm:
            rvmexec = open(rvm_rc).read()
            log.info("RVMRC: %s" % rvmexec)

            # I need the output not to log on file
            rvm_cmd = subprocess.Popen('/usr/local/rvm/bin/rvm info %s' % rvmexec.split()[1],
                    shell=True, stdout=subprocess.PIPE)
            rvm_cmd.wait()

            rvm_env = {}
            for line in rvm_cmd.stdout.readlines():
                if 'PATH' in line or 'HOME' in line:
                    name, value = line.split()
                    rvm_env[name.strip(':')] = value.strip('"')
            rvm_env['HOME'] = os.environ['HOME']

            if len(rvm_env.keys()) < 1:
                rvm_env = os.environ
            else:
                try:
                    os.environ.pop('PATH')
                    os.environ.pop('GEM_HOME')
                    os.environ.pop('BUNDLER_PATH')
                except Exception, e:
                    pass
                for param in os.environ.keys():
                    if param.find('PROXY') != -1:
                        rvm_env[param] = os.environ[param]
                rvm_env.update(os.environ)

            environment = rvm_env
            log.info(environment)

        if os.path.isfile(os.path.join(self.builder.workdir, 'rpm', "%s.spec" % self.project.name)):
            self.dos2unix(os.path.join(self.builder.workdir, 'rpm', "%s.spec" % self.project.name))
            template_fd = open(os.path.join(self.builder.workdir, 'rpm', "%s.spec" % self.project.name))
        else:
            template_fd = open(os.path.join(templates_dir, 'project.spec'))

        rendered_template = open(spec_filename, 'w+')
        rendered_template.write(pystache.template.Template(template_fd.read()).render(context=template_data))
        template_fd.close()
        rendered_template.close()

        rendered_template = open(spec_filename, 'a')
        rendered_template.write("* %(date)s %(username)s <%(email)s> - %(version)s-1\n" % template_data)

        for git_log in self.builder.git.log():
            rendered_template.write('- %s' % git_log)
        rendered_template.close()

        self.project.save()

        if type(environment) is NoneType:
            environment = os.environ

        rpm_cmd = self.builder._exec([ "rpmbuild", "--define", "_topdir %s" % rpm_dir, "-ba", spec_filename ],
            cwd=self.builder.workdir, env=environment, stdout=self.stdout, stderr=self.stderr
        )

        rpm_cmd.wait()

        for path, dirs, files in os.walk(rpm_dir):
            if os.path.isdir(path):
                for file in (os.path.join(path, file) for file in files):
                    try:
                        if os.path.isfile(file) and file.endswith('.rpm'):
                            shutil.copy(file, self.builder.workspace)
                    except Exception, e:
                        log.error(e)

        shutil.rmtree(rpm_dir)

    def upload(self, branch):
        repository_url, user, passwd = self.project.repository()
        repository_dir = self.distribution

        files = glob(os.path.join(self.builder.workspace,
            '%s-%s%s' % (self.project.name,
                self.version,
                '*.rpm')
            )
        )

        if len(files) > 0:
            if repository_dir != None:
                ftp = ftplib.FTP()
                try:
                    ftp.connect(repository_url)
                    log.error('Repository: %s' % repository_url)
                    ftp.login(user, passwd)
                    ftp.cwd(repository_dir)
                except ftplib.error_reply, e:
                    log.error('Cannot conect to ftp server %s' % e)

                for file in files:
                    filename = os.path.basename(file)
                    try:
                        if os.path.isfile(file):
                            f = open(file, 'rb')
                            ftp.storbinary('STOR %s' % filename, f)
                            f.close()
                            log.info("File %s has been successfully sent to repository_url %s" % (filename, repository_url))
                    except ftplib.error_reply, e:
                        log.error(e)

            ftp.quit()

