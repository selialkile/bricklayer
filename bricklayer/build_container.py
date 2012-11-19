import subprocess
import shutil

from bricklayer.config import BrickConfig

class BuildContainer(object):

	def __init__(self, project):
		self.type = BrickConfig().get('bricklayer', 'container_type')
		self.container_base = BrickConfig.get('bricklayer', '%s_base' % self.type)
		self.project = project

		if ! os.path.isdir("%s-%s" % (self.container_base, self.project.name)):
			sh
	

	def setup(self):
		for mount in ['proc', 'sys']:
			p = subprocess.Popen(
				['mount', '-o', 'bind', mount, '%s/%s' % (self.project.name, mount)], 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE
			)
			p.wait()

			p = subprocess.Popen(
				[
					'mount',
					'-o',
					'bind',
					BrickConfig().get('bricklayer', 'workspace'),
					'%s-%s/%s' % (self.container_base, self.project.name, BrickConfig().get('bricklayer', 'workspace'))
				]
			)
			p.wait()

	def teardown(self):
		for mount in ['proc', 'sys']:
			p = subprocess.Popen(
				['umount', '%s/%s' % (self.project.name, mount)], 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE
			)
			p.wait()

	def destroy(self):
		pass