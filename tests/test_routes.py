def test_home_page_loads(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'stUwa' in response.data


def test_resources_page_loads(client):
    response = client.get('/resources')

    assert response.status_code == 200
    assert b'Resources' in response.data


def test_missing_unit_returns_404(client):
    response = client.get('/unit/NOPE9999')

    assert response.status_code == 404


def test_onboarding_data_contains_catalogue(client):
    response = client.get('/api/onboarding-data')

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['units']
    assert payload['degrees']
