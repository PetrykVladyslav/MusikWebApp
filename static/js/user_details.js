// Функція для перемикання видимості пароля
function toggleVisibility(inputId) {
    const inputField = document.getElementById(inputId);
    const eyeIcon = inputField.nextElementSibling; // Отримуємо іконку ока

    if (inputField.type === 'password') {
        inputField.type = 'text';
        eyeIcon.classList.remove('fa-eye');
        eyeIcon.classList.add('fa-eye-slash');
    } else {
        inputField.type = 'password';
        eyeIcon.classList.remove('fa-eye-slash');
        eyeIcon.classList.add('fa-eye');
    }
}

// Функция для отображения всплывающего сообщения
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.innerText = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 5000);
}

// Запускаємо оновлення при завантаженні та кожну хвилину
document.addEventListener('DOMContentLoaded', function () {
    updateActivity();
    setInterval(updateActivity, 60000);
});