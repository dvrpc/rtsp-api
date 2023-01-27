import pytest

endpoint = "/api/rtsp/v2/frequency/"


@pytest.mark.parametrize("path", ["zone", "bus", "rail", "transit"])
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


@pytest.mark.parametrize(
    "linename,abs_change,percent",
    [
        (57, 1762.94, 10.62),
        ("PART_HIGH", 21.69, 66.07),
        ("409", 901.5, 28.46),
        ("115", 850.24, 55.99),
    ],
)
def test_bus_frequency_data_correct(client, linename, abs_change, percent):
    response = client.get(endpoint + "bus")
    r = response.json()
    for each in r:
        if each["linename"] == linename:
            assert each["AbsChange"] == abs_change
            assert each["Percent"] == percent


@pytest.mark.parametrize(
    "line,percent,absolute",
    [
        ("10", -2.44, -293.48),
        ("CHW", 27.13, 1085.62),
        ("NOR", 31.19, 2883.62),
    ],
)
def test_rail_frequency_data_correct(client, line, percent, absolute):
    response = client.get(endpoint + "rail")
    r = response.json()
    assert r[line]["percent"] == percent
    assert r[line]["absolute"] == absolute


@pytest.mark.parametrize(
    "line,am,avg_freq",
    [
        ("1", 10, 2.25),
        ("35", 45, 0.71),
        ("J", 20, 3.58),
    ],
)
def test_transit_frequency_data_correct(client, line, am, avg_freq):
    response = client.get(endpoint + "transit")
    r = response.json()
    assert r[line]["am"] == am
    assert r[line]["avg_freq"] == avg_freq
