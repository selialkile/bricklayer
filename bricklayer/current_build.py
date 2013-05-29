import redis
from model_base import ModelBase, transaction

class CurrentBuild(ModelBase):
    namespace = 'current_build'
  
    def __init__(self, name=''):
        self.name = name
        self.populate(self.name)

    def __dir__(self):
        return ['name']
   
    @classmethod
    def get_all(self):
        connection_obj = CurrentBuild()
        redis_cli = connection_obj.connect()
        keys = redis_cli.keys('%s:*' % self.namespace)
        currents = []
        for key in keys:
            key = key.replace('%s:' % self.namespace, '')
            currents.append(CurrentBuild(key)) 
        return currents   

    @classmethod
    def delete_all(self):
        connection_obj = CurrentBuild()
        redis_cli = connection_obj.connect()
        keys = redis_cli.keys('%s:*' % self.namespace)
        for key in keys:
            redis_cli.delete(key)
        return True
