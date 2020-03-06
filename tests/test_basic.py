from scctool.tasks.aligulac import AligulacInterface
from scctool.tasks.liquipedia import LiquipediaGrabber

def test_aligulac(aligulac_api_key):
    aligulac = AligulacInterface(aligulac_api_key)
    player1 = aligulac.search_player('pressure', 'P')
    assert player1['id'] == 2701
    assert player1['tag'] == 'pressure'
    assert player1['race'] == 'P'
    assert player1['country'] == 'DE'
    #TODO: fix this
    #player2 = aligulac.get_player(player1)
    #assert player2['id'] == player1['id']
    player2 = aligulac.get_player(player1['id'])
    assert player2['id'] == player1['id']
    
    prediction = aligulac.predict_match('Maru', 'Serral', bo=5, score1=0, score2=0)
    assert prediction is not None
    assert len(prediction['outcomes']) == 6
    assert prediction['pla']['id'] == 49
    assert prediction['plb']['id'] == 485
    score = aligulac.predict_score(prediction)
    assert score is not None

    history = aligulac.get_history('Maru', 'Serral')
    assert history is not None
    assert len(history['objects']) > 0
    
def test_liquipedia():
    grabber = LiquipediaGrabber()
    mappool = list(grabber.get_ladder_mappool())
    print(mappool)
    assert len(mappool) == 7
    stats = list(grabber.get_map_stats(mappool))
    print(stats)
    assert len(stats) == len(mappool)
    for map_stats in stats:
        assert map_stats['map'] in mappool
