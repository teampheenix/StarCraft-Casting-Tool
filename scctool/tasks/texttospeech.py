import base64

import requests

import scctool.settings


class TextToSpeech:

    def __init__(self):
        self.__synthesize_url =\
            'https://texttospeech.googleapis.com/v1/text:synthesize?key={}'
        self.__voices_url =\
            'https://texttospeech.googleapis.com/v1/voices'
        self.defineOptions()

    def synthesize(self, ssml, file, voice, pitch=0.00):
        post_data = {}
        post_data['input'] = {'ssml': ssml}
        post_data['voice'] = {
            'languageCode': 'en-US',
            'name': voice}
        post_data['audioConfig'] = {
            'audioEncoding': 'LINEAR16',
            'speakingRate': '1.00',
            'pitch': str(pitch)}

        url = self.__synthesize_url.format(self.getKey())

        response = requests.post(url, json=post_data)
        content = response.json()

        with open(file, 'wb') as the_file:
            the_file.write(base64.b64decode(content['audioContent']))

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

    def defineOptions(self):
        self.options = {}

        option = {}
        option['desc'] = '{% player %}'
        option['ssml'] = '<emphasis level="strong">{player}</emphasis>'
        option['backup'] = ''
        self.options['player'] = option

        option = {}
        option['desc'] = '{% player %} playing as {% race %}'
        option['ssml'] = """<emphasis level="strong">{player}</emphasis>
<break strength="strong"/> playing as
<emphasis level="moderate">{race}</emphasis>"""
        option['backup'] = ''
        self.options['player_race'] = option

        option = {}
        option['desc'] = '{% team %} - {% player %}'
        option['ssml'] = """{team} <break strength="strong"/>
<emphasis level="strong">{player}</emphasis>"""
        option['backup'] = 'player'
        self.options['team_player'] = option

        option = {}
        option['desc'] = '{% player %} playing for {% team %}'
        option['ssml'] = """<emphasis level="strong">{player}</emphasis>
<break strength="strong"/> playing for <break strength="strong"/>
<emphasis level="moderate">{team}</emphasis>
"""
        option['backup'] = 'player'
        self.options['team_player_2'] = option

        option = {}
        option['desc'] = '{% player %} representing {% team %}'
        option['ssml'] = """<emphasis level="strong">{player}</emphasis>
<break strength="strong"/> representing <break strength="strong"/>
<emphasis level="moderate">{team}</emphasis>
"""
        option['backup'] = 'player'
        self.options['team_player_3'] = option

        option = {}
        option['desc'] = '{% player %} playing as {% race %} for {% team %}'
        option['ssml'] = """<emphasis level="strong">{player}</emphasis>
<break strength="strong"/> playing as
<emphasis level="moderate">{race}</emphasis> for <break strength="strong"/>
<emphasis level="moderate">{team}</emphasis>
"""
        option['backup'] = 'player_race'
        self.options['team_player_race'] = option
