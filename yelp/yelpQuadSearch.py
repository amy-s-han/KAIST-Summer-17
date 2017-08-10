#!/usr/bin/python
# -*- coding: utf-8 -*

# Amy Han - Summer 2017 - KIXLAB
# Uses quad tree search method and the Yelp 2.0 API to find all locations 
# in the Greater Seattle area within one location category. Writes out a
# tsv file with [ id, name, rating, rating_cnt, url_yelp_mobile, url_yelp, 
#               categories, info_phone, info_address, info_city, 
#               info_country, loc_x, loc_y ]

# This tsv file can then be fed into the scrapeYelpFromFile python script
# to get more information about the locations from Yelp.

# For areas around malls/shopping centers where there may be more than 20
# stores for one location type (fashion), it is impossible to get all the 
# stores in the mall and it only gets the 20 locations that Yelp happens
# to return. This is because Yelp returns at most 20 locations for any 
# api search call. 

import urllib, urllib2
import requests, socket
import rauth
import csv, json, sys, time
import os.path
import oauth2
import threading
import time

city = "seattleData/"
locType = "zoos"
count = 0
filename = ""
apiHits = 0

foundLocs = {}

g_box ={ #geographical bounding box
  "S":47.395, #SW latitude : 47.3956
  "W":-122.440, #SW longitude : -122.4379
  "N":47.859, #NE latitude : 47.8591
  "E":-122.075 #NE longitude : -122.0791
}

yelp_auth1 = { #YS
  "c_key": "ehFLGk-NHTxL6kq5roKvnA",
  "c_secret": "pHhLtTES7IMCr-DR4fQZQCsrIE8",
  "t": "0wewkIEeImyXojuvRdi8aoEMDk7NlSvl",
  "t_secret": "NlR1WUyu7_Jk6Obwd33EXp2IFV0"
}

yelp_auth2 = { #media.ray.hong@gmail.com
    "c_key": "S5_BC3VbhWnHHnBydhkpkA",
    "c_secret": "jBd3rq4Ao1BwpPqhwtyBaZxKeoA",
    "t": "iungqKfR4LtiIGYa3AUeDF7nIlCnhgRQ",
    "t_secret": "fcFssUnSlxh5Y4REJlyDE6mGx-c"  
}

yelp_auth3 = { 
    "c_key": "KebuzyDt6v1VtHu1BTYiBQ",
    "c_secret": "lUHtfPGHJpUdqJoENKAIFxiblRA",
    "t": "USCS2ns3HHCUHAZ8hAvnBpCUEu2NY-zB",
    "t_secret": "x_benaM_8Cud2ud5_QIMqhubj5M"
}  

auth = yelp_auth1

def getBusinessData(data):
  global count
  global foundLocs
  global duplicateCounter

  startCount = count

  #Print out the result
  for i in range(len(data["businesses"])):
    if foundLocs.has_key(data['businesses'][i]['id'].encode('utf8')):
      # print "*** Already had key: ", data['businesses'][i]['id'].encode('utf8')
      continue
    else:
      foundLocs[data['businesses'][i]['id'].encode('utf8')] = 1

    count = count + 1
    #Error check
    try: loc_long = data['businesses'][i]['location']['coordinate']['longitude']
    except: continue
    try: loc_lat = data['businesses'][i]['location']['coordinate']['latitude']
    except: continue

    if (loc_long > g_box["W"] and loc_long < g_box["E"]) and (loc_lat < g_box["N"] and loc_lat > g_box["S"]):
      fout = open(filename, 'a')
      each = []
      try: each.append(data['businesses'][i]['id'].encode('utf8'))
      except: each.append('N/A')
      try: each.append(data['businesses'][i]['name'].encode('utf8'))
      except: each.append('N/A')
      try: each.append(str(data['businesses'][i]['rating']).encode('utf8')) 
      except: each.append('N/A')
      try: each.append(str(data['businesses'][i]['review_count']).encode('utf8'))
      except: each.append('N/A')
      try: each.append(data['businesses'][i]['mobile_url'].encode('utf8')) 
      except: each.append('N/A')
      try: each.append(data['businesses'][i]['url'].encode('utf8')) 
      except: each.append('N/A')
      try: each.append(location_type.encode('utf8')) 
      except: each.append('N/A')
      try: each.append(data['businesses'][i]['display_phone'].encode('utf8')) 
      except: each.append('N/A')
      try: each.append(' '.join(data['businesses'][i]['location']['display_address'].encode('utf8'))) 
      except: each.append('N/A')
      try: each.append(data['businesses'][i]['location']['city'].encode('utf8')) 
      except: each.append('N/A')
      try: each.append(str(data['businesses'][i]['location']['postal_code']).encode('utf8'))
      except: each.append('N/A')
      try: each.append(str(data['businesses'][i]['location']['country_code']).encode('utf8'))
      except: each.append('N/A')
      try: each.append(str(data['businesses'][i]['location']['coordinate']['longitude']).encode('utf8'))
      except: each.append('N/A')
      try: each.append(str(data['businesses'][i]['location']['coordinate']['latitude']).encode('utf8'))
      except: each.append('N/A')

      line_each = '\t'.join(each) + '\n'
      fout.write(line_each)
      fout.close()

      print "[" + str(count) + "] Added "+ data['businesses'][i]['id'].encode('utf8')
  
  print "Sum: " + str(count - startCount) + " points were added."  


