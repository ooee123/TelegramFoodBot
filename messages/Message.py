
class Message(object):
    def __init__(self, json):
        self.json = json
        self.date = json["date"]
        self.sender = json["from"]
        self.message_id = json["message_id"]

#    def __init__(self, date, sender, id):
#        self.date = date
#        self.sender = sender 
#        self.id = id
    def __str__(self):
        print(self.sender)
