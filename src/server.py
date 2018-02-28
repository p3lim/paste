from os import path, environ
from dataset import connect
import bottle

# constants
HOST = environ.get('LISTEN_ADDRESS', '0.0.0.0')
PORT = environ.get('LISTEN_PORT', 8080)
LEN = environ.get('PATH_LENGTH', 4)
PATH = path.dirname(path.realpath(__file__))
STATIC = path.join(PATH, 'static')
VIEWS = path.join(PATH, 'views')

# set path to views
bottle.TEMPLATE_PATH.append(VIEWS)

def get(content, raw=False):
	'''
	Formats given content for HTML
	'''
	if raw:
		from html import escape
		return '<pre>%s</pre>' % escape(content)

	from pygments import highlight
	from pygments.lexers import guess_lexer
	from pygments.formatters import HtmlFormatter

	lexer = guess_lexer(content)

	return highlight(content, lexer, HtmlFormatter(
		linenos=True,
		linespans='L',
		lineanchors='L',
		anchorlinenos=True,
	))

@bottle.get('/')
def index():
	with open(path.join(PATH, 'README.md')) as file:
		content = file.read().replace('{{url}}', bottle.request.url)

		return bottle.template('view', dict(
			content = get(content, True),
			path = None
		))

@bottle.get('/<ident>')
@bottle.get('/raw/<ident>')
def show(ident):
	try:
		db = connect('sqlite:////config/db/paste.db')['pastes']
		data = db.find_one(ident=ident)

		return bottle.template('view', dict(
			content = get(data['content'], bottle.request.path.startswith('/raw/')),
			path = bottle.request.path
		))
	except:
		bottle.abort(404)

@bottle.post('/')
def post():
	try:
		content = None

		file = bottle.request.files.get('c')
		if file:
			content = file.file.read().decode('utf-8')

		form = bottle.request.forms.get('c')
		if form:
			content = bottle.request.forms.get('c')

		if content:
			from uuid import uuid4
			ident = uuid4().hex[:LEN]

			db = connect('sqlite:////config/db/paste.db')['pastes']
			while db.find_one(ident=ident):
				ident = uuid4().hex[:LEN]

			db.insert(dict(
				ident = ident,
				content = content
			))

			return bottle.request.url + ident
		else:
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
