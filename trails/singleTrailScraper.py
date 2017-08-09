#!/usr/bin/env python3

# Amy Han - Summer 2017 - KIXLAB
# Uses Selenium to scrape data for one trail off the WTA hiking page 

from __future__ import print_function
import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver

def main():

  startTime = time.time()

  baseURL = "http://www.wta.org/go-hiking/hikes/"
  trail1 = "skyline-divide"
  trail2 = "rainbow-creek-trail"
  trail3 = "summer-blossom"
  trail4 = "big-cedar-tree"
  trail5 = "delate-meadow"
  trail6 = "shell-rock"
  trail7 = "cascade-falls"

  url = baseURL + trail7

  driverStart = time.time()

  response = requests.get(url)
  soup = BeautifulSoup(response.content, "html.parser")
  # driver = webdriver.PhantomJS()
  # driver.get(url)
  # driverEnd = time.time()

  # print("It took driver: " + str(driverEnd - driverStart))

  # html = driver.page_source

  # soup = BeautifulSoup(html, "html.parser")
  # print(soup.prettify())

  topHeader = soup.find(id="hike-top")

  trailName = topHeader.h1.get_text()

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
  description = description.encode("ascii", "replace")

  try:
    drivingDirections = soup.find(id="driving-directions").get_text().rstrip("\n")[20:]
    drivingDirections = drivingDirections.encode("ascii", "replace")
  except:
    drivingDirections = "N/A"

  try:
    imgSrc = soup.find(id="hike-carousel").find(class_ = "photo-caption-wrapper")["href"]
  except:
    imgSrc = "N/A"  

  try:
    reportElem = driver.find_element_by_id("trip-reports")

    htmlReport = driver.execute_script("return arguments[0].innerHTML;", reportElem)

    soupReport = BeautifulSoup(htmlReport, "html.parser").find(class_="item")

    reportAuthor = soupReport.find(class_= "CreatorInfo").span.a.get_text().strip("\n")
    reportDate = soupReport.find(class_ = "elapsed-time").get_text()
    try:
      reportBeware = " ".join(soupReport.find(class_ = "trail-issues").get_text().split())
      reportBeware = reportBeware.encode("ascii", "replace")
    except:
      reportBeware = "N/A"
    reportText = soupReport.find(class_ = "report-text").div.div.get_text()
    reportText = reportText.encode("ascii", "replace")
  except:
    reportAuthor = reportDate = reportBeware = reportText = "N/A"
  
  endTime = time.time()

  print("Trail Name:", trailName)
  print("Region:", region)
  print("Required Pass/Entry Fee:", fee)
  print("Rating:", rating)
  print("Number of Voters:", numVoters)
  print("Distance:", distance)

  if elevationGain:
    print("Elevation Gain:", elevationGain, "ft.")
  elif highestPoint:
    print("Highest Point:", highestPoint)
  else:
    print("No elevation information available")
  
  print("Description:", description)
  print ("Driving Instructions:", drivingDirections)

  print("Author name: ", reportAuthor)
  print("Report Date: ", reportDate)
  print(reportBeware)
  print("Report: ", reportText)

  print(str(endTime - startTime))

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
  trailInfoArray.append(imgSrc)
  trailInfoArray.append(reportAuthor)
  trailInfoArray.append(reportDate)
  trailInfoArray.append(reportBeware)
  trailInfoArray.append(reportText)
  
  fileName = "trail2.txt"
  f = open(fileName, 'a')
  
  for i in range(len(trailInfoArray)):
    if i == 0:
      f.write("||")
    if i == (len(trailInfoArray) - 1):
      f.write(trailInfoArray[i])
    else:
      f.write(trailInfoArray[i] + "|")
  f.write("\n")

if __name__ == '__main__':
  main() 