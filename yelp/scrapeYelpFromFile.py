#!/usr/bin/env python
import requests
import threading
import time
import Queue
from bs4 import BeautifulSoup

readInQueue = Queue.Queue()
finishedReading = False

loc = "theater1"

def makeArrayNA(num):
  na = []
  for i in range(num):
    na.append("N/A")
  return na

def photoFunc(locId, toWriteArray):
  # get 5 photos
  photoBaseURL = "https://www.yelp.com/biz_photos/"
  photoURL = photoBaseURL + locId

  photoResponse = requests.get(photoURL)

  if photoResponse.status_code == 200:
    print("Successfully got photo HTML")

    # TODO: test this?
    photoSoup = BeautifulSoup(photoResponse.content, "html.parser")

    try:
      gridTag = photoSoup.find("ul", class_="photo-box-grid photo-box-grid--highlight photo-box-grid--small clearfix lightbox-media-parent")
      allPics = gridTag.find_all("li")
      for i in range(min(5, len(allPics))):
        picURL = allPics[i].img["src"]
        toWriteArray.append(picURL)
      if len(allPics) < 5:
        toWriteArray += makeArrayNA(5 - len(allPics))
      

    except: 
      toWriteArray += makeArrayNA(5)

    return toWriteArray

  else:
    toWriteArray += makeArrayNA(5)
    return toWriteArray



