#!/usr/bin/python

#import xml.etree.ElementTree as et
import xml.etree.cElementTree as ET
#import lxml.etree as et
import sys, os, string, re

lastAlbum = 0

def parseSubalbum(subalbumTree):
	global lastAlbum
	
	subalbum = dict()
	
	subalbum['name'] = subalbumTree.find('name').text
	subalbum['desc'] = subalbumTree.find('description').text
	thumb = subalbumTree.find('thumb')
	if thumb != None:
		subalbum['thumb'] = thumb.get("path")
		subalbum['dir'] = re.search('[^/]*/([^_]*).*', subalbum['thumb']).group(1)
		lastAlbum = int(subalbum['dir'])
	else:
		lastAlbum += 1
		subalbum['dir'] = str(lastAlbum)
		
	print "    " + subalbum['name'] + " in dir " + subalbum['dir']
	
	photos = dict()
	for photoTree in subalbumTree.findall('photo'):
		desc = photoTree.find('description').text
		photos[photoTree.find('image').find('md5').text] = desc
		if desc != None and len(desc) != 0:
			print "        " + desc
		
	subalbum['photos'] = photos
	
	return subalbum


# parse cmdline
if len(sys.argv) < 3:
	print "not enough parameters"
	print "usage: " + sys.argv[0] + " <source dir> <target dir>"
	exit(1)

source = sys.argv[1]
target = sys.argv[2]

# load tree
tree = ET.parse(source + '/Album.xml')
albumTree = tree.getroot()

# basic album info
albumName = albumTree.find('name').text
albumDesc = albumTree.find('description').text
albumThumb = albumTree.find('thumb')
if albumThumb != None: 
	albumThumb = albumThumb.get('path')

print albumName

# iterate albums
albums = dict()

for subalbum in albumTree.findall('subalbum'):
	parseSubalbum(subalbum)


#os.mkdir(target + albumName.translate(string.maketrans(" ", "_")))

