$(document).ready(function() {


const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const sliceId = parseInt(urlParams.get('slice_id'))

function getSql() {
    return sqlQuery
}

//var chrt_id = parseInt( $('#chart_id').val(), 10 )
console.log("Check inserted value")
console.log(getSql())

if (typeof(sliceId) !== 'undefined') {
$.getJSON('/tables/get_columns',{ chart_id : sliceId } , function(sqlcolumns) {

      sqlcolumns.forEach(function(col_n, index) {
       $('#serverside_table thead tr:eq(0)').append("<th>"+ col_n.data +"</th>")

       $('#serverside_table thead tr:eq(1)').append("<th>"+ '<input type="text" placeholder="Search '+col_n.data+'" />' +"</th>")
       });
var table =  $('#serverside_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    sPaginationType: "full_numbers",
    lengthMenu: [[10, 25, 50, 100], [10, 25, 50, 100]],
    renderer: { "header": "bootstrap" },
    bjQueryUI: true,
    orderCellsTop: true,
    dom: 'lBfrtip',
            colReorder: true,
            stateSave: true,
            buttons: [
             'csv', 'excel'
            ],
    sAjaxSource: '/tables/serverside_table',
    fnServerParams: function ( aoData ) { var limit = parseInt( $('#limit').val(), 10 ); const queryString = window.location.search; const urlParams = new URLSearchParams(queryString); const sliceId = parseInt(urlParams.get('slice_id')) ; aoData.push( { 'name': 'query_limit', 'value':limit });aoData.push( { 'name': 'chart_id', 'value':sliceId });},
    columns:sqlcolumns,
    initComplete: function () {
            // Apply the search
            this.api().columns().every( function () {
                var that = this;
           $('.dataTables_scrollBody thead tr').css({visibility:'collapse'});
        }
    );
}

} );

    table.columns().every(function (index) {
        $('#serverside_table thead tr:eq(1) th:eq(' + index + ') input').on('keyup change', function () {
            table.column($(this).parent().index() + ':visible')
                .search(this.value)
                .draw();
        });
    });

$('#limit').keyup( function() {
        table.draw();
    } );

});
}
else {
 return
}
});
