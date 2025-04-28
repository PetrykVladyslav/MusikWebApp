import random

import requests

# Deezer API базовий URL
DEEZER_API_URL = "https://api.deezer.com"


def search_tracks(query):
    """Пошук треків за запитом"""
    url = f"{DEEZER_API_URL}/search?q={query}"
    params = {"limit": 1000}
    response = requests.get(url, params=params)
    data = response.json()
    tracks = []

    for item in data.get("data", []):
        tracks.append(
            {
                "type": "track",  # Додаємо тип
                "title": item["title"],
                "artist": item["artist"]["name"],
                "image": item["album"]["cover_big"],
                "id": item["id"],  # Добавляем ID трека
                "preview_url": item.get("preview", ""),  # Добавляем ссылку на превью
            }
        )
    return tracks


def search_albums(query):
    """Пошук альбомів за запитом з додатковою перевіркою"""
    try:
        url = f"{DEEZER_API_URL}/search/album?q={query}"
        params = {"limit": 1000}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        albums = []
        seen_albums = set()  # Для уникнення дублікатів

        for item in data.get("data", []):
            # Додаткова перевірка, що це дійсно альбом
            if not item.get("title") or not item.get("artist") or not item.get("cover_big"):
                continue

            # Унікальний ідентифікатор альбому (artist + title)
            album_key = f"{item['artist']['name']}-{item['title']}"

            if album_key not in seen_albums:
                albums.append({"type": "album", "title": item["title"], "artist": item["artist"]["name"], "image": item["cover_big"], "id": item["id"], "tracks_count": item.get("nb_tracks", 0)})  # Додаємо кількість треків
                seen_albums.add(album_key)

        # Фільтруємо альбоми з малою кількістю треків (можливо, це не альбоми)
        return [album for album in albums if album["tracks_count"] > 1]

    except Exception as e:
        print(f"Помилка пошуку альбомів: {str(e)}")
        return []


def get_popular_tracks():
    """Отримання популярних треків"""
    try:
        # Отримуємо популярні треки з Deezer (наприклад, чарт)
        url = f"{DEEZER_API_URL}/chart/0/tracks"
        params = {"limit": 1000}
        response = requests.get(url, params=params)
        data = response.json()
        tracks = []

        for item in data.get("data", []):
            tracks.append({"title": item["title"], "artist": item["artist"]["name"], "image": item["album"]["cover_big"], "id": item["id"], "preview_url": item.get("preview", "")})  # Добавляем ID трека  # Добавляем ссылку на превью

        return random.sample(tracks, min(10, len(tracks)))
    except Exception as e:
        print(f"Помилка отримання популярних треків: {str(e)}")
        return []


def get_popular_albums():
    """Отримання популярних альбомів"""
    try:
        # Отримуємо популярні альбоми з Deezer (наприклад, чарт)
        url = f"{DEEZER_API_URL}/chart/0/albums"
        params = {"limit": 1000}
        response = requests.get(url, params=params)
        data = response.json()
        albums = []

        for item in data.get("data", []):
            albums.append({"title": item["title"], "artist": item["artist"]["name"], "image": item["cover_big"], "id": item["id"]})  # Добавляем ID альбома

        return random.sample(albums, min(10, len(albums)))
    except Exception as e:
        print(f"Помилка отримання популярних альбомів: {str(e)}")
        return []


def get_all_genres():
    """Отримує всі жанри з Deezer API."""
    try:
        url = f"{DEEZER_API_URL}/genre"
        response = requests.get(url)
        data = response.json()

        if "data" in data:
            genres = []
            for genre in data["data"]:
                # Розділяємо складові жанри
                if "/" in genre["name"]:
                    split_genres = genre["name"].split("/")
                    for g in split_genres:
                        genres.append({"name": g.strip()})  # Додаємо кожен жанр окремо
                else:
                    genres.append({"name": genre["name"]})
            return genres
        else:
            print("Помилка: Не вдалося отримати жанри.")
            return []
    except Exception as e:
        print(f"Помилка отримання жанрів: {str(e)}")
        return []
