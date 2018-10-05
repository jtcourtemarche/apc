var socket = io.connect('ws://' + document.domain + ':' + location.port);

var $form = $('#apc-form');

window.onload = function() {
    // Generate breadcrumb forms
    var i;
    var html = ""
    for (i=0; i<=5; i++) {
        html += '<tr><td><input type="text" id="breadcrumb-'+i+'-title" placeholder="Title #'+i+'"></td><td><input type="text" id="breadcrumb-'+i+'-link" placeholder="Link #'+i+'"></td></tr>';
    }
    $('.breadcrumbs').html(html);
}

$form.submit(function() {
    if ($('textarea').val() == '') {
        return false;
    } else {
        var breadcrumbs = [];
        for (i=0; i<=5; i++) {
            var title = $('#breadcrumb-'+i+'-title').val();
            var link = $('#breadcrumb-'+i+'-link').val();
        
            if (title == '') {
                break;
            } else {
                breadcrumbs.push(title, link);
            }
        }

        socket.emit('run_crawler', {data:$form.serializeArray(), breadcrumbs:breadcrumbs})
        $('textarea').prop('disabled', true);
        return false;
    }
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
    //$('textarea').val('');
    $('#output-log').empty();
});
$('#clear_output_button').click(function() {
    $.post('/clear'); 
});
$('#clear_cache_button').click(function() {
    socket.emit('clear_img_cache');
})

socket.on('crawler-change', function(crawler) {
    $('#output-log').empty();
    $('.crawler').html(crawler.toUpperCase());
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