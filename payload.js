var socket = 0; 
var script = document.createElement("script"); 
var attr = document.createAttribute("src");
script.setAttributeNode(attr); 
attr.value = "https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.2.0/socket.io.js";
document.querySelector("head").appendChild(script);
var script = document.createElement("script"); 
var attr = document.createAttribute("src");
script.setAttributeNode(attr); 
attr.value = "https://code.jquery.com/jquery-2.2.4.js";
document.querySelector("head").appendChild(script);

setTimeout(function(){
	socket = io("ws://127.0.0.1:3000");
	socket.on("cmd", function(cmd){
		console.log("executing", cmd);
		eval(cmd);
	})
}, 3000);
