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
	'''convert json object to python object. '''
	o = JsonObject()
	for k, v in pairs.iteritems():
		o[str(k)] = v
	return o

class JsonObject(dict):
	'''general json object that can bind any fields. '''
	def __getattr__(self, attr):
		return self[attr]

	def __setattr__(self, attr, value):
		self[attr] = value

class User:
	"""docstring for User"""
	def __init__(self, ip):
		self.ip = ip
		self.uid = ""
		self.admin = 0
		self.nick = ""
	
	def GenUid(self):
		self.uid = encrypt(self.ip + self.nick)
	
	def GenNick(self):
		import time,random
		self.nick = str(int(time.time())) + str(random.randint(10000,20000))

class IndexHandler(tornado.web.RequestHandler):
	"""Regular HTTP handler to serve the chatroom page"""
	def get(self):
		info = self.request.headers
		cookie = self.get_cookie('uinfo')
		if not cookie:
			self.render('login.html')
		else:
			if decrypt(cookie).split("##")[0] == USERNAME and decrypt(cookie).split("##")[1] == PASSWD:
				self.render('index.html')
			else:
				self.render('login.html')
	
	def post(self):
		u = self.get_arguments('username')[0]
		p = self.get_arguments('password')[0]
		if u == USERNAME and p == PASSWD:
			uinfo = encrypt(u + '##' + p)
			self.set_cookie(name='uinfo',value=uinfo)
		self.redirect('/')

class ChatConnection(tornadio2.conn.SocketConnection):
	# Class level variable
	participants = set()
	user = None

	def on_open(self, info):
		self.send(dict(sys="Initiating Connection..."))
		self.user = User(info.ip)
		self.user.GenNick()
		self.user.GenUid()
		self.send(dict(uid=self.user.uid))
		self.send(dict(sys="You are Connected...."))
		self.participants.add(self)
		print dir(info)

	def on_message(self, message):
		# Pong message back
		try:
			msg = json.loads(message,object_hook=_obj_hook)
		except ValueError:
			pass

		if str(msg.type) == 'IdentifyAdminNow':
			self.user.admin = 1
			self.user.nick = "Service"
			global ADMIN
			ADMIN = 1
		else:
			nick = ""
			target = ""
			c = msg.content	
			for p in self.participants:
				if p.user.uid == str(msg.type):
					nick = p.user.nick
				if p.user.admin == 1:
					target = msg.content.split('#')[0]
					try:
						c = msg.content.split('#')[1]
					except IndexError:
						c = msg.content
					if c == '':
						return
			#The Broadcasting
			if target == "BroadCast":
				for p in self.participants:
					p.send(dict(broadcast=c,nick=nick))
				return
			#Normal Distribution
			for p in self.participants:
				if p.user.uid == str(msg.type) or p.user.admin == 1 or p.user.nick == target:
					p.send(dict(chat=c,nick=nick))

	def on_close(self):
		if self.user.admin == 1:
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
		message['total'] = str(len(self.participants) + 180)
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
