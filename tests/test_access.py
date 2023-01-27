import pytest

endpoint = "/api/rtsp/v2/access/"


@pytest.mark.parametrize("path", ["stations", "zones"])
def test_success(client, path):
    response = client.get(endpoint + path)
    assert response.status_code == 200


def test_invalid_variant_422(client):
    response = client.get(endpoint + "notvalidoption")
    assert response.status_code == 422


def test_no_path_param_404(client):
    response = client.get(endpoint)
    assert response.status_code == 404


# spotchecking data


@pytest.mark.parametrize("station,expected", [("1", 0), ("7", 0), ("40", 1), ("48", 2), ("336", 1)])
def test_access_station_data_correct(client, station, expected):
    response = client.get(endpoint + "stations")
    r = response.json()
    assert r[station] == expected


@pytest.mark.parametrize(
    "zone,expected",
    [
        ("1", [1, 0, 0, 0, 1, 1]),
        ("23", [23, 1271755, 966139, 1085665, 5, 3]),
        ("90205", [90205, 825936, 747757, 781962, 2, 1]),
    ],
)
def test_access_zone_data_correct(client, zone, expected):
    response = client.get(endpoint + "zones")
    r = response.json()
    assert r[zone]["no"] == expected[0]
    assert r[zone]["all_rail"] == expected[1]
    assert r[zone]["current"] == expected[2]
    assert r[zone]["future"] == expected[3]
    assert r[zone]["discur"] == expected[4]
    assert r[zone]["disfut"] == expected[5]
