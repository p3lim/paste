from os import path, environ
from uuid import uuid4

# from flask import Flask, request
import flask
from dataset import connect
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import HtmlFormatter

app = flask.Flask(__name__)

# constants
LEN = environ.get('PATH_LENGTH', 4)
CONFIG_PATH = environ.get('CONFIG_PATH', '/config')

def get_content(ident):
	db = connect('sqlite:///%s/db/paste.db' % CONFIG_PATH)['pastes']
	data = db.find_one(ident=ident)
	return data['content'], data['type']

@app.route('/', methods=['GET', 'POST'])
def index():
	if flask.request.method == 'POST':
		return post()
	else:
		return flask.redirect('https://github.com/p3lim/paste')

@app.route('/<ident>')
def show(ident):
	try:
		content, contentType = get_content(ident)
		if contentType.startswith('image'):
			return flask.Response(
				response = content,
				mimetype = contentType
			)
		else:
			title = content.split('\n')[0]
			content = highlight(content, guess_lexer(content), HtmlFormatter(
				linenos=True,
				linespans='L',
				lineanchors='L',
				anchorlinenos=True,
			))

			return flask.render_template('view.html', content=content, title=title)
	except:
		flask.abort(404)

@app.route('/raw/<ident>')
def show_raw(ident):
	try:
		return flask.Response(
			response = get_content(ident)[0],
			mimetype = 'text/plain'
		)
	except:
		flask.abort(404)

def post():
	content = None
	contentType = 'text/plain'

	if 'c' in flask.request.files:
		file = flask.request.files['c']
		if file.content_type.startswith('image'):
			contentType = file.content_type
			content = file.read()
		elif file.content_type.startswith('text'):
			content = file.read()

	if 'c' in flask.request.form:
		content = flask.request.form['c']

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

		return flask.request.url_root + ident

	flask.abort(400)

@app.route('/highlight.css')
def style():
	return flask.send_from_directory('static', 'highlight.css')

@app.errorhandler(400)
def error(e):
	return 'Unable to process request.\n'

@app.errorhandler(404)
def error404(e):
	return 'Nothing here, sorry.\n'

@app.errorhandler(500)
def error500(e):
	return 'Something went wrong!\n'
