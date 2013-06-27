import re
import json
import time
import socket
import apachelog
import urllib, urllib2

def parseLog(logfile, outfile):
	"""Parses apache logs and performs lookup on where the access is from"""

	#Options
	LOG_ACCESS_DATA = False
	PRINT_PROGRESS = True
	IPINFODB_API_KEY = ''
	apache_log_format = r'%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'

	p = apachelog.parser(apache_log_format)
	total_lines = str(sum(1 for line in open(logfile)))
	current_line = 1
	parsed_log = {}
	
	for line in open(logfile, 'r'):
		try:
			data = p.parse(line)
			ip = data['%h']
			if ip not in parsed_log: #new entry
				parsed_log[ip] = {}
				parsed_log[ip]['access_count'] = 1

				if LOG_ACCESS_DATA:
					parsed_log[ip].setdefault('accessed_files', []).append((data['%t'], data['%r'])) #convert to date time

				ipinfo_url = 'http://api.ipinfodb.com/v3/ip-city/?key=' + IPINFODB_API_KEY + '&ip=' + ip + '&format=json'

				try:
					req = urllib2.Request(ipinfo_url)
					response = urllib2.urlopen(req)
				except URLError as e:
					print 'TODO'

				ipinfo = json.load(response)
				parsed_log[ip]['country'] = ipinfo['countryName']
				parsed_log[ip]['city'] = ipinfo['cityName']
				parsed_log[ip]['lat'] = ipinfo['latitude']
				parsed_log[ip]['lon'] = ipinfo['longitude']

				try:
					parsed_log[ip]['hostname'] = socket.gethostbyaddr(ip)[0]
				except:
					parsed_log[ip]['hostname'] = ''

				if PRINT_PROGRESS:
					print "INSERTED: " + ip + " LINES: " + str(current_line) + "/" + total_lines

			else:
				parsed_log[ip]['access_count'] += 1
				if LOG_ACCESS_DATA:
					parsed_log[ip].setdefault('accessed_files', []).append((data['%t'], data['%r']))

				if PRINT_PROGRESS:
					print "UPDATED: " + ip + " LINES: " + str(current_line) + "/" + total_lines

		except:
			print "Parse error: %s" % line

		current_line += 1

	#output file in pretty JSON print
	with open(outfile, 'w') as output:
  		json.dump(parsed_log, output, sort_keys=True, indent=4, separators=(',', ': '))


logfile = 'access_log-20130609.txt'
output = 'parsed_log_test.json'
parseLog(logfile, output)