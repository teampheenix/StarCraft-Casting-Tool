from scctool.tasks.aligulac import AligulacInterface

def test_aligulac(aligulac_api_key):
    aligulac = AligulacInterface(aligulac_api_key)
    player = aligulac.search_player('pressure', 'P')
    assert player['id'] == 2701
    assert player['tag'] == 'pressure'
    assert player['race'] == 'P'
    assert player['country'] == 'DE'
    
    prediction = aligulac.predict_match('Maru', 'Serral', bo=5, score1=0, score2=0)
    assert prediction is not None
    assert len(prediction['outcomes']) == 6
    assert prediction['pla']['id'] == 49
    assert prediction['plb']['id'] == 485

    history = aligulac.get_history('Maru', 'Serral')
    assert history is not None
    assert len(history['objects']) > 0