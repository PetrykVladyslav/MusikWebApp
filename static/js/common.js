function togglePlaylistDropdown() {
    const dropdown = document.getElementById("playlistDropdown");
    if (dropdown.style.display === "block") {
        dropdown.style.display = "none";
    } else {
        dropdown.style.display = "block";
    }
}

function closeAddToPlaylistModal() {
    document.getElementById("addToPlaylistModal").style.display = "none";
    document.getElementById("playlistDropdown").style.display = "none"; // Закрываем выпадающий список при закрытии модального окна
}

document.querySelectorAll(".flash").forEach(flash => {
    setTimeout(() => {
        flash.remove();
    }, 3000);

    flash.addEventListener("click", () => {
        flash.remove();
    });
});

// Функция для сохранения состояния плеера в localStorage
function savePlayerState() {
    const playerState = {
        trackId: currentTrack?.id,
        trackTitle: currentTrack?.title,
        trackArtist: currentTrack?.artist,
        trackImage: currentTrack?.image,
        previewUrl: audioPlayer.src,
        currentTime: audioPlayer.currentTime,
        volume: audioPlayer.volume,
        isPlaying: !audioPlayer.paused,
    };
    localStorage.setItem("playerState", JSON.stringify(playerState));
}

// Функция для удаления состояния плеера из localStorage
function closePlayerState() {
    localStorage.removeItem("playerState"); // Удаляем состояние плеера из localStorage
    localStorage.setItem("playerManuallyClosed", "true"); // Устанавливаем флаг, что плеер был закрыт вручную
}

// Функция для восстановления состояния плеера из localStorage
function restorePlayerState() {
    const savedState = localStorage.getItem("playerState");
    const isManuallyClosed = localStorage.getItem("playerManuallyClosed") === "true"; // Проверяем флаг

    if (savedState && !isManuallyClosed) { // Восстанавливаем только если плеер не был закрыт вручную
        const playerState = JSON.parse(savedState);

        if (playerState.trackId) {
            currentTrack = {
                id: playerState.trackId,
                title: playerState.trackTitle,
                artist: playerState.trackArtist,
                image: playerState.trackImage,
            };

            audioPlayer.src = playerState.previewUrl;
            audioPlayer.currentTime = playerState.currentTime || 0;
            audioPlayer.volume = playerState.volume || 1;

            if (playerState.isPlaying) {
                audioPlayer.play();
                playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            } else {
                audioPlayer.pause();
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            }

            document.getElementById("player-track-image").src = playerState.trackImage;
            document.getElementById("player-track-title").textContent = playerState.trackTitle;
            document.getElementById("player-track-artist").textContent = playerState.trackArtist;
            document.getElementById("player").classList.add("active");

            // Восстанавливаем значение ползунка громкости
            const volumeControl = document.getElementById("volume-control");
            volumeControl.value = playerState.volume || 1;
        }
    }
}

// Восстанавливаем состояние плеера при загрузке страницы
window.addEventListener("load", restorePlayerState);

// Функція для перегляду пароля
function togglePasswordVisibility() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.querySelector('.toggle-password');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

//Випадаюче вікно
function toggleDropdown() {
    const dropdown = document.getElementById("userDropdown");
    if (dropdown.style.display === "block") {
        dropdown.style.display = "none";
    } else {
        dropdown.style.display = "block";
    }
}

// Закриваємо випадаюче меню, якщо клікнули поза ним
window.onclick = function(event) {
    if (!event.target.matches('.user-avatar img')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.style.display === "block") {
                openDropdown.style.display = "none";
            }
        }
    }
}

// Получаем модальное окно
var modal = document.getElementById("errorModal");

// Когда пользователь кликает вне модального окна, закрываем его
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Функция для отображения модального окна с сообщением об ошибке
function showErrorModal(message) {
    document.getElementById("errorMessage").innerText = message;
    modal.style.display = "block";
}

// Функция для очистки сообщений flash
function clearFlashMessages() {
    fetch('/clear_flash_messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    }).then(response => {
        if (response.status === 204) {
            console.log("Flash messages cleared successfully.");
        }
    });
}

// Функция для открытия модального окна
function openModal(inputId) {
    document.getElementById(inputId).style.display = 'block';
}

// Функция для закрытия модального окна
function closeModal(inputId) {
    document.getElementById(inputId).style.display = 'none';
}