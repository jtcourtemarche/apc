var socket = io.connect('ws://' + document.domain + ':' + location.port);

var $form = $('#apc-form');

$form.submit(function() {
	socket.emit('run_crawler', {data:$form.serializeArray()})
	return false;
});

socket.on('payload', function(data) {
	if (data.includes('[Complete]')) {
		$('#output-log').append('<div class="alert alert-success" role="alert">'+ data +'</div><hr>');
	} else if (data.includes('[Error]')) {
		$('#output-log').append('<div class="alert alert-danger" role="alert">'+ data +'</div><hr>');	
	}
	else {
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