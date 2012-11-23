import os
import yaml

class BuildOptions(object):
	options = {'changelog': False, 'experimental': False, 'rvm': 'system', 'not_found': False}

	def __init__(self, wdir):
		if os.path.isfile(os.path.join(wdir, '.bricklayer.yml')):
			bricklayer_yml = open(os.path.join(wdir, '.bricklayer.yml')).read()
			self.options.update(yaml.load(bricklayer_yml))
		else:
			self.options.update({'not_found': True})


	def __dir__(self):
		return self.options.keys()

	def __getattr__(self, attr):
		return self.options[attr]