import ndnlog
from ndnlog import NdnLogToken
import os
import re
import sys
import logging
import model
from model import db
from model import Session
from model import Report
import json

class NdnRtcLogParser:
	def __init__(self, logFile):
		self.logFile = logFile
		self.summaryStat = []

	def getSummaryStatistics(self):
		if not self.summaryStat:
			self.summaryStat = ndnlog.getSummaryStat(self.logFile)
		return self.summaryStat

class NdnSessionController:
	sessionFolderNameRegexStr = '(?P<user>.*)-(?P<timestamp>[0-9]+)$'
	logFileNameRegexStr = '(?P<log_type>consumer|producer)-(?P<user>.+)-(?P<stream>.+)\.log$'
	config = {
		'SESSIONS_FOLDER':None
	}

	def parseSessions(self):
		sessionFolders = self.getNewSessions()
		logFileNameRegex = re.compile(self.logFileNameRegexStr)
		sessions = []
		if len(sessionFolders) > 0:
			for session in sessionFolders:
				sessionObject = Session(user=session['user'], timestamp=session['timestamp'], folderPath=session['path'])
				for logFile in session['files']:
					m = logFileNameRegex.match(logFile)
					if m:
						report = Report(user=m.group('user'), stream=m.group('stream'),\
							logPath=os.path.join(session['path'], logFile), reportType=m.group('log_type'))
						report.session = sessionObject
						fullPath = os.path.join(self.config['SESSIONS_FOLDER'], session['path'], logFile)
						logParser = NdnRtcLogParser(fullPath)
						logging.debug('parsing log %r...'%fullPath)
						report.summary = json.dumps(logParser.getSummaryStatistics())
				print "session reports: %r" % sessionObject.reports
				db.add(sessionObject)
				db.commit()
				sessions.append(sessionObject)
		else:
			logging.info('no new sessions since previous run')
		return sessions

	def getNewSessions(self):
		sessionFolders = []
		sessionFolderRegex = re.compile(self.sessionFolderNameRegexStr)
		for root, dirs, files in os.walk(self.config['SESSIONS_FOLDER']):
			if not root == self.config['SESSIONS_FOLDER']:
				if len(files) > 0:
					sessionFolder = os.path.basename(root)
					m = sessionFolderRegex.match(sessionFolder)
					if m:
						if not self.isSessionAlreadyProcessed(m.group('user'), m.group('timestamp')):
							sessionFolder = {'path':os.path.basename(root), 'user':m.group('user'), 'timestamp':m.group('timestamp'), 'files':files}
							sessionFolders.append(sessionFolder)
							logging.debug("found session folder %r" % sessionFolder)
						else:
							logging.debug("session %r-%r already processed"% (m.group('user'), m.group('timestamp')))
					else:
						logging.debug("unexpected folder %r" % sessionFolder)
				else:
					logging.debug("session %r has no files" % root)
		return sessionFolders
					
	def isSessionAlreadyProcessed(self, username, timestamp):
		session = Session.query.filter_by(timestamp=timestamp, user=username).first()
		if session:
			return True
		return False

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print 'usage: %r <sessions_folder>' % sys.argv[0]
		exit(0)

	logging.basicConfig(filename='session_parser.log', level=logging.DEBUG, format = '%(asctime)-15s %(message)s')
	sessionController = NdnSessionController()
	sessionController.config['SESSIONS_FOLDER'] = sys.argv[1]
	sessionController.parseSessions();
