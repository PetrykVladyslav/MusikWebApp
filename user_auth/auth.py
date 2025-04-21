# Імпорт всіх необхідних бібліотек.
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# Ініціалізація SQLAlchemy
db = SQLAlchemy()

# Ініціалізація Flask-Login
login_manager = LoginManager()

# Модель користувача
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)  # Уникальный ник
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), nullable=False, default='images/default_avatar.png')
    playlists = db.relationship('Playlist', backref='user', lazy=True, cascade="all, delete-orphan")
    last_active = db.Column(db.DateTime, default=datetime.utcnow)  # Последняя активность
    total_time_online = db.Column(db.Integer, default=0)  # Время в секундах

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Модель плейліста
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)  # Указывает, что это избранный плейлист
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tracks = db.relationship('Track', backref='playlist', lazy=True, cascade="all, delete-orphan")

    def get_favorite_playlist(user_id):
        return Playlist.query.filter_by(user_id=user_id, is_favorite=True).first()

# Модель треку
class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deezer_id = db.Column(db.String(50), nullable=False)  # ID трека в Deezer API
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    preview_url = db.Column(db.String(200))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)

def get_user_playlists(user_id):
    return Playlist.query.filter_by(user_id=user_id).all()

# Завантажувач користувача для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Функція для реєстрації користувача
def register_user(email, password, username):
    user = User.query.filter_by(email=email).first()
    if user:
        return False, "Користувач з таким email вже існує!"

    # Создание нового пользователя
    new_user = User(email=email, username=username)  # Добавляем ник
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()

        # Создаем плейлист "Обрані" сразу после регистрации
        favorite_playlist = Playlist(name="Обрані", is_favorite=True, user_id=new_user.id)
        db.session.add(favorite_playlist)
        db.session.commit()

        login_user(new_user)  # Автоматически логиним пользователя после регистрации
        return True, "Реєстрація успішна!"
    except Exception as e:
        db.session.rollback()
        return False, f"Помилка реєстрації: {str(e)}"

# Функція для входу користувача
def login_user_by_credentials(email, password):
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):  # Проверка хеша пароля
        user.last_active = datetime.utcnow()  # Фиксируем вход
        db.session.commit()
        login_user(user)
        return True, "Ви успішно увійшли!"

    return False, " Неправильний email або пароль!"

# Функція для виходу користувача
def logout_current_user(user):
    if user.is_authenticated:
        update_user_activity(user)  # Передаем user
        user.last_active = None  # Обнуляем
        db.session.commit()

    logout_user()
    return "Ви вийшли з системи."

# Функція для оновлення часу активності користувача.
def update_user_activity(user):
    """ Обновляет время активности пользователя """
    if user.is_authenticated:
        now = datetime.utcnow()
        if user.last_active:
            elapsed = (now - user.last_active).total_seconds()
            # Добавляем только если прошло не более 3 минут (чтобы избежать больших скачков при перезагрузке)
            if elapsed < 180:  # 3 минут в секундах
                user.total_time_online += int(elapsed)

        user.last_active = now
        db.session.commit()
