from zope.interface import implements
from twisted.python import usage
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
import bricklayer

class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    options = usage.Options
    tapname = "bricklayer"
    description = "Bricklayer service."
    
    def makeService(self, config):
        print bricklayer.__file__
        return bricklayer.service.BricklayerService()

serviceMaker = MyServiceMaker()
