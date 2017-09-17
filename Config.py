import json
import os
class Config:

    def __init__(self, config_filename):
        self.config_filename = config_filename
        if not os.path.isfile(config_filename):
            self.config = {"last_offset": -1}
        else:
            self.config = json.load(open(self.config_filename, "r"))

    def saveConfig(self):
        json.dump(self.config, open(self.config_filename, "w"))

    def getLastOffset(self):
        return self.config["last_offset"]

    def setLastOffset(self, last_offset):
        self.config["last_offset"] = int(last_offset)
        self.saveConfig()

    def getStickers(self):
        return self.config["stickers"]

    def saveStickers(self, stickers):
        self.config["stickers"] = stickers
        self.saveConfig()

    def putStickers(self, stickerName, stickerFilename):
        self.config["stickers"][stickerName] = stickerFilename
        self.saveConfig()
