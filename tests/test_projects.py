import sys
import os
import ConfigParser
from nose.tools import *

sys.path.append('../bricklayer')
sys.path.append('../bricklayer/utils')

from bricklayer.projects import Projects
from bricklayer.config import BrickConfig

class TestProjects:
    def create_test(self):
        p = Projects('test')
        p.git_url = 'test/test_repo'
        p.group = 'test_group'
        p.save()

        p = Projects('test')
        assert p.name == 'test'
        assert p.git_url == 'test/test_repo'

    def exist_test(self):
        p = Projects('test')
        assert p.name == 'test'

    def delete_test(self):
        p = Projects('test')
        p.delete()
        assert Projects('test').git_url == ''

    def add_branch_test(self):
        p = Projects('test')
        p.add_branch('test_branch')
        assert 'test_branch' in p.branches()