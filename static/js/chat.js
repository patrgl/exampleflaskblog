$(document).ready(function() {
    var socket = io.connect("http://127.0.0.1:5000"); // switch to current ip on network if you want chat to work on local network
    socket.on('connect', function() {
        socket.send("User connected");
    });

    socket.on('message', function(data) {
        $('#messages').append($('<p>').text(data));
        $('#messages').scrollTop($('#messages')[0].scrollHeight);
    });

    function sendMessage() {
        socket.send($('#username').val() + ': ' + $('#message').val());
        $('#message').val('');
    }

    $('#sendBtn').on('click', function() {
        sendMessage();
    });

    $('#message').on('keypress', function(event) {
        if (event.which === 13) { // Enter key pressed
            sendMessage();
        }
    });
});