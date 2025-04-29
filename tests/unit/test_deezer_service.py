import pytest

import requests

from services.deezer_service import (
    get_all_genres,
    get_popular_albums,
    get_popular_tracks,
    search_albums,
    search_tracks,
)


# ==== Тести для search_tracks ====
def test_search_tracks_success():
    """Тест успішного пошуку трека"""
    tracks = search_tracks("Houdini")

    assert isinstance(tracks, list)
    if tracks:  # Якщо API повернуло результати
        track = tracks[0]
        assert "title" in track
        assert "artist" in track
        assert "image" in track
        assert "id" in track
        assert "preview_url" in track
        assert track["type"] == "track"


def test_search_tracks_empty_query():
    """Тест порожнього запиту"""
    tracks = search_tracks("")
    assert tracks == []


def test_search_tracks_real_empty():
    """Тест запиту із неправильною назвою треку"""
    result = search_tracks("неіснуючийтрек")
    assert result == []


def test_search_tracks_special_chars():
    """Тест запиту із спецсимволами"""
    tracks = search_tracks("mötley crüe")
    assert isinstance(tracks, list)


def test_search_tracks_long_query():
    """Тест дуже довгого запиту"""
    long_query = "a" * 500
    tracks = search_tracks(long_query)
    assert isinstance(tracks, list)


def test_search_tracks_invalid_response(monkeypatch):
    """Тест обробки невалідної відповіді для треків"""

    def mock_get(*args, **kwargs):
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"invalid": "data"}'
        return response

    monkeypatch.setattr(requests, 'get', mock_get)
    tracks = search_tracks("test")
    assert tracks == []


# ==== Тести для search_albums ====
def test_search_albums_success():
    """Тест успішного пошуку альбомів"""
    albums = search_albums("metallica")

    assert isinstance(albums, list)
    if albums:
        album = albums[0]
        assert "title" in album
        assert "artist" in album
        assert "image" in album
        assert "id" in album
        assert "tracks_count" in album
        assert album["type"] == "album"
        assert album["tracks_count"] > 1


def test_search_albums_empty_query():
    """Тест порожнього запиту"""
    albums = search_albums("")
    assert albums == []


def test_search_albums_real_empty():
    """Тест запиту із неправильною назвою альбома"""
    result = search_albums("неіснуючийальбом")
    assert result == []


def test_search_albums_no_results():
    """Тест запиту без результатів"""
    albums = search_albums("nonexistentartist12345")
    assert albums == []


def test_search_albums_real_invalid_url(monkeypatch):
    """Тест запиту із неправильним посиланням"""
    monkeypatch.setattr("services.deezer_service.DEEZER_API_URL", "http://invalid.url")
    result = search_albums("test")
    assert result == []


def test_search_albums_invalid_response(monkeypatch):
    """Тест обробки невалідної відповіді"""

    def mock_get(*args, **kwargs):
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"invalid": "data"}'
        return response

    monkeypatch.setattr(requests, 'get', mock_get)
    albums = search_albums("test")
    assert albums == []


# ==== Тести для get_popular_tracks ====
def test_get_popular_tracks_success():
    """Тест отримання популярних треків"""
    tracks = get_popular_tracks()

    assert isinstance(tracks, list)
    assert len(tracks) <= 10
    if tracks:
        track = tracks[0]
        assert "title" in track
        assert "artist" in track
        assert "image" in track
        assert "id" in track
        assert "preview_url" in track


def test_get_popular_tracks_limit():
    """Тест обмеження кількості треків"""
    tracks = get_popular_tracks()
    assert len(tracks) <= 10


def test_get_popular_tracks_structure():
    """Тест структури даних, що повертаються"""
    tracks = get_popular_tracks()
    if tracks:
        assert all(isinstance(track["id"], int) for track in tracks)
        assert all(len(track["title"]) > 0 for track in tracks)


def test_get_popular_tracks_api_failure(monkeypatch):
    """Тест обробки помилок API"""

    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException("API Error")

    monkeypatch.setattr(requests, 'get', mock_get)
    tracks = get_popular_tracks()
    assert tracks == []


def test_get_popular_tracks_invalid_url(monkeypatch):
    """Тест запиту із неправильним посиланням"""
    monkeypatch.setattr("services.deezer_service.DEEZER_API_URL", "http://invalid.url")
    result = get_popular_tracks()
    assert result == []


def test_get_popular_tracks_empty(monkeypatch):
    """Тест запиту із порожнім результатом"""
    monkeypatch.setattr(requests, "get", lambda *a, **kw: type("Fake", (), {"json": lambda: {"data": []}})())
    result = get_popular_tracks()
    assert result == []


# ==== Тести для get_popular_albums ====
def test_get_popular_albums_success():
    """Тест отримання популярних альбомів"""
    albums = get_popular_albums()

    assert isinstance(albums, list)
    assert len(albums) <= 10
    if albums:
        album = albums[0]
        assert "title" in album
        assert "artist" in album
        assert "image" in album
        assert "id" in album


def test_get_popular_albums_limit():
    """Тест обмеження кількості альбомів"""
    albums = get_popular_albums()
    assert len(albums) <= 10


def test_get_popular_albums_structure():
    """Тест структури даних, що повертаються"""
    albums = get_popular_albums()
    if albums:
        assert all(isinstance(album["id"], int) for album in albums)
        assert all(len(album["title"]) > 0 for album in albums)


def test_get_popular_albums_api_failure(monkeypatch):
    """Тест обробки помилок API"""

    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException("API Error")

    monkeypatch.setattr(requests, 'get', mock_get)
    albums = get_popular_albums()
    assert albums == []


def test_get_popular_albums_empty(monkeypatch):
    """Тест обробки отримки порожньої структури"""
    monkeypatch.setattr(requests, "get", lambda *a, **kw: type("Fake", (), {"json": lambda: {"data": []}})())
    result = get_popular_albums()
    assert result == []


# ==== Тести для get_all_genres ====
def test_get_all_genres_success():
    """Тест отримання усіх жанрів"""
    genres = get_all_genres()

    assert isinstance(genres, list)
    if genres:
        genre = genres[0]
        assert "name" in genre
        assert len(genre["name"]) > 0


def test_get_all_genres_structure():
    """Тест структури жанрів"""
    genres = get_all_genres()
    if genres:
        assert all(isinstance(genre["name"], str) for genre in genres)


def test_get_all_genres_split():
    """Тест розділення складових жанрів"""
    genres = get_all_genres()
    if genres:
        composite_genres = [g for g in genres if '/' in g["name"]]
        if composite_genres:
            assert any(' ' not in g["name"] for g in genres)


def test_get_all_genres_api_failure(monkeypatch):
    """Тест обробки помилок API"""

    def mock_get(*args, **kwargs):
        raise requests.exceptions.RequestException("API Error")

    monkeypatch.setattr(requests, 'get', mock_get)
    genres = get_all_genres()
    assert genres == []


def test_get_all_genres_no_data(monkeypatch):
    """Тест обробки отримки порожньої структури"""

    monkeypatch.setattr(requests, "get", lambda *a, **kw: type("Fake", (), {"json": lambda: {}})())
    genres = get_all_genres()
    assert genres == []
