import os
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, get_flashed_messages
import requests
import random
from auth import db, login_manager, register_user, login_user_by_credentials, logout_current_user, User, \
    get_user_playlists, Playlist, Track
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Deezer API базовий URL
DEEZER_API_URL = "https://api.deezer.com"

UPLOAD_FOLDER = 'static/images/avatars/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Налаштування бази даних
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Создание БД только при первом запуске
with app.app_context():
    if not os.path.exists("music.db"):  # Проверяем, существует ли уже база
        db.create_all()

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
            "preview_url": item.get("preview", ""),  # Добавляем ссылку на превью
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
    genres = get_all_genres()  # Отримуємо всі жанри
    user_playlists = get_user_playlists(current_user.id) if current_user.is_authenticated else []

    return render_template("index.html", popular_tracks=popular_tracks, popular_albums=popular_albums,
                           playlists=user_playlists, genres=genres, user=current_user)

# Сторінка з результатами пошуку
@app.route("/search")
def search():
    query = request.args.get("query", "")
    results = search_tracks(query) if query else []
    genres = get_all_genres()  # Отримуємо всі жанри
    user_playlists = get_user_playlists(current_user.id) if current_user.is_authenticated else []
    return render_template("search_results.html", query=query, results=results,
                           playlists=user_playlists, genres=genres, user=current_user)

# Створення нового плейліста
@app.route('/create_playlist', methods=['POST'])
@login_required  # Только авторизованные пользователи могут создавать плейлисты
def create_playlist():
    playlist_name = request.form.get("playlist_name")
    if playlist_name:
        # Создаем новый плейлист для текущего пользователя
        new_playlist = Playlist(name=playlist_name, user_id=current_user.id)
        db.session.add(new_playlist)
        db.session.commit()
        flash("Плейліст успішно створено!", category='success_playlist')
    else:
        flash("Назва плейліста не може бути порожньою!", category='error_playlist')
    return redirect(request.referrer)

# Додавання треку до плейліста
@app.route("/add_to_playlist", methods=["POST"])
@login_required  # Только авторизованные пользователи могут добавлять треки
def add_to_playlist():
    playlist_id = request.form.get("playlist_id")
    deezer_id = request.form.get("track_id")
    track_title = request.form.get("track_title")
    track_artist = request.form.get("track_artist")
    track_image = request.form.get("track_image")

    if not playlist_id:
        flash("Не обрано плейліст!", "error")
        return redirect(request.referrer)

    try:
        playlist_id = int(playlist_id)  # Преобразуем в int
    except ValueError:
        flash("Некоректний ID плейліста", "error")
        return redirect(request.referrer)

        # Проверяем, что плейлист принадлежит текущему пользователю
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        flash("Плейлист не знайдено!", "error")
        return redirect(request.referrer)

    # Проверяем, нет ли уже этого трека в плейлисте
    existing_track = Track.query.filter_by(deezer_id=deezer_id, playlist_id=playlist.id).first()
    if existing_track:
        flash("Трек уже є в цьому плейлісті!", "warning")
        return redirect(request.referrer)

    # Добавляем новый трек в плейлист
    new_track = Track(
        title=track_title,
        artist=track_artist,
        image=track_image,
        preview_url=f"https://api.deezer.com/track/{deezer_id}/preview",
        playlist_id=playlist.id,
        deezer_id=deezer_id
    )
    db.session.add(new_track)
    db.session.commit()

    flash("Трек успішно додано до плейліста!", "success")
    return redirect(request.referrer)

@app.route("/delete_track", methods=["POST"])
@login_required  # Только авторизованные пользователи могут удалять треки
def delete_track():
    data = request.get_json()
    track_id = data.get("track_id")
    playlist_id = data.get("playlist_id")

    # Проверяем, что плейлист принадлежит текущему пользователю
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if not playlist:
        return jsonify({"success": False, "error": "Плейлист не знайдено!"}), 404

    # Проверяем, что трек существует в плейлисте
    track = Track.query.filter_by(id=track_id, playlist_id=playlist.id).first()
    if not track:
        return jsonify({"success": False, "error": "Трек не знайдено в плейлисті!"}), 404

    # Удаляем трек
    db.session.delete(track)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/playlist/<int:playlist_id>")
@login_required  # Только авторизованные пользователи могут просматривать плейлисты
def playlist_detail(playlist_id):
    """Сторінка з деталями плейліста"""
    genres = get_all_genres()  # Отримуємо всі жанри
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=current_user.id).first()
    if playlist:
        return render_template("playlist_detail.html", playlist=playlist, genres=genres, user=current_user)
    else:
        flash("Плейліст не знайдено!", "error")
        return redirect(url_for("home"))

@app.route("/album/<int:album_id>")
def album_detail(album_id):
    """Сторінка з деталями альбома"""
    genres = get_all_genres()  # Отримуємо всі жанри
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

        user_playlists = get_user_playlists(current_user.id) if current_user.is_authenticated else []

        return render_template("album_detail.html", album=album, playlists=user_playlists, genres=genres, user=current_user)
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

    print(f"DEBUG: Получен ответ от Deezer API для track_id {track_id}: {data}")
    preview_url = data.get("preview", "")  # Ссылка на 30-секундный фрагмент
    return {"preview_url": preview_url}

