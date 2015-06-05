# PeerProxy

Ajax to websocket proxy.
It takes over XMLHttpRequest and transfers all data through the server using websockets.
The files that do the magic are:
- hello/hello.py
- hello/web/peerproxy.js

Uses [crossbar](http://crossbar.io) and is based on the hello example. 


Install crossbar and clone proxy
```
pip install crossbar
git clone https://github.com/PeerBay/PeerProxy
```
To start using it:
```
cd PeerProxy
crossbar start
```
and try the example (check the inspect element network tab):
```
http://localhost:8080/example.html
```
