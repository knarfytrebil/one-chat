from os import path as op

import tornado
import tornado.web
import tornado.httpserver
import tornadio2
import tornadio2.router
import tornadio2.server
import tornadio2.conn
import datetime
import json

USERNAME = "manaflame"
PASSWD = "N2u1c3l4e5ar"

ADMIN = 0

ROOT = op.normpath(op.dirname(__file__))

def encrypt(s):
	from base64 import urlsafe_b64encode as encode
	b64 = encode(s)
	r = []
	for i in b64:
		r.append(i)
	r.reverse()
	return "".join(r)

def decrypt(s):
	from base64 import urlsafe_b64decode as decode
	r = []
	for i in s:
		r.append(i)
	r.reverse()
	return decode("".join(r))

def _obj_hook(pairs):
	'''
	convert json object to python object.
	'''
	o = JsonObject()
	for k, v in pairs.iteritems():
		o[str(k)] = v
	return o

class JsonObject(dict):
	'''
	general json object that can bind any fields.
	'''
	def __getattr__(self, attr):
		return self[attr]

	def __setattr__(self, attr, value):
		self[attr] = value

class User:
	"""docstring for User"""
	def __init__(self, ip, ua, level):
		self.ua = ua
		self.ip = ip
	
	def uid(self):
		import time
		now = str(int(time.time()))
		return encrypt(self.ua+self.ip+now)

class IndexHandler(tornado.web.RequestHandler):
	"""Regular HTTP handler to serve the chatroom page"""
	def get(self):
		info = self.request.headers
		cookie = self.get_cookie('uinfo')
		user = User(info['Host'],info['User-Agent'],0)
		uid = user.uid()
		if not cookie:
			self.render('login.html',uid=uid)
		else:
			if decrypt(cookie).split("##")[0] == USERNAME and decrypt(cookie).split("##")[1] == PASSWD:
				self.render('chatserv.html',uid=uid)
			else:
				self.render('login.html',uid=uid)
	
	def post(self):
		u = self.get_arguments('username')[0]
		p = self.get_arguments('password')[0]
		uid = self.get_arguments('uid')[0]
		if u == USERNAME and p == PASSWD:
			uinfo = encrypt(u + '##' + p)
			self.set_cookie(name='uinfo',value=uinfo)
		self.redirect('/')

class ChatConnection(tornadio2.conn.SocketConnection):
	# Class level variable
	participants = set()
	uid = ""
	admin = 0

	def on_open(self, info):
		self.send("Welcome from the server.")
		self.participants.add(self)

	def on_message(self, message):
		# Pong message back
		try:
			msg = json.loads(message,object_hook=_obj_hook)
		except ValueError:
			pass
		if str(msg.type) == 'uid':
			self.uid = msg.content
		elif str(msg.type) == 'IdentifyAdminNow':
			self.admin = 1
			global ADMIN
			ADMIN = 1
		else:
			for p in self.participants:
				if p.uid == str(msg.type) or p.admin == 1:
					p.send(msg.content)

	def on_close(self):
		if self.admin == 1:
			global ADMIN
			ADMIN = 0
		self.participants.remove(self)

class PingConnection(tornadio2.conn.SocketConnection):
	participants = set()

	def on_open(self, info):
		print 'Ping', repr(info)
		self.participants.add(self)

	def on_message(self, message):
		now = datetime.datetime.now()
		message['server'] = [now.hour, now.minute, now.second, now.microsecond / 1000]
		message['total'] = str(len(self.participants))
		message['admin'] = str(ADMIN)
		self.send(message)
	
	def on_close(self):
		self.participants.remove(self)

class RouterConnection(tornadio2.conn.SocketConnection):
	__endpoints__ = {'/chat': ChatConnection,
					 '/ping': PingConnection}

	def on_open(self, info):
		print 'Router', repr(info)

# Create tornadio server
ChatRouter = tornadio2.router.TornadioRouter(RouterConnection)

# Create socket application
sock_app = tornado.web.Application(
	ChatRouter.urls,
	flash_policy_port = 843,
	flash_policy_file = op.join(ROOT, 'flashpolicy.xml'),
	socket_io_port = 8002
)

# Create HTTP application
http_app = tornado.web.Application([
		(r"/", IndexHandler), 
		(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": op.join(ROOT, 'static/')} )
	])

if __name__ == "__main__":
	import logging
	logging.getLogger().setLevel(logging.DEBUG)

	# Create http server on port 8001
	http_server = tornado.httpserver.HTTPServer(http_app)
	http_server.listen(8001)

	# Create tornadio server on port 8002, but don't start it yet
	tornadio2.server.SocketServer(sock_app, auto_start=False)

	# Start both servers
	tornado.ioloop.IOLoop.instance().start()
