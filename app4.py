import os
from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Глобальний список для зберігання плейлістів
playlists = []

# Deezer API базовий URL
DEEZER_API_URL = "https://api.deezer.com"

def search_tracks(query):
    """Пошук треків за запитом"""
    url = f"{DEEZER_API_URL}/search?q={query}"
    response = requests.get(url)
    data = response.json()
    tracks = []

    for item in data.get("data", []):
        tracks.append({
            "title": item["title"],
            "artist": item["artist"]["name"],
            "image": item["album"]["cover_big"],
            "id": item["id"],  # Добавляем ID трека
            "preview_url": item.get("preview", "")  # Добавляем ссылку на превью
        })
    return tracks

def get_popular_tracks():
    """Отримання популярних треків"""
    try:
        # Отримуємо популярні треки з Deezer (наприклад, чарт)
        url = f"{DEEZER_API_URL}/chart/0/tracks"
        params = {
            "limit": 100
        }
        response = requests.get(url, params=params)
        data = response.json()
        tracks = []

        for item in data.get("data", []):
            tracks.append({
                "title": item["title"],
                "artist": item["artist"]["name"],
                "image": item["album"]["cover_big"],
                "id": item["id"],  # Добавляем ID трека
                "preview_url": item.get("preview", "")  # Добавляем ссылку на превью
            })

        return random.sample(tracks, min(10, len(tracks)))
    except Exception as e:
        print(f"Помилка отримання популярних треків: {str(e)}")
        return []

def get_popular_albums():
    """Отримання популярних альбомів"""
    try:
        # Отримуємо популярні альбоми з Deezer (наприклад, чарт)
        url = f"{DEEZER_API_URL}/chart/0/albums"
        params = {
            "limit": 1000
        }
        response = requests.get(url, params=params)
        data = response.json()
        albums = []

        for item in data.get("data", []):
            albums.append({
                "title": item["title"],
                "artist": item["artist"]["name"],
                "image": item["cover_big"]
            })

        return random.sample(albums, min(10, len(albums)))
    except Exception as e:
        print(f"Помилка отримання популярних альбомів: {str(e)}")
        return []

# Головна сторінка з полем пошуку
@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        query = request.form.get("search_query", "")
        return redirect(url_for("search", query=query))

    # Отримуємо популярні треки та альбоми
    popular_tracks = get_popular_tracks()
    popular_albums = get_popular_albums()

    return render_template("index.html", popular_tracks=popular_tracks, popular_albums=popular_albums, playlists=playlists)

# Сторінка з результатами пошуку
@app.route("/search")
def search():
    query = request.args.get("query", "")
    results = search_tracks(query) if query else []
    return render_template("search_results.html", query=query, results=results, playlists=playlists)

# Створення нового плейліста
@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    playlist_name = request.form.get("playlist_name")
    if playlist_name:
        playlists.append({"name": playlist_name, "tracks": []})
        flash("Плейліст успішно створено!", "success")
    else:
        flash("Назва плейліста не може бути порожньою!", "error")
    return redirect(url_for("home"))

# Додавання треку до плейліста
@app.route("/add_to_playlist", methods=["POST"])
def add_to_playlist():
    playlist_id = int(request.form.get("playlist_id"))
    track_id = request.form.get("track_id")
    track_title = request.form.get("track_title")
    track_artist = request.form.get("track_artist")
    track_image = request.form.get("track_image")

    if playlist_id < len(playlists):
        playlists[playlist_id]["tracks"].append({
            "title": track_title,
            "artist": track_artist,
            "image": track_image,
            "id": track_id
        })
        flash("Трек успішно додано до плейліста!", "success")
    else:
        flash("Плейліст не знайдено!", "error")
    return redirect(url_for("home"))


@app.route("/playlist/<int:playlist_id>")
def playlist_detail(playlist_id):
    """Сторінка з деталями плейліста"""
    if playlist_id < len(playlists):
        playlist = playlists[playlist_id]
        return render_template("playlist_detail.html", playlist=playlist)
    else:
        flash("Плейліст не знайдено!", "error")
        return redirect(url_for("home"))


@app.route("/get_preview/<track_id>")
def get_preview(track_id):
    """Возвращает 30-секундный превью-урл трека"""
    url = f"{DEEZER_API_URL}/track/{track_id}"
    response = requests.get(url)
    data = response.json()

    preview_url = data.get("preview", "")  # Ссылка на 30-секундный фрагмент
    return {"preview_url": preview_url}


if __name__ == "__main__":
    app.run(debug=True)