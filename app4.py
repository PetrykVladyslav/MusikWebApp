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
    params = {
        "limit": 1000
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
    return tracks

def get_popular_tracks():
    """Отримання популярних треків"""
    try:
        # Отримуємо популярні треки з Deezer (наприклад, чарт)
        url = f"{DEEZER_API_URL}/chart/0/tracks"
        params = {
            "limit": 1000
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
                "image": item["cover_big"],
                "id": item["id"]  # Добавляем ID альбома
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
    return redirect(request.referrer)

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
    return redirect(request.referrer)


@app.route("/delete_track", methods=["POST"])
def delete_track():
    data = request.get_json()
    track_id = data.get("track_id")
    playlist_name = data.get("playlist_name")

    # Находим нужный плейлист и удаляем трек только из него
    for playlist in playlists:
        if playlist["name"] == playlist_name:
            playlist["tracks"] = [t for t in playlist["tracks"] if t["id"] != track_id]
            return {"success": True}

    return {"success": False}, 404


@app.route("/playlist/<int:playlist_id>")
def playlist_detail(playlist_id):
    """Сторінка з деталями плейліста"""
    if playlist_id < len(playlists):
        playlist = playlists[playlist_id]
        return render_template("playlist_detail.html", playlist=playlist)
    else:
        flash("Плейліст не знайдено!", "error")
        return redirect(url_for("home"))


@app.route("/album/<int:album_id>")
def album_detail(album_id):
    """Сторінка з деталями альбома"""
    try:
        # Получаем основную информацию об альбоме
        album_url = f"{DEEZER_API_URL}/album/{album_id}"
        album_response = requests.get(album_url)
        album_data = album_response.json()

        if "error" in album_data:
            flash("Альбом не знайдено!", "error")
            return redirect(url_for("home"))

        # Получаем треки альбома из основного ответа (без отдельного запроса)
        tracks = []
        for item in album_data.get("tracks", {}).get("data", []):
            tracks.append({
                "title": item["title"],
                "artist": item["artist"]["name"],
                "image": album_data["cover_big"],
                "id": item["id"],
                "preview_url": item.get("preview", "")
            })

        album = {
            "title": album_data["title"],
            "artist": album_data["artist"]["name"],
            "image": album_data.get("cover_big", ""),
            "tracks": tracks
        }

        return render_template("album_detail.html", album=album, playlists=playlists)
    except Exception as e:
        print(f"Помилка отримання альбому: {str(e)}")
        flash("Помилка отримання даних альбому", "error")
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