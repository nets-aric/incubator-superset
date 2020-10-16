/*jslint browser: true*/
/*global $*/


$(document).ready(function () {
  $.get('/tables/clientside_table', function (data) {
    $('#clientside_table').DataTable({
      data: data.data,
      paging: true,
      dom: 'frtipB',
      columns: [
        {"data": "ID", "title": "ID"},
        {"data": "mD_country", "title": "mD_country"},
        {"data": "lookup", "title": "lookup"}
      ]
    });
  });
});
