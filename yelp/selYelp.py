#!/usr/bin/env python

# Amy Han - Summer 2017 - KIXLAB
# Uses Selenium to get information on one location from Yelp
# Wrote this to quickly test out and learn Selenium -> that's why everything is in main!

import requests
import time

from bs4 import BeautifulSoup

def makeArrayNA(num):
  na = []
  for i in range(num):
    na.append("N/A")
  return na


def main():

  #encoding: utf-8
  import sys;
  reload(sys);
  sys.setdefaultencoding('utf8');

  toWriteArray = ["id", "name", "rating", "reviewCount", "mobileUrl", "url",
                  "locationType", "phone", "address", "city", "zip", "countryCode",
                  "long", "lat"]

  baseURL = "https://www.yelp.com/biz/"
  photoBaseURL = "https://www.yelp.com/biz_photos/"

  r1 = "joe-and-the-juice-san-francisco-6"
  r2 = "paradise-valley-conservation-area-woodinville"
  r3 = "kilbourne-park-seattle"

  # TODO: Make into functions -> photo func and main page func

  # get 5 photos
  photoURL = photoBaseURL + r1
  url = baseURL + r1

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



  response = requests.get(url)


      # [id, name, rating, review count, mobile url, url, location type, phone, address,
      #  city, zip, country code, long, lat] [reviewer1 id, reviewer1 image, 
      #  review1 date, review1, reviewer2 id, reviewer2 image, review2 date, 
      #  review2, price range, hours]


  if  response.status_code == 200:
    print("Successfully got HTML")

    soup = BeautifulSoup(response.content, "html.parser")
    # print(soup.prettify())

    # f = open("testYelp.txt", 'a')
    # f.write(str(soup.prettify()))

    # f.close()
    smallerChunk = soup.find(class_ = "main-content-wrap main-content-wrap--full")
    
    # time to find the address:
    addressTag = smallerChunk.find("address", itemprop="address")
    addr = addressTag.find("span", itemprop="streetAddress").get_text()
    toWriteArray[8] = addr


    # get the first 3 general reviews
    try:
      genReviewsList = smallerChunk.find(class_="review-highlights").find_all("li", class_="media-block media-block--12 review-highlight")
      print 
      for i in range(min(3, len(genReviewsList))):
        genReviewTag = genReviewsList[i]
        userId = genReviewTag.img["alt"]
        userImage = genReviewTag.img["src"]
        shortReview = genReviewTag.find("p").get_text().lstrip().rstrip()

        # print "\n~~~~~~\n"
        # print userId
        # print userImage
        # print shortReview

        toWriteArray.append(userId)
        toWriteArray.append(userImage)
        toWriteArray.append(shortReview)

      if(len(genReviewsList) < 3):
        for i in range(3 - len(genReviewsList)):
          toWriteArray += makeArrayNA(3)

    except: # there are no general reviews of this place
      print "there are no general reviews"
      for i in range(3):
        toWriteArray += makeArrayNA(3)


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
        reviewText = smallerReviewTag.find("p").get_text()

        try: 
          largePhotoTag = smallerReviewTag.find("ul", class_="photo-box-grid clearfix js-content-expandable lightbox-media-parent")
          reviewPhotoURL = largePhotoTag.img["data-async-src"]
        except: reviewPhotoURL = "N\A"

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

        toWriteArray.append(bizInfoStr)

      except:
        toWriteArray.append("N/A")

    except: # pad with N/A
      # 2 prices + hours for 7 days + 1 biz info = 10 entries
      toWriteArray += makeArrayNA(2 + 7 + 1) 

    for thing in toWriteArray:
      print thing

      # TODO: FIX THE ORDER HERE::::

      # [id, name, rating, reviewCount, mobileURL, url, locationType, phone, address,
      #  city, zip, countryCode, long, lat] [pic1, pic2, pic3, pic4, pic5, genRev1 id,
      #  genRev1 image, genRev1 review, genRev2 id, genRev2 image, genRev2 review,
      #  genRev3 id, genRev3 image, genRev3 review, reviewer1 id, reviewer1 image, 
      #
      #  review1 date, review1, reviewer2 id, reviewer2 image, review2 date, 
      #  review2, price range, hours]



if __name__ == '__main__':
  main() 