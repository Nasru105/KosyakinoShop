$(document).ready(function () {

})
function bindNotificationHandlers() {
    // Берем из разметки элемент по id - оповещения от django
    var notification = $('#notification');
    // И через 7 сек. убираем
    if (notification.length > 0) {
        setTimeout(function () {
            notification.alert('close');
        }, 5000);
    }
}
function showNotification(message, duration = 5000) {
    const notification = $("#jq-notification");
    notification.html(message).fadeIn(400);
    setTimeout(() => notification.fadeOut(400), duration);
}