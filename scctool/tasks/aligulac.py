import logging
import requests
import queue
from functools import lru_cache

from scctool.tasks.tasksthread import TasksThread

# create logger
module_logger = logging.getLogger(__name__)

class AligulacInterface:

    base_url = 'http://aligulac.com'

    def __init__(self, api_key):
        self._api_key = api_key
        self._params = {'apikey': self._api_key, 'format': 'json'}

    @lru_cache(maxsize=None)
    def search_player(self, name):
        url = self.base_url + '/search/json/'
        r = requests.get(url, params={'q': name})
        data = r.json().get('players', [])
        return data.pop(0)

    @lru_cache(maxsize=None)
    def _player_to_id(self, player):
        if isinstance(player, int):
            return player
        if isinstance(player, dict):
            return player.get('id')
        if isinstance(player, str):
            return self.search_player(player).get('id')

    @lru_cache(maxsize=None)
    def get_player(self, player):
        id = self._player_to_id(player)
        url = self.base_url + '/api/v1/player/{}/'.format(id)
        r = requests.get(url, params=self._params)
        r.raise_for_status()
        return r.json()

    @lru_cache(maxsize=None)
    def predict_match(self, player1, player2, bo=1, score1=0, score2=0):
        print('predict_match:', player1, player2, bo, score1, score2)
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

    @lru_cache(maxsize=None)
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
        self._aligulac = AligulacInterface('bokFdvyJebCv50IQt58P')
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
            item = self._q.get(False, 1)
            match = self._matchControl.activeMatch()
            if match.getSolo():
                player = list()
                for idx in range(2):
                    player.append(match.getPlayer(idx, 0))
                bestof = match.getBestOf()
                score = match.getScore()
                prediction = self._aligulac.predict_match(
                    player[0], player[1], bestof,
                    score[0], score[1])
                prob1 = prediction.get('proba')
                prob2 = prediction.get('probb')
                self._websocket.sendData2Path(
                    'aligulac', "DATA",
                    {'player1': player[0],
                     'player2': player[1],
                     'bestof': bestof,
                     'prob1': prob1,
                     'prob2': prob2})

        except queue.Empty:
            pass

# if __name__ == '__main__':
#     interface = AligulacInterface('bokFdvyJebCv50IQt58P')
#     print(interface.predict_match('Snute', 'DNS', 3, 1, 0))
