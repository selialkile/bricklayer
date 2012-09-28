import os
import yaml

class BuildOptions(object):
	options = {'changelog': False, 'experimental': False, 'rvm': 'system'}

	def __init__(self, wdir):
		if os.path.isfile(os.path.join(wdir, '.bricklayer.yml')):
			bricklayer_yml = open(os.path.join(wdir, '.bricklayer.yml')).read()
			self.options = yaml.load(bricklayer_yml)

	def __dir__(self):
		return self.options.keys()

	def __getattr__(self, attr):
		return self.options['options'][attr]