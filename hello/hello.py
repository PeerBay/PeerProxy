###############################################################################
#
# Copyright (C) 2014, Tavendo GmbH and/or collaborators. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
import httplib

from httplib import HTTPConnection as _HTTPConnection
from threading import Thread as _Thread
from base64 import encodestring as _b64
import extraction
import json
from requests import Request, Session,utils
def _host_path(url):
    url = url.lstrip('http://')
    parts = url.split('/')
    host = parts[0]
    path = '/'+'/'.join(parts[1:])
    return host, path

_RESERVED_HEADERS = '''Accept-Charset
Accept-Encoding
Connection
Content-Length
Cookie
Cookie2
Content-Transfer-Encoding
Date
Expect
Host
Keep-Alive
Referer
TE
Trailer
Transfer-Encoding
Upgrade
User-Agent
Via'''.splitlines()


# Exceptions
class INVALID_STATE_ERR(BaseException): pass
class SYNTAX_ERR(BaseException): pass
class SECURITY_ERR(BaseException): pass

class XMLHttpRequest(object):
    '''
    http://www.w3.org/TR/XMLHttpRequest/
    '''
    
    def __init__(self):
        # event handler attributes
        self.onreadystatechange = None
        
        # States
        self.UNSENT = 0
        self.OPENED = 1
        self.HEADERS_RECEIVED = 2
        self.LOADING = 3
        self.DONE = 4
                
        # Private
        self._readyState = self.UNSENT
        self._status = None
        self._responseText = ''
        self._statusText = None
        self._responseXML = None
        
        self._method = None
        self._url = None
        self._async = None
        self._user = None
        self._password = None
        self._rheaders = {}
        self._response_headers = {}
        self._ebody = None
        
        self._send = False
    
    
    # event handler attributes
    readyState = property(lambda self: self._readyState)
    
    # Response attributes
    status = property(lambda self: self._status)
    statusText = property(lambda self: self._statusText)
    responseText = property(lambda self: self._responseText)
    responseXML = property(lambda self: self._responseXML)
    
    # Request
    def open(self,sesID, id,method, url, async=False, user=None, password=None):
        self._method = method.upper()
        # print  id,method, url
        # if self._method in ['CONNECT','TRACE','TRACK']:
        #     raise SECURITY_ERR
        # if self._method not in 'DELETE,GET,HEAD,OPTIONS,POST,PUT'.split(','):
        #     raise SYNTAX_ERR
        # self.abort()
        if url.startswith("blob:"):
            url=url.replace("blob:","")
            url=utils.unquote(url)
        if not url.startswith("http://"):
            url="http://"+url
        print url
        self._url=url
        self._sesID=sesID
        self._id=id
        self._send = False
        self._rheaders = {}
        host, self._path = _host_path(url)
        # self._http_connection = _HTTPConnection(host)
        self._user = user
        self._password = password
        self._async = async
        self._readyState = self.OPENED

        
    def setRequestHeader(self, header, value):
        print self._rheaders ,header, value   
        if self.readyState != self.OPENED or self._send:
            raise INVALID_STATE_ERR
        if header in _RESERVED_HEADERS:
            return
        if header in self._rheaders:
            self._rheaders = self._rheaders+', '+value
        else:
            self._rheaders[header] = value
        
    def send(self, data=None):
        print data
        # TODO: use the data parameter
        self._rheaders["cookie"]=""
        for i in ses[self._sesID].cookies.iterkeys():
            self._rheaders["cookie"] = self._rheaders["cookie"]+i+"="+ses[self._sesID].cookies.get(i)
        print self._rheaders["cookie"]        
        req = Request(self._method, self._url,
            data=data,
            headers=self._rheaders
        )
     
        prepped=req.prepare()
        resp=ses[self._sesID].send(prepped,
            timeout=20
        )
        print resp.text[:100]
        self._status=resp.status_code

        return resp.text
        # if self.readyState != self.OPENED or self._send:
        #     print self.readyState
        #     print self._send
        #     raise INVALID_STATE_ERR
        # self._error = False
        # if self._user and self._password:
        #     auth = _b64(self._user+':'+self._password)
        #     self._rheaders['Authorization'] = 'Basic '+auth
        # if self._async:
        #     self._send = True
        #     self._call_state_change()
        #     self._request_async()
        #     return
        # answer= self._request()
        # print 164,answer
        # return answer
    
    def abort(self):
        self._error = True
        if (self.readyState in (self.UNSENT, self.OPENED) 
                and not self._send) or self.readyState == self.DONE:
            self._readyState = self.DONE
            self._send = False
            self._call_state_change()
        self._readyState = self.UNSENT

    # Response
    def getResponseHeader(self, header):
        if self._readyState < self.HEADERS_RECEIVED:
            return
        if self._error:
            return
        lheader = header.lower() 
        if lheader in ('set-cookie', 'set-cookie2'):
            return
        for k,v in self._response_headers.items():
            if lheader == k.lower():
                return v
        
    def getAllResponseHeaders(self):
        t = ''
        for k,v in self._response_headers.items():
            if k.lower() not in ('set-cookie', 'set-cookie2'):
                t += k+': '+v+'\n'
        return t
    
    
    # Private
    def _call_state_change(self, event=None):
        if not event:
            event = 'onReadyStateChangeEvent'
        if self.onreadystatechange:
            print self.onreadystatechange ,self._id
            self.onreadystatechange(self._id)
    
    def _request_async(self):
        th = _Thread(target=self._request)
        th.start()
        
    def _request(self):
        # self._http_connection.request(self._method, self._path,None, self._rheaders)
        print self._method, self._url,None, self._rheaders
        # res = self._http_connection.getresponse()
        print res ,self
        

        self._status = res.status
        self._statusText = res.reason
        self._responseText = res.read()
        self._response_headers = dict(res.getheaders())
        res.close()
        self._readyState = self.DONE
        # self._call_state_change()
        print 222,self._responseText
        return self._responseText 

