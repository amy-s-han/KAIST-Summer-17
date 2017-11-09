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
import sqlite3 as lite

city = "detroit"
locType = ""
count = 0
filename = ""
apiHits = 0
db = None
conn = None

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

auth = yelp_auth1

destList = ["newamerican", "tradamerican", "chinese", "french", "indpak", "italian", "japanese", "mexican",
            "mediterranean", "thai", "vegan", "vegetarian", "hotdogs", "cafes", "coffee", "coffeeroasteries", "bubbletea",
            "tea", "juicebars", "desserts", "icecream", "gelato", "landmarks", "museums", "aquariums", "parks",
            "beaches", "amusementparks", "zoos", "theater", "artsandcrafts", "bookstores", "cosmetics", 
            "deptstores", "drugstores", "electronics", "fashion", "jewelry", "servicestations", "grocery", 
            "wholesale_stores", "intlgrocery", "bars", "beergardens", "jazzandblues", "karaoke", "comedyclubs", 
            "musicvenues", "danceclubs", "elementaryschools", "highschools", "montessori", "preschools", "privateschools",
            "religiousschools", "specialed", "specialtyschools", "postoffices", "libraries", "emergencymedicine",
            "hospitals"]


#  = {"S":, "W":, "N":, "E": }
   

searched = []



# # inland empire
# listOfDests = [
# {"S": 34.050113, "W": -117.424317, "N": 34.24764, "E": -117.164972},
# {"S": 33.872517, "W":-117.523882, "N":34.019514, "E": -117.275174},
# {"S": 34.033412, "W":-117.524483, "N":34.184159, "E": -117.401056},
# {"S": 33.859073, "W":-117.296775, "N":33.984516, "E": -117.088077},
# {"S": 34.076527, "W":-117.636887, "N":34.17138, "E": -117.478789},
# {"S": 33.975213, "W": -117.683588, "N":34.09281, "E": -117.524278},
# {"S": 33.80272, "W": -117.673749, "N":33.91596, "E": -117.483803},
# {"S": 34.435648, "W": -117.468974, "N":34.644937, "E": -117.253879},
# {"S": 33.447929, "W": -117.190267, "N":33.554813, "E": -117.054222},
# {"S": 33.513363, "W": -117.278596, "N":33.641557, "E": -117.118285}
# ]

# San Bernardino = {"S": 34.050113, "W": -117.424317, "N": 34.24764, "E": -117.164972}
# Riverside = {"S": 33.872517, "W":-117.523882, "N":34.019514, "E": -117.275174}
# Fontana = {"S": 34.033412, "W":-117.524483, "N":34.184159, "E": -117.401056}
# Moreno Valley = {"S": 33.859073, "W":-117.296775, "N":33.984516, "E": -117.088077}
# Rancho Cucamonga = {"S": 34.076527, "W":-117.636887, "N":34.17138, "E": -117.478789}
# Ontario = {"S": 33.975213, "W": -117.683588, "N":34.09281, "E": -117.524278}
# Corona = {"S": 33.80272, "W": -117.673749, "N":33.91596, "E": -117.483803}
# Victorville = {"S": 34.435648, "W": -117.468974, "N":34.644937, "E": -117.253879}
# Temecula = {"S": 33.447929, "W": -117.190267, "N":33.554813, "E": -117.054222}
# Murrieta = {"S": 33.513363, "W": -117.278596, "N":33.641557, "E": -117.118285}


# # detroit
listOfDests = [
{"S":42.255192, "W": -83.287959, "N":42.45023, "E": -82.910451},
{"S":43.027668, "W": -83.36252, "N":43.069267, "E": -83.284834},
{"S":42.423904, "W": -84.158189, "N":42.783263, "E": -83.664808},
{"S":42.627811, "W": -82.976908, "N":42.718133, "E":  -82.85613},
{"S":42.709529, "W": -83.217454, "N":42.80055, "E": -83.095436},
{"S":42.806802, "W": -82.515983, "N":42.857952, "E": -82.471452},
{"S":42.265714, "W": -83.427436, "N":42.289186, "E":  -83.34807}
]

# Detroit = {"S":42.255192, "W": -83.287959, "N":42.45023, "E": -82.910451}
# Lapeer = {"S":43.027668, "W": -83.36252, "N":43.069267, "E": -83.284834}
# Livingston = {"S":42.423904, "W": -84.158189, "N":42.783263, "E": -83.664808}
# Macomb = {"S":42.627811, "W": -82.976908, "N":42.718133, "E":  -82.85613}
# Oakland = {"S":42.709529, "W": -83.217454, "N":42.80055, "E": -83.095436}
# St. Clair = {"S":42.806802, "W": -82.515983, "N":42.857952, "E": -82.471452}
# Wayne = {"S":42.265714, "W": -83.427436, "N":42.289186, "E":  -83.34807}




     
bb = listOfDests[0]




# g_box ={ # geographical bounding box for Greater Seattle Area
#   "S":47.395, #SW latitude : 47.3956
#   "W":-122.440, #SW longitude : -122.4379
#   "N":47.859, #NE latitude : 47.8591
#   "E":-122.075 #NE longitude : -122.0791
# }

# g_box1 ={ # geographical bounding box for Staten Island
#   "S":40.495979, #SW latitude
#   "W":-74.256341, #SW longitude 
#   "N":40.650187, #NE latitude
#   "E":-74.051666 #NE longitude 
# }

# g_box2 ={ # geographical bounding box for Bronx, Brooklyn and Manhattan
#   "S":40.530056, #SW latitude
#   "W":-74.041617, #SW longitude 
#   "N":40.907521, #NE latitude
#   "E":-73.685714 #NE longitude 
# }

