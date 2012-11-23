import subprocess
import shutil
import os

from bricklayer.config import BrickConfig

class BuildContainer(object):

	def __init__(self, project):
		self.type = BrickConfig().get('container', 'container_type')
		self.container_base = BrickConfig().get('container', '%s_base' % self.type)
		self.project = project
		self.workspace = '%s-%s%s' % (self.container_base, self.project.name, BrickConfig().get('workspace', 'dir'))

		if not os.path.isdir("%s-%s" % (self.container_base, self.project.name)):
			shutil.copytree(self.container_base, "%s-%s" % (self.container_base, self.project.name))
		self.dir = "%s-%s" % (self.container_base, self.project.name)
	

	def setup(self):
		for mount in ['proc', 'sys']:
			p = subprocess.Popen(
				['mount', '-o', 'bind', mount, '%s/%s' % (self.project.name, mount)], 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE
			)
			p.wait()

			if not os.path.isdir(self.workspace):
				os.makedirs(self.workspace)

		p = subprocess.Popen(
			[
				'mount',
				'-o',
				'bind',
				BrickConfig().get('workspace', 'dir'),
				self.workspace,
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

		p = subprocess.Popen(['umount', '-l', self.workspace], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		p.wait()
		print p.stdout.read(), p.stderr.read()

	def destroy(self):
		pass
