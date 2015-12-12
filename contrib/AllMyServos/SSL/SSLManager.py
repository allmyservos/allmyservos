#!/usr/bin/python
#######################################################################
# AllMyServos - Fun with PWM
# Copyright (C) 2015  Donate BTC:14rVTppdYQzLrqay5fp2FwP3AXvn3VSZxQ
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#######################################################################
import os, subprocess, re, datetime, Specification
from Setting import *
class SSLManager(object):
	def __init__(self):
		self.basepath = os.path.join(Specification.Specification.filebase, 'certificate')
		self.certificate = os.path.join(self.basepath, 'certificate.pem')
		self.request = os.path.join(self.basepath, 'request.pem')
		self.key = os.path.join(self.basepath, 'key.pem')
		if not os.path.exists(self.basepath):
			os.makedirs(self.basepath)
		if not self.validateCertificate():
			self.generateCertificate()
	def validateCertificate(self):
		try:
			assert self.keyExists()
			assert self.certificateExists()
			assert self.isValid()
			return True
		except Exception as e:
			#print('not valid: {0}: {1}'.format(e.errno, strerror))
			pass
		return False
	def certificateExists(self):
		if os.path.exists(self.certificate):
			return True
		return False
	def keyExists(self):
		if os.path.exists(self.key):
			return True
		return False
	def isValid(self):
		try:
			p = subprocess.Popen(['openssl', 'x509', '-noout', '-startdate', '-enddate', '-subject'],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
			f = open(self.certificate, 'r')
			p.stdin.write(f.read())
			output = p.communicate()[0]
			f.close()
			p.stdin.close()
			self.start = None
			self.end = None
			self.domain = None
			self.company = None
			self.country = None
			startpattern = re.compile(r"""notBefore=(?P<date>.*)""")
			endpattern = re.compile(r"""notAfter=(?P<date>.*)""")
			subjectpattern = re.compile(r"""subject=\s*\/CN=(?P<domain>[^\/]+)\/O=(?P<company>[^\/]+)\/C=(?P<country>.*)""")
			#subjectpattern = re.compile(r'subject=\s*(?P<country>.*)')
			for l in output.split('\n'):
				match = startpattern.match(l)
				if(match):
					self.start = datetime.datetime.strptime(match.group('date'),'%b %d %H:%M:%S %Y %Z')
				match = endpattern.match(l)
				if(match):
					self.end = datetime.datetime.strptime(match.group('date'),'%b %d %H:%M:%S %Y %Z')
				match = subjectpattern.match(l)
				if(match):
					self.domain = str(match.group('domain'))
					self.company = str(match.group('company'))
					self.country = str(match.group('country'))
			today = datetime.datetime.today()
			assert today >= self.start and today <= self.end
			return True
		except:
			pass
		return False
	def generateCertificate(self):
		try:
			subprocess.check_call(['openssl', 'genrsa', '-out', self.key, '1024'])
		except Exception as e:
			print('Unable to create private key: {0}'.format(e))
		else:
			try:
				subject = '/CN={0}/O={1}/C={2}'.format(Setting.get('rpc_server_ssl_domain', 'localhost'), Setting.get('rpc_server_ssl_company', 'TestCo'), Setting.get('rpc_server_ssl_country', 'GB'))
				subprocess.check_call(['openssl', 'req', '-new', '-key', self.key, '-out', self.request, '-subj', subject])
			except Exception as e:
				print('Unable to create signing request: {0}'.format(e))
			else:
				try:
					subprocess.check_call(['openssl', 'x509', '-req', '-days', '365', '-in', self.request, '-signkey', self.key, '-out', self.certificate])
				except Exception as e:
					print('Unable to self sign request: {0}'.format(e))
				else:
					self.isValid()
					return True
		return False
	def countryCodes(self):
		return ['US',
				'CA',
				'AX',
				'AD',
				'AE',
				'AF',
				'AG',
				'AI',
				'AL',
				'AM',
				'AN',
				'AO',
				'AQ',
				'AR',
				'AS',
				'AT',
				'AU',
				'AW',
				'AZ',
				'BA',
				'BB',
				'BD',
				'BE',
				'BF',
				'BG',
				'BH',
				'BI',
				'BJ',
				'BM',
				'BN',
				'BO',
				'BR',
				'BS',
				'BT',
				'BV',
				'BW',
				'BZ',
				'CA',
				'CC',
				'CF',
				'CH',
				'CI',
				'CK',
				'CL',
				'CM',
				'CN',
				'CO',
				'CR',
				'CS',
				'CV',
				'CX',
				'CY',
				'CZ',
				'DE',
				'DJ',
				'DK',
				'DM',
				'DO',
				'DZ',
				'EC',
				'EE',
				'EG',
				'EH',
				'ER',
				'ES',
				'ET',
				'FI',
				'FJ',
				'FK',
				'FM',
				'FO',
				'FR',
				'FX',
				'GA',
				'GB',
				'GD',
				'GE',
				'GF',
				'GG',
				'GH',
				'GI',
				'GL',
				'GM',
				'GN',
				'GP',
				'GQ',
				'GR',
				'GS',
				'GT',
				'GU',
				'GW',
				'GY',
				'HK',
				'HM',
				'HN',
				'HR',
				'HT',
				'HU',
				'ID',
				'IE',
				'IL',
				'IM',
				'IN',
				'IO',
				'IS',
				'IT',
				'JE',
				'JM',
				'JO',
				'JP',
				'KE',
				'KG',
				'KH',
				'KI',
				'KM',
				'KN',
				'KR',
				'KW',
				'KY',
				'KZ',
				'LA',
				'LC',
				'LI',
				'LK',
				'LS',
				'LT',
				'LU',
				'LV',
				'LY',
				'MA',
				'MC',
				'MD',
				'ME',
				'MG',
				'MH',
				'MK',
				'ML',
				'MM',
				'MN',
				'MO',
				'MP',
				'MQ',
				'MR',
				'MS',
				'MT',
				'MU',
				'MV',
				'MW',
				'MX',
				'MY',
				'MZ',
				'NA',
				'NC',
				'NE',
				'NF',
				'NG',
				'NI',
				'NL',
				'NO',
				'NP',
				'NR',
				'NT',
				'NU',
				'NZ',
				'OM',
				'PA',
				'PE',
				'PF',
				'PG',
				'PH',
				'PK',
				'PL',
				'PM',
				'PN',
				'PR',
				'PS',
				'PT',
				'PW',
				'PY',
				'QA',
				'RE',
				'RO',
				'RS',
				'RU',
				'RW',
				'SA',
				'SB',
				'SC',
				'SE',
				'SG',
				'SH',
				'SI',
				'SJ',
				'SK',
				'SL',
				'SM',
				'SN',
				'SR',
				'ST',
				'SU',
				'SV',
				'SZ',
				'TC',
				'TD',
				'TF',
				'TG',
				'TH',
				'TJ',
				'TK',
				'TM',
				'TN',
				'TO',
				'TP',
				'TR',
				'TT',
				'TV',
				'TW',
				'TZ',
				'UA',
				'UG',
				'UM',
				'US',
				'UY',
				'UZ',
				'VA',
				'VC',
				'VE',
				'VG',
				'VI',
				'VN',
				'VU',
				'WF',
				'WS',
				'YE',
				'YT',
				'ZA',
				'ZM',
				'COM',
				'EDU',
				'GOV',
				'INT',
				'MIL',
				'NET',
				'ORG',
				'ARPA']
if __name__ == '__main__':
	sm = SSLManager()