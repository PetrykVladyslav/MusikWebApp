import pytest
import requests
from services.deezer_service import (
    search_tracks,
    search_albums,
    get_popular_tracks,
    get_popular_albums,
    get_all_genres,
)

# Щоб не робити реальних запитів до Deezer API, використовуємо мокінг:
from unittest.mock import patch


# ==== Тести для функції search_tracks ====

@patch("services.deezer_service.requests.get")
def test_search_tracks_success(mock_get):
    # Мок успішної відповіді
    mock_get.return_value.json.return_value = {
        "data": [
            {
                "title": "Song 1",
                "artist": {"name": "Artist 1"},
                "album": {"cover_big": "cover1.jpg"},
                "id": 123,
                "preview": "preview_url_1",
            }
        ]
    }

    tracks = search_tracks("test_query")
    assert len(tracks) == 1
    assert tracks[0]["title"] == "Song 1"
    assert tracks[0]["artist"] == "Artist 1"
    assert tracks[0]["preview_url"] == "preview_url_1"


@patch("services.deezer_service.requests.get")
def test_search_tracks_empty(mock_get):
    # Мок порожньої відповіді
    mock_get.return_value.json.return_value = {"data": []}

    tracks = search_tracks("unknown_query")
    assert tracks == []


# ==== Тести для функції search_albums ====

@patch("services.deezer_service.requests.get")
def test_search_albums_success(mock_get):
    # Мок успішної відповіді
    mock_get.return_value.json.return_value = {
        "data": [
            {
                "title": "Album 1",
                "artist": {"name": "Artist A"},
                "cover_big": "coverA.jpg",
                "id": 111,
                "nb_tracks": 10,
            }
        ]
    }

    albums = search_albums("test_album")
    assert len(albums) == 1
    assert albums[0]["title"] == "Album 1"
    assert albums[0]["artist"] == "Artist A"
    assert albums[0]["tracks_count"] == 10


@patch("services.deezer_service.requests.get")
def test_search_albums_empty(mock_get):
    # Мок порожньої відповіді
    mock_get.return_value.json.return_value = {"data": []}

    albums = search_albums("unknown_album")
    assert albums == []


@patch("services.deezer_service.requests.get")
def test_search_albums_incorrect_data(mock_get):
    # Мок неправильної відповіді (наприклад, немає поля artist)
    mock_get.return_value.json.return_value = {
        "data": [
            {
                "title": "Album without artist",
                "cover_big": "coverX.jpg",
                "id": 999,
            }
        ]
    }

    albums = search_albums("bad_album")
    assert albums == []


@patch("services.deezer_service.requests.get", side_effect=requests.exceptions.RequestException)
def test_search_albums_request_error(mock_get):
    # Мок помилки запиту (наприклад, проблеми з Інтернетом)
    albums = search_albums("error_album")
    assert albums == []


# ==== Тести для функції get_popular_tracks ====

@patch("services.deezer_service.requests.get")
@patch("services.deezer_service.random.sample", side_effect=lambda x, y: x[:y])  # упрощаем random.sample
def test_get_popular_tracks_success(mock_sample, mock_get):
    mock_get.return_value.json.return_value = {
        "data": [
            {
                "title": "Popular Track 1",
                "artist": {"name": "Artist X"},
                "album": {"cover_big": "coverX.jpg"},
                "id": 101,
                "preview": "preview1.mp3",
            }
        ]
    }

    tracks = get_popular_tracks()
    assert len(tracks) == 1
    assert tracks[0]["title"] == "Popular Track 1"

@patch("services.deezer_service.requests.get", side_effect=requests.exceptions.RequestException)
def test_get_popular_tracks_error(mock_get):
    tracks = get_popular_tracks()
    assert tracks == []


# ==== Тести для функції get_popular_albums ====

@patch("services.deezer_service.requests.get")
@patch("services.deezer_service.random.sample", side_effect=lambda x, y: x[:y])
def test_get_popular_albums_success(mock_sample, mock_get):
    mock_get.return_value.json.return_value = {
        "data": [
            {
                "title": "Popular Album 1",
                "artist": {"name": "Artist Y"},
                "cover_big": "coverY.jpg",
                "id": 202,
            }
        ]
    }

    albums = get_popular_albums()
    assert len(albums) == 1
    assert albums[0]["title"] == "Popular Album 1"

@patch("services.deezer_service.requests.get", side_effect=requests.exceptions.RequestException)
def test_get_popular_albums_error(mock_get):
    albums = get_popular_albums()
    assert albums == []


# ==== Тести для функції get_all_genres ====

@patch("services.deezer_service.requests.get")
def test_get_all_genres_success(mock_get):
    mock_get.return_value.json.return_value = {
        "data": [
            {"name": "Rock/Pop"},
            {"name": "Jazz"},
        ]
    }

    genres = get_all_genres()
    assert {"name": "Rock"} in genres
    assert {"name": "Pop"} in genres
    assert {"name": "Jazz"} in genres
    assert len(genres) == 3  # Rock + Pop + Jazz

@patch("services.deezer_service.requests.get")
def test_get_all_genres_empty(mock_get):
    mock_get.return_value.json.return_value = {"data": []}
    genres = get_all_genres()
    assert genres == []

@patch("services.deezer_service.requests.get", side_effect=requests.exceptions.RequestException)
def test_get_all_genres_error(mock_get):
    genres = get_all_genres()
    assert genres == []