$(document).ready(function () {
  $('#form-place').on('submit', function (e) {
    e.preventDefault();
    var place = $("#input-place").val();
    var link = '/search/' + place;
    window.location.href = link;
  });
});