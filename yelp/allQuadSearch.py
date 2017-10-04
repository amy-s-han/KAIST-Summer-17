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

# for large cities with weird geometry, you can split it up into rectangle sections and put each section into a g_box.
# then, just do quadSearch(gbox...) for each section.



import urllib, urllib2
import requests, socket
import rauth
import csv, json, sys, time
import os.path
import oauth2
import threading
import time
import sys
import json

city = "nyc"
locType = ""
count = 0
filename = ""
apiHits = 0
zipsExist = False
zipCodes = []
locDict = {}

destList = ["icecream"]


# destList = ["newamerican", "tradamerican", "chinese", "french", "indpak", "italian", "japanese", "mexican",
#             "mediterranean", "thai", "vegan", "vegetarian", "cafes", "coffee", "coffeeroasteries", "bubbletea",
#             "tea", "juicebars", "desserts", "icecream", "gelato", "landmarks", "museums", "aquariums", "parks",
#             "beaches", "amusementparks", "zoos", "theater", "artsandcrafts", "bookstores", "cosmetics", 
#             "deptstores", "drugstores", "electronics", "fashion", "jewelry", "grocery", "bars", "beergardens", 
#             "jazzandblues", "karaoke", "comedyclubs", "musicvenues", "danceclubs"]


g_box ={ # geographical bounding box for Greater Seattle Area
  "S":47.395, #SW latitude : 47.3956
  "W":-122.440, #SW longitude : -122.4379
  "N":47.859, #NE latitude : 47.8591
  "E":-122.075 #NE longitude : -122.0791
}

g_box1 ={ # geographical bounding box for Staten Island
  "S":40.495979, #SW latitude
  "W":-74.256341, #SW longitude 
  "N":40.650187, #NE latitude
  "E":-74.051666 #NE longitude 
}

g_box2 ={ # geographical bounding box for Bronx, Brooklyn and Manhattan
  "S":40.530056, #SW latitude
  "W":-74.041617, #SW longitude 
  "N":40.907521, #NE latitude
  "E":-73.685714 #NE longitude 
}

bb_nyc ={ # geographical bounding box for NYC
  "S":40.477399, #SW latitude
  "W":-74.25909, #SW longitude 
  "N":40.917577, #NE latitude
  "E":-73.700272 #NE longitude 

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
                "11001", "11561", "11509", "11516", "10803", "12144", "11559", "11580", "11557", "11003", "11010",
                "11023", "11096", "11020", "11024", "11530", "11025"]

cities = ["Staten Island", "New York", "Annadale", "Bronx", "Sunnyside", "Travis", "Elm Park", "Great Kills", "East Bronx",
          "Manhattan", "Long Island City", "New  York", "Greenpoint", "Brooklyn", "Astoria", "Queens", "East Elmhurst",
          "Woodside", "Corona", "City Island", "College Point", "Flushing", "Whitestone", "Forest Hills", "Rego Park", 
          "Bowling Green", "Williamsburg", "Park Slope", "Clinton Hill", "Bedford-Stuyvesant", "Fort Greene", "Crown Heights",
          "Ozone Park", "S Richmond Hill", "Jamaica", "Briarwood", "Hollis", "Rosedale", "Springfield Gardens",
          "Rockaway Park", "Broad Channel", "Arverne", "Kew Gardens", "Coney Island", "Canarsie", "Midwood", "Breezy Point",
          "East Flatbush", "Ridgewood", "Glendale", "Elmhurst", "Jackson Heights", "Bayside", "Douglaston", "Bellerose",
          "Downtown Brooklyn", "Gowanus", "South Ozone Park", "Richmond Hill", "Bushwick", "East Williamsburg", "Flatbush",
          "Prospect Lefferts Gardens", "Woodhaven", "East New York", "Sunset Park", "Randall Manor", "Mariners Harbor",
          "Saint George", "New Dorp Beach", "Bronx Riverdale", "Morris Heights", "West Bronx", "Woodstock", "Chelsea", 
          "Canal Street", "Roosevelt Island", "New york", "Maspeth", "Middletown - Pelham Bay", "Throggs Neck", "Malba",
          "Fresh Meadows", "Little Neck", "Far Rockaway", "Rockaway Beach", "Cambria Heights", "Saint Albans", "Howard Beach",
          "South Richmond Hill", "Bath Beach", "Brighton Beach", "Gravesend", "Sheepshead Bay", "Bay Ridge", "Carroll Gardens",
          "Borough Park", "Brooklyn Heights", "Stockholm", "Brownsville", "Jamacia", "Tottenville", "Fleetwood - Concourse Village",
          "E Elmhurst", "Middle Village", "Norwood", "Oakland Gardens", "Fresh Meadow", "Queens Village", "Glen Oaks",
          "Kensington", "Dyker Heights", "Cypress Hills", "Flatlands", "Bensonhurst", "Marine Park", "Forrest Hills",
          "Boerum Hill", "Floral Park", "New York City", "Harlem", "Eltingville", "Bay Terrace", "Lighthouse Hill",
          "Belle Harbor", "St. Albans", "Rockaway", "Tompkinsville", "New Dorp", "Fordham Manor", "Fieldston", "Foxhurst",
          "NY", "Tompkins Park North", "Cobble Hill", "Corona Queens", "Grymes Hill", "Central Park", "Park Hill", 
          "Bellerose Queens", "Riverdale", "Kingsbridge", "Belmont", "Tremont", "Concourse", "Travis - Chelsea",
          "Heartland Village", "Red Hook", "Spuyten Duyvil", "Greenwood", "Flatbush - Ditmas Park", "Seaside", "Mill Basin",
          "Mapleton", "Windsor Terrace", "Corona", "Prince's Bay"]

