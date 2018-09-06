import logging
import queue
from functools import lru_cache

import requests

import scctool.settings
from scctool.tasks.tasksthread import TasksThread

# create logger
module_logger = logging.getLogger(__name__)


class AligulacInterface:

    base_url = 'http://aligulac.com'

    def __init__(self, api_key):
        self._api_key = api_key
        self._params = {'apikey': self._api_key, 'format': 'json'}

    @lru_cache(maxsize=32)
    def search_player(self, name):
        url = self.base_url + '/search/json/'
        r = requests.get(url, params={'q': name})
        data = r.json().get('players', [])
        return data.pop(0)

    @lru_cache(maxsize=32)
    def _player_to_id(self, player):
        if isinstance(player, int):
            return player
        if isinstance(player, dict):
            return player.get('id')
        if isinstance(player, str):
            try:
                id = self.search_player(player).get('id')
            except IndexError:
                id = 0
            return id

    @lru_cache(maxsize=32)
    def get_player(self, player):
        id = self._player_to_id(player)
        url = self.base_url + '/api/v1/player/{}/'.format(id)
        r = requests.get(url, params=self._params)
        r.raise_for_status()
        return r.json()

    @lru_cache(maxsize=32)
    def predict_match(self, player1, player2, bo=1, score1=0, score2=0):
        id1 = self._player_to_id(player1)
        id2 = self._player_to_id(player2)
        url = self.base_url + '/api/v1/predictmatch/{},{}/'.format(id1, id2)
        params = self._params
        params['bo'] = bo
        params['s1'] = score1
        params['s2'] = score2
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def predict_score(self, prediction):
        outcomes = prediction.get('outcomes')
        outcomes = sorted(outcomes,
                          key = lambda i: i['prob'])
        return outcomes.pop()

    @lru_cache(maxsize=32)
    def get_history(self, player1, player2):
        id1 = self._player_to_id(player1)
        id2 = self._player_to_id(player2)
        url = self.base_url + '/api/v1/match/'
        params = self._params
        params['pla__in'] = '{},{}'.format(id1, id2)
        params['plb__in'] = '{},{}'.format(id1, id2)
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()


class AligulacThread(TasksThread):
    """Calls Aligulac to predict match if browser sources is connected."""

    def __init__(self, matchControl, websocket):
        """Init the thread."""
        super().__init__()
        self._matchControl = matchControl
        self._websocket = websocket
        self._aligulac = AligulacInterface(
            scctool.settings.safe.get('aligulac-api-key'))
        self._q = queue.Queue()
        self._matchControl.dataChanged.connect(self.receive_data)
        self._matchControl.metaChanged.connect(self.receive_data)
        self.addTask('process', self.__processTask)

    def activate(self):
        self.activateTask('process')

    def receive_data(self, item='meta', *args):
        if self.hasActiveTask() and item in ['meta', 'score', 'player']:
            self._q.put({'item': item})

    def __processTask(self):
        try:
            self._q.get(False, 1)
            match = self._matchControl.activeMatch()
            if match.getSolo():
                player = list()
                for idx in range(2):
                    player.append(match.getPlayer(idx, 0))
                bestof = match.getBestOf()
                score = match.getScore()
                try:
                    prediction = self._aligulac.predict_match(
                        player[0], player[1], bestof,
                        score[0], score[1])
                    predicted_score = self._aligulac.predict_score(prediction)
                    print(predicted_score)
                    score1 = predicted_score.get('sca')
                    score2 = predicted_score.get('scb')
                    prob1 = prediction.get('proba')
                    prob2 = prediction.get('probb')
                    player1 = prediction['pla']['tag']
                    player2 = prediction['plb']['tag']
                except requests.exceptions.HTTPError:
                    module_logger.info(
                        'Aligulac was unable to predict {} vs {}'.format(
                            player[0], player[1]))
                    prob1 = 0.5
                    prob2 = 0.5
                    score1 = 0
                    score2 = 0
                    player1 = player[0]
                    player2 = player[1]

                self._websocket.sendData2Path(
                    'aligulac', "DATA",
                    {'player1': player[0],
                     'player2': player[1],
                     'bestof': bestof,
                     'prob1': prob1,
                     'prob2': prob2,
                     'score1': score1,
                     'score2': score2})

        except queue.Empty:
            pass