# bb_nyc ={ # geographical bounding box for NYC
#   "S":40.477399, #SW latitude
#   "W":-74.25909, #SW longitude 
#   "N":40.917577, #NE latitude
#   "E":-73.700272 #NE longitude 
# }

def catListJoiner(catList):
  catString = ""

  for cat in catList:
    catString = catString + cat[1] + "#"

  return catString

def getBusinessData(data, W, E, N, S):
  global count
  global duplicateCounter

  startCount = count

  #Print out the result
  for i in range(len(data["businesses"])):
    # check if we already found this location
    db.execute("SELECT COUNT(*) FROM " + city + " WHERE name='" + data['businesses'][i]['id'].encode('utf8') + "'")

    if db.fetchone()[0]: 
      print "*** DB already had: ", data['businesses'][i]['id'].encode('utf8')
      # db.execute("DELETE FROM " + city + " WHERE name='" + data['businesses'][i]['id'].encode('utf8') + "'")
      # print "...deleted"
      continue

    count = count + 1

    db.execute("INSERT INTO " + city + " VALUES('" + data['businesses'][i]['id'].encode('utf8') + "')")
    conn.commit()

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
      try: each.append((catListJoiner(data['businesses'][i]['categories'])).encode('utf8'))
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

      print ".",
      if count%20 == 0: 
        print count,

      sys.stdout.flush()
      # print "[" + str(count) + "] Added "+ data['businesses'][i]['id'].encode('utf8')
  
  # print "Sum: " + str(count - startCount) + " points were added."  


def quadSearch(xStart, xEnd, yStart, yEnd, W, E, N, S):
  global apiHits

  # print xStart, xEnd, yStart, yEnd

  # check if we have already searched this bounding box before
  for loc in searched:
    if (N <= loc["N"] and E <= loc["E"] and S >= loc["S"] and W >= loc["W"]):
      print "already did this box"
      return

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
  try:
    request = session.get("http://api.yelp.com/v2/search", params=params)
  except:
    try:
      request = session.get("http://api.yelp.com/v2/search", params=params)
    except:
      print "!"

      errorLog = open("error.txt", "a")
      errorLog.write("W: " + str(W) + "E: " + str(E) + "N: " + str(N) + "S: " + str(S))
      errorLog.close()
      return
  data = {}

  try:
    data = request.json()

  except:
    try:
      print "~"
      dataform = str(request).decode('utf-8').strip("'<>() ").replace('\'', '\"','\0', '')
      data = json.loads(dataform)
    except:
      print "!"

      errorLog = open("error.txt", "a")
      errorLog.write(str(request))
      errorLog.close()


      return

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
  reload(sys);
  sys.setdefaultencoding('utf8');

  global locType
  global filename
  global apiHits
  global count
  global conn
  global db
  global listOfDests
  global destList
  global bb
  global searched

  loadKeys()

  conn = lite.connect(city + '.db')
  db = conn.cursor()

  db.execute("CREATE TABLE IF NOT EXISTS " + city + "(Name TEXT)")

  start = time.time()

  for i in range(len(listOfDests)):
    bb = listOfDests[i]
    searched = listOfDests[0:i]

    for dest in destList:

      locType = dest
      filename = city + "Data/" + dest + ".tsv"

      #add header

      if not os.path.isfile(filename):
        fout = open(filename, "w")
        line_header = 'id'+'\t'+'name'+'\t'+'rating'+'\t'+'rating_cnt'+'\t'+'url_yelp_mobile'+'\t'+'url_yelp'+'\t'+'categories'+'\t'+'info_phone'+'\t'+'info_address'+'\t'+'info_city'+'\t'+'info_zip'+'\t'+'info_country'+'\t'+'loc_x'+'\t'+'loc_y'+'\n'
        fout.write(line_header)
        fout.close()

      # fout = open(filename, "w")
      # line_header = 'id'+'\t'+'name'+'\t'+'rating'+'\t'+'rating_cnt'+'\t'+'url_yelp_mobile'+'\t'+'url_yelp'+'\t'+'categories'+'\t'+'info_phone'+'\t'+'info_address'+'\t'+'info_city'+'\t'+'info_zip'+'\t'+'info_country'+'\t'+'loc_x'+'\t'+'loc_y'+'\n'
      # fout.write(line_header)
      # fout.close()

      print "starting quad search for location: " + locType
      
      locStart = time.time()
      # try:
      quadSearch(bb["W"], bb["E"], bb["N"], bb["S"], bb["W"], bb["E"], bb["N"], bb["S"])
      print "\nfinished", city, "with", count, "locs and", apiHits, "apiHits.\n"
      
      locEnd = time.time()

      elapsedTime = locEnd - locStart

      print "Took", str(elapsedTime), "seconds, which is", str(elapsedTime/60.0), "minutes. \n"


      conn.commit()

      # write out number of locations and api calls to stats file
      statsFilename = city + "Data/" + "stats.txt"
      fstats = open(statsFilename, "a")
      stat = locType + " " + str(count) + " " + str(apiHits) + " " + str(elapsedTime) + "\n"
      fstats.write(stat)
      fstats.close()

      apiHits = 0
      count = 0


  end = time.time()

  conn.commit()
  conn.close()

  totalTime = end-start
  print "elapsed time:", str(totalTime), "seconds, which is", str(totalTime/60.0), "minutes. \n"

  statsFilename = city + "Data/" + "stats.txt"
  fstats = open(statsFilename, "a")
  stat = "\n\n\n~~~ Total time elapsed for metropolitan area: " + str(totalTime) + "\n"
  fstats.write(stat)
  fstats.close()

if __name__ == "__main__":
    main()