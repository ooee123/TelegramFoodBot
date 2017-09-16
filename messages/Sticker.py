from messages.Message import Message

class Sticker(Message):
    
    def __init__(self, json):
        super().__init__(json)
        self.sticker = json["sticker"]

    def getSticker(self):
        return self.sticker["file_id"]

    def __str__(self):
        print(str(super()))
        print(self.sticker)
