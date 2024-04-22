from unittest.mock import patch
from app import execute_query, app

def test_execute_query():
    queries = ['SELECT 1', 'SELECT 2']
    expected_results = [{'1': 1}, {'2': 2}]

    for query, expected_result in zip(queries, expected_results):
        result = execute_query(query)
        assert result == expected_result

@patch('app.execute_query')
def test_list_transactions(mock_execute_query):
    mock_execute_query.return_value = [{'id': 1, 'amount_btc': 0.5, 'spent': False}]

    client = app.test_client()
    response = client.get('/transactions')

    assert response.status_code == 200
    assert 'id' in response.json[0]
    assert 'amount_btc' in response.json[0]
    assert 'spent' in response.json[0]

@patch('app.execute_query')
def test_get_balance(mock_execute_query):
    mock_execute_query.return_value = {'total_balance': 10}

    client = app.test_client()
    response = client.get('/balance')

    assert response.status_code == 200
    assert 'BTC' in response.json
    assert 'EUR' in response.json

@patch('app.execute_query')
def test_create_transfer(mock_execute_query):

    mock_execute_query.side_effect = [
        [{'amount_btc': 10, 'spent': False}],
        None
    ]

    client = app.test_client()
    data = {'amount_eur': '50000'}
    response = client.post('/transfer', data=data)

    assert response.status_code == 200
    assert 'message' in response.json
