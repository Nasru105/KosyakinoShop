function bindCartHandlers() {
    console.log("Cart handlers initialized");

    $(document).off("click.cart");

    // Добавление товара
    $(document).on("click.cart", ".add-to-cart", function (e) {
        e.preventDefault();

        const productId = $(this).data("product-id");
        const url = $(this).attr("href");
        const cartCounter = $("#goods-in-cart-count");
        let cartCount = parseInt(cartCounter.text() || 0);

        $.ajax({
            type: "POST",
            url: url,
            data: {
                product_id: productId,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                showSuccessMessage(data.message);

                cartCount++;
                cartCounter.text(cartCount);

                $("#cart-items-container").html(data.cart_items_html);

                // Переинициализация обработчиков на новых элементах, если нужно
                bindCartHandlers();
            },
            error: function () {
                console.error("Ошибка при добавлении товара в корзину");
            },
        });
    });

    // Удаление товара
    $(document).on("click.cart", ".remove-from-cart", function (e) {
        e.preventDefault();

        const cartId = $(this).data("cart-id");
        const url = $(this).attr("href");
        const cartCounter = $("#goods-in-cart-count");
        let cartCount = parseInt(cartCounter.text() || 0);

        $.ajax({
            type: "POST",
            url: url,
            data: {
                cart_id: cartId,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                showSuccessMessage(data.message);

                cartCount -= data.quantity_deleted;
                cartCounter.text(cartCount);

                $("#cart-items-container").html(data.cart_items_html);

                bindCartHandlers();
            },
            error: function () {
                console.error("Ошибка при удалении товара из корзины");
            },
        });
    });

    // Увеличение и уменьшение количества
    $(document).on("click.cart", ".increment, .decrement", function () {
        const $this = $(this);
        const $input = $this.closest(".input-group").find(".number");
        const currentValue = parseInt($input.val());
        const cartID = $this.data("cart-id");
        const url = $this.data("cart-change-url");

        let newValue = currentValue;
        let change = 0;

        if ($this.hasClass("increment")) {
            newValue = currentValue + 1;
            change = 1;
        } else if ($this.hasClass("decrement") && currentValue > 1) {
            newValue = currentValue - 1;
            change = -1;
        }

        if (newValue !== currentValue) {
            $input.val(newValue);
            updateCart(cartID, newValue, change, url);
        }
    });
}

function updateCart(cartID, quantity, change, url) {
    $.ajax({
        type: "POST",
        url: url,
        data: {
            cart_id: cartID,
            quantity: quantity,
            csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
        },
        success: function (data) {
            const cartCounter = $("#goods-in-cart-count");
            let cartCount = parseInt(cartCounter.text() || 0);
            cartCount += change;
            cartCounter.text(cartCount);

            $("#cart-items-container").html(data.cart_items_html);
            bindCartHandlers();
        },
        error: function () {
            console.error("Ошибка при изменении количества товара");
        },
    });
}

function showSuccessMessage(message) {
    const successMessage = $("#jq-notification");
    successMessage.html(message).fadeIn(400);
    setTimeout(() => successMessage.fadeOut(400), 5000);
}
