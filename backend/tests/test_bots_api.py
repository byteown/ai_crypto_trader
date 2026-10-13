BOT = {"name": "json", "symbol": "BTC/USD", "timeframe": "1h"}


def test_create_bot(client):
    response = client.post("/api/v1/bots/", json=BOT)
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["mode"] == "paper"


def test_name_duplicate(client):
    response1 = client.post("/api/v1/bots/", json=BOT)
    assert response1.status_code == 201
    response2 = client.post("/api/v1/bots/", json=BOT)
    assert response2.status_code == 409


def test_get_nonexistbot(client):
    response = client.get("/api/v1/bots/1337")
    assert response.status_code == 404


def test_list_pagination(client):
    client.post("/api/v1/bots/", json={**BOT, "name": "John1"})
    client.post("/api/v1/bots/", json={**BOT, "name": "John2"})
    client.post("/api/v1/bots/", json={**BOT, "name": "John3"})
    response = client.get("/api/v1/bots/", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2
    response = client.get("/api/v1/bots/", params={"offset": 2})
    assert response.status_code == 200
    assert len(response.json()) == 1
    response = client.get("/api/v1/bots/")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert (response.json())[0]["name"] == "John1"
    assert (response.json())[1]["name"] == "John2"
    assert (response.json())[2]["name"] == "John3"


def test_patch_changes_only_sent_fields(client):
    bot = client.post("/api/v1/bots/", json=BOT).json()
    response = client.patch(f"/api/v1/bots/{bot['id']}", json={"name": "something"})
    assert response.status_code == 200
    response = client.get(f"/api/v1/bots/{bot['id']}")
    assert (response.json())["name"] == "something"
    assert (response.json())["symbol"] == "BTC/USD"
    assert (response.json())["timeframe"] == "1h"


def test_path_with_name_taken_already(client):
    response = client.post("/api/v1/bots/", json=BOT)
    assert response.status_code == 201
    response = client.post("/api/v1/bots/", json={**BOT, "name": "another"})
    assert response.status_code == 201
    response = client.patch(
        f"/api/v1/bots/{(response.json())['id']}", json={"name": "json"}
    )
    assert response.status_code == 409


def test_delete_then_cant_get(client):
    response = client.post("/api/v1/bots/", json=BOT)
    assert response.status_code == 201
    bot_id: int = (response.json())["id"]
    response = client.delete(f"/api/v1/bots/{bot_id}")
    assert response.status_code == 204
    response = client.get(f"/api/v1/bots/{bot_id}")
    assert response.status_code == 404


def test_invalid_params(client):
    response = client.get("api/v1/bots/", params={"limit": 999, "offset": -1})
    assert response.status_code == 422
