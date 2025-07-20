function bindCommentHandlers() {

    $(document).on("click", ".edit-comment-btn, .add-comment-btn", function() {
        let orderId = $(this).data("order-id");
        console.log("Клик по .save-comment-btn");
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
            error: function(xhr, status, error) {
                console.error("AJAX Error:", status, error);
                console.error("Response Text:", xhr.responseText);
                alert("Ошибка при сохранении комментария.");
            }
        });
    });
};