@app.route("/genre/<genre_name>")
def search_by_genre(genre_name):
    """Пошук треків за жанром"""
    genres = get_all_genres()  # Отримуємо всі жанри
    try:
        # Пошук треків за жанром через Deezer API
        url = f"{DEEZER_API_URL}/search"
        params = {
            "q": f"genre:'{genre_name}'",
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
                "id": item["id"],
                "preview_url": item.get("preview", ""),
            })

        user_playlists = get_user_playlists(current_user.id) if current_user.is_authenticated else []

        return render_template("search_results.html", query=genre_name, results=tracks, playlists=user_playlists, genres=genres, user=current_user)
    except Exception as e:
        print(f"Помилка пошуку за жанром: {str(e)}")
        flash("Помилка пошуку за жанром", "error")
        return redirect(url_for("home"))

# Маршрут для реєстрації
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')  # Получаем никнейм
        remember = True if request.form.get('remember') else False  # Проверка чекбокса

        success, message = register_user(email, password, username)  # Передаем никнейм

        if success:
            session.permanent = remember  # Если remember = True, сессия будет храниться долго
            user = User.query.filter_by(email=email).first()
            session.permanent = True
            login_user(user)  # Автоматический вход после регистрации
            flash(message, category='success_reg')
            return redirect(url_for('home'))
        else:
            flash(message, category='error_reg')

    return render_template('register.html')

# Маршрут для входу
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False  # Проверка чекбокса

        success, message = login_user_by_credentials(email, password)
        if success:
            session.permanent = remember  # Если remember = True, сессия будет храниться долго
            session.permanent = True
            flash(message, category='success')  # Категория для успешного входа
            return redirect(url_for('home'))
        else:
            flash(message, category='error')  # Категория для ошибки входа
            return redirect(request.referrer)

    return render_template('login.html')

# Маршрут для виходу
@app.route('/logout')
@login_required
def logout():
    message = logout_current_user()
    flash(message, category='success_logout')  # Категория для успешного выхода
    return redirect(url_for('home'))

@app.route('/user_details')
@login_required
def user_details():
    genres = get_all_genres()  # Отримуємо всі жанри
    user_playlists = get_user_playlists(current_user.id) if current_user.is_authenticated else []
    return render_template('user_details.html', user=current_user, playlists=user_playlists, genres=genres)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.get(current_user.id)
    if user:
        user.name = name
        user.email = email
        if password:
            user.set_password(password)
        db.session.commit()
        flash("Профіль успішно оновлено!", "success")
    else:
        flash("Помилка оновлення профілю", "error")

    return redirect(url_for('user_details'))

# Маршрут для удаления аккаунта
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    data = request.get_json()
    password = data.get('password')

    if current_user.check_password(password):
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Невірний пароль"}), 401

# Маршрут для обновления ника
@app.route('/update_username', methods=['POST'])
@login_required
def update_username():
    data = request.get_json()
    new_username = data.get('username')

    if not new_username:
        return jsonify({"success": False, "error": "Нік не може бути порожнім"}), 400

    # Проверяем, что ник уникальный
    existing_user = User.query.filter_by(username=new_username).first()
    if existing_user:
        return jsonify({"success": False, "error": "Користувач з таким ніком вже існує"}), 400

    current_user.username = new_username
    db.session.commit()

    return jsonify({"success": True})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    if 'avatar' not in request.files:
        return jsonify({"success": False, "error": "Файл не знайдено."})

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({"success": False, "error": "Файл не вибрано."})

    if file and allowed_file(file.filename):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filename = secure_filename(f"{current_user.id}.png")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Обновляем аватар в БД и в объекте current_user
        current_user.avatar = f"images/avatars/{filename}"  # Сохраняем путь без префикса static/
        db.session.commit()
        db.session.refresh(current_user)  # Обновляем объект current_user без выхода

        return jsonify(
            {"success": True, "avatar": url_for('static', filename=current_user.avatar, _external=True)})

    return jsonify({"success": False, "error": "Неправильний формат файлу."})

@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    data = request.get_json()
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if new_password != confirm_password:
        return jsonify({"success": False, "error": "Паролі не співпадають"}), 400

    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({"success": True})


@app.route('/get_user_password', methods=['POST'])
@login_required
def get_user_password():
    data = request.get_json()
    entered_password = data.get('password')

    if current_user.check_password(entered_password):
        return jsonify({"success": True, "password": entered_password})
    else:
        return jsonify({"success": False}), 401


@app.route('/clear_flash_messages', methods=['POST'])
def clear_flash_messages():
    session.pop('_flashes', None)  # Очищаем все сообщения flash
    return '', 204  # Возвращаем пустой ответ с кодом 204 (No Content)

if __name__ == "__main__":
    app.run(debug=True)