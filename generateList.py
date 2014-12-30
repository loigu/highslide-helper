#!/usr/bin/python

import fnmatch, sys, os, string
import xml.etree.cElementTree as ET

def getAlbums(directory):
	albums = []
	
	for dirname in fnmatch.filter(sorted(os.listdir(directory)), "20[0-9][0-9]_*[0-9]_*[0-9]_*"):
		xmlFile = os.path.join(directory, dirname, "Album.xml")
		if os.path.isfile(xmlFile):
			albumName = ET.parse(xmlFile).getroot().find('name').text
		else:
			albumName = dirname[11:].translate(string.maketrans("_", " "))
		albums.append({'name': albumName, 'dir': dirname})
	
	return sorted(albums, key=lambda x: x['dir'], reverse = True)
	
def generateAlbum(f, album):
	f.write('\t<span class="subalbum-link">\n')
	
	# thumbnail with link to first photo & album name
	directory = album['dir']
	f.write('\t<a id="' + directory + '" href="' + os.path.join(directory, 'index.html') + '">\n')
	f.write('\t\t<img class="subalbum-link" src="' + os.path.join(directory, 'thumb.jpg') + '" title="Click to view this album"/>\n')
	f.write('\t</a>\n')
	f.write('\t<div class="subalbum-name">' + album['name'] + '</div>\n')

	f.write('\t</span>\n') # subalbum-link
	f.write('\n')
	

def generateHeader(f):
	# create header, put album thumbnail & name(desc) there in center
	f.write(
	'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "xhtml11.dtd">\n'
	'<html>\n'
	'<head>\n'
	'\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
	'\t<title>Lokiho fotecky</title>\n'
	"\n"
	'\t<link rel="stylesheet" type="text/css" href="' + highslidePath + '/global.css"/>\n'
	'</head>\n'
	'\n'
	'<body>\n'
	'\t<div class="album-name">Lokiho fotecky</div>\n'
	)

	f.write('\t<div class="thumbnails-wrapper">\n\n')

def generateFooter(f):
	# close everything
	f.write('\t</div>\n') # thumbnails-wrapper
	f.write('<center><b><b>Jste jiz <a target="_parent" href="http://counter.cnw.cz"><img alt="[CNW:Counter]" src="http://counter.cnw.cz/paula.cgi?loigu&amp;5&amp;FFFFFF&amp;000000&amp;on" border="0"></a> navstevnikem teto stranky. </b></b></center>')
	f.write('</body></html>\n')
	
root = sys.argv[1]
highslidePath = "../../highslide" # TODO: customize this

albums = getAlbums(root)
f = open(os.path.join(root, 'index.html'), 'w')

generateHeader(f)

# iterate album(s)
for album in albums:
	generateAlbum(f, album)

generateFooter(f)

f.close()
exit(0)

