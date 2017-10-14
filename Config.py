import json
import os
from JsonSerializable import MyJSONEncoder

class Config:
    def __init__(self, config_filename, autoCommit=True):
        self.config_filename = config_filename
        self.autoCommit = autoCommit
        if not os.path.isfile(config_filename):
            self.config = {}
        else:
            self.config = json.load(open(self.config_filename, "r"))

    def saveConfig(self):
        json.dump(self.config, open(self.config_filename, "w"), cls=MyJSONEncoder)

    def get(self, attribute, default=None):
        if attribute not in self.config:
            return default
        return self.config[attribute]

    def set(self, attribute, value):
        self.config[attribute] = value
        if self.autoCommit:
            self.saveConfig()
