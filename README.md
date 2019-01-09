This is a small security project that I put together in my spare time, and is inspired by the BEEF browser exploitation framework and XSStrike 
Comprises two parts: 
1) A script to automatically generate a Reflective XSS payload
2) The payload itself which starts reverse shell using a WebSocket client in the injected JS context that communicates back to our listening server. Arbitrary commands can then be sent thru the reverse shell to be executed inside the injected JS context. 

Usage Steps:
1. Install Python3 (Tested with 3.6.6 but will probably work for other versions)
2. Run "npm install"
3. Run "python3 xss.py website" to scan for possible Reflective XSS on website
4. If the Step 3 is successful, copy the output (it should contain an URL with payload embedded inside a GET parameter) open it in a browser window
5. Start listening server with "node server.js"
6. $$$

To test WebSocket shell:
1. alert(0)
2. And all BEEF payloads (currently only dom.js) can be accessed using dom Object:
ie. dom.removeStylesheets()

Future Features:
1. Filter Evasion
2. More JS modules for the WebSocket client
3. Better commandline interface for the shell (ala Metasploit shell autocomplete, search commands, list modules)

Summary of Exploit:
precondition: xss.py will only look for vectors XSS resulting input values that have the same "name" as the name of a corresponding GET url. This is a pretty big assumption to make, since any input GET parameter that does not have the same name as an input element will be missed. No filter evasion was implemented so any client/serverside filtering will render the generated payload useless. The final XSS payload is also blocked by XSS filters on modern IE and Chrome browsers, but works fine in FireFox. 
The payload will work in most situations, since WebSockets connections are not blocked under the CORS policy(however, since I am using the socket.io implementation, on older browsers that do not support WebSockets, socket.io will default to using XMLHttpRequests, which will be blocked by CORS). Strict CSP rules are the only instance that I've come across in which the attempt to connect back to the listening server is blocked, but this only applies to ~5% of webpages that I've tested on.

attack: xss.py only supports Relfective XSS where the GET parameters contained in the URL reflect potential sites for JS payload to be injected. The way it searches for parameters is it searches the DOM for input elements, and ASSUMES that the "name" attribute of the input element is the same as the GET parameter expected by the server. It then reloads the page by filling each GET parameter it found with a test string, and then looks for the test string within the reloaded DOM to determine the context that they landed in (single quotes, double quotes, between tags[not yet implemented], etc.). Finally, it will generate a URL with the payload as the value of one of the GET parameters.
Once uploaded, the payload will continuously try to make a connection back to the listening server. Once the connection is established, the attacker can enter commands in listener shell, which will geforwarded to the remote WebSocket client. All commands are put into eval() and executed within the current JS context.

postcondition: if the generated payload was successful, then a connection will established with the listening server

cleanup: currently cleanup of the payload is supported

NOTE: I missed the line where it said cannot use OSS. If that is the case then you can just evaluate xss.py, because that is coded in vanilla Python3

I am particularly proud of the way I coded xss.py. Although it's probably not the "pythonic way", I think I made good use of python's language features (filter, map, v3 format strings) to make my codeconcise and (hopefully) easy to understand. Comments are also tastefully added to enhance comprehension. Honestly, I think this is probably the best piece of python code I've ever written.
Originally I was just going to do the initial XSS exploit but was glad I also added the WebSocket payload. With the addition of the BEEF modules, the WebSocket payload becomes really flexible and powerful, such as stealing browser cookies, logging keystrokes, messing with the DOM (tested this on my friends), and even lateral movements through WebRTC(not tested but I do remember reading an article about compromising WebRTC-enabled IoT devices). All in all, I had alot of fun coding this, and found it to be an invaluable learning opportunity. 


