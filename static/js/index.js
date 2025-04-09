function showToast(message) {
    let toastContainer = document.getElementById("toast-container");
    let toast = document.createElement("div");
    toast.classList.add("toast");
    toast.innerHTML = `${message} <span class="close-toast" onclick="this.parentElement.style.display='none'">&times;</span>`;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.style.display = "none";
    }, 10000);
}

function submitPlaylist() {
    let playlistName = document.getElementById("playlistNameInput").value.trim();
    if (playlistName === "") {
        showToast("Назва плейліста не може бути порожньою!");
        return;
    }
    document.getElementById("hiddenPlaylistName").value = playlistName;
    document.getElementById("createPlaylistForm").submit();
}

let currentPlaylistId = null;

// Функції для роботи з модальними вікнами
function openRenameModal(playlistId, currentName) {
    currentPlaylistId = playlistId;
    document.getElementById('newPlaylistName').value = currentName;
    document.getElementById('renameModal').style.display = 'flex';
}

function openDeletePlaylistModal(playlistId) {
    currentPlaylistId = playlistId;
    document.getElementById('deletePlaylistModal').style.display = 'flex';
}

// Оновлення назви плейліста
function updatePlaylistName() {
    const newName = document.getElementById("newPlaylistName").value.trim();
    if (!newName) {
        showToast("Назва плейліста не може бути порожньою!");
        return;
    }

    fetch("/update_playlist_name", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            playlist_id: currentPlaylistId,
            new_name: newName
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast("Назву плейліста оновлено!");
                window.location.reload();
            } else {
                showToast("Помилка: " + (data.error || "Не вдалося оновити назву"));
            }
            closeModal('renameModal');
        });
}

// Видалення плейліста
function deletePlaylist() {
    fetch("/delete_playlist", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            playlist_id: currentPlaylistId
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                 window.location.reload();
            } else {
                showToast("Помилка: " + (data.error || "Не вдалося видалити плейліст"));
                closeModal('deletePlaylistModal');
            }
        });
}