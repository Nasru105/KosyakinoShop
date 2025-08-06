
// Закрытие Django-уведомлений
function bindNotificationHandlers() {
    const notification = $('#notification');
    if (notification.length > 0) {
        setTimeout(() => {
            notification.fadeOut(400, () => notification.remove());
        }, 5000);
    }
}

// Универсальная функция для показа уведомлений
function showNotification(message, type = "success", duration = 5000) {
    const notification = $("#jq-notification");

    // Удаляем предыдущие классы и добавляем новый по типу уведомления
    notification
        .removeClass("alert-success alert-danger alert-warning alert-info")
        .addClass(`alert alert-${type}`)
        .html(message)
        .fadeIn(300);

    // Автоматическое скрытие
    setTimeout(() => {
        notification.fadeOut(400);
    }, duration);
}
