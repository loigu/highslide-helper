#!/bin/bash
# $1 target dir
# $2 image dir relative position
# $3 highslide relative position
# rest - gallery name

# TODO: other file types
# TODO: multilayer galleries

# TODO: image & thumbnail size config
IMG_SIZE="1600x1200"
THUMB_SIZE="144x144"
ROTATION="-auto-orient" # rotate by default

ORIGIN="${PWD}"

# $1 script name
function printHelp()
{
	tee << END
	
generates gallery :)
usage: $1 <args> TARGET_DIR [GALLERY NAME]
	-h print help
	-i IMAGE_PATH path to images relative to TARGET_DIR
	-t THUMBNAIL_PATH path to thumbnails relative to TARGET_DIR
	-s SOURCE_DIR generate even the web gallery images (if missing), take them from SOURCE_DIR
	-T generate thumbnails
	-H HIGHSLIDE_PATH path to highslide & config relative to TARGET_DIR
	-f force regenerate all images (requested by other options)
	-n don't rotate images
	if no GALLERY NAME is given, basename of target dir will be used
	
END
}

function die()
{
	if [ "$1" = "-h" ]; then
		printHelp >&2
		shift 1
	fi
	
	echo $* >&2
	cd "${ORIGIN}"
	exit 1
}

function parseArgs()
{
	while getopts hi:t:s:TH:fn flag; do
		case ${flag} in
			(h) printHelp; exit 0 ;;
			(i) IMAGE_PATH="${OPTARG}" ;;
			(t) THUMB_PATH="${OPTARG}" ;;
			(s) SOURCE_DIR="${OPTARG}" ;;
			(T) GENERATE_THUMBNAILS=1 ;;
			(H) HIGHSLIDE_PATH="${OPTARG}" ;;
			(f) FORCE_REGENERATE=1 ;;
			(n) ROTATION='' ;;
			(*) die -h "unknown flag ${flag}" ;;
		esac
	done
	shift $(( OPTIND-1 ))
	
	TARGET_DIR="$1"
	shift 1
	GALLERY_NAME="$*"
}

function checkConf()
{
	[ ! -d "${TARGET_DIR}" -a ! -d "${SOURCE_DIR}" ] && die -h "target or source dir must exist"
	
	[ -z "${IMAGE_PATH}" ] && IMAGE_PATH="."
	[ -z "${THUMB_PATH}" ] && THUMB_PATH="./thumbs"
	[ -z "${HIGHSLIDE_PATH}" ] && HIGHSLIDE_PATH="."
	[ -z "${GALLERY_NAME}" ] && GALLERY_NAME=$(basename "${TARGET_DIR}" | tr "_" " ")
	
	[ ! -f "${TARGET_DIR}/${HIGHSLIDE_PATH}/highslide.css" -o ! -f "${TARGET_DIR}/${HIGHSLIDE_PATH}/highslide.js" -o ! -f "${TARGET_DIR}/${HIGHSLIDE_PATH}/config.js" -o ! -f "${TARGET_DIR}/${HIGHSLIDE_PATH}/global.css" ] && echo "WARNING: some highslide files not found" >&2
	[ ! -d "${TARGET_DIR}/${THUMB_PATH}" -a -z "${GENERATE_THUMBNAILS}" ] && echo "WARNING: thumbnails not requested while thumbnail path doesn't exist" >&2
}

# $1 gallery name
# $2 highslide home
function putStart()
{
	tee << END

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "xhtml11.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>$1</title>

<script type="text/javascript" src="$2/highslide.js"></script>
<link rel="stylesheet" type="text/css" href="$2/highslide.css" />
<!--[if lt IE 7]>
<link rel="stylesheet" type="text/css" href="$2/highslide-ie6.css" />
<![endif]-->

<script type="text/javascript">
	hs.graphicsDir = '$2/graphics/';
</script>
<script type="text/javascript" src="$2/config.js"></script>
<link rel="stylesheet" type="text/css" href="$2/global.css"/>

<!-- overrides here -->
</head>

<body style="background-color: black">
<h1 style="color:white">$1</h1>
<div class="highslide-gallery" style="margin: auto">

END
}

function endGallery()
{
	echo '</div> <!-- highslide-gallery -->'
}

function putEnd()
{
	tee << END

</body>
</html>

END
}


# $1 list name
# $2 dir path
# $3 thumb path
# $@ file list
function putList()
{
	local LIST_NAME="$1"
	local DIR_PATH="$2"
	local THUMB_PATH="$3"
	shift 3
	
	local LIST_GROUP=$(echo ${DIR_PATH} | tr -d '.," \t')
	[ -n "${LIST_GROUP}" -a "${LIST_GROUP}" != '/' ] && local GROUPING=", { thumbnailId: '${LIST_GROUP}', slideshowGroup: '${LIST_GROUP}' }"
	
	for image in "$@"; do
		[ "${image}" = 'thumb.jpg' ] && continue
		echo "<a class='highslide' href='${DIR_PATH}/${image}' onclick=\"return hs.expand(this${GROUPING})\">"
		echo "<img src='${THUMB_PATH}/${image}'/></a>"
	done
}

function putVideos()
{
	echo '<ul>'
	
	for video in "$@"; do
		local name=$(basename "$video")
		tee << END
<li>
<video controls>
  <source src="$video" type="video/mp4">
  Your browser does not support the video tag.
</video>
<br/>
<a href="$video">$name</a>
</li>
END
	done

	echo '</ul>'
}


# $1 where are images
# $2 where to put smaller images
# $3 new size
# $@ image names
function scaleImages()
{
	local IMAGE_DIR="$1"
	local TARGET_DIR="$2"
	local TARGET_SIZE="$3"
	shift 3
	
	mkdir -p "${TARGET_DIR}" || die "can't create ${TARGET_DIR} dir"
	for image in "$@"; do
		[ ! "${FORCE_REGENERATE}" -a -f "${TARGET_DIR}/${image}" ] && continue
		convert "${IMAGE_DIR}/${image}" ${ROTATION} -resize "${TARGET_SIZE}" "${TARGET_DIR}/${image}" || die "can't convert file ${image}"
	done
}

parseArgs "$@"
checkConf

cd "${TARGET_DIR}" || die "can't chdir to ${TARGET_DIR}"

IMAGES=$(ls -1 "${IMAGE_PATH}" | xargs -d \\n file -i | sed -n 's/\([^:]*\):\ *image\/.*/\1/p')
VIDEOS=$(ls -1 "${IMAGE_PATH}" | xargs -d \\n file -i | sed -n 's/\([^:]*\):\ *video\/.*/\1/p')

if [ "${SOURCE_DIR}" ]; then
	scaleImages "${SOURCE_DIR}" "${IMAGE_PATH}" "${IMG_SIZE}" ${IMAGES}
	[ "$?" -eq 0 ] || die "can't generate thumbnails"
fi

if [ "${GENERATE_THUMBNAILS}" ]; then 
	scaleImages "${IMAGE_PATH}" "${THUMB_PATH}" "${THUMB_SIZE}" ${IMAGES}
	[ "$?" -eq 0 ] || die "can't generate thumbnails"
fi

putStart "${GALLERY_NAME}" "${HIGHSLIDE_PATH}" > index.html || die "can't put start of html file"
putList "${GALLERY_NAME}" "${IMAGE_PATH}" "${THUMB_PATH}" ${IMAGES} >> index.html
[ "$?" -eq 0 ] || die "can't put image list"
endGallery >> index.html
putVideos ${VIDEOS} >> index.html
putEnd >> index.html

cd "${ORIGIN}"
exit 0

