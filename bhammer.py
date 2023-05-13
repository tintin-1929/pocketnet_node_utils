# Ban Hammer by James Lawrence
#
# Filename: bhammer.py
# Version: 0.0.7
# Date: 13 May 2023
# A Script to ban downlevel Pocketcoin Nodes
#
# Freely use or distribute this code. No warrenties of anykind. Use at your own risk
# Requires Python 3.9 (It might work on downlevel versions)

#Output detail line
def nodeLinePrint(peer, dd, hh, mm, ss, banstat):
	print("  {0}\t\t{1}\t{2}\t{3:>14,}\t{4:>16,}\t{5}\t{6}\t{7}".format(peer['addr'], peer['subver'], peer['inbound'], peer['bytesrecv'],
							     peer['bytessent'], datetime.fromtimestamp(peer['conntime']).strftime("%m/%d/%Y %I:%M:%S %Z"),
								    str(dd).zfill(2) + ":" + str(hh).zfill(2) + ":" + str(mm).zfill(2) + ":" + str(ss).zfill(2),
									  banstat))

#Output top/bottem seperators 
def nodeLineSep():
	print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------")

#Sleep
def nodeSleep(sleeptime):
	import time
	import datetime

	now = datetime.datetime.now()
	print("Sleeping for " + sleeptime + " seconds @ " + now.strftime("%d/%m/%Y %H:%M:%S") + " - Ctrl-C to Exit")
	time.sleep(int(sleeptime))

#Convert seconds to days, hours, minutes and seconds.
def getDurationStr(connSeconds):

	#get minutes, seconds 
	mm, ss = divmod(connSeconds, 60)
	#get hours
	hh, mm= divmod(mm, 60)
	#get days
	dd, hh= divmod(hh, 24)
	
	return(dd, hh, mm, ss)

def nodeBan(tmpip, bantime):
	#bh = subprocess.check_output('pocketcoin-cli setban \"'+ tmpip[0] +'\" add 36288000', shell=True)
	bh = subprocess.check_output('pocketcoin-cli setban \"'+ tmpip[0] +'\" add \"' + bantime + '\"', shell=True)


#import the nesscary libraries
import subprocess
import json
import time
import datetime
import logging
import sys
from datetime import datetime
from datetime import timedelta
import configparser

#Configure logging
logging.basicConfig(filename='bhammer.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S %Z')

logging.debug("***************************************************************************************")
logging.debug("************************** Starting bHammer Version: 0.0.7 ****************************")
logging.debug("***************************************************************************************")

#Load Settings
config = configparser.ConfigParser()

config.read('bhammer.conf')
sleeptime = config['main']['sleepseconds']
banbytes = config['main']['banbytes']
lowver = config['main']['lowver']
noversionbanseconds = config['main']['noversionbanseconds']
noversionbantime = config['main']['noversionbantime']
hogcheckstopseconds = config['main']['hogcheckstopseconds']
hogbanseconds = config['main']['hogbanseconds']
versioncheck  = config['main']['versioncheck']
leachcheck = config['main']['leachcheck']
emptyversioncheck = config['main']['emptyversioncheck']

#logging.debug(sleeptime)
#logging.debug(banbytes)
#logging.debug(lowver)


#Set Lowest Acceptable Version
LAV = lowver.split(".", 2)
LAVtxt = str(LAV)
logging.debug("")
logging.debug("Lowest Acceptable Version (LAV): " + LAVtxt)
logging.debug("")

