# Ban Hammer by James Lawrence
#
# Filename: bhammer.py
# Version: 0.0.3
# Date: 16 NOV 2022
# A Script to ban downlevel Pocketcoin Nodes
#
# Freely use or distribute this code. No warrenties of anykind. Use at your own risk
# Requires Python 3.9 (It might work on downlevel versions)

#import libraries
import subprocess
import json
import time
import datetime
import logging
import sys

#configure logging
logging.basicConfig(filename='bhammer.log', encoding='utf-8', level=logging.DEBUG)

logging.debug("***************************************************************************************")
logging.debug("************************** Starting bHammer Version: 0.0.3 ****************************")
logging.debug("***************************************************************************************")

#Set Lowest Acceptable Version
LAV = [0,21,0]
LAVtxt = str(LAV)
logging.debug("")
logging.debug("Lowest Acceptable Version (LAV): " + LAVtxt)
logging.debug("")

#infinte loop, will have to ctl-c to exit
while True:

	#load json peerlist
	try:
		peerlist = json.loads(subprocess.check_output('pocketcoin-cli getpeerinfo', shell=True))
	except:
		now = datetime.datetime.now()
		print("Sleeping for 1 minute @ " + now.strftime("%d/%m/%Y %H:%M:%S"))
		time.sleep(60)
		continue

		
	inboundcount = 0
	outbountcount = 0
	
	print()
	print("  IP Address:Port\t\tVersion\t\t\tInbound\t\tBanned")
	print("---------------------------------------------------------------------------------------")

	#iterate through peers and do work
	for index, peer in enumerate(peerlist):

		#If version string is empty then skip it for now and exit the loop so we don't crash on an empty string
		if str(peer['subver']) == '':
			banstat = "Version string is empty - Skipping node"
			#logging.debug("Skipped Node: " + peer['addr'] + "  " + banstat)
			print("  {0}\t\t\t\t{1}\t{2}\t\t{3}".format(peer['addr'], peer['subver'], peer['inbound'], banstat))
			continue

		#Strip leading and trailing space (just in case)
		banstat = ""
		tmpver = peer['subver'].strip()
		tmpip = peer['addr'].strip()
		#remove slashes
		tmpver = tmpver.strip('/')
		#remove 'Satoshi:'
		tmpver = tmpver.strip('Satoshi:')
		#split on version periods and ip address on colon
		tmpver = tmpver.split('.')
		tmpip = tmpip.split(':')
		#logging.debug("************")
		#logging.debug("peer: " + str(peer))
		#logging.debug("************")
		#logging.debug("tmpver: " + str(tmpver))
		#logging.debug("LAV: " + str(LAV))
		#logging.debug("index: " + str(index))

		if peer['inbound'] == True:
			inboundcount += 1

		if peer['inbound'] == False:
			outbountcount += 1

		if int(tmpver[1]) < LAV[1]:
			#logging.debug("This node has an old major version")
			#logging.debug("pocketcoin-cli setban \""+ tmpip[0] +"\" add 604800")
			bh = subprocess.check_output('pocketcoin-cli setban \"'+ tmpip[0] +'\" add 604800', shell=True)
			banstat = "¡Prohibición del martillo! - Major version ban - length 604800 minutes"
			#logging.debug(banstat)
			#logging.debug(bh)
			#logging.debug("BAN HAMMERED!!!!!!!!!!!!!")
			if peer['inbound'] == True:
				peertype = "Inbound"
			if peer['inbound'] == False:
				peertype = "Outbound"
			logging.debug("Banned Node: " + peer['addr'] + "  " + peer['subver'] + "  " + peertype + "  " + banstat)
			print("  {0}\t\t{1}\t{2}\t\t{3}".format(peer['addr'], peer['subver'], peer['inbound'], banstat))
			continue

		#If minor version is less than LAV AND major version is equal to or greater than
		#have to cast str's to int's so we don't crash
		if int(tmpver[2]) < LAV[2] and int(tmpver[1]) <= LAV[1]:
			logging.debug("This node has an old minor version")
			logging.debug("pocketcoin-cli setban \""+ tmpip[0] +"\" add 604800")
			bh = subprocess.check_output('pocketcoin-cli setban \"' + tmpip[0] + '\" add 604800', shell=True)
			banstat = "¡Prohibición del martillo! - Minor version ban - length 604800 minutes"
			#logging.debug(banstat)
			#logging.debug(bh)
			#logging.debug("BAN HAMMERED!!!!!!!!!!!!!")
			if peer['inbound'] == True:
				peertype = "Inbound"
			if peer['inbound'] == False:
				peertype = "Outbound"
			logging.debug("Banned Node: " + peer['addr'] + "  " + peer['subver'] + "  " + peertype + "  " + banstat)
			print("  {0}\t\t{1}\t{2}\t\t{3}".format(peer['addr'], peer['subver'], peer['inbound'], banstat))
			continue

		banstat = "Pass - No Ban"
		print("  {0}\t\t{1}\t{2}\t\t{3}".format(peer['addr'], peer['subver'], peer['inbound'], banstat))

	print("---------------------------------------------------------------------------------------")

	now = datetime.datetime.now()
	try:
		banlist = json.loads(subprocess.check_output('pocketcoin-cli listbanned', shell=True))
	except:
		print("Load listbanned exeption. " + now.strftime("%d/%m/%Y %H:%M:%S"))
		banlist = ""

	print()
	print("{0} peers banned".format(len(banlist)))
	print("{0} peers connected. {1} inbound peers. {2} outbound peers.".format(len(peerlist), inboundcount, outbountcount))
	print("Sleeping for 1 minute @ " + now.strftime("%d/%m/%Y %H:%M:%S"))
	time.sleep(60)
	print()
	print()
