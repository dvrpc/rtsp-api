endpoint = "/api/rtsp/v2/access/"


def test_success(client):
    response = client.get(endpoint + "stations")
    assert response.status_code == 200
