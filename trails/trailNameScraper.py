#!/usr/bin/env python3
from __future__ import print_function
import requests
import time
from bs4 import BeautifulSoup


def getTrailName(url, f):

    response = requests.get(url)

    if  response.status_code == 200:

        soup = BeautifulSoup(response.content, "html.parser")
        topHeader = soup.find(id="hike-top")
        trailName = topHeader.h1.get_text()
        print(trailName+"\n")

        f.write(trailName+"\n")

def main():

    hikingGuideURLBase = "http://www.wta.org/go-outside/hikes?b_start:int="
    resultInt = 2850
    trailCount = 0

    f = open('trailNames.txt', 'a')

    start = time.time()

    while(True):

        response = requests.get(hikingGuideURLBase+str(resultInt))

        if  response.status_code == 200:

            soup = BeautifulSoup(response.content, "html.parser")

            resultList = soup.find(id="search-result-listing")

            links = resultList.find_all("a")

            if len(links) == 0:
                print("Finished getting trail data.")
                break

            for i in range(len(links)):

                link = links[i]['href']
                if i != 0 and link == links[i-1]['href']:
                    continue

                getTrailName(link, f)
                trailCount += 1
                # print(str(trailCount)+ " resInt: " + str(resultInt))

            resultInt += 30
            print(str(trailCount) + " Time elapsed: " + str(time.time()-start))

        else: 
            print("Failed to get HTML")
            break

    end = time.time()   
    elapsedTime = end - start
    f.close()

    print("Got information for [" + str(trailCount) + "] trails.")
    print("It took " + str(elapsedTime) + " seconds")

if __name__ == '__main__':
    main() 