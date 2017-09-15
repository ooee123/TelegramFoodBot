class Message:

    def __init__(self, date, from, id):
        self.date = date
        self.from = from
        self.id = id

    def jsonToMessage(json):
        if "text" in json:
            # Is text
        elif "sticker" in json:
            # Is a sticker

    def __str__(self):
        raise "IMPLEMENT ME"
