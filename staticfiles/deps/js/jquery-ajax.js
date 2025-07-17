// Когда html документ готов (прорисован)
$(document).ready(function () {
    // берем в переменную элемент разметки с id jq-notification для оповещений от ajax
    var successMessage = $("#jq-notification");

    // Ловим собыитие клика по кнопке добавить в корзину
    $(document).on("click", ".add-to-cart", function (e) {
        // Блокируем его базовое действие
        e.preventDefault();

        // Берем элемент счетчика в значке корзины и берем оттуда значение
        var goodsInCartCount = $("#goods-in-cart-count");
        var cartCount = parseInt(goodsInCartCount.text() || 0);

        // Получаем id товара из атрибута data-product-id
        var product_id = $(this).attr("data-product-id");


        // Из атрибута href берем ссылку на контроллер django
        var add_to_cart_url = $(this).attr("href");

        // делаем post запрос через ajax не перезагружая страницу
        $.ajax({
            type: "POST",
            url: add_to_cart_url,
            data: {
                product_id: product_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 5сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 5000);

                // Увеличиваем количество товаров в корзине (отрисовка в шаблоне)
                cartCount++;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины на ответ от django (новый отрисованный фрагмент разметки корзины)
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },

            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    });

    // Ловим собыитие клика по кнопке удалить товар из корзины
    $(document).on("click", ".remove-from-cart", function (e) {
        // Блокируем его базовое действие
        e.preventDefault();

        // Берем элемент счетчика в значке корзины и берем оттуда значение
        var goodsInCartCount = $("#goods-in-cart-count");
        var cartCount = parseInt(goodsInCartCount.text() || 0);

        // Получаем id корзины из атрибута data-cart-id
        var cart_id = $(this).data("cart-id");
        // Из атрибута href берем ссылку на контроллер django
        var remove_from_cart = $(this).attr("href");

        // делаем post запрос через ajax не перезагружая страницу
        $.ajax({

            type: "POST",
            url: remove_from_cart,
            data: {
                cart_id: cart_id,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function (data) {
                // Сообщение
                successMessage.html(data.message);
                successMessage.fadeIn(400);
                // Через 5сек убираем сообщение
                setTimeout(function () {
                    successMessage.fadeOut(400);
                }, 5000);

                // Уменьшаем количество товаров в корзине (отрисовка)
                cartCount -= data.quantity_deleted;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины на ответ от django (новый отрисованный фрагмент разметки корзины)
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },

            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    });

    // Теперь + - количества товара 
    // Обработчик события для уменьшения значения
    $(document).on("click", ".decrement", function () {
        // Берем ссылку на контроллер django из атрибута data-cart-change-url
        var url = $(this).data("cart-change-url");
        // Берем id корзины из атрибута data-cart-id
        var cartID = $(this).data("cart-id");
        // Ищем ближайшеий input с количеством 
        var $input = $(this).closest('.input-group').find('.number');
        // Берем значение количества товара
        var currentValue = parseInt($input.val());
        // Если количества больше одного, то только тогда делаем -1
        if (currentValue > 1) {
            $input.val(currentValue - 1);
            // Запускаем функцию определенную ниже
            // с аргументами (id карты, новое количество, количество уменьшилось или прибавилось, url)
            updateCart(cartID, currentValue - 1, -1, url);
        }
    });

    // Обработчик события для увеличения значения
    $(document).on("click", ".increment", function () {
        // Берем ссылку на контроллер django из атрибута data-cart-change-url
        var url = $(this).data("cart-change-url");
        // Берем id корзины из атрибута data-cart-id
        var cartID = $(this).data("cart-id");
        // Ищем ближайшеий input с количеством 
        var $input = $(this).closest('.input-group').find('.number');
        // Берем значение количества товара
        var currentValue = parseInt($input.val());

        $input.val(currentValue + 1);

        // Запускаем функцию определенную ниже
        // с аргументами (id карты, новое количество, количество уменьшилось или прибавилось, url)
        updateCart(cartID, currentValue + 1, 1, url);
    });

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

                // Изменяем количество товаров в корзине
                var goodsInCartCount = $("#goods-in-cart-count");
                var cartCount = parseInt(goodsInCartCount.text() || 0);
                cartCount += change;
                goodsInCartCount.text(cartCount);

                // Меняем содержимое корзины
                var cartItemsContainer = $("#cart-items-container");
                cartItemsContainer.html(data.cart_items_html);

            },
            error: function (data) {
                console.log("Ошибка при добавлении товара в корзину");
            },
        });
    }

    // Берем из разметки элемент по id - оповещения от django
    var notification = $('#notification');
    // И через 7 сек. убираем
    if (notification.length > 0) {
        setTimeout(function () {
            notification.alert('close');
        }, 5000);
    }

    // При клике по значку корзины открываем всплывающее(модальное) окно
    $('#modalButton').click(function () {
        $('#exampleModal').appendTo('body');

        $('#exampleModal').modal('show');
    });

    // Собыите клик по кнопке закрыть окна корзины
    $('#exampleModal .btn-close').click(function () {
        $('#exampleModal').modal('hide');
    });

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


    // Форматирование номера телефона при вводе
    document.getElementById('id_phone_number').addEventListener('input', function (e) {
        var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
        e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '') + (x[4] ? '-' + x[4] : '');
    });

    // Форматирование номера при загрузке страницы
    document.addEventListener('DOMContentLoaded', function () {
        var input = document.getElementById('id_phone_number');
        if (!input) return;

        var val = input.value.replace(/\D/g, ''); // убираем всё, кроме цифр

        // Ожидаем, что вал содержит 10 цифр — без кода страны +7
        if (val.length === 10) {
            var formatted = '(' + val.substr(0,3) + ') ' + val.substr(3,3) + '-' + val.substr(6,4);
            input.value = formatted;
        }
    });


    // Проверяем на стороне клиента корректность номера телефона в форме 8 xxx-xxx-хх-хх
    function validatePhoneNumber(event) {
        var phoneNumber = $('#id_phone_number').val();
        var cleanedPhoneNumber = phoneNumber.replace(/[()\+\-\s]/g, ''); // Убираем скобки, пробелы, + и -

        // Проверяем, что номер либо пустой, либо ровно 11 цифр (формат 8xxxxxxxxxx)
        if (cleanedPhoneNumber === '' || /^\d{10}$/.test(cleanedPhoneNumber)) {
            $('#phone_number_error').hide();
            $('#id_phone_number').val(cleanedPhoneNumber);
        } else {
            $('#phone_number_error').show();
            event.preventDefault();
        }
    }

    $('#create_order_form').on('submit', function (event) {
        validatePhoneNumber(event);
    });

    $('#profile_form').on('submit', function (event) {
        validatePhoneNumber(event);
    });

    $(document).on("click", ".edit-comment-btn, .add-comment-btn", function() {
        let orderId = $(this).data("order-id");
        $("#comment-form-container-" + orderId).removeClass("d-none");
    });

    $(document).on("click", ".cancel-comment-btn", function() {
        let orderId = $(this).data("order-id");
        $("#comment-form-container-" + orderId).addClass("d-none");
    });

    $(document).on("click", ".save-comment-btn", function() {
        let orderId = $(this).data("order-id");
        let comment = $("#comment-text-" + orderId).val();
        let update_order_comment_url = $(this).data("url");

        $.ajax({
            url: update_order_comment_url,
            method: "POST",
            data: {
                comment: comment,
                csrfmiddlewaretoken: $("[name=csrfmiddlewaretoken]").val(),
            },
            success: function(data) {
                // Найти контейнер кнопки или блока комментария
                let commentContainer = $("#order-comment-" + orderId);

                if (commentContainer.length > 0) {
                    // Если блок уже есть, просто обновить текст
                    commentContainer
                        .html("<strong>Комментарий:</strong> " + comment)
                        .show();
                } else {
                    // Иначе создать новый блок комментария перед кнопкой добавления
                    let commentHtml = `
                        <div class="mb-2">
                            <p id="order-comment-${orderId}">
                                <strong>Комментарий:</strong> ${comment}
                            </p>
                            <button id="edit-comment-btn-${orderId}"
                                    class="btn btn-sm btn-primary edit-comment-btn"
                                    data-order-id="${orderId}">
                                Редактировать
                            </button>
                        </div>
                    `;

                    // Вставить новый блок перед кнопкой "Добавить комментарий"
                    $("#add-comment-btn-" + orderId).before(commentHtml);

                    // Удалить кнопку "Добавить комментарий"
                    $("#add-comment-btn-" + orderId).remove();
                }

                $("#comment-form-container-" + orderId).hide();
            },
            error: function() {
                alert("Ошибка при сохранении комментария.");
            }
        });
    });

});