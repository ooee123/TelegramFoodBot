from messages.Text import Text

class BotCommand(Text):
    
    def __init__(self, json):
        super().__init__(json)

    def __str__(self):
        print(str(super()))
