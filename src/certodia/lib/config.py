import yaml
import os
import inflection


class config(object):
    def __init__(self, log, args):
        self.__log = log
        self.__args = args

        self.__conf = {}
        if self.__args.config and os.path.exists(self.__args.config):
            self.__file()
        else:
            self.__cli()

    def __file(self):
        with open(self.__args.config) as f:
            dataMap = yaml.safe_load(f)
        if dataMap:
            self.__conf = dataMap

    def __cli(self):
        for param in vars(self.__args):
            n = inflection.camelize(param, True)
            self.__conf[n] = getattr(self.__args, param)

    def getParam(self, param):
        if param in self.__conf:
            return self.__conf[param]

    def getConf(self):
        return self.__conf
