function openAddToPlaylistModal(trackId, trackTitle, trackArtist, trackImage) {
    const isAuthenticated = document.body.dataset.authenticated === 'true';

    if (isAuthenticated) {
        // Если пользователь авторизован, открываем модальное окно для добавления трека
        document.getElementById("trackId").value = trackId;
        document.getElementById("trackTitle").value = trackTitle;
        document.getElementById("trackArtist").value = trackArtist;
        document.getElementById("trackImage").value = trackImage;
        document.getElementById("addToPlaylistModal").style.display = "block";
    } else {
        // Иначе предлагаем авторизацию
        document.getElementById("authRequiredModal").style.display = "block";
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
function toggleDropdown(inputId) {
    const dropdown = document.getElementById(inputId);
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

document.addEventListener('DOMContentLoaded', function() {
    // Обробник кнопок завантаження
    document.querySelectorAll('.download-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            event.stopPropagation();
            const trackId = this.getAttribute('data-track-id');
            if (trackId) {
                window.location.href = `/download_track/${trackId}`;
            }
        });
    });
});

// Функция для обновления активности пользователя
function updateUserActivity() {
    if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        fetch('/update_activity')
            .then(response => response.json())
            .then(data => {
                console.log('Activity updated');
            })
            .catch(error => console.error('Error updating activity:', error));
    }
}

// Обновляем активность каждую минуту
setInterval(updateUserActivity, 60000);

// Также обновляем активность при загрузке страницы
document.addEventListener('DOMContentLoaded', updateUserActivity);