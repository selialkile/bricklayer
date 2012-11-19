import os
import sys
import shutil
import mocker

sys.path.append('..')
sys.path.append('../utils')

from nose.tools import *
from bricklayer.git import Git

def setup():
    if not os.path.isdir('tests/workspace'):
        os.mkdir('tests/workspace')

def teardown():
    if os.path.isdir('tests/workspace'):
        shutil.rmtree('tests/workspace', ignore_errors=True)
    
class TestGit:
    def __init__(self):
        self.project = mocker.Mocker()
        self.project.name = 'test_repo'
        self.project.git_url = 'tests/test_repo'
        self.project.version = '1.0'
        self.project.branch = 'master'
        self.project.last_tag = ''
        self.project.last_commit = ''
        self.project.build_cmd = 'python setup.py build'
        self.project.install_cmd = 'python setup.py install --root=BUILDROOT'
        self.project.replay()
        self.git = Git(self.project, workdir=os.path.join(os.path.dirname(__file__), 'workspace'))

        if not os.path.isdir(self.git.workdir):
            self.git.clone(self.project.branch)

    def clone_test(self):
        assert os.path.isdir(self.git.workdir)
        assert os.path.isdir(os.path.join(self.git.workdir, '.git'))

    def checkout_tag_test(self):
        self.git.checkout_tag('testing_0.0.1')
        assert_true(os.path.isfile(os.path.join(self.git.workdir, 'a')))
        assert_true(os.path.isfile(os.path.join(self.git.workdir, 'b')))
        assert_false(os.path.isfile(os.path.join(self.git.workdir, 'c')))
        self.git.checkout_tag('testing_0.0.2')
        assert_true(os.path.isfile(os.path.join(self.git.workdir, 'c')))
    
    def last_tag_test(self):
        assert_equal(self.git.last_tag('testing'), 'testing_0.0.2')
