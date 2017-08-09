#!/usr/bin/env python

# Amy Han - Summer 2017 - KIXLAB
# Identifies non-alphanumeric characters that causes problems later on

def main():

  #encoding: utf-8
  import sys;
  reload(sys);
  sys.setdefaultencoding('utf8');

  safeChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-'

  locs = ["amusementparks", "aquariums", "artsandcrafts", "bars", "beaches", 
  		  "beergardens", "bookstores", "bubbletea", "cafes", "chinese", "coffee",
  		  "coffeeroasteries", "comedyclubs", "cosmetics", "danceclubs", "deptstores",
  		  "desserts", "drugstores", "electronics", "fashion", "french", "gelato", 
  		  "grocery", "icecream", "indpak", "italian", "japanese", "jazzandblues",
  		  "jewelry", "juicebars", "karaoke", "landmarks", "mediterranean", "mexican",
  		  "museums", "musicvenues", "newamerican", "parks", "tea", "thai", "theater",
  		  "tradamerican", "vegan", "vegetarian", "zoos"]

  print len(locs)

  for loc in locs:
	  filename = loc + "_final.tsv"
	  print filename

	  fout = open(loc + "_final.tsv", "r")

	  fout.readline()

	  badCounter = 0

	  for line in fout.readlines():

	  	for i in range(2, len(line)):
	  		if line[i] == "|":
	  			# print "not bad: " + line[2:i]
	  			break
	  		if safeChars.find(line[i]) == -1: #if there is a bad char
	  			print "bad: " + line [2:i+10]
	  			print "bad char: " + line[i]
	  			badCounter += 1

	  fout.close()  
	  
	  if badCounter != 0:
	  	print "Bad things left: " + str(badCounter) + "\n"


if __name__ == '__main__':
  main() 