def quadSearch(xStart, xEnd, yStart, yEnd):
  global apiHits

  # print xStart, xEnd, yStart, yEnd

  params={
    'bounds': str(yEnd) +","+ str(xStart) +"|"+ str(yStart) +","+ str(xEnd),
    'category_filter': locType,
    'sort': "2"
  }

  # print params
  session = rauth.OAuth1Session(
    consumer_key = auth['c_key'],
    consumer_secret = auth['c_secret'],
    access_token = auth['t'],
    access_token_secret = auth['t_secret'])
  request = session.get("http://api.yelp.com/v2/search", params=params)
  data = {}
  data = request.json()
  session.close()
  
  apiHits += 1

  if data.has_key('error'):
    print "Failed gathering."
    return

  elif len(data["businesses"]) == 0:
    return

  elif len(data["businesses"]) == 20:
    # print "More than 20!"
    xMid = round(xStart + (xEnd - xStart)/2.0, 4)
    yMid = round(yStart - (yStart - yEnd)/2.0, 4)
    if abs(xEnd-xMid) < 0.001 or abs(yEnd-yMid) < 0.001:
      # print abs(xEnd-xMid), abs(yEnd-yMid)
      print "just getting data even though >20"
      getBusinessData(data)
    else:
      quadSearch(xStart, xMid, yStart, yMid)
      quadSearch(xMid, xEnd, yStart, yMid)
      quadSearch(xStart, xMid, yMid, yEnd)
      quadSearch(xMid, xEnd, yMid, yEnd)

  else:
    getBusinessData(data)

def main():

  #encoding: utf-8
  import sys;
  reload(sys);
  sys.setdefaultencoding('utf8');

  global filename

  filename = city + locType + ".tsv"

  #add header
  fout = open(filename, "w")
  line_header = 'id'+'\t'+'name'+'\t'+'rating'+'\t'+'rating_cnt'+'\t'+'url_yelp_mobile'+'\t'+'url_yelp'+'\t'+'categories'+'\t'+'info_phone'+'\t'+'info_address'+'\t'+'info_city'+'\t'+'info_zip'+'\t'+'info_country'+'\t'+'loc_x'+'\t'+'loc_y'+'\n'
  fout.write(line_header)
  fout.close()

  print "starting quad search for location: " + locType
  quadSearch(g_box["W"], g_box["E"], g_box["N"], g_box["S"])

  print "Hit the api", apiHits, "times.\n"

  statsFilename = city+"stats.txt"
  fstats = open(statsFilename, "a")
  stat = locType + " " + str(count) + " " + str(apiHits) + "\n"
  fstats.write(stat)
  fstats.close()


if __name__ == "__main__":
    main()