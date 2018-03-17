from os import path, environ
from uuid import uuid4

import bottle
from dataset import connect
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter

# constants
HOST = environ.get('LISTEN_ADDRESS', '0.0.0.0')
PORT = environ.get('LISTEN_PORT', 8080)
LEN = environ.get('PATH_LENGTH', 4)
CONFIG_PATH = environ.get('CONFIG_PATH', '/config')

PATH = path.dirname(path.realpath(__file__))
STATIC = path.join(PATH, 'static')
VIEWS = path.join(PATH, 'views')

# set path to views
bottle.TEMPLATE_PATH.append(VIEWS)

def get_content(ident):
	db = connect('sqlite:///%s/db/paste.db' % CONFIG_PATH)['pastes']
	data = db.find_one(ident=ident)
	return data['content'], data['type']

@bottle.get('/')
def index():
	bottle.redirect('https://github.com/p3lim/paste')

@bottle.get('/<ident>')
def show(ident):
	try:
		content, contentType = get_content(ident)
		if contentType.startswith('image'):
			bottle.response.content_type = contentType
			return content
		else:
			lexer = guess_lexer(content)

			content = highlight(content, lexer, HtmlFormatter(
				linenos=True,
				linespans='L',
				lineanchors='L',
				anchorlinenos=True,
			))

			return bottle.template('view', dict(content=content))
	except:
		bottle.abort(404)

@bottle.get('/raw/<ident>')
def show_raw(ident):
	try:
		bottle.response.content_type = 'text/plain; charset=UTF-8'
		return get_content(ident)[0]
	except:
		bottle.abort(404)

@bottle.post('/')
def post():
	try:
		content = None
		contentType = 'text/plain'

		file = bottle.request.files.get('c')
		if file:
			if file.content_type.startswith('image'):
				contentType = file.content_type
				content = file.file.read()
			else:
				content = file.file.read().decode('utf-8')

		form = bottle.request.forms.get('c')
		if form:
			content = bottle.request.forms.getunicode('c')

		if content:
			ident = uuid4().hex[:LEN]

			db = connect('sqlite:///%s/db/paste.db' % CONFIG_PATH)['pastes']
			while db.find_one(ident=ident):
				ident = uuid4().hex[:LEN]

			db.insert(dict(
				ident = ident,
				content = content,
				type = contentType
			))

			return bottle.request.url + ident

		bottle.abort(400)
	except:
		bottle.abort(500)

@bottle.get('/highlight.css')
def style():
	bottle.response.content_type = 'text/css'
	return bottle.static_file('highlight.css', root=STATIC)

@bottle.error(400)
def error(e):
	return 'Unable to process request.\n'

@bottle.error(404)
def error404(e):
	return 'Nothing here, sorry.\n'

@bottle.error(500)
def error500(e):
	return 'Something went wrong!\n'

bottle.run(host=HOST, port=PORT)
