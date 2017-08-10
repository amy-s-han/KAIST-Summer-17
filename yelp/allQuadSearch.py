#!/usr/bin/python
# -*- coding: utf-8 -*

# Amy Han - Summer 2017 - KIXLAB
# Uses quad tree search method and the Yelp 2.0 API to find all locations 
# in the Greater Seattle area for a list of categories. Writes out tsv
# files with [ id, name, rating, rating_cnt, url_yelp_mobile, url_yelp, 
#              categories, info_phone, info_address, info_city, 
#              info_country, loc_x, loc_y ]

# The tsv files can then be fed into the scrapeYelpFromFile python script
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
import sys

city = "nyc"
locType = ""
count = 0
filename = ""
apiHits = 0
zipsExist = False
zipCodes = []

foundLocs = {}

destList = ["newamerican"]


# destList = ["newamerican", "tradamerican", "chinese", "french", "indpak", "italian", "japanese", "mexican",
#             "mediterranean", "thai", "vegan", "vegetarian", "cafes", "coffee", "coffeeroasteries", "bubbletea",
#             "tea", "juicebars", "desserts", "icecream", "gelato", "landmarks", "museums", "aquariums", "parks",
#             "beaches", "amusementparks", "zoos", "theater", "artsandcrafts", "bookstores", "cosmetics", 
#             "deptstores", "drugstores", "electronics", "fashion", "jewelry", "grocery", "bars", "beergardens", 
#             "jazzandblues", "karaoke", "comedyclubs", "musicvenues", "danceclubs"]


g_box ={ #geographical bounding box for Greater Seattle Area
  "S":47.395, #SW latitude : 47.3956
  "W":-122.440, #SW longitude : -122.4379
  "N":47.859, #NE latitude : 47.8591
  "E":-122.075 #NE longitude : -122.0791
}

g_box1 ={ #geographical bounding box for Staten Island
  "S":40.495979, #SW latitude
  "W":-74.256341, #SW longitude 
  "N":40.650187, #NE latitude
  "E":-74.051666 #NE longitude 
}

g_box2 ={ #geographical bounding box for Bronx, Brooklyn and Manhattan
  "S":40.530056, #SW latitude
  "W":-74.041617, #SW longitude 
  "N":40.907521, #NE latitude
  "E":-73.685714 #NE longitude 
}

yelp_auth1 = { 
  "c_key": "",
  "c_secret": "",
  "t": "",
  "t_secret": ""
}

yelp_auth2 = { 
  "c_key": "",
  "c_secret": "",
  "t": "",
  "t_secret": ""
}  

auth = yelp_auth2

# Zips to ignore for nyc
zipsToIgnore = ["11050", "10704", "10550", "10801", "10805", "11042", "11021", "11030", "11040", "11581", "11598",
                "11001", "11561", "11509", "11516"]

cities = ["Staten Island", "New York", "Annadale", "Bronx", "Sunnyside", "Travis", "Elm Park", "Great Kills", "East Bronx",
          "Manhattan", "Long Island City", "New  York", "Greenpoint", "Brooklyn", "Astoria", "Queens", "East Elmhurst",
          "Woodside", "Corona", "City Island", "College Point", "Flushing", "Whitestone", "Forest Hills", "Rego Park", 
          "Bowling Green", "Williamsburg", "Park Slope", "Clinton Hill", "Bedford-Stuyvesant", "Fort Greene", "Crown Heights",
          "Ozone Park", "S Richmond Hill", "Jamaica", "Briarwood", "Hollis", "Rosedale", "Springfield Gardens",
          "Rockaway Park", "Broad Channel", "Arverne", "Kew Gardens", "Coney Island", "Canarsie", "Midwood", "Breezy Point",
          "East Flatbush", "Ridgewood", "Glendale", "Elmhurst", "Jackson Heights", "Bayside", "Douglaston", "Bellerose",
          "Downtown Brooklyn", "Gowanus", "South Ozone Park", "Richmond Hill", "Bushwick", "East Williamsburg", "Flatbush",
          "Prospect Lefferts Gardens", "Woodhaven", "East New York"]

