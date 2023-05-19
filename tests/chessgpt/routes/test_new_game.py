from unittest.mock import MagicMock, patch
import pytest
from flask import Flask
from flask.testing import FlaskClient
from chessgpt.routes.new_game import new_game_routes


# create a pytest fixture to initialize a Flask test client
@pytest.fixture
def client():
    app = Flask(__name__)
    app.logger = MagicMock()
    app.dynamodb_client = MagicMock()
    app.GAMES_TABLE = "test_games_table"
    new_game_routes(app)  # register the route
    with app.test_client() as client:
        yield client


def test_new_game_rejects_when_no_assistant_color(client: FlaskClient):
    response = client.post(
        "/api/new_game", headers={"Openai-Conversation-Id": "testcid"}, json={}
    )

    assert response.status_code == 400
    assert response.json["success"] == False
    assert (
        response.json["message"]
        == "Missing assistant_color in request data. Please specify 'white' or 'black'"
    )


def test_new_game_rejects_when_no_elo(client: FlaskClient):
    response = client.post(
        "/api/new_game",
        headers={"Openai-Conversation-Id": "testcid"},
        json={"assistant_color": "white"},
    )

    assert response.status_code == 400
    assert response.json["success"] == False
    assert (
        response.json["message"]
        == "Missing elo in request data. Please specify a number between 1350 and 2850"
    )


def test_new_game_rejects_when_invalid_assistant_color(client: FlaskClient):
    response = client.post(
        "/api/new_game",
        headers={"Openai-Conversation-Id": "testcid"},
        json={"assistant_color": "red", "elo": 1200},
    )

    assert response.status_code == 400
    assert response.json["success"] == False
    assert (
        response.json["message"]
        == "Invalid assistant_color in request data. Please specify 'white' or 'black'"
    )


@patch("chessgpt.routes.new_game.save_board")
def test_new_game_happy_path(save_board, client: FlaskClient):
    response = client.post(
        "/api/new_game",
        headers={"Openai-Conversation-Id": "testcid"},
        json={"assistant_color": "white", "elo": 1200},
    )

    assert response.status_code == 200

    # check that the board was saved
    assert save_board.call_count == 1
