"""Provide StarCraft Casting Tool with text-to-speech from google-API."""
import base64
import json
import logging
import os
import random

import requests

import scctool.settings
import scctool.settings.translation

module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class TextToSpeech:
    """Provide StarCraft Casting Tool with text-to-speech from google-API."""

    def __init__(self):
        """Init tts manager."""
        self.__cache_size = 20
        self.__synthesize_url =\
            'https://texttospeech.googleapis.com/v1/text:synthesize?key={}'
        self.__voices_url =\
            'https://texttospeech.googleapis.com/v1/voices'
        self.__voices = []
        self.defineOptions()
        self.loadJson()

    def synthesize(self, ssml, voice, pitch=0.00, rate=1.00):
        """Synthesize a voice line."""
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
        """Get all voices (and cache them)."""
        if len(self.__voices) > 0:
            return self.__voices
        params = {}
        params['languageCode'] = 'en-US'
        params['key'] = self.getKey()

        response = requests.get(self.__voices_url, params=params)
        voices = response.json().get('voices', [])

        def sortVoices(elem):
            return elem['name']

        voices.sort(key=sortVoices)
        return voices

    @classmethod
    def getKey(cls):
        """Return google-api key."""
        return scctool.settings.safe.get('texttospeech-api-key')

    def getOptions(self):
        """Get options."""
        return self.options

    def getLine(self, option, player, race, team=''):
        """Convert a line to ssml."""
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
        except Exception:
            data = []

        self.__cache = data

    def dumpJson(self):
        """Write json data to file."""
        try:
            with open(scctool.settings.getJsonFile('tts'), 'w',
                      encoding='utf-8-sig') as outfile:
                json.dump(self.__cache, outfile)
        except Exception:
            module_logger.exception("message")

    def _uniqid(self):
        while True:
            uniqid = hex(random.randint(49152, 65535))[2:]
            ids = self.getIDs()
            if uniqid not in ids:
                return uniqid

    def getIDs(self):
        """Return all ids."""
        for item in self.__cache:
            yield item['id']

    def newCacheItem(self, ssml, voice, pitch=0.00, rate=1.00):
        """Add a new item to the cache."""
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
        """Limit the cache size."""
        while len(self.__cache) > self.__cache_size:
            item = self.__cache.pop()
            try:
                os.remove(scctool.settings.getAbsPath(item['file']))
            except FileNotFoundError:
                pass

    def searchCache(self, ssml, voice, pitch=0.00, rate=1.00):
        """Search cache for an item."""
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
        """Remove all invalid items from cache."""
        ids = set()
        for item in self.__cache:
            if not os.path.isfile(scctool.settings.getAbsPath(item['file'])):
                self.__cache.remove(item)
            else:
                ids.add(item['id'])

        tts_dir = scctool.settings.getAbsPath(scctool.settings.ttsDir)
        for fname in os.listdir(tts_dir):
            full_fname = os.path.join(tts_dir, fname)
            name, ext = os.path.splitext(fname)
            ext = ext.replace(".", "")
            if (os.path.isfile(full_fname) and name not in ids):
                os.remove(full_fname)
                module_logger.info("Removed tts file {}".format(full_fname))

    def defineOptions(self):
        """Define the available voicelines."""
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
        option['ssml'] = ('<speak><emphasis level="moderate">{player}'
                          '</emphasis>playing as {race}</speak>')
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
        option['ssml'] = """<speak>
<emphasis level="moderate">{team}</emphasis>
<emphasis level="moderate">{player}</emphasis>
</speak>"""
        option['backup'] = 'player'
        self.options['team_player'] = option

        option = {}
        option['desc'] = '{% player %} playing for {% team %}'
        option['ssml'] = """<speak>
<emphasis level="moderate">{player}</emphasis>
playing for <emphasis level="moderate">{team}</emphasis>
</speak>
"""
        option['backup'] = 'player'
        self.options['team_player_2'] = option

        option = {}
        option['desc'] = '{% player %} representing {% team %}'
        option['ssml'] = """<speak>
<emphasis level="moderate">{player}</emphasis>
representing <emphasis level="moderate">{team}</emphasis>
</speak>
"""
        option['backup'] = 'player'
        self.options['team_player_3'] = option

        option = {}
        option['desc'] = '{% player %} playing as {% race %} for {% team %}'
        option['ssml'] = """<speak>
<emphasis level="moderate">{player}</emphasis>
playing as {race} for
<emphasis level="moderate">{team}</emphasis></speak>
"""
        option['backup'] = 'player_race'
        self.options['team_player_race'] = option
