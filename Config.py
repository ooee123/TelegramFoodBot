import json
import os
class Config:

    def __init__(self, config_filename):
        self.config_filename = config_filename
        if not os.path.isfile(config_filename):
            self.config = {}
        else:
            self.config = json.load(open(self.config_filename, "r"))

    def saveConfig(self):
        json.dump(self.config, open(self.config_filename, "w"))

    def getAttribute(self, attribute, default=None):
        if attribute not in self.config:
            self.setAttribute(attribute, default)
        return self.config[attribute]

    def setAttribute(self, attribute, value):
        self.config[attribute] = value
        self.saveConfig()
