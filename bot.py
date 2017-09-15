#!/usr/bin/python3
import sys
import requests
import json

global baseUrl

def main():
    if len(sys.argv) < 2:
        print("Usage {0} <bot_token>".format(sys.argv[0]))
        sys.exit(-1)

    global baseUrl
    baseUrl = "https://api.telegram.org/bot{token}".format(token=sys.argv[1])

    chatroom = int(open("chatroom_id").read())
    response = sendSticker(chatroom, "CAADAgAD2QMAAjq5FQLlmqkIqp10lQI")
    printJSON(response)

    response = postAPI("getUpdates")
    printJSON(response)

def getAPI(api, params=None):
    return requests.get("{baseUrl}/{api}".format(baseUrl=baseUrl, api=api), params=params).json()
   
def postAPI(api, params=None):
    headers = {'content-type': 'application/json'}
    return requests.post("{baseUrl}/{api}".format(baseUrl=baseUrl, api=api), params=params, headers=headers).json()

def printJSON(message):
    print(json.dumps(message, indent=4, sort_keys=True, separators=(',', ': ')))

def sendSticker(chat_id, sticker, params={}):
    chat_id = int(chat_id)
    sticker = str(sticker)
    params['chat_id'] = chat_id
    params['sticker'] = sticker 
    getAPI("sendSticker", params)

main()
