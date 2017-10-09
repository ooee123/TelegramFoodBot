#!/usr/bin/python3
import requests
import json

class ChatroomConnection:

    def __init__(self, token, chat_id):
        self.baseUrl = "https://api.telegram.org/bot{token}".format(token=token)
        self.chat_id = int(chat_id)

    def getAPI(self, api, params=None):
        return requests.get("{baseUrl}/{api}".format(baseUrl=self.baseUrl, api=api), params=params).json()
       
    def postAPI(self, api, params=None):
        headers = {'content-type': 'application/json'}
        return requests.post("{baseUrl}/{api}".format(baseUrl=self.baseUrl, api=api), params=params, headers=headers).json()

    def sendSticker(self, sticker, params={}):
        params['chat_id'] = self.chat_id
        params['sticker'] = str(sticker)
        self.getAPI("sendSticker", params=params)

    def getUpdates(self, offset=None, timeout=None, allowed_updates=None, params={}):
        params['offset'] = offset
        params['timeout'] = timeout 
        params['allowed_updates'] = allowed_updates
        return self.postAPI("getUpdates", params=params)

    def sendMessage(self, text, params={}):
        params['chat_id'] = self.chat_id
        params['text'] = text
        return self.postAPI("sendMessage", params)

    def sendPhoto(self, photo, caption=None, params={}):
        api="sendPhoto"
        params['chat_id'] = self.chat_id
        params["photo"] = open(photo, "rb")
        #params["photo"] = photo
        files = {photo: open(photo, 'rb')}
        return requests.post("{baseUrl}/{api}".format(baseUrl=self.baseUrl, api=api), files=files, params=params).json()
        #return self.postAPI('sendPhoto', params=params)
        #files = {'file': open(photo, 'rb')}
