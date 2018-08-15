from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit
from apc.crawler import APCCrawler
from apc.tools import clear_output

app = Flask(__name__, 
	template_folder='../templates', 
	static_folder='../static')

app.config.update(
	TEMPLATE_AUTO_RELOAD = True,
	DEBUG=True	
)

socketio = SocketIO(app)

apc_settings = {
	'write': False
}

@app.route('/')
def index():
	return render_template('interface.html')

def run_crawler(link):
	socketio.emit('payload', 'Loading <a href="'+link+'" target="_blank">'+link+'</a>')

	try:
		scraper.connect(link)
	except Exception:
		socketio.emit('payload', '[Error] Not a valid URL')
		return None  

	socketio.emit('payload', 'Parsing link')
	try:
		scraper.parse(apc_settings['write'])
	except Exception as e:
		socketio.emit('payload', '[Error] Could not parse URL: {}'.format(e))

	socketio.emit('payload', 'Applying template')
	try:
		part_num = scraper.apply_template()
	except Exception as e:
		socketio.emit('payload', '[Error] Could not render template: {}'.format(e))

	socketio.emit('payload', '[Complete] '+part_num)

@socketio.on('set')
def change_settings(settings):
	# Wrapper for changing crawler settings
	apc_settings[settings[0]] = settings[1]

@socketio.on('run_crawler')
def handle_run(form):
	form = form['data'][0]['value']
	res = map(lambda link: run_crawler(link), form.splitlines())

@app.route('/clear', methods=['POST', 'GET'])
def handle_clear():
	if request.method == 'POST':
		clear_output()
		return jsonify('Cleared output')
	# Accessing /clear directly
	return redirect('/')

@app.route('/logs')
def handle_log():
	with open('crawler.log', 'r+') as logs:
		log = reversed(logs.readlines())
		logs.close()
	return render_template('logs.html', log=log)

def run():
	global scraper
	scraper = APCCrawler()
	socketio.run(app)
	