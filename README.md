# PeerProxy

Ajax to websocket proxy.
It takes over XMLHttpRequest and transfers all data through the server using websockets.

Uses [crossbar](http://crossbar.io) and is based on the hello example. 

Install crossbar and clone proxy

pip install crossbar
git clone https://github.com/PeerBay/PeerProxy

To start using it:

cd PeerProxy
crossbar start

and visit:
http://localhost:8080/example.html

