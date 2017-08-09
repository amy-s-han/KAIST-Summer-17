#!/usr/bin/env python3

# Amy Han - Summer 2017 - KIXLAB
# Uses Selenium and crawls through the entire WTA hiking list.
# Scrapes all the relevant data into a txt file.

# If the program gets interrupted, you can start again from where it left
# off by setting startNum to the page number that the program stopped
# on. You may have to manually delete any entries for that page that were
# already written to file so that there are no duplicate entries

# Note: If anyone writes a new review while the crawler is running, you risk
# missing that trail (because it gets bumped to the first page and the crawler
# traverses the pages in order) or you might end up with duplicate entries. 

from __future__ import print_function
import Queue
import requests
import threading
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

toWriteQueue = Queue.Queue()
notDoneGettingData = True

def getPageInfo(link):

  notDone = True
  while(notDone):
    try:
      print("*** here getting driver for: ", link)
      driver = webdriver.PhantomJS()
      driver.get(link)

      html = driver.page_source

      soup = BeautifulSoup(html, "html.parser")
      # print(soup.prettify())


      topHeader = soup.find(id="hike-top")

      trailName = topHeader.h1.get_text()
      notDone = False
      break
    except:
      print("!!!Something went wrong in getting webpage")
      driver.close()


  trailStats = topHeader.find_all("div", class_="hike-stat")
  assert len(trailStats) is 4
  
  try:
    regionTag = trailStats[0]
    region = regionTag.div.get_text()
  except:
    region = "N/A"

  try:
    fee = topHeader.find("div", class_="alerts-and-conditions").h4.next_sibling.get_text()
  except:
    fee = "N/A"

  ratingString = topHeader.find("div", class_="current-rating").get_text()
  rating = ratingString.split()[0]

  numVotersString = topHeader.find("div", class_="rating-count").get_text()
  numVoters = numVotersString.strip("()").split()[0]
  
  try:
    distance = topHeader.find(id="distance").get_text().strip('\n')
  except:
    distance = "N/A"

  elevationTag = trailStats[2]

  try:
    allDivs = elevationTag.find_all("div")

    if len(allDivs) == 2:
      temp = allDivs[0].get_text().strip("\n").split()
      elevationGain = temp[1]

      temp = allDivs[1].get_text().strip("\n").split()
      highestPoint = temp[2]

    else:
      elevationGain = "N/A"

      temp = allDivs[1].get_text().strip("\n").split()
      highestPoint = temp[2]

  except:
    elevationGain = "N/A"
    highestPoint = "N/A"
  
  
  description = soup.find(id="hike-body-text").get_text().rstrip("\n")
  description = description#.encode("ascii", "replace")

  try:
    drivingDirections = soup.find(id="driving-directions").get_text().rstrip("\n")[20:]
    drivingDirections = drivingDirections#.encode("ascii", "replace")
  except:
    drivingDirections = "N/A"

  try:
    coordsTag = soup.find(class_ = "latlong").find_all("span")
    coords = str(coordsTag[0].get_text()) + " " + str(coordsTag[1].get_text())
  except:
    coords = "N/A"

  try:
    imgSrc = soup.find(id="hike-carousel").find(class_ = "photo-caption-wrapper")["href"]
  except:
    imgSrc = "N/A"  

  try:
    reportElem = driver.find_element_by_id("trip-reports")

    htmlReport = driver.execute_script("return arguments[0].innerHTML;", reportElem)

    soupReport = BeautifulSoup(htmlReport, "html.parser").find(class_="item")

    reportAuthor = soupReport.find(class_= "CreatorInfo").span.a.get_text().strip("\n")#.encode("ascii", "replace")
    reportDate = soupReport.find(class_ = "elapsed-time").get_text()
    
    try:
      reportBeware = " ".join(soupReport.find(class_ = "trail-issues").get_text().split())
      reportBeware = reportBeware#.encode("ascii", "replace")
    except:
      reportBeware = "N/A"
    
    reportText = soupReport.find(class_ = "report-text").div.div.get_text()
    reportText = reportText#.encode("ascii", "replace")
  except:
    reportAuthor = reportDate = reportBeware = reportText = "N/A"
  
  driver.close()

  trailInfoArray = []
  trailInfoArray.append(trailName)
  trailInfoArray.append(region)
  trailInfoArray.append(fee)
  trailInfoArray.append(rating)
  trailInfoArray.append(numVoters)
  trailInfoArray.append(distance)
  trailInfoArray.append(elevationGain)
  trailInfoArray.append(highestPoint)
  trailInfoArray.append(description)
  trailInfoArray.append(drivingDirections)
  trailInfoArray.append(coords)
  trailInfoArray.append(imgSrc)
  trailInfoArray.append(reportAuthor)
  trailInfoArray.append(reportDate)
  trailInfoArray.append(reportBeware)
  trailInfoArray.append(reportText)

  global toWriteQueue
  toWriteQueue.put(trailInfoArray)


def getData():

  hikingGuideURLBase = "http://www.wta.org/go-outside/hikes?b_start:int="
  trailCount = 0
  startNum = 0
  start = time.time()

  while(True):

    response = requests.get(hikingGuideURLBase+str(startNum))

    if  response.status_code == 200:
      # print("Successfully got HTML")

      soup = BeautifulSoup(response.content, "html.parser")

      resultList = soup.find(id="search-result-listing")

      links = resultList.find_all("a")

      if len(links) == 0:
        print("Finished getting trail data.")
        break

      for i in range(len(links)):
        # if i < 17:
        #   continue

        link = links[i]['href']
        if i != 0 and link == links[i-1]['href']:
          continue

        getPageInfo(link)
        trailCount += 1
        print("*** Got link: ", link)
      
      print("*** Finished page: ", str(startNum))
      startNum += 30

    else: 
      print("Failed to get HTML")
      break

  end = time.time() 
  elapsedTime = end - start

  print("It took " + str(elapsedTime) + " seconds to get info for [" + str(trailCount) + "] trails.\n")

def writingFunc(fileName):
  global toWriteQueue
  global notDoneGettingData

  print("~~~ Writing thread starting...\n")
  f = open(fileName, 'a')

  while(notDoneGettingData):
    print("~~~ checking")
    if not toWriteQueue.empty(): 
      toWriteArray = toWriteQueue.get() 
      print("~~~ Writing: ", toWriteArray[0])

      for i in range(len(toWriteArray)):
        if i == 0:
          f.write("||")
        if i == (len(toWriteArray) - 1):
          f.write(toWriteArray[i])
        else:
          f.write(toWriteArray[i] + "|")
      f.write("\n")
    else:
      time.sleep(8)

  print("Writing thread finished.")
  f.close()

def main():

  #encoding: utf-8
  import sys;
  reload(sys);
  sys.setdefaultencoding('utf8');

  global notDoneGettingData
  notDoneGettingData = True
  fileName = "trail5.txt"

  writerThread = threading.Thread(target=writingFunc, args=(fileName,))
  writerThread.setDaemon(True)
  writerThread.start()

  getData()

  while True:
    if toWriteQueue.empty():
      notDoneGettingData = False
      break


  writerThread.join()


if __name__ == '__main__':
  main() 