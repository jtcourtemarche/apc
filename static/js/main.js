var socket = io.connect('ws://' + document.domain + ':' + location.port);

var $form = $('#apc-form');

$form.submit(function() {
    socket.emit('run_crawler', {data:$form.serializeArray()})
    $('textarea').prop('disabled', true);
    return false;
});

socket.on('payload', function(data) {
    if (data.includes('[Complete]')) {
        $('#output-log').append('<div class="alert alert-success" role="alert">'+ data +'</div><hr>');
        $('textarea').prop('disabled', false);
    } else if (data.includes('[Error]')) {
        $('#output-log').append('<div class="alert alert-danger" role="alert">'+ data +'</div><hr>');   
        $('textarea').prop('disabled', false);
    } else if (data.includes('[Warning]')) {
        $('#output-log').append('<div class="alert alert-warning" role="alert">'+ data +'</div>');  
    } else {
        $('#output-log').append('<span>'+data+'</span><br/>');
    }
});

$('#clear_button').click(function() {
    $('textarea').val('');
    $('#output-log').empty();
});
$('#clear_output_button').click(function() {
    $.post('/clear'); 
});

// Get list of available crawlers
socket.emit('list-crawlers')

socket.on('crawlers', function(crawlers) {
    for (crawler in crawlers) {
        $('.dropdown-menu').append('<a class="dropdown-item" href="#" onclick="set_crawler(\''+ crawlers[crawler] +'\')">' + crawlers[crawler] + '</a>')
    }
});

function set_crawler(crawler) {
    socket.emit('set', {settings: ['crawler', crawler]})
}