def getMoreInfo(locId, toWriteArray):
  baseURL = "https://www.yelp.com/biz/"

  url = baseURL + locId

  response = requests.get(url)


      # [id, name, rating, review count, mobile url, url, location type, phone, address,
      #  city, zip, country code, long, lat] [reviewer1 id, reviewer1 image, 
      #  review1 date, review1, reviewer2 id, reviewer2 image, review2 date, 
      #  review2, price range, hours]


  if  response.status_code == 200:
    print("Successfully got HTML for: " + locId)

    soup = BeautifulSoup(response.content, "html.parser")
    # print(soup.prettify())

    # f = open("testYelp.txt", 'a')
    # f.write(str(soup.prettify()))

    # f.close()
    smallerChunk = soup.find(class_ = "main-content-wrap main-content-wrap--full")
    
    # time to find the address:
    try:
      addressTag = smallerChunk.find("address", itemprop="address")
      addr = addressTag.find("span", itemprop="streetAddress").get_text()
    except:
      addr = "N/A"
    toWriteArray[8] = addr


    # get the first 3 highlight reviews
    try:
      highlightsList = smallerChunk.find(class_="review-highlights").find_all("li", class_="media-block media-block--12 review-highlight")
      for i in range(min(3, len(highlightsList))):
        highlightTag = highlightsList[i]
        # userId = highlightTag.img["alt"] # not always present
        userImage = highlightTag.img["src"]
        shortReview = highlightTag.find("p").get_text().lstrip().rstrip()

        # print "\n~~~~~~\n"
        # print userId
        # print userImage
        # print shortReview

        # toWriteArray.append(userId)
        toWriteArray.append(userImage)
        toWriteArray.append(shortReview)

      if(len(highlightsList) < 3):
        for i in range(3 - len(highlightsList)):
          toWriteArray += makeArrayNA(2)

    except: # there are no highlight reviews of this place
      print "there are no general reviews"
      for i in range(3):
        toWriteArray += makeArrayNA(2)


    # get the first two full reviews
    numReviewItems = 7

    try:
      fullReviewsTag = smallerChunk.find(class_="review-list")
      reviewsList = fullReviewsTag.find_all(class_="review review--with-sidebar")
      for i in range(min(2, len(reviewsList))):
        reviewTag = reviewsList[i]
        reviewerId = reviewTag.find("a", class_="user-display-name js-analytics-click").get_text().rstrip()
        reviewerPhotoURL = reviewTag.find("div", class_="photo-box pb-60s").img["src"]
        reviewerLocation = reviewTag.find("li", class_="user-location responsive-hidden-small").get_text().lstrip().rstrip()
        
        smallerReviewTag = reviewTag.find(class_="review-wrapper")

        reviewRatingStr = smallerReviewTag.find(class_="biz-rating biz-rating-large clearfix").div.div["title"]
        reviewRating = reviewRatingStr.split(" ")[0]

        reviewDate = smallerReviewTag.find("span", class_="rating-qualifier").get_text().lstrip().rstrip()
        reviewDate = " ".join(reviewDate.split())
        reviewText = smallerReviewTag.find("p").get_text()

        try: 
          largePhotoTag = smallerReviewTag.find("ul", class_="photo-box-grid clearfix js-content-expandable lightbox-media-parent")
          reviewPhotoURL = largePhotoTag.img["data-async-src"]
        except: reviewPhotoURL = "N/A"

        # print "\n######\n"
        # print reviewerId
        # print reviewerLocation
        # print reviewerPhotoURL
        # print reviewRating
        # print reviewDate
        # print reviewText
        # print reviewPhotoURL

        toWriteArray.append(reviewerId)
        toWriteArray.append(reviewerLocation)
        toWriteArray.append(reviewerPhotoURL)
        toWriteArray.append(reviewRating)
        toWriteArray.append(reviewDate)
        toWriteArray.append(reviewText)
        toWriteArray.append(reviewPhotoURL)

      
      if len(reviewsList) < 2:
        for i in range(2 - len(reviewsList)):
          toWriteArray += makeArrayNA(numReviewItems)

    except: # There are no full reviews, pad with N/A
      for i in range(2):
        toWriteArray += makeArrayNA(numReviewItems)



    # get price range, hours, biz info if availible
    try:
      sideMenu = smallerChunk.find(class_="column column-beta sidebar") 
      
      # price:
      try: 
        priceSign = sideMenu.find(class_="business-attribute price-range").get_text().rstrip().lstrip()
        priceDescription = sideMenu.find(class_="nowrap price-description").get_text().rstrip().lstrip()

        toWriteArray.append(priceSign)
        toWriteArray.append(priceDescription)

      except: toWriteArray += makeArrayNA(2)

      # hours:
      try:
        hoursTable = sideMenu.find("table").find_all("tr")
        for entry in hoursTable:
          hours = entry.td.get_text().rstrip().lstrip()
          toWriteArray.append(hours)

      except: # pad with N/A
        toWriteArray += makeArrayNA(7) # hours for 7 days

      try:

        bizInfo = sideMenu.find("ul", class_="ylist").find_all("dl")

        bizInfoStr = ""
        for item in bizInfo:
          bizInfoStr = bizInfoStr + item.dt.get_text().lstrip().rstrip() + ": " + \
                    item.dd.get_text().lstrip().rstrip() + "#"

        if bizInfoStr == "":
          bizInfoStr = "N/A"

        toWriteArray.append(bizInfoStr)

      except:
        toWriteArray.append("N/A")

    except: # pad with N/A
      # 2 prices + hours for 7 days + 1 biz info = 10 entries
      toWriteArray += makeArrayNA(2 + 7 + 1) 

    # get categories
    try:
      catList = smallerChunk.find("span", class_="category-str-list").find_all("a")
      catStr = ""
      for item in catList:
        catStr = catStr + "#" + item.get_text()


    except:
      catStr = "N/A"

    toWriteArray.append(catStr)

  return toWriteArray

def fileLoader(filename):
  global readInQueue
  global finishedReading
  fin = open(filename, 'r')
  count = 0
  for line in fin:
    if count == 0:
      count += 1
      continue
    tempList = line.split('\t')
    newArray = []
    for item in tempList:
      newArray.append(item.rstrip())
    readInQueue.put(newArray)
    count += 1

  print "finished reading in: " + str(count) + " lines. "
  finishedReading = True

