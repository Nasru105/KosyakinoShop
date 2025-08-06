function bindPhoneFormatters() {
    const phoneInput = document.getElementById('id_phone_number');

    if (phoneInput) {
        // Форматирование при вводе
        phoneInput.addEventListener('input', function (e) {
            let phone = e.target.value.replace(/\D/g, '');

            // Убираем +7, 7 или 8 в начале
            if (phone.startsWith('7') || phone.startsWith('8')) {
                phone = phone.substring(1);
            } else if (phone.startsWith('7')) {
                phone = phone.substring(1);
            }

            // Ограничение на 10 цифр
            phone = phone.slice(0, 10);

            const match = phone.match(/^(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})$/);

            let formatted = '';
            if (match[1]) formatted += `(${match[1]}`;
            if (match[2]) formatted += `) ${match[2]}`;
            if (match[3]) formatted += `-${match[3]}`;
            if (match[4]) formatted += `-${match[4]}`;

            e.target.value = formatted;
        });

        // Форматирование при загрузке
        const val = phoneInput.value.replace(/\D/g, '').slice(0, 10);
        if (val.length === 10) {
            phoneInput.value = `(${val.substr(0, 3)}) ${val.substr(3, 3)}-${val.substr(6, 2)}-${val.substr(8, 2)}`;
        }
    }

    // Валидация телефона
    function validatePhoneNumber(event) {
        const $phone = $('#id_phone_number');
        if ($phone.length === 0) return;

        const cleaned = $phone.val().replace(/[()\+\-\s]/g, '');
        if ( /^\d{10}$/.test(cleaned)) {
            $('#phone_number_error').hide();
            $phone.val(cleaned);
        } else {
            $('#phone_number_error').show();
            event.preventDefault();
        }
    }

    // Подключаем валидацию к формам
    if ($('#create_order_form').length > 0) {
        $('#create_order_form').on('submit', validatePhoneNumber);
    }
    if ($('#profile_form').length > 0) {
        $('#profile_form').on('submit', validatePhoneNumber);
    }
}
