import pytest
from data import load_dataset, preprocess, insights
from search import KeywordSearch
from evaluation import metrics

def test_preprocessing_and_missing_values():
    df = preprocess([{'id':'01','name':{'local':'ทดสอบ','en':'Test'},'children_count':{'district':4}, 'geo':{'lat':'1.5'}}])
    assert df.loc[0, 'id'] == '01'
    assert df.loc[0, 'districts'] == 4
    assert df.loc[0, 'latitude'] == 1.5
    assert df['subdistricts'].isna().all()

def test_snapshot_loading():
    assert len(load_dataset('provinces')) == 77
    assert len(load_dataset('districts')) == 928
    with pytest.raises(ValueError): load_dataset('missing')

def test_keyword_ranking_and_empty():
    engine = KeywordSearch()
    assert engine.search('จังหวัด')[0][0]['id'] == 'provinces'
    assert engine.search('   ') == []
    assert engine.search('zzzzzzzz') == []

def test_insights_use_filtered_data():
    df = load_dataset('provinces').head(2)
    lines = insights(df, 'districts')
    assert '50' in lines[-1]
    assert 'กรุงเทพมหานคร' in lines[-1]
    assert insights(df.iloc[0:0], 'districts') == []

def test_metrics():
    assert metrics(['a','b','c'], {'b'}, 1) == (0,0,0.5)
    assert metrics(['a','b','c'], {'a','b'}, 2) == (1,1,1)
    assert metrics([], {'a'}, 1) == (0,0,0)
