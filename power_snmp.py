#!/usr/bin/env python
# *** power_snmp.py ***
# Controls an apc power strip model ap9210 via snmp
# Can use this class as an api or can use from the command line
# see the section at the bottom for example use, or run with help option

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
import argparse

class APC9210(object):
	ON = 1
	OFF = 2
	REBOOT = 3

	STATUS_DICT = {1: 'ON', 2: 'OFF'}

	OUTLET_CONTROL = '1.3.6.1.4.1.318.1.1.4.4.2.1.3.%s'
	OUTLET_NAMES = '1.3.6.1.4.1.318.1.1.4.4.2.1.4.%s'
	MASTER_STATE = '1.3.6.1.4.1.318.1.1.4.2.2.0'

	def __init__(self, address, community='private', udp_port=161):
		self.address = address
		self.community = community
		self.udp_port = udp_port

	def port_status_str(self, port_number):
		return self.__class__.STATUS_DICT[self.port_status(port_number)]

	def port_status(self, port_number):
		return int(self._get_port_str(port_number, self.__class__.OUTLET_CONTROL))

	def port_name(self, port_number):
		return self._get_port_str(port_number, self.__class__.OUTLET_NAMES)

	def _get_port_str(self, port_number, oid_format_str):
		cmdGen = cmdgen.CommandGenerator()

		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
				cmdgen.CommunityData(self.community, mpModel=0),
				cmdgen.UdpTransportTarget((self.address, self.udp_port)),
				# need to convert to string before passing to format. format doesn't like unicode strings
				(str.format(oid_format_str % (str(port_number)))),
				)
		(var, val) = varBinds[0]
		return str(val)

	def on(self, port_number):
		self._send_command(port_number, self.__class__.ON)

	def off(self, port_number):
		self._send_command(port_number, self.__class__.OFF)

	def reboot(self, port_number):
		self._send_command(port_number, self.__class__.REBOOT)

	def _send_command(self, port_number, cmd):
		cmdGen = cmdgen.CommandGenerator()
		errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
			cmdgen.CommunityData(self.community, mpModel=0),
			cmdgen.UdpTransportTarget((self.address, self.udp_port)),

			# need to convert to string before passing to format. format doesn't like unicode strings
			(str.format(self.__class__.OUTLET_CONTROL % (str(port_number))),
				rfc1902.Integer(cmd)),
		)
		'''
		# Check for errors and print out results
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBinds[int(errorIndex)-1] or '?'
					)
				)
			else:
				for name, val in varBinds:
					print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
		'''

def main():	
	parser = argparse.ArgumentParser(description='Control APC MasterSwitch 9210')
	parser.add_argument('-c', '--community', default='private',
			help='SNMP Community name')
	parser.add_argument('port', type=int,
			help='Port number to control')
	parser.add_argument('mode',
			help='Mode to put port into. (On|Off|Reboot)')
	parser.add_argument('host',
			help='Name or ip address of APC MasterSwitch host')

	args = parser.parse_args()
	modes = {'on': APC9210.ON, 'off': APC9210.OFF, 'reboot': APC9210.REBOOT}
	mode = args.mode.lower().strip()

	# Error checking
	if mode not in modes.keys():
		print '*** Please enter a proper mode! ***'
		parser.print_help()
		exit(1)

	if args.port < 1 or args.port > 8:
		print '*** Your port is out of range! ***'
		parser.print_help()
		exit(2)

	apc = APC9210(args.host, community=args.community)
	apc._send_command(args.port, modes[mode])

if __name__ == '__main__':
	main()
	''' ### Test code for showing port number, name, and status
	apc = APC9210('172.16.0.12')
	#apc.off(8)

	for i in range(1,8+1):
		print "%s: %s = %s " % (i, apc.port_name(i), apc.port_status_str(i))
	'''

