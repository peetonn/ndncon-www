from flask import Flask, jsonify, render_template, request
from model import db, Session, Report
import session_parser
from session_parser import NdnSessionController
import model
import logging
import json

app = Flask(__name__)
logging.basicConfig(filename='main.log', level=logging.DEBUG, format = '%(asctime)-15s %(message)s')

@app.route('/')
def root():
	logging.debug('querying all sessions...')
	sessions = Session.query.all()
	logging.debug('retrieved %r sessions' % len(sessions))
	return render_template('index.html', sessions=sessions)

@app.route('/_check_new_sessions')
def check_new_sessions():
	logging.debug('checking new sessions...')
	#a = request.args.get('a', 0, type=int)
	#b = request.args.get('b', 0, type=int)
	controller = NdnSessionController()
	controller.config['SESSIONS_FOLDER'] = '../../../NdnCon-Reports'
	newSessions = controller.parseSessions()
	logging.debug('%r new sessions' % len(newSessions))
	sessions = []
	for session in newSessions:
		sessions.append({"session":{"time":str(session.time()), "user":session.user, \
			"consumers":len(session.consumerReports()), "producers":len(session.producerReports())}})
	return jsonify(result=len(newSessions), sessions=sessions)

if __name__ == '__main__':
	app.debug = (logging.getLogger().getEffectiveLevel() == logging.DEBUG)
	logging.info('starting main (debug is %r)...' % app.debug)
	app.run('0.0.0.0')

