$(document).ready(function () {
    var successMessage = $("#jq-notification");

    bindCartHandlers();
    bindCheckoutHandlers();
    bindCommentHandlers();
    bindModalHandlers();
    bindNotificationHandlers();
    bindPhoneFormatters();
    bindCancelOrderHandlers();
});
