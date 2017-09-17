from messages.Message import Message

class Text(Message):

    def __init__(self, json):
        super().__init__(json)
        self.text = json["text"]

    def __str__(self):
        print(str(super()))
        print(self.text)
