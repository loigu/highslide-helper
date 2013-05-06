#!/usr/bin/python

import xml.etree.cElementTree as ET
import sys, os, string, re, shutil, hashlib, fnmatch

# TODO: nicer block schema (div around links, block them, center them)
# TODO: fix the first in thumbstrip
# TODO: bigger thumbstrip

# TODO: customize this
highslidePath = '../../../highslide'

THUMB_SIZE="144x144"

def parseDir(directory, path):
	subalbum = {}
	subalbum['name'] = directory.translate(string.maketrans("_", " "))
	subalbum['dir'] = directory
	print("parsing dir " + directory)
	
	thumbDir = os.path.join(path, 'thumbs')
	if not os.path.isdir(thumbDir):
		os.makedirs(thumbDir)
	
	photos = []
	for file in fnmatch.filter(os.listdir(path), "*.[Jj][Pp][Gg]"):
		thumb = os.path.join(thumbDir, file)
		if not os.path.isfile(thumb):
			os.system("convert " + os.path.join(path, file) + " -resize " + THUMB_SIZE + " " + thumb)
		if file == "thumb.jpg":
			continue
		photos.append({'name' : file})
		
	subalbum['photos'] = photos
	
	if os.path.isfile(os.path.join(path, "thumb.jpg")):
		subalbum['thumb'] = 'thumb.jpg'
	else:
		subalbum['thumb'] = photos[0]['name']
	
	return subalbum


def parseDirs(target):
	subalbums = []
	for dirname in os.listdir(target):
		dirPath = os.path.join(target, dirname)
		if os.path.isdir(dirPath) and not dirname.startswith('.'):
			subalbums.append(parseDir(dirname, dirPath))
	
	return subalbums

def generateSubalbum(f, subalbum):
	global source
	global target
	subalbumDirName = subalbum['name'].translate(string.maketrans(" .", "__"), "'\"")
	thumbsDirName = os.path.join(subalbumDirName, "thumbs")
	thumbsDir = os.path.join(target, thumbsDirName)
	
	if not os.path.isdir(thumbsDir):
		os.makedirs(thumbsDir)
	
	f.write('<span class="highslide-gallery">\n')
	
	subalbumThumbThumb =  os.path.join(thumbsDirName, subalbum['thumb'])
	subalbumThumb = os.path.join(subalbumDirName, subalbum['thumb'])
	
	group = ", { thumbnailId: '" + subalbumThumb + "', slideshowGroup: '" + subalbum['dir'] + "' }"
	
	f.write('\t<span class="subalbum-link">\n')
	
	# thumbnail with link to first photo & album name
	f.write('\t<a class="highslide" id="' + subalbumThumb + '" href="' + subalbumThumb + '" onclick="return hs.expand(this' + group + ')">\n')
	f.write('\t\t<img src="' + subalbumThumbThumb + '" title="Click to view this album"/>\n\t</a>\n')
	
	# name (desc) if there is some
	f.write('\t<div class="subalbum-name">' + subalbum['name'])
	f.write('</div>\n')
	f.write('\t</span>\n\n') # subalbum-link
	
	# append hidden container
	f.write('\t<span class="hidden-container">\n')
	
	for photo in subalbum['photos']:
		#TODO: generate thumbs?
		f.write('\t\t<span class="thumb"><a id="' + subalbumDirName + '-' + photo['name'] + '" class="highslide" href="' + os.path.join(subalbumDirName, photo['name']) + '" onclick="return hs.expand(this' + group + ')">\n')
		f.write("\t\t\t<img src='" + os.path.join(thumbsDirName, photo['name']) + "'/>\n\t\t</a>\n")
		f.write('\t\t</span>\n\n')
	
	f.write('\t</span>\n') # hidden-container
	f.write('</span>\n\n') # highslide-gallery

# parse cmdline
if len(sys.argv) < 3:
	print "not enough parameters"
	print "usage: " + sys.argv[0] + " <source dir> <albumName>"
	exit(1)

# basic album info
target = sys.argv[1]
albumName = sys.argv[2]

# iterate albums
subalbums = parseDirs(target)

f = open(os.path.join(target, 'index.html'), 'w')
# create header, put album thumbnail & name(desc) there in center
f.write(
'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "xhtml11.dtd">\n'
'<html>\n'
'<head>\n'
'\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
'\t<title>' + albumName + '</title>\n'
"\n"
'\t<script type="text/javascript" src="' + highslidePath + '/highslide.js"></script>\n'
'\t<link rel="stylesheet" type="text/css" href="' + highslidePath + '/highslide.css"/>\n'
"\n"
'\t<script type="text/javascript">\n'
"\t\ths.graphicsDir = '" + highslidePath + "/graphics/';\n"
'\t</script>\n'
'\t<script type="text/javascript" src="' + highslidePath + '/config.js"></script>\n'
'\t<link rel="stylesheet" type="text/css" href="' + highslidePath + '/global.css"/>\n'
'\n'
'\t<!-- overrides here -->\n'
'</head>\n'
'\n'
'<body>\n'
'\t<div class="album-name">' + albumName + '</div>\n'
)

f.write('\t<div class="album-thumb"><img src="thumb.jpg"/></div>\n')


f.write('\t<div class="thumbnails-wrapper">\n\n')

# iterate album(s)
for subalbum in subalbums:
	generateSubalbum(f, subalbum)
	
# close everything
f.write('\t</div>\n') # thumbnails-wrapper
f.write('</body></html>\n')
f.close()

exit(0)
