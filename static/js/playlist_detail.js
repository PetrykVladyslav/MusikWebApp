let currentTrackIdToDelete = null;

// Функция для показа модального окна
function showDeleteModal(trackId, event) {
    event.stopPropagation(); // Останавливаем всплытие события
    currentTrackIdToDelete = trackId;
    document.getElementById("deleteModal").style.display = "flex";
}

// Функция для показа toast-уведомления
function showToast(message) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}