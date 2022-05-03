

def test_basic(client):
    response = client.get("/")
    assert b"Test your user base without risk." in response.data
