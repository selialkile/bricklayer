import sys
import os
from nose import *

from bricklayer.projects import Projects
from bricklayer.builder import Builder
from bricklayer.build_info import BuildInfo


def setup():
    os.chdir(os.path.join(os.path.dirname(__file__), '..'))

class TestBuilder:
    def build_init_test(self):
        print os.path.abspath(os.path.curdir)
        p = Projects('test_build')
        p.git_url = 'test/test_repo'
        p.group = 'test_group'
        p.version = '0.100.0'
        p.save()

        b = Builder(p.name)
        pre_build_id = BuildInfo(p)
        b.build_project(branch='master', release='testing', version='0.0.1', commit=None)
        
        assert( BuildInfo(p).build_id != pre_build_id)
