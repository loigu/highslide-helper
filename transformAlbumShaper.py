#!/usr/bin/python

import xml.etree.cElementTree as ET
import sys, os, string, re, shutil, hashlib, fnmatch

# TODO: nicer block schema (div around links, block them, center them)
# TODO: fix the first in thumbstrip
# TODO: bigger thumbstrip

# TODO: customize this
highslidePath = '../../../highslide'

lastAlbum = 0

def md5sum(filename):
	md5 = hashlib.md5()
	with open(filename,'rb') as f: 
		for chunk in iter(lambda: f.read(128*md5.block_size), b''): 
			md5.update(chunk)
	return md5.hexdigest()

def matchFiles(directory, photos):
	files = []
	for filename in fnmatch.filter(os.listdir(directory), "*[0-9].[Jj][Pp][Gg]"):
		desc = None
		found = False
		
		# try find by file itself
		filePath = os.path.join(directory, filename)
		fileSum = md5sum(filePath)
		if fileSum in photos:
			desc = photos[fileSum]
			found = True
			
		# no luck yet, try thumb
		if desc == None:
			try:
				sum = md5sum(os.path.join(directory, filename[:filename.find('.')] + "_thumb.jpg"))
			except IOError:
				sum = 'not a sum'
			if sum in photos:
				desc = photos[sum]
				found = True
				
		# no luck yet, try slide
		if desc == None:
			try:
				sum = md5sum(os.path.join(directory, filename[:filename.find('.')] + "_slideshow.jpg"))
			except IOError:
				sum = 'not a sum'
			if sum in photos:
				desc = photos[sum]
				found = True
				
		hidden = False
		if not found:
			print "photo " + filename + " not in album " + directory
			hidden = True
			
		files.append({'name':filename, 'desc':desc, 'hidden':hidden})
		
	return files

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
		photos[photoTree.find('thumb').find('md5').text] = desc
		photos[photoTree.find('slideshow').find('md5').text] = desc
	
	global source
	files = matchFiles(os.path.join(source, 'img', subalbum['dir']), photos)
	subalbum['photos'] = sorted(files, key = lambda x: int(x['name'][:-4]))
	
	return subalbum


def generateSubalbum(f, subalbum, hidden):
	global source
	global target
	subalbumDirName = subalbum['name'].translate(string.maketrans(" .", "__"), "'\"")
	thumbsDirName = os.path.join(subalbumDirName, "thumbs")
	sourceDir = os.path.join(source, 'img', subalbum['dir'])
	targetDir = os.path.join(target, subalbumDirName)
	thumbsDir = os.path.join(target, thumbsDirName)
	
	if not os.path.isdir(thumbsDir):
		os.makedirs(thumbsDir)
	
	f.write('<span class="highslide-gallery">\n')
	if hidden:
		# copy subalbum thumbnail
		if 'thumb' in subalbum and subalbum['thumb'] != None and len(subalbum['thumb']) > 0:
			shutil.copy(os.path.join(source, subalbum['thumb']), os.path.join(targetDir, "thumb.jpg"))
			subalbum['thumb'] = os.path.join(subalbumDirName, "thumb.jpg")
		else:
			# if there is no thumbnail, use first image
			subalbum['thumb'] = os.path.join(thumbsDirName, subalbum['photos'][0]['name'])
		
		group = ", { thumbnailId: '" + subalbum['thumb'] + "', slideshowGroup: " + subalbum['dir'] + " }"
		
		f.write('\t<span class="subalbum-link">\n')
		
		# thumbnail with link to first photo & album name
		f.write('\t<a class="highslide" id="' + subalbum['thumb'] + '" href="' + os.path.join(subalbumDirName, subalbum['photos'][0]['name']) + '" onclick="return hs.expand(this' + group + ')">\n')
		f.write('\t\t<img src="' + subalbum['thumb'] + '" title="Click to view this album"/>\n\t</a>\n')
		
		# name (desc) if there is some
		f.write('\t<div class="subalbum-name">' + subalbum['name'])
		if subalbum['desc'] != None and len(subalbum['desc']) > 0:
			f.write(' (' + subalbum['desc'] + ')')
		f.write('</div>\n')

		f.write('\t</span>\n\n') # subalbum-link
		
		# append hidden container
		f.write('\t<span class="hidden-container">\n')
	else:
		group = ''
	
	for photo in subalbum['photos']:
		#copy file and thumb
		shutil.copy(os.path.join(sourceDir, photo['name']), targetDir)
		shutil.copyfile(os.path.join(sourceDir, photo['name'].partition('.')[0] + '_thumb.jpg'), os.path.join(thumbsDir, photo['name']))
		
		if not photo['hidden']:
			f.write('\t\t<span class="thumb"><a id="' + subalbumDirName + '-' + photo['name'] + '" class="highslide" href="' + os.path.join(subalbumDirName, photo['name']) + '" onclick="return hs.expand(this' + group + ')">\n')
			f.write("\t\t\t<img src='" + os.path.join(thumbsDirName, photo['name']) + "'/>\n\t\t</a>\n")
		
			#  put / put with desc if present
			if photo['desc'] != None and len(photo['desc']) > 0:
				f.write('\t\t\t<div class="highslide-caption">' + photo['desc'] + '</div>\n')
			f.write('\t\t</span>\n\n')
	
	if hidden:
		f.write('\t</span>\n') # hidden-container
	f.write('</span>\n\n') # highslide-gallery

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
if albumDesc != None and len(albumDesc) > 0:
	albumName += " (" + albumDesc + ")"

albumThumb = albumTree.find('thumb')
if albumThumb != None: 
	albumThumb = albumThumb.get('path')

print albumName

# iterate albums
subalbums = []

for subalbum in albumTree.findall('subalbum'):
	subalbums.append(parseSubalbum(subalbum))
	
tmp = sorted(subalbums, key=lambda x: int(x['dir']))
subalbums = tmp

# create global dir, backup xml
if not os.path.isdir(target):
	os.makedirs(target)
shutil.copy(source + '/Album.xml', target)

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

# copy album thumbnail if present
if albumThumb != None and len(albumThumb) > 0:
	shutil.copyfile(os.path.join(source, albumThumb), os.path.join(target, "thumb.jpg"));
	f.write('\t<div class="album-thumb"><img src="thumb.jpg"/></div>\n')

if len(subalbums) <= 1:
	hidden = False
else:
	hidden = True
	
f.write('\t<div class="thumbnails-wrapper">\n\n')

# iterate album(s)
for subalbum in subalbums:
	generateSubalbum(f, subalbum, hidden)
	
# close everything
f.write('\t</div>\n') # thumbnails-wrapper
f.write('</body></html>\n')
f.close()

exit(0)
