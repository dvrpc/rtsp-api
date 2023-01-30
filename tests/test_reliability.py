import pytest

endpoint = "/api/rtsp/v2/reliability/"


@pytest.mark.parametrize(
    "path", ["tti", "weighted", "score", "speed", "otp", "septa", "njt", "filter"]
)
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
    "path,key,expected",
    [
        ("tti", "1", 1.19),
        ("tti", "358", 1.02),
        ("tti", "24395", 1),
        ("filter", "1", "1"),
        ("filter", "R", "R"),
    ],
)
def test_tti_filter_data_ok(client, path, key, expected):
    response = client.get(endpoint + path)
    r = response.json()
    assert r[key] == expected


@pytest.mark.parametrize(
    "path, key1, key2, expected",
    [
        ("weighted", "1", "weighted", 11.11),
        ("weighted", "1", "lines", "110,111,117"),
        ("weighted", "23953", "weighted", 15.88),
        ("weighted", "23953", "lines", "313,408,412"),
        ("weighted", "29865", "weighted", 9.57),
        ("weighted", "29865", "lines", None),
        ("score", "1", "score", 11.11),
        ("score", "1", "lines", "110,111,117"),
        ("score", "23953", "score", 15.88),
        ("score", "23953", "lines", "313,408,412"),
        ("score", "29865", "score", 9.57),
        ("score", "29865", "lines", None),
        ("speed", "1", "avg_speed", 6),
        ("speed", "1", "line", "108"),
        ("speed", "30704", "avg_speed", 23),
        ("speed", "30704", "line", "412"),
        ("speed", "67395", "avg_speed", 5),
        ("speed", "67395", "line", "XH"),
        ("otp", "1", "otp", 70),
        ("otp", "1", "line", "400"),
        ("otp", "97", "otp", 81),
        ("otp", "97", "line", "67"),
        ("septa", "91139", "line", "22"),
        ("septa", "91139", "total_loads", 206.2),
        ("septa", "99857", "line", "40"),
        ("septa", "99857", "total_loads", 1138.68),
        ("septa", "136893", "line", "120"),
        ("septa", "136893", "total_loads", 134.0),
        ("njt", "3", "line", "403"),
        ("njt", "3", "ridership", 2834),
        ("njt", "12", "line", "413"),
        ("njt", "12", "ridership", 1726),
        ("njt", "43", "line", "317"),
        ("njt", "43", "ridership", 874),
    ],
)
def test_remaining_data_ok(client, path, key1, key2, expected):
    response = client.get(endpoint + path)
    r = response.json()
    assert r[key1][key2] == expected