class AppSession(ApplicationSession):

    @inlineCallbacks
    # def onConnect(req):
    #     print "onconnect",dir(req)
    #     return req
    def onJoin(self, details):
        req={}
        global ses
        ses={}
        print "onjoin"
        # def ready(id):
        #     print id
        #     data={
        #         id:id,
        #         responseText:req[id].responseText,
        #         status:req[id].status,
        #         statusText:req[id].statusText
        #     }
        #     print data
        #     yield self.publish(id,data)
        def newSession(id):
            print "session:",id
            ses[id]=Session()
          
        yield self.subscribe(newSession,"session")
        def startRequest(sesID,id, method, url, async=False, user=None, password=None):
            # req[id]={url:url,method:method, async:async, user:user, password:password)}
            req[id]=XMLHttpRequest()
            print id,method,url
            req[id].url=url
            req[id].open(sesID,id, method, url, async=False, user=None, password=None)
            print req[id]
        yield self.subscribe(startRequest,"open")

        def send(id,data=None):
            # req[id].onreadystatechange=ready
            print "sending"+id
            answer={}
            # try:
            answer["data"]= req[id].send(data)
            answer["status"]= req[id].status
            # except:
            #     answer.data=requests.get(req[id].url)
            #     answer.status= ""
            print answer["status"]
            return answer
            # extracted = extraction.Extractor().extract(answer, source_url=req[id].url)
            # print dir(extracted._unexpected_values),extracted._unexpected_values
            # return json.dumps(extracted, default=lambda o: o.__dict__)
            # return  {"title":extracted.title,"description": extracted.description,"image": extracted.image,"url": extracted.url}
            # return answer
        yield self.register(send,"send")

        def setRequestHeader(id, headerkey, value):
            req[id].setRequestHeader(headerkey, value)
            print 273,headerkey,value
        yield self.subscribe(setRequestHeader,"setRequestHeader")
        def getResponseHeader(id, header):
            return req[id].getResponseHeader(header, value)
        yield self.register(getResponseHeader,"getRequestHeader")
        def getAllResponseHeaders(id):
            return req[id].getAllResponseHeaders()
        yield self.register(getAllResponseHeaders,"getAllResponseHeaders")
       
        def abort(id):
            req[id].abort()
        yield self.subscribe(abort,"abort")
