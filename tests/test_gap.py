import pytest

endpoint = "/api/rtsp/v2/gap/"


@pytest.mark.parametrize("path", ["summary"])
def test_summary_success(client, path):
    response = client.get(endpoint + path)
    assert response.status_code == 200


def test_no_path_param_404(client):
    response = client.get(endpoint)
    assert response.status_code == 404


def test_zones_tozone_success(client):
    response = client.get(endpoint + "zones/14635,15249/ToZone")
    assert response.status_code == 200


def test_zones_fromzone_success(client):
    response = client.get(endpoint + "zones/14635,15249/FromZone")
    assert response.status_code == 200


def test_zones_invalid_variant_422(client):
    response = client.get(endpoint + "zones/14635,15249/notvalidoption")
    assert response.status_code == 422


def test_muni_tozone_success(client):
    response = client.get(endpoint + "muni/3402119780/ToZone")
    assert response.status_code == 200


def test_muni_fromzone_success(client):
    response = client.get(endpoint + "muni/3402119780/FromZone")
    assert response.status_code == 200


def test_muni_invalid_variant_422(client):
    response = client.get(endpoint + "muni/3402119780/notvalidoption")
    assert response.status_code == 422


# spotchecking data


def test_from_zone_data_ok(client):
    response = client.get(endpoint + "zones/6811/FromZone")
    r = response.json()
    assert r["7426.0"] == 9
    assert r["7603.0"] == 8
    assert r["7419.0"] == 8
    assert r["7021.0"] == 10


def test_to_zones_data_ok(client):
    response = client.get(endpoint + "zones/22824,22822/ToZone")
    r = response.json()
    assert r["22019.0"] == 2
    assert r["22615.0"] == 9
    assert r["20815.0"] == 8
    assert r["24405.0"] == 3


def test_from_muni_data_ok(client):
    response = client.get(endpoint + "muni/3402119780/FromZone")
    r = response.json()
    assert r["gaps"]["15403.0"] == 4
    assert r["gaps"]["18615.0"] == 5
    assert r["gaps"]["18014.0"] == 4
    assert r["gaps"]["18624.0"] == 10
    assert r["gaps"]["20252.0"] == 4
    assert r["gaps"]["18220.0"] == 5
    assert r["demand_score"][0] == 59611


def test_to_muni_data_ok(client):
    response = client.get(endpoint + "muni/3402133180/ToZone")
    r = response.json()
    assert r["gaps"]["16048.0"] == 4
    assert r["gaps"]["15210.0"] == 10
    assert r["gaps"]["20442.0"] == 2
    assert r["gaps"]["15828.0"] == 5
    assert r["demand_score"][0] == 53374
