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