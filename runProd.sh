#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

./Bot.py $(cat morningBot.token) $(cat DankGeneral_id)
