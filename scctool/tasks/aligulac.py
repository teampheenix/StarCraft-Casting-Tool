"""Interface to aligulac to predict the outcome of an 1vs1 match."""
import logging
import queue
from difflib import SequenceMatcher
from functools import lru_cache

import requests

import scctool.settings
import scctool.settings.translation
from scctool.tasks.tasksthread import TasksThread

# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class AligulacInterface:
    """Interface to aligulac to predict the outcome of an 1vs1 match."""

    base_url = 'http://aligulac.com'

    def __init__(self, api_key):
        """Init the interface with a aligulac api key."""
        self._api_key = api_key
        self._params = {'apikey': self._api_key, 'format': 'json'}

    @lru_cache(maxsize=32)
    def search_player(self, name, race='R'):
        """Search for a player by name."""
        race = race[:1].upper()
        url = self.base_url + '/search/json/'
        r = requests.get(url, params={'q': name, 'search_for': 'players'})
        data = r.json().get('players', [])
        return self.match_player(data, name, race)

    @classmethod
    def match_player(cls, data, name, race='R'):
        """Choose the best player based on SequenceMatcher."""
        best_ratio = 0.0
        match = None
        race_found = False
        for player in data:
            race_match = race == player.get('race', 'R')
            if race == 'R' or race_match or not race_found:
                ratio = SequenceMatcher(
                    None, name.upper(), player.get('tag', '').upper()).ratio()
                if not race_found and race_match:
                    best_ratio = ratio
                    race_found = True
                    match = player
                elif ratio > best_ratio and race_match:
                    best_ratio = ratio
                    race_found = True
                    match = player
                elif ratio > best_ratio and not race_found:
                    best_ratio = ratio
                    race_found = False
                    match = player
        if match is None:
            return data.pop(0)
        else:
            return match

    @lru_cache(maxsize=32)
    def _player_to_id(self, player, race='R'):
        """Convert a player to an id."""
        if isinstance(player, int):
            return player
        if isinstance(player, dict):
            return player.get('id')
        if isinstance(player, str):
            try:
                return self.search_player(player, race).get('id')
            except IndexError:
                return 0

    @lru_cache(maxsize=32)
    def get_player(self, player):
        """Get player info from the api."""
        ident = self._player_to_id(player)
        url = f'{self.base_url}/api/v1/player/{ident}/'
        r = requests.get(url, params=self._params)
        r.raise_for_status()
        return r.json()

    @lru_cache(maxsize=32)
    def predict_match(self, player1, player2, race1='R', race2='R',
                      bo=1, score1=0, score2=0):
        """Get a match prediction from the api."""
        id1 = self._player_to_id(player1, race1)
        id2 = self._player_to_id(player2, race2)
        url = f'{self.base_url}/api/v1/predictmatch/{id1},{id2}/'
        params = self._params
        params['bo'] = bo
        params['s1'] = score1
        params['s2'] = score2
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    @classmethod
    def predict_score(cls, prediction):
        """Predict the score."""
        outcomes = prediction.get('outcomes')
        outcomes = sorted(outcomes,
                          key=lambda i: i['prob'])
        return outcomes.pop()

    @lru_cache(maxsize=32)
    def get_history(self, player1, player2):
        """Get the match history of two players."""
        id1 = self._player_to_id(player1)
        id2 = self._player_to_id(player2)
        url = self.base_url + '/api/v1/match/'
        params = self._params
        params['pla__in'] = f'{id1},{id2}'
        params['plb__in'] = f'{id1},{id2}'
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()


class AligulacThread(TasksThread):
    """Calls Aligulac to predict match if browser sources is connected."""

    def __init__(self, matchControl, websocket, aligulacManager):
        """Init the thread."""
        super().__init__()
        self._matchControl = matchControl
        self._websocket = websocket
        self._manager = aligulacManager
        self._aligulac = AligulacInterface(
            scctool.settings.safe.get('aligulac-api-key'))
        self._q = queue.Queue()
        self._matchControl.dataChanged.connect(self.receive_data)
        self._matchControl.metaChanged.connect(self.receive_data)
        self._manager.dataChanged.connect(self.receive_data)
        self.addTask('process', self.__processTask)

    def activate(self):
        """Activate the task thread."""
        self.activateTask('process')

    def receive_data(self, item='meta', *args):
        """Request new data."""
        if(self._q.qsize() < 2
                and self.hasActiveTask()
                and item in ['meta', 'score', 'player', 'race']):
            self._q.put({'item': item})

    def __processTask(self):
        try:
            self._q.get(False, 1)
            match = self._matchControl.activeMatch()
            if match.getSolo():
                player = list()
                race = list()
                for idx in range(2):
                    player.append(match.getPlayer(idx, 0))
                    race.append(match.getRace(idx, 0))
                bestof = match.getBestOf()
                score = match.getScore()
                try:
                    if 'TBD' in player:
                        raise ValueError('Playername is TBD')
                    prediction = self._aligulac.predict_match(
                        self._manager.translate(player[0]),
                        self._manager.translate(player[1]),
                        race[0], race[1],
                        bestof,
                        score[0], score[1])
                    predicted_score = self._aligulac.predict_score(prediction)
                    score1 = predicted_score.get('sca')
                    score2 = predicted_score.get('scb')
                    prob1 = prediction.get('proba')
                    prob2 = prediction.get('probb')
                    player1 = prediction['pla']['tag']
                    player2 = prediction['plb']['tag']
                except (requests.exceptions.HTTPError, ValueError):
                    module_logger.info(
                        'Aligulac was unable to predict '
                        f'{player[0]} vs {player[1]}')
                    prob1 = 0.5
                    prob2 = 0.5
                    score1 = 0
                    score2 = 0
                    player1 = player[0]
                    player2 = player[1]

                self._websocket.sendData2Path(
                    'aligulac', "DATA",
                    {'player1': player1,
                     'player2': player2,
                     'bestof': bestof,
                     'prob1': prob1,
                     'prob2': prob2,
                     'score1': score1,
                     'score2': score2})

        except queue.Empty:
            pass
