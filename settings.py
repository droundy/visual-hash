from kivy.config import Config
from kivy.uix.settings import Settings

import socket

json = """
[
    { "type": "string",
      "title": "Your name",
      "desc": "Your name",
      "section": "game",
      "key": "username" },

    { "type": "string",
      "title": "Device name",
      "desc": "Name of this device",
      "section": "game",
      "key": "devicename" },

    { "type": "options",
      "title": "Difficulty",
      "desc": "What difficulty ",
      "section": "game",
      "key": "difficulty",
      "options": ["easy", "normal", "challenging", "impossible"] },

    { "type": "options",
      "title": "Hash type",
      "desc": "Type of hash ",
      "section": "game",
      "key": "hashtype",
      "options": ["hex32", "hex64", "hex128",
                  "flag", "tflag", "fractal", "identicon", "randomart"] }

]
"""

defaults = { 'username': socket.gethostname(),
             'devicename': socket.gethostname(),
             'difficulty': 'normal',
             'hashtype': 'flag' }