def getBusinessData(data, W, E, N, S):
  global count
  global locDict
  global duplicateCounter

  startCount = count

  #Print out the result
  for i in range(len(data["businesses"])):
    # check if we already found this location
    if locDict.has_key(data['businesses'][i]['id'].encode('utf8')): 
      # print "*** Already had key: ", data['businesses'][i]['id'].encode('utf8')
      continue
    else:
      locDict[data['businesses'][i]['id'].encode('utf8')] = 1

    # check to see that the location has the right zip code
    if zipsExist:
      try:
        thisZip = str(data['businesses'][i]['location']['postal_code']).encode('utf8')
        thisCity = data['businesses'][i]['location']['city'].encode('utf8')
        if thisZip not in zipCodes and thisCity not in cities:
          # print data['businesses'][i]['id'].encode('utf8'), "with zip: ", thisZip, "not in zipcodes\n"

          if thisZip[0] != "0" and thisZip not in zipsToIgnore:
            badZipFilename = city + "Data2/" + "badZip.txt"
            f = open(badZipFilename, "a")
            f.write(data['businesses'][i]['id'].encode('utf8')+ " " + thisCity + " " + thisZip + "\n")
            f.close()
          continue
      except:
        # print "!!!!!", data['businesses'][i]['id'].encode('utf8'), "doesn't have a zip"
        try:
          thisCity = data['businesses'][i]['location']['city'].encode('utf8')
          if thisCity not in cities:

            noZipFilename = city + "Data2/" + "noZips.txt"
            f = open(noZipFilename, "a")
            f.write(data['businesses'][i]['id'].encode('utf8') + " " + thisCity + "\n")
            f.close()

            continue
        except:
          noZipFilename = city + "Data2/" + "noZips.txt"
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

  zipfile = city + "Data2/" + city + "ZipCodes.txt"

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

def loadLocDict():
  dictFile = city + "Data2/" + city + "LocationDictionary.json"

  with open(dictFile) as f:
    locDict = json.load(f)

def main():

  #encoding: utf-8
  import sys;
  reload(sys);
  sys.setdefaultencoding('utf8');

  global locType
  global filename
  global apiHits
  global count

  loadZips()
  loadKeys()
  loadLocDict()

  start = time.time()

  for dest in destList:

    locType = dest
    filename = city + "Data2/" + dest + ".tsv"

    #add header
    fout = open(filename, "w")
    line_header = 'id'+'\t'+'name'+'\t'+'rating'+'\t'+'rating_cnt'+'\t'+'url_yelp_mobile'+'\t'+'url_yelp'+'\t'+'categories'+'\t'+'info_phone'+'\t'+'info_address'+'\t'+'info_city'+'\t'+'info_zip'+'\t'+'info_country'+'\t'+'loc_x'+'\t'+'loc_y'+'\n'
    fout.write(line_header)
    fout.close()

    print "starting quad search for location: " + locType
    
    locStart = time.time()
    # try:
    quadSearch(bb_nyc["W"], bb_nyc["E"], bb_nyc["N"], bb_nyc["S"], bb_nyc["W"], bb_nyc["E"], bb_nyc["N"], bb_nyc["S"])
    print "\nfinished", city, "with", count, "locs and", apiHits, "apiHits.\n"

    dictFile = city + "Data2/" + city + "LocationDictionary.json"

    with open(dictFile, "w") as f:
      json.dump(locDict, f)

    # except:
    #   print "Error in quad search for", locType, "with", count, "locs. Saving dictionary and exiting"
    #   dictFile = city + "Data2/" + city + "LocationDictionary.json"

    #   with open(dictFile, "w") as f:
    #     json.dump(locDict, f)

    #   return

    locEnd = time.time()

    elapsedTime = locEnd - locStart

    print "Took", str(elapsedTime), "seconds. \n"

    print "Hit the api", apiHits, "times and got", count, "locations.\n"

    # write out number of locations and api calls to stats file
    statsFilename = city + "Data2/" + "stats.txt"
    fstats = open(statsFilename, "a")
    stat = locType + " " + str(count) + " " + str(apiHits) + " " + str(elapsedTime) + "\n"
    fstats.write(stat)
    fstats.close()

    apiHits = 0
    count = 0

  end = time.time()

  print "elapsed time:", str(end-start)

if __name__ == "__main__":
    main()