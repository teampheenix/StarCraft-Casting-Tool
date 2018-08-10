import base64

import requests

import scctool.settings


class TextToSpeech:

    def __init__(self):
        self.__synthesize_url =\
            'https://texttospeech.googleapis.com/v1/text:synthesize?key={}'
        self.__voices_url =\
            'https://texttospeech.googleapis.com/v1/voices'

    def synthesize(self, text, file, voice):
        post_data = {}
        post_data['input'] = {'text': text}
        post_data['voice'] = {
            'languageCode': 'en-US',
            'name': voice}
        post_data['audioConfig'] = {
            'audioEncoding': 'MP3',
            'speakingRate': '1.00',
            'pitch': '0.00'}

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
