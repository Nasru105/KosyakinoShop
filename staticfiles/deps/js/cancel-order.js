function bindCancelOrderHandlers() {
    console.log("Привет");
    $(document).on("click", ".cancel-order-btn", function () {

        let orderId = $(this).data("order-id");
        let cancelUrl = $(this).data("url");

        if (!confirm("Вы уверены, что хотите отменить заказ?")) return;

        $.ajax({
            url: cancelUrl,
            method: "POST",
            data: {
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                if (data.success) {
                    // Меняем статус на "Отменён"
                    $("#cancel-order-btn-" + orderId)
                        .replaceWith('<span class="badge bg-danger">Отменён</span>');
                    $("#order-status-" + orderId)
                        .replaceWith('<span class="badge bg-danger">Заказ отменён</span>');
                    $("#order-delivery-status-" + orderId)
                        .replaceWith('<span class="badge bg-danger">Заказ отменён</span>');

                    // Показываем уведомление об успехе
                    showNotification(data.message || "Заказ успешно отменён!", "success");
                } else {
                    // Показываем уведомление об ошибке
                    showNotification(data.message || "Невозможно отменить заказ", "danger");
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX Error:", status, error);
                console.error("Response Text:", xhr.responseText);
                showNotification("Ошибка при отмене заказа. Попробуйте позже.", "danger");
            }
        });
    });
}
