#!/usr/bin/python

from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit

from .vendors import apc, eaton, hmcragg, pulizzi, vertiv
from .utils import clear_output

import traceback
import os

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

app.config.update(
    TEMPLATE_AUTO_RELOAD=True,
    DEBUG=True,
    TESTING=True
)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

socketio = SocketIO(app)
    
crawl_settings = {
    # Write output to JSON
    'write': False,
    # Template filename
    'template': 'base.html',
    # Default crawler
    'crawler': 'apc'
}

@app.route('/')
def index():
    return render_template('interface.html')

def run_crawler(link, crawler):
    # Remove anchor from link
    link = link.split('#')[0]

    crawler.reset()

    socketio.emit('payload', 'Loading <a href="' +
                  link+'" target="_blank">'+link+'</a>')

    try:
        crawler.connect(link)
    except Exception as e:
        socketio.emit('payload', '[Error] Not a valid URL: '+str(e))
        return None

    socketio.emit('payload', 'Applying template')
    try:
        part_num = crawler.apply(
            write=crawl_settings['write'],
            template=crawl_settings['template'],
        )
    except Exception as e:
        trace = traceback.format_exc().replace(' File ', '<br/><br/>')
        socketio.emit(
            'payload', '[Error] Could not render template: {0} <br/><br/> <code>{1}</code>'.format(e, trace)
        )
        return None

    if crawler.parser_warning:
        socketio.emit('payload', '[Warning] {}'.format(crawler.parser_warning))

    socketio.emit('payload', '[Complete] '+part_num)


@socketio.on('flash')
def flash(msg):
    # Flash a message in payload
    socketio.emit('payload', '[Complete] '+msg)


@socketio.on('list-crawlers')
def list_crawlers():
    # Provide list of available crawlers to interface
    crawlers = [filename.replace('.py', '') for filename in os.listdir(os.getcwd()+'/bomara/vendors') if filename[0] != '_' and filename[-3:] == '.py']
    socketio.emit('crawlers', crawlers)


@socketio.on('set')
def change_settings(s):
    # Wrapper for changing crawler settings
    crawl_settings[s['settings'][0]] = s['settings'][1]
    socketio.emit('payload', '[Complete] Set {0} to {1}'.format(s['settings'][0], s['settings'][1]))


@socketio.on('run_crawler')
def handle_run(form):
    form = form['data'][0]['value']
    
    [run_crawler(link, eval('{}.crawler'.format(crawl_settings['crawler']))) for link in form.splitlines()]

@app.route('/clear', methods=['POST'])
def handle_clear():
    clear_output()
    socketio.emit('payload', '[Complete] Cleared output folder')
    return jsonify('Cleared output')


@app.route('/logs')
def handle_log():
    with open('crawler.log', 'r+') as logs:
        log = reversed(logs.readlines())
        logs.close()
    return render_template('logs.html', log=log)


def run():
    socketio.run(app)