try:
	#infinte loop, will have to ctl-c to exit
	while True:

		#load json peerlist
		try:
			peerlist = json.loads(subprocess.check_output('pocketcoin-cli getpeerinfo', shell=True))
		except:
			nodeSleep(sleeptime)
			continue

			
		inboundcount = 0
		outbountcount = 0
		
		print()
		print("  IP Address:Port\t\tVersion\t\t       Inbound\t   Bytes Rec'd\t      Bytes Sent  \tConnected@\t\tDuration\tNode Status")
		print("\t\t\t\t\t\t\t\t\t\t\t\t\t(dd:hh:mm:ss)")
		
		#print("----------------------------------------------------------------------------------------------------------------------------")
		nodeLineSep()

		#iterate through peers and do work
		for index, peer in enumerate(peerlist):

			#Strip leading and trailing space (just in case)
			banstat = ""
			tmpver = peer['subver'].strip()
			tmpip = peer['addr'].strip()
			tmpbs = peer['bytessent']
			#remove slashes
			tmpver = tmpver.strip('/')
			#remove 'Satoshi:'
			tmpver = tmpver.strip('Satoshi:')
			#split on version periods and ip address on colon
			tmpver = tmpver.split('.')
			tmpip = tmpip.split(':')
			connSeconds = round(time.time())-int(peer['conntime'])
			#logging.debug("************")
			#logging.debug("peer: " + str(peer))
			#logging.debug("************")
			#logging.debug("tmpver: " + str(tmpver))
			#logging.debug("LAV: " + str(LAV))
			#logging.debug("index: " + str(index))

			#If version string is empty then skip it for now and exit the loop so we don't crash on an empty string
			if str(peer['subver']) == '':
				banstat = " - Connected: " + str(connSeconds) + "s"
				#If empty version check is true
				if int(emptyversioncheck) == 1:
					if str(peer['subver']) == '' and connSeconds >= int(noversionbanseconds):
						logging.debug("tmpip[0]: " + tmpip[0] + " noversionbantime: " + noversionbantime) + "duration: " + str(connSeconds)
						nodeBan(tmpip[0], noversionbantime)
						peer['subver'] = "*No Verson Info*"
						
						logging.debug("peer['conntime']: " + str(peer['conntime']) + " noversionbanseconds: " + str(noversionbanseconds))
						logging.debug("Skipped Node: " + peer['addr'] + "  " + peer['subver'] + " " + banstat)

						dd, hh, mm, ss = getDurationStr(connSeconds)
						nodeLinePrint(peer, dd, hh, mm, ss, banstat)
						continue

				peer['subver'] = "*No Verson Info*"
				
				logging.debug("Skipped Node: " + peer['addr'] + "  " + peer['subver'] + " " + banstat)
				
				dd, hh, mm, ss = getDurationStr(connSeconds)
				nodeLinePrint(peer, dd, hh, mm, ss, banstat)
				continue

			if peer['inbound'] == True:
				inboundcount += 1

			if peer['inbound'] == False:
				outbountcount += 1

			#If version check is enabled (true)
			if int(versioncheck) == 1:
				#If major version is less than LAV
				#have to cast str's to int's so we don't crash
				if int(tmpver[1]) < int(LAV[1]):
					#logging.debug("This node has an old major version")
					#logging.debug("pocketcoin-cli setban \""+ tmpip[0] +"\" add 604800")
					bh = subprocess.check_output('pocketcoin-cli setban \"'+ tmpip[0] +'\" add 36288000', shell=True)
					banstat = "Major version ban - length 36288000 seconds"
					#logging.debug(banstat)
					#logging.debug(bh)
					#logging.debug("BAN HAMMERED!!!!!!!!!!!!!")
					if peer['inbound'] == True:
						peertype = "Inbound"
					if peer['inbound'] == False:
						peertype = "Outbound"
					logging.debug("Banned Node: " + peer['addr'] + "  " + peer['subver'] + "  " + peertype + "  " + banstat)
					#calculate duration
					dd, hh, mm, ss = getDurationStr(connSeconds)
					#output to console
					nodeLinePrint(peer, dd, hh, mm, ss, banstat)
					continue

				#If minor version is less than LAV AND major version is equal to or greater than LAV
				#have to cast str's to int's so we don't crash
				if int(tmpver[2]) < int(LAV[2]) and int(tmpver[1]) <= int(LAV[1]):
					#logging.debug("This node has an old minor version")
					#logging.debug("pocketcoin-cli setban \""+ tmpip[0] +"\" add ")
					bh = subprocess.check_output('pocketcoin-cli setban \"' + tmpip[0] + '\" add 36288000', shell=True)
					banstat = "Minor version ban - length 36288000 seconds"
					#logging.debug(banstat)
					#logging.debug(bh)
					#logging.debug("BAN HAMMERED!!!!!!!!!!!!!")
					if peer['inbound'] == True:
						peertype = "Inbound"
					if peer['inbound'] == False:
						peertype = "Outbound"
					logging.debug("Banned Node: " + peer['addr'] + "  " + peer['subver'] + "  " + peertype + "  " + banstat)
					#calculate duration
					dd, hh, mm, ss = getDurationStr(connSeconds)
					#output to console
					nodeLinePrint(peer, dd, hh, mm, ss, banstat)
					continue
				
			
			if int(leachcheck) == 1:
				#If bytessent is over the threasehold (1gb or 1073741824 bytes is the default)
				#have to cast str's to int's so we don't crash
				if int(tmpbs) >= int(banbytes) and connSeconds < int(hogcheckstopseconds):
					#logging.debug("This node has an old minor version")
					#logging.debug("pocketcoin-cli setban \""+ tmpip[0] +"\" add ")
					bh = subprocess.check_output('pocketcoin-cli setban \"' + tmpip[0] + '\" add 86400', shell=True)
					nodeBan(tmpip[0], hogbanseconds)
					banstat = "Bandwidth ban for length 86400 seconds. Node used: " + str(tmpbs) + "bytes"
					#logging.debug(banstat)
					#logging.debug(bh)
					#logging.debug("BAN HAMMERED!!!!!!!!!!!!!")
					if peer['inbound'] == True:
						peertype = "Inbound"
					if peer['inbound'] == False:
						peertype = "Outbound"
					logging.debug("Banned Node: " + peer['addr'] + "  " + peer['subver'] + "  " + peertype + "  " + banstat)
					#calculate duration
					dd, hh, mm, ss = getDurationStr(connSeconds)
					#output to console
					nodeLinePrint(peer, dd, hh, mm, ss, banstat)
					continue

			banstat = "Pass - No Ban"
			#calculate duration
			dd, hh, mm, ss = getDurationStr(connSeconds)
			#output to console
			nodeLinePrint(peer, dd, hh, mm, ss, banstat)

		#print("----------------------------------------------------------------------------------------------------------------------------")
		nodeLineSep()

		now = datetime.now()
		try:
			banlist = json.loads(subprocess.check_output('pocketcoin-cli listbanned', shell=True))
		except:
			print("Load listbanned exeption. " + now.strftime("%m/%d/%Y %H:%M:%S %Z"))
			banlist = ""

		print()
		print("{0} peers banned".format(len(banlist)))
		print("{0} peers connected. {1} inbound peers. {2} outbound peers.".format(len(peerlist), inboundcount, outbountcount))
		nodeSleep(sleeptime)
		print()
		print()

except KeyboardInterrupt:
	print()
	print()
	exit()
