from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit
from crawler import APCCrawler
from tools import clear_output

app = Flask(__name__, 
	template_folder='../templates', 
	static_folder='../static')

app.config.update(
	TEMPLATE_AUTO_RELOAD = True,
	DEBUG=True	
)

socketio = SocketIO(app)

@app.route('/')
def index():
	return render_template('interface.html')

def run_crawler(link):
	socketio.emit('payload', 'Loading <a href="'+link+'" target="_blank">'+link+'</a>')
	try:
		scraper = APCCrawler(link)
	except:
		socketio.emit('payload', '[Error] Not a valid URL')
		return None  

	socketio.emit('payload', 'Parsing link')
	scraper.parse(write=True)

	socketio.emit('payload', 'Applying template')
	part_num = scraper.apply_template()

	

	socketio.emit('payload', '[Complete] '+part_num)

@socketio.on('run_crawler')
def handle_run(form):
	form = form['data'][0]['value']
	res = map(lambda link: run_crawler(link), form.splitlines())

@app.route('/clear', methods=['POST', 'GET'])
def handle_clear():
	if request.method == 'POST':
		clear_output()
		return jsonify('Cleared output')
	else:
		# Accessing /clear directly
		return redirect('/')

@app.route('/logs')
def handle_log():
	with open('crawler.log', 'r+') as logs:
		log = reversed(logs.readlines())
		logs.close()
	return render_template('logs.html', log=log)

def run():
	socketio.run(app)