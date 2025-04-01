#!/usr/bin/env python3

#cron entry
#*/5 * * * * /usr/bin/flock -w 1 /run/lock/technitium_dhcp_scope_reserve_sync.lock /home/<user>/bin/technitium_dhcp_scope_reserve_sync.py >> /home/<user>/log/technitium_dhcp_scope_reserve_sync-`/usr/bin/date +\%F`.log

import datetime
import time
import requests
import json

datetime = time.strftime("%m-%d-%Y %H:%M:%S", time.localtime())
tdns_source_host = "dns01.<domainname>"
tdns_source_token = "<api key>"
tdns_dest_host = "dns02.<domainname>"
tdns_dest_token = "<api key>"

#Functions
def purgecopy(scopeName):
  print(f'{datetime} - Purge and Copy - {scopeName}')
  #Purge
  try:
    for x in response_dest['response']['reservedLeases']:
      #print(x['hardwareAddress'])
      hardwareaddress = x['hardwareAddress']
      response = requests.get(f'http://{tdns_dest_host}:5380/api/dhcp/scopes/removeReservedLease?token={tdns_dest_token}&name={scopeName}&hardwareAddress={hardwareaddress}').json()
  except:
    print("error in purge")
  #Copy
  try:
    for x in response_source['response']['reservedLeases']:
      hostName = x['hostName']
      hardwareaddress = x['hardwareAddress']
      address = x['address']
      comments = x['comments']
      if (hostName is None) and (comments is None):
        response = requests.get(f'http://{tdns_dest_host}:5380/api/dhcp/scopes/addReservedLease?token={tdns_dest_token}&name={scopeName}&hardwareAddress={hardwareaddress}&ipAddress={address}').json()
      elif (hostName is not None) and (comments is None):
        response = requests.get(f'http://{tdns_dest_host}:5380/api/dhcp/scopes/addReservedLease?token={tdns_dest_token}&name={scopeName}&hardwareAddress={hardwareaddress}&ipAddress={address}&hostName={hostName}').json()
      elif (hostName is None) and (comments is not None):
        response = requests.get(f'http://{tdns_dest_host}:5380/api/dhcp/scopes/addReservedLease?token={tdns_dest_token}&name={scopeName}&hardwareAddress={hardwareaddress}&ipAddress={address}&comments={comments}').json()
      else:
        response = requests.get(f'http://{tdns_dest_host}:5380/api/dhcp/scopes/addReservedLease?token={tdns_dest_token}&name={scopeName}&hardwareAddress={hardwareaddress}&ipAddress={address}&hostName={hostName}&comments={comments}').json()
  except:
    print("error in copy")

#Main
try:
  response_source_scopes = requests.get(f'http://{tdns_source_host}:5380/api/dhcp/scopes/list?token={tdns_source_token}').json()
  for s in response_source_scopes['response']['scopes']:
    scopeName = s['name']
    response_source = requests.get(f'http://{tdns_source_host}:5380/api/dhcp/scopes/get?token={tdns_source_token}&name={scopeName}').json()
    response_dest = requests.get(f'http://{tdns_dest_host}:5380/api/dhcp/scopes/get?token={tdns_dest_token}&name={scopeName}').json()
    if (len(response_source['response']['reservedLeases']) == 0) and (len(response_dest['response']['reservedLeases']) == 0):
      pass
    elif (len(response_source['response']['reservedLeases']) == 0) or (len(response_dest['response']['reservedLeases']) == 0):
      purgecopy(scopeName)
    elif (len(response_source['response']['reservedLeases']) != len(response_dest['response']['reservedLeases'])):
      purgecopy(scopeName)

    else:
      for r in range(len(response_source['response']['reservedLeases'])):
        if response_source['response']['reservedLeases'][r] == response_dest['response']['reservedLeases'][r]:
          pass
        else:
          print(response_source['response']['reservedLeases'][r])
          print(response_dest['response']['reservedLeases'][r])
          print("No Match")
          purgecopy(scopeName)
          break

except Exception as e:
  print("error" + str(e))
