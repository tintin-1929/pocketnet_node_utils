# Ban Hammer by James Lawrence
#
# Filename: bhammer.py
# Version: 0.00.01
# Date: 16 NOV 2022
# A Script to ban downlevel Pocketcoin Nodes
#
# Freely use or distribute this code. No warrenties of anykind. Use at your own risk
# Requires Python 3.9

#import libraries
import subprocess
import json
import time
import datetime

#infinte loop, will have to ctl-c to exit
while True:

	#load json peerlist
	peerlist = json.loads(subprocess.check_output('pocketcoin-cli getpeerinfo', shell=True))

	#Set Lowest Acceptable Version
	LAV = [0,20,27]
	print("Lowest Acceptable Version (LAV): ", LAV)
	print()
	print()

	#iterate through peers and do work
	for peer in peerlist:
		print("*********************")
		print("Peer Version: " + peer['subver'])
		print("Peer IP Address (address:port): " + peer['addrbind'])
		#Strip leading and trailing space (just in case)
		tmpver = peer['subver'].strip()
		tmpip = peer['addrbind'].strip()
		#remove slashes
		tmpver = tmpver.strip('/')
		#remove 'Satoshi:'
		tmpver = tmpver.strip('Satoshi:')
		#split on version periods and ip address on colon
		tmpver = tmpver.split('.')
		tmpip = tmpip.split(':')
		#If major version is less than LAV
		#have to cast str's to int's so we don't crash
		if int(tmpver[1]) < LAV[1]:
			print("This node has an old major version")
			print("pocketcoin-cli setban \""+ tmpip[0] +"\" add 9999999999")
			bh = subprocess.check_output('pocketcoin-cli setban \"'+ tmpip[0] +'\" add 9999999999', shell=True)
			print(bh)
			continue
		#If minor version is less than LAV AND major version is equal to or greater than
		#have to cast str's to int's so we don't crash
		if int(tmpver[2]) < LAV[2] and int(tmpver[1]) <= LAV[1]:
			print("This node has an old minor version")
			print("pocketcoin-cli setban \""+ tmpip[0] +"\" add 9999999999")
			bh = subprocess.check_output('pocketcoin-cli setban \"' + tempip[0] + '\" add 9999999999', shell=True)
			print(bh)
			continue
		print("*********************")

	now = datetime.datetime.now()
	print()
	print("*********************")
	print("Sleeping for 5 minutes @ " + now.strftime("%d/%m/%Y %H:%M:%S"))
	print("*********************")
	print()
	time.sleep(300)