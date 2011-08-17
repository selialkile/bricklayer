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

class RpmBuilder():

    def __init__(self, builder):
        self.builder = builder
        self.project = self.builder.project
        self.distribution = None

    def dos2unix(self, file):
        f = open(file, 'r').readlines()
        new_file = open(file, "w+")
        match = re.compile('\r\n')
        for line in f:
            new_file.write(match.sub('\n', line))
        new_file.close()
        
    def build(self, branch, last_tag=None):
        templates_dir = os.path.join(self.builder.templates_dir, 'rpm')
        rpm_dir = os.path.join(self.builder.workspace, 'rpm')
        spec_filename = os.path.join(rpm_dir, 'SPECS', "%s.spec" % self.project.name)
        dir_prefix = "%s-%s" % (self.project.name, self.project.version())

        self.build_info = BuildInfo(self.project.name)
        logfile = os.path.join(self.builder.workspace, 'log', '%s.%s.log' % (self.project.name, self.build_info.build_id))
        self.build_info.log(logfile)
        self.stdout = open(logfile, 'a+')
        self.stderr = self.stdout

        for dir in ('SOURCES', 'SPECS', 'RPMS', 'SRPMS', 'BUILD', 'TMP'):
            if not os.path.isdir(os.path.join(rpm_dir, dir)):
                os.makedirs(os.path.join(rpm_dir, dir))
        
        build_dir = os.path.join(rpm_dir, 'TMP', self.project.name)
        
        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        source_file = os.path.join(rpm_dir, 'SOURCES', '%s.tar.gz' % dir_prefix)

        cur_dir = os.getcwd()
        os.chdir(self.builder.workspace)

        if os.path.isdir(dir_prefix):
            shutil.rmtree(dir_prefix)

        shutil.copytree(self.project.name, dir_prefix)

        if os.path.isfile(source_file):
            os.unlink(source_file)

        tar = tarfile.open(source_file, 'w:gz')
        tar.add(dir_prefix)
        tar.close()
        shutil.rmtree(dir_prefix)
        os.chdir(cur_dir)

        if self.project.install_prefix is None:
            self.project.install_prefix = 'opt'

        if not self.project.install_cmd:

            self.project.install_cmd = 'cp -r \`ls | grep -Ev "debian|rpm"\` %s/%s/%s' % (
                    build_dir,
                    self.project.install_prefix,
                    self.project.name
                )

        template_data = {
                'name': self.project.name,
                'version': self.project.version(branch),
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

            # Fix to rvm users that cannot read the f* manual
            # for this i need to fix their stupid .rvmrc
            if rvmexec.split()[1] == "use":
                rvmexec = rvmexec.split()[2]
            else:
                rvmexec = rvmexec.split()[1]
            
            # I need the output not to log on file
            rvm_cmd = subprocess.Popen('/usr/local/rvm/bin/rvm info %s' % rvmexec,
                    shell=True, stdout=subprocess.PIPE)
            rvm_cmd.wait()

            rvm_env = {}
            for line in rvm_cmd.stdout.readlines():
                if 'PATH' in line or 'HOME' in line:
                    name, value = line.split()
                    rvm_env[name.strip(':')] = value.replace('"', '')
            rvm_env['HOME'] = os.environ['HOME']

            if len(rvm_env.keys()) < 1:
                rvm_env = os.environ
            else:
                for param in os.environ.keys():
                    if param.find('PROXY') != -1:
                        rvm_env[param] = os.environ[param]
                try:
                    os.environ.pop('PATH')
                    os.environ.pop('GEM_HOME')
                    os.environ.pop('BUNDLER_PATH')
                except Exception, e:
                    pass
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

        if environment == None:
            environment = os.environ

        rpm_cmd = self.builder._exec([ "rpmbuild", "--define", "_topdir %s" % rpm_dir, "-ba", spec_filename ],
            cwd=self.builder.workdir, env=environment, stdout=self.stdout, stderr=self.stderr
        )

        rpm_cmd.wait()

    def upload(self, branch):
        repository_url, user, passwd = self.project.repository()
        repository_dir = self.distribution
        rpm_dir = os.path.join(self.builder.workspace, 'rpm')
        rpm_prefix = "%s-%s-1" % (self.project.name, self.project.version())
        list = []
        for path, dirs, files in os.walk(rpm_dir):
            if os.path.isdir(path):
                for file in (os.path.join(path, file) for file in files):
                    try:
                        if os.path.isfile(file) and file.find(rpm_prefix) != -1:
                            list.append(file)
                    except Exception, e:
                        log.error(e)

        if len(list) > 0:
            ftp = ftplib.FTP()
            try:
                ftp.connect(repository_url)
                ftp.login(user, passwd)
                ftp.cwd(repository_dir)
            except ftplib.error_reply, e:
                log.error('Cannot conect to ftp server %s' % e)

            for file in list:
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
