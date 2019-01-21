This is a small security project that I put together in my spare time, and is inspired by the BEEF browser exploitation framework and XSStrike
Comprises two parts:
1) A script to automatically generate a Reflective XSS payload
2) The payload itself which starts reverse shell using a WebSocket client in the injected JS context that communicates back to our listening server. Arbitrary commands can then be sent thru the reverse shell to be executed inside the injected JS context. Payload also 

Usage Steps:
1. Install Python2.7.11
2. Run "npm install" in the root folders
3. Run "python xss.py <url>" to scan for possible Reflective XSS on <url>
4. If the Step 3 is successful (injection has been identified and payload generated), copy the payload (it should contain an URL with payload embedded inside a GET parameter) open it in a browser window
5. After a couple of seconds, should get output in the shell showing that the Websocket has connected back to our listener. Now we can execute commands on the victim's Javascript Context!

To test WebSocket shell:
1. alert(0)
2. document.location.href 
3. beef.dom.removeStylesheets()

Future Features:
1. Filter Evasion
2. More JS modules for the WebSocket client
3. Better commandline interface for the shell (ala Metasploit shell autocomplete, search commands, list modules)

Summary of Exploit:

Precondition: Current version is not very comprehensive/robust, and currently it will only detect XSS injections that occur within HTML attributes. Also, no filter-evasion have been implemented as of yet so any client/server side filtering will most likely break the payload.
One positive is that WebSockets connections are not blocked under the CORS policy (however, since I am using the socket.io implementation, on older browsers that do not support WebSockets, socket.io will default to using XMLHttpRequests, which will be blocked by CORS). 

Attack: xss.py only supports XSS where the GET parameters contained in the URL reflect potential sites for XSS payloads to be injected. It will first search for GET parameters by identifying input elements on the page, and assumes that parameter will have the same name as the input element’s “name” attribute. It then reloads the page by filling each GET parameter it found with a test string, and then looks for the test string within the reloaded DOM to determine the context that they landed in (single quotes, double quotes, between tags[not yet implemented], etc.). Finally, depending on the context, it will generate a URL with the payload as the value of one of the GET parameters.
Once uploaded, the payload will continuously try to make a connection back to the listening server. Once the connection is established, the attacker can enter commands in listener shell, which will get forwarded to the remote WebSocket client. All commands are put into eval() and executed within the current JS context. Output from the executed command are also sent back to the server (although currently, if output is a JS Object, then nothing is sent).

Postcondition: if the generated payload was successful, then a connection will established with the listening server

Cleanup: currently cleanup of the payload is not supported

NOTE: I missed the line where it said cannot use OSS. If that is the case then you can just evaluate xss.py, because that is coded in vanilla python

I am particularly proud of the way I coded xss.py. Although it's probably not the "pythonic way", I think I made good use of python's language features (filter, map, v3 format strings) to make my code concise and (hopefully) easy to understand. Comments are also tastefully added to enhance comprehension. Honestly, I think this is probably the best piece of python code I've ever written.
Originally I was just going to do the initial XSS exploit but was glad I also added the WebSocket payload. With the addition of the BEEF modules, the WebSocket payload becomes really flexible and powerful, such as stealing browser cookies, logging keystrokes, messing with the DOM (tested this on my friends), and even lateral movements through WebRTC(not tested but I do remember reading an article about compromising WebRTC-enabled IoT devices). All in all, I had alot of fun coding this, and found it to be an invaluable learning opportunity.





