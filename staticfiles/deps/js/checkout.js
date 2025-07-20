function bindCheckoutHandlers() {

    // Инициализация - проверяем выбранную радиокнопку при загрузке страницы
    var initialValue = $("input[name='requires_delivery']:checked").val();
    if (initialValue === "1") {
        $("#deliveryAddressField").show();
    }

    var defaultDelivery = $("input[name='requires_delivery']:checked").val();
    if (defaultDelivery === "0") {
        $("#pickupAddressField").show();
    }

    $("input[name='requires_delivery']").change(function() {
        var selectedValue = $(this).val();
        if (selectedValue === "1") {
            // Доставка
            $("#deliveryAddressField").slideDown(200);
            $("#pickupAddressField").slideUp(200);
            $("#paymentOnGetField1").slideUp(200);

            // Установить оплату картой (value="0")
            $("input[name='payment_on_get'][value='0']").prop("checked", true);

        } else {
            // Самовывоз
            $("#deliveryAddressField").slideUp(200);
            $("#paymentOnGetField1").slideDown(200);
            $("#pickupAddressField").slideDown(200);
        }
    });
}