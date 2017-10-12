import json
import os
from JsonSerializable import MyJSONEncoder

class Config:
    def __init__(self, config_filename, init=lambda: {}):
        self.config_filename = config_filename
        if not os.path.isfile(config_filename):
            self.config = init()
        else:
            self.config = json.load(open(self.config_filename, "r"))

    def saveConfig(self):
        json.dump(self.config, open(self.config_filename, "w"), cls=MyJSONEncoder)

    def getAttribute(self, attribute, default=None):
        if attribute not in self.config:
            self.setAttribute(attribute, default)
        return self.config[attribute]

    def setAttribute(self, attribute, value):
        self.config[attribute] = value
        self.saveConfig()
