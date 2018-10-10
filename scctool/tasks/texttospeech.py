import base64
import json
import logging
import os
import random

import requests

import scctool.settings

module_logger = logging.getLogger(
    'scctool.settings.texttospeech')  # create logger


class TextToSpeech:

    def __init__(self):
        self.__cache_size = 20
        self.__synthesize_url =\
            'https://texttospeech.googleapis.com/v1/text:synthesize?key={}'
        self.__voices_url =\
            'https://texttospeech.googleapis.com/v1/voices'
        self.defineOptions()
        self.loadJson()

    def synthesize(self, ssml, voice, pitch=0.00, rate=1.00):

        cache = self.searchCache(ssml, voice, pitch, rate)
        if cache:
            return cache
        file = self.newCacheItem(ssml, voice, pitch, rate)

        post_data = {}
        post_data['input'] = {'ssml': ssml}
        post_data['voice'] = {
            'languageCode': 'en-US',
            'name': voice}
        post_data['audioConfig'] = {
            'audioEncoding': 'LINEAR16',
            'speakingRate': str(rate),
            'pitch': str(pitch)}

        url = self.__synthesize_url.format(self.getKey())

        response = requests.post(url, json=post_data)
        content = response.json()

        with open(scctool.settings.getAbsPath(file), 'wb') as of:
            of.write(base64.b64decode(content['audioContent']))

        return file

    def getVoices(self):
        params = {}
        params['languageCode'] = 'en-US'
        params['key'] = self.getKey()

        response = requests.get(self.__voices_url, params=params)
        voices = response.json().get('voices', [])
        voices.sort(key=self.sortVoices)
        return voices

    def sortVoices(self, elem):
        return elem['name']

    def getKey(self):
        return scctool.settings.safe.get('texttospeech-api-key')

    def getOptions(self):
        return self.options

    def getLine(self, option, player, race, team=''):
        option = self.options[option]
        if not team and option['backup']:
            option = self.options[option['backup']]

        return option['ssml'].format(player=player, race=race, team=team)

    def loadJson(self):
        """Read json data from file."""
        try:
            with open(scctool.settings.getJsonFile('tts'), 'r',
                      encoding='utf-8-sig') as json_file:
                data = json.load(json_file)
                if not isinstance(data, list):
                    data = []
        except Exception as e:
            data = []

        self.__cache = data

    def dumpJson(self):
        """Write json data to file."""
        try:
            with open(scctool.settings.getJsonFile('tts'), 'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(self.__cache, outfile)
        except Exception as e:
            module_logger.exception("message")

    def _uniqid(self):
        while True:
            uniqid = hex(random.randint(49152, 65535))[2:]
            ids = self.getIDs()
            if uniqid not in ids:
                return uniqid

    def getIDs(self):
        for item in self.__cache:
            yield item['id']

    def newCacheItem(self, ssml, voice, pitch=0.00, rate=1.00):
        item = {}
        item['id'] = self._uniqid()
        item['ssml'] = ssml
        item['voice'] = voice
        item['pitch'] = pitch
        item['rate'] = rate
        item['file'] = os.path.join(scctool.settings.ttsDir,
                                    item['id'] + '.wav')

        self.__cache.insert(0, item)
        self.limitCacheSize()

        return item['file']

    def limitCacheSize(self):
        while len(self.__cache) > self.__cache_size:
            item = self.__cache.pop()
            try:
                os.remove(scctool.settings.getAbsPath(item['file']))
            except FileNotFoundError:
                pass

    def searchCache(self, ssml, voice, pitch=0.00, rate=1.00):
        for item in self.__cache:
            if item['ssml'] != ssml:
                continue
            if item['voice'] != voice:
                continue
            if item['pitch'] != pitch:
                continue
            if item['rate'] != rate:
                continue
            if os.path.isfile(scctool.settings.getAbsPath(item['file'])):
                return item['file']
            else:
                self.__cache.remove(item)
                return None
        return None

    def cleanCache(self):
        ids = set()
        for item in self.__cache:
            if not os.path.isfile(scctool.settings.getAbsPath(item['file'])):
                self.__cache.remove(item)
            else:
                ids.add(item['id'])

        dir = scctool.settings.getAbsPath(scctool.settings.ttsDir)
        for fname in os.listdir(dir):
            full_fname = os.path.join(dir, fname)
            name, ext = os.path.splitext(fname)
            ext = ext.replace(".", "")
            if (os.path.isfile(full_fname) and name not in ids):
                os.remove(full_fname)
                module_logger.info("Removed tts file {}".format(full_fname))

    def defineOptions(self):
        self.options = {}

        option = {}
        option['desc'] = '{% player %}'
        option['ssml'] = """<speak>
<emphasis level="moderate">{player}</emphasis></speak>
"""
        option['backup'] = ''
        self.options['player'] = option

        option = {}
        option['desc'] = '{% player %} playing as {% race %}'
        option['ssml'] = """<speak><emphasis level="moderate">{player}</emphasis>
playing as {race}</speak>"""
        option['backup'] = ''
        self.options['player_race'] = option

        option = {}
        option['desc'] = ('This beautiful corner of the map is occupied by the'
                          ' {% race %} player: {% player %}')
        option['ssml'] = """<speak>This beautiful corner of the map
is occupied by the {race} player:
<emphasis level="moderate">{player}</emphasis></speak>
        """
        self.options['player_race_2'] = option

        option = {}
        option['desc'] = '{% team %} - {% player %}'
        option['ssml'] = """<speak><emphasis level="moderate">{team}</emphasis>
<emphasis level="moderate">{player}</emphasis></speak>"""
        option['backup'] = 'player'
        self.options['team_player'] = option

        option = {}
        option['desc'] = '{% player %} playing for {% team %}'
        option['ssml'] = """<speak><emphasis level="moderate">{player}</emphasis>
playing for <emphasis level="moderate">{team}</emphasis></speak>
"""
        option['backup'] = 'player'
        self.options['team_player_2'] = option

        option = {}
        option['desc'] = '{% player %} representing {% team %}'
        option['ssml'] = """<speak><emphasis level="moderate">{player}</emphasis>
representing <emphasis level="moderate">{team}</emphasis></speak>
"""
        option['backup'] = 'player'
        self.options['team_player_3'] = option

        option = {}
        option['desc'] = '{% player %} playing as {% race %} for {% team %}'
        option['ssml'] = """<speak><emphasis level="moderate">{player}</emphasis>
playing as {race} for
<emphasis level="moderate">{team}</emphasis></speak>
"""
        option['backup'] = 'player_race'
        self.options['team_player_race'] = option