def getBusinessData(data, W, E, N, S):
  global count
  global foundLocs
  global duplicateCounter

  startCount = count

  #Print out the result
  for i in range(len(data["businesses"])):
    # check if we already found this location
    if foundLocs.has_key(data['businesses'][i]['id'].encode('utf8')): 
      # print "*** Already had key: ", data['businesses'][i]['id'].encode('utf8')
      continue
    else:
      foundLocs[data['businesses'][i]['id'].encode('utf8')] = 1


    if zipsExist:
      try:
        zippy = str(data['businesses'][i]['location']['postal_code']).encode('utf8')
        thisCity = data['businesses'][i]['location']['city'].encode('utf8')
        if zippy not in zipCodes and thisCity not in cities:
          # print data['businesses'][i]['id'].encode('utf8'), "with zip: ", zippy, "not in zipcodes\n"

          if zippy[0] != "0" and zippy not in zipsToIgnore:
            badZipFilename = city + "Data/" + "badZip.txt"
            f = open(badZipFilename, "a")
            f.write(data['businesses'][i]['id'].encode('utf8')+ " " + thisCity + " " + zippy + "\n")
            f.close()
          continue
      except:
        # print "!!!!!", data['businesses'][i]['id'].encode('utf8'), "doesn't have a zip"
        try:
          thisCity = data['businesses'][i]['location']['city'].encode('utf8')
          if thisCity not in cities:

            noZipFilename = city + "Data/" + "noZips.txt"
            f = open(noZipFilename, "a")
            f.write(data['businesses'][i]['id'].encode('utf8') + " " + thisCity + "\n")
            f.close()

            continue
        except:
          noZipFilename = city + "Data/" + "noZips.txt"
          f = open(noZipFilename, "a")
          f.write(data['businesses'][i]['id'].encode('utf8')+"\n")
          f.close()
          continue

    count = count + 1
    #Error check
    try: loc_long = data['businesses'][i]['location']['coordinate']['longitude']
    except: continue
    try: loc_lat = data['businesses'][i]['location']['coordinate']['latitude']
    except: continue

    if (loc_long > W and loc_long < E) and (loc_lat < N and loc_lat > S):
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
      try: 
        each.append(data['businesses'][i]['location']['city'].encode('utf8')) 
        if data['businesses'][i]['location']['city'].encode('utf8') not in cities:
          print data['businesses'][i]['location']['city'].encode('utf8')
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

      print ".",
      sys.stdout.flush()
      # print "[" + str(count) + "] Added "+ data['businesses'][i]['id'].encode('utf8')
  
  # print "Sum: " + str(count - startCount) + " points were added."  


def quadSearch(xStart, xEnd, yStart, yEnd, W, E, N, S):
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
      # print "just getting data even though >20"
      getBusinessData(data, W, E, N, S)
    else:
      quadSearch(xStart, xMid, yStart, yMid, W, E, N, S)
      quadSearch(xMid, xEnd, yStart, yMid, W, E, N, S)
      quadSearch(xStart, xMid, yMid, yEnd, W, E, N, S)
      quadSearch(xMid, xEnd, yMid, yEnd, W, E, N, S)

  else:
    getBusinessData(data, W, E, N, S)

def loadZips():
  global zipCodes
  global zipsExist

  zipfile = city + "Data/" + city + "ZipCodes.txt"

  if os.path.isfile(zipfile):
    zipsExist = True
    fzips = open(zipfile, "r")
    line = fzips.readline()
    zipCodes = line.split()

def loadKeys():
  fkeys = open("key.txt")
  key1 = fkeys.readline().split()
  yelp_auth1["c_key"] = key1[0]
  yelp_auth1["c_secret"] = key1[1]
  yelp_auth1["t"] = key1[2]
  yelp_auth1["t_secret"] = key1[3]

  key2 = fkeys.readline().split()
  yelp_auth2["c_key"] = key2[0]
  yelp_auth2["c_secret"] = key2[1]
  yelp_auth2["t"] = key2[2]
  yelp_auth2["t_secret"] = key2[3]

def main():

  #encoding: utf-8
  import sys;
  reload(sys);
  sys.setdefaultencoding('utf8');

  global locType
  global filename
  global apiHits
  global count
  global foundLocs

  loadZips()
  loadKeys()

  start = time.time()

  for dest in destList:

    locType = dest
    filename = city + "Data/" + dest + ".tsv"

    #add header
    fout = open(filename, "w")
    line_header = 'id'+'\t'+'name'+'\t'+'rating'+'\t'+'rating_cnt'+'\t'+'url_yelp_mobile'+'\t'+'url_yelp'+'\t'+'categories'+'\t'+'info_phone'+'\t'+'info_address'+'\t'+'info_city'+'\t'+'info_zip'+'\t'+'info_country'+'\t'+'loc_x'+'\t'+'loc_y'+'\n'
    fout.write(line_header)
    fout.close()

    print "starting quad search for location: " + locType
    
    # for large cities with weird geometry, you can split it up into rectangle sections and put each section into a g_box.
    # then, just do quadSearch(gbox...) for each section.

    locStart = time.time()
    
    quadSearch(g_box1["W"], g_box1["E"], g_box1["N"], g_box1["S"], g_box1["W"], g_box1["E"], g_box1["N"], g_box1["S"])
    print "\nfinished staten island with", count, "locs and", apiHits, "apiHits.\n"
    
    quadSearch(g_box2["W"], g_box2["E"], g_box2["N"], g_box2["S"], g_box2["W"], g_box2["E"], g_box2["N"], g_box2["S"])
    print "\nfinished Bronx, Brooklyn, Manhattan"
    
    locEnd = time.time()

    elapsedTime = locEnd - locStart

    print "Took", str(elapsedTime), "seconds. \n"

    print "Hit the api", apiHits, "times and got", count, "locations.\n"

    # write out number of locations and api calls to stats file
    statsFilename = city + "Data/" + "stats.txt"
    fstats = open(statsFilename, "a")
    stat = locType + " " + str(count) + " " + str(apiHits) + " " + str(elapsedTime) + "\n"
    fstats.write(stat)
    fstats.close()

    apiHits = 0
    count = 0
    foundLocs.clear()

  end = time.time()

  print "elapsed time:", str(end-start)

if __name__ == "__main__":
    main()