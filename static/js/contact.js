$(function () {
  var form = $("#ajax_form");
  var formMessages = $("#form-messages");

  form.on("submit", function (event) {
    event.preventDefault();

    $.ajax({
      type: "POST",
      url: form.attr("action"),
      data: form.serialize(),
    })
      .done(function (response) {
        formMessages.removeClass("alert-danger").addClass("alert-success");
        formMessages.text(response);

        $("#name").val("");
        $("#email").val("");
        $("#message").val("");
      })
      .fail(function (data) {
        formMessages.removeClass("alert-success").addClass("alert-danger");

        if (data.responseText !== "") {
          formMessages.text(data.responseText);
          return;
        }

        formMessages.text(
          "Oops! An error occurred and your message could not be sent."
        );
      });
  });
});
