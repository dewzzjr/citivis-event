function loadRefreshButton(data, url) {
  var html =
    `<a href='#' ` +
    `onclick='sendAjax(` +
    JSON.stringify(data) + `,"` + url + `")'>` +
    `<i class='material-icons'>refresh</i>` +
    `</a>`;
  $('#sideList').html(html);
}

function sendAjax(data, url) {
  $.ajax({
    contentType: "application/json",
    type: "POST",
    url: url,
    data: JSON.stringify(data),
    dataType: "text",
    onLoading: function () {
      $('#sideList').html('<div class="loader"></div>');
    },
    success: function (text) {
      $('#sideList').html(text);
    },
    error: function (xhr, ajaxOptions, thrownError) {
      console.log(xhr.status);
      console.log(xhr.responseText);
      console.log(thrownError);

      loadRefreshButton(data, url);
    }
  });
}