def main():

  global loc

  #encoding: utf-8
  import sys;
  reload(sys);
  sys.setdefaultencoding('utf8');

  global finishedReading

  # toWriteArray = ["id", "name", "rating", "reviewCount", "mobileUrl", "url",
  #                 "locationType", "phone", "address", "city", "zip", "countryCode",
  #                 "long", "lat"]


  # r1 = "joe-and-the-juice-san-francisco-6"
  # r2 = "paradise-valley-conservation-area-woodinville"

  filename = loc + ".tsv"

  writingThread = threading.Thread(target=fileLoader, args=(filename,))
  writingThread.setDaemon(True)
  writingThread.start()

  fout = open(loc + "_final.tsv", "w")
  line_header = 'id'+'|'+'name'+'|'+'rating'+'|'+'rating_cnt'+'|'+'url_yelp_mobile'+'|' \
                +'url_yelp'+'|'+'categories'+'|'+'info_phone'+'|'+'info_address' \
                +'|'+'info_city'+'|'+'info_zip'+'|'+'info_country'+'|'+'loc_x' \
                +'|'+'loc_y'+'|'+'pic1'+'|'+'pic2'+'|'+'pic3'+'|'+ 'pic4'\
                +'|'+'pic5'+'|'+'highlight1Img'+'|'+'highlight1Txt' \
                +'|'+'highlight2Img'+'|'+'highlight2Txt'+'|'+'highlight3Img' \
                +'|'+'highlight3Txt'+'|'+'fullRev1Id'+'|'+'fullRev1Loc' \
                +'|'+'fullRev1UsrImg'+'|'+'fullRev1Rating'+'|'+'fullRev1Date'+'|'+ \
                'fullRev1Txt'+'|'+'fullRev1Img'+'|'+'fullRev2Id'+'|'+'fullRev2Loc' \
                +'|'+'fullRev2UsrImg'+'|'+'fullRev2Rating'+'|'+'fullRev2Date'+'|'+ \
                'fullRev2Txt'+'|'+'fullRev2Img'+'|'+'fullRev3Id'+'|'+'fullRev3Loc' \
                +'|'+'fullRev3UsrImg'+'|'+'fullRev3Rating'+'|'+'fullRev3Date'+'|'+ \
                'fullRev1Txt'+'|'+'fullRev1Img'+'|'+'priceSign'+'|'+'priceDesc'+'|'+ \
                'monHrs'+'|'+'tuesHrs'+'|'+'wedHrs'+'|'+'thursHrs'+'|'+'friHrs'+'|'+ \
                'satHrs'+'|'+'sunHrs'+'|'+'extraDetails'+'|'+'completeCategories'+'\n'
  fout.write(line_header)
  fout.close()


  fout = open(loc + "_final.tsv", "a")
  count = 0

  while True:
    if readInQueue.empty() and finishedReading:
      break

    if readInQueue.empty():
      time.sleep(5)
    else:
      count += 1

      toWriteArray = readInQueue.get()
      locId = toWriteArray[0]
      toWriteArray = photoFunc(locId, toWriteArray)
      toWriteArray = getMoreInfo(locId, toWriteArray)
      
      line = '||'+'|'.join(toWriteArray) + '\n'
      fout.write(line)
      print "~~~ Finished writing: " + str(count)

  fout.close()  

      # TODO: FIX THE ORDER HERE::::

      # [id, name, rating, reviewCount, mobileURL, url, locationType, phone, address,
      #  city, zip, countryCode, long, lat] [pic1, pic2, pic3, pic4, pic5, genRev1 id,
      #  highlight1 image, highlight1 review, highlight2 id, highlight2 image, highlight2 review,
      #  highlight3 id, highlight3 image, highlight3 review, reviewer1 id, reviewer1 image, 
      #
      #  review1 date, review1, reviewer2 id, reviewer2 image, review2 date, 
      #  review2, price range, hours]

  writingThread.join()

if __name__ == '__main__':
  main() 