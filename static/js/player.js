const player = document.getElementById("player");
const audioPlayer = document.getElementById("audio-player");
const playPauseBtn = document.getElementById("play-pause-btn");
const speedUpBtn = document.getElementById("speed-up-btn");
const closePlayerBtn = document.getElementById("close-player-btn");
const seekBar = document.getElementById("seek-bar");
const volumeControl = document.getElementById("volume-control");
let currentTrack = null;

// Функция для открытия плеера и загрузки трека
function playPreview(trackId, trackTitle, trackArtist, trackImage) {
    localStorage.setItem("playerManuallyClosed", "false"); // Сбрасываем флаг, так как плеер снова открыт
    fetch(`/get_preview/${trackId}`)
        .then(response => response.json())
        .then(data => {
            let previewUrl = data.preview_url;
            if (previewUrl) {
                document.getElementById("audio-player").src = previewUrl;
                document.getElementById("player-track-image").src = trackImage;
                document.getElementById("player-track-title").textContent = trackTitle;
                document.getElementById("player-track-artist").textContent = trackArtist;
                document.getElementById("player").classList.add("active");
                document.getElementById("audio-player").play();

                currentTrack = {id: trackId, title: trackTitle, artist: trackArtist, image: trackImage};
                savePlayerState(); // Сохраняем состояние плеера
            } else {
                showToast("Цей трек не підтримує прев'ю!");
            }
        })
        .catch(error => console.error("Ошибка загрузки превью:", error));
}

// Добавляем обработчик клика по трекам
document.querySelectorAll(".result-card, .track-card, .track-item").forEach(card => {
    card.addEventListener("click", () => {
        let trackId = card.dataset.trackId;
        let trackTitle = card.querySelector("h3").textContent;
        let trackArtist = card.querySelector("p").textContent;
        let trackImage = card.querySelector("img").src;
        playPreview(trackId, trackTitle, trackArtist, trackImage);
    });
});

// Управление воспроизведением
playPauseBtn.addEventListener("click", () => {
    if (audioPlayer.paused) {
        audioPlayer.play();
        playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
    } else {
        audioPlayer.pause();
        playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
    }
    savePlayerState(); // Сохраняем состояние
});

// Ускорение трека
speedUpBtn.addEventListener("click", () => {
    if (audioPlayer.playbackRate === 1) {
        audioPlayer.playbackRate = 1.5;
    } else {
        audioPlayer.playbackRate = 1;
    }
    savePlayerState(); // Сохраняем состояние
});

// Закрытие плеера
closePlayerBtn.addEventListener("click", () => {
    player.classList.remove("active");
    audioPlayer.pause();
    closePlayerState(); // Удаляем состояние плеера из localStorage и устанавливаем флаг
});

// Перемотка трека
seekBar.addEventListener("input", () => {
    const seekTime = (audioPlayer.duration / 100) * seekBar.value;
    audioPlayer.currentTime = seekTime;
    savePlayerState(); // Сохраняем состояние
});

// Обновление ползунка при воспроизведении
audioPlayer.addEventListener("timeupdate", () => {
    const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
    seekBar.value = progress;
    savePlayerState(); // Сохраняем состояние
});

// Обработчик изменения громкости
volumeControl.addEventListener("input", () => {
    audioPlayer.volume = volumeControl.value;
    savePlayerState(); // Сохраняем состояние
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