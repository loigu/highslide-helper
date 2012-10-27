#!/bin/bash
# $1 target dir
# $2 image dir relative position
# $3 highslide relative position
# rest - gallery name

# TODO: proper args, for example generateThumbs, resize, recursive, etc
# TODO: other file types

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
	-T generate thumbnails
	-H HIGHSLIDE_PATH path to highslide & config relative to TARGET_DIR
	if no GALLERY NAME is given, basename of target dir will be used
	
END
}

function parseArgs()
{
	while getopts hi:t:TH: flag; do
		case ${flag} in
			(h) printHelp; exit 0 ;;
			(i) IMAGE_PATH="${OPTARG}" ;;
			(t) THUMB_PATH="${OPTARG}" ;;
			(T) GENERATE_THUMBNAILS=1 ;;
			(H) HIGHSLIDE_PATH="${OPTARG}" ;;
			(*) die "unknown flag ${flag}" ;;
		esac
	done
	
	TARGET_DIR="$1"
	shift 1
	GALLERY_NAME="$*"
}

function checkConf()
{
	[ -z "${IMAGE_PATH}" ] && IMAGE_PATH="."
	[ -z "${THUMB_PATH}" ] && THUMB_PATH="./thumbs"
	[ -z "${HIGHSLIDE_PATH}" ] && HIGHSLIDE_PATH="."
	[ -z "${GALLERY_NAME}" ] && GALLERY_NAME=$(basename ${TARGET_DIR} | tr "_" " ")
	
	[ ! -d "${TARGET_DIR}" ] && die "target dir must exist"
	[ ! "${GENERATE_THUMBNAILS}" -a ! -d "${TARGET_DIR}/${THUMB_PATH}" ] && die "thumbs not requested but thumb dir doesn't exist"
	
	[ ! -f "${HIGHSLIDE_PATH}/highslide.css" -o ! -f "${HIGHSLIDE_PATH}/highslide-with-gallery.packed.js" -o ! -f "${HIGHSLIDE_PATH}/config.js" -o ! -f "${HIGHSLIDE_PATH}/default.css" ] && die "some highslide files missing"
}

function die()
{
	echo $* >&2
	cd "${ORIGIN}"
	exit 1
}

# $1 gallery name
# $2 highslide home
function putStart()
{
	tee << END

<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"xhtml11.dtd\">
<html>
<head>
<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />
<title>$1</title>

<script type=\"text/javascript\" src=\"$2/highslide-with-gallery.packed.js\"></script>
<link rel=\"stylesheet\" type=\"text/css\" href=\"$2/highslide.css\" />
<!--[if lt IE 7]>
<link rel=\"stylesheet\" type=\"text/css\" href=\"$2/highslide-ie6.css\" />
<![endif]-->

<script type=\"text/javascript\" src="$2/config.js\"></script>
<link rel=\"stylesheet\" type=\"text/css\" href="$2/global.css\"/>

<!-- overrides here -->
</head>

<body style=\"background-color: black\">
<div class=\"highslide-gallery\" style=\"width: 600px; margin: auto\">

END
}

function putEnd()
{
	tee << END

</div>
</body>
</html>

END
}


# $1 list name
# $2 dir path
# $3 thumb path
# [$4 thumb image name] - hides rest of list under this image
# STDIN list of files
function putList()
{
	local LIST_NAME="$1"
	local DIR_PATH="$2"
	local THUMB_PATH="$3"
	local THUMB_IMAGE="$4" # TODO: implement this
	
	echo '<div class="highslide-gallery" style="width: 600px; margin: auto">'
	echo "<h1>${LIST_NAME}</h1>"
	
	while read image; do
		echo "<a class='highslide' href='${THUMB_PATH}/${image}' onclick=\"return hs.expand(this)\">"
		echo "<img src='${DIR_PATH}/${image}'/></a>"
	done
	
	echo '</div>' #highslide-gallery
}

# $1 where are images
# $2 where to put thumbnails
# stdin image list
function generateThumbnails()
{
	mkdir -p "$2" || die "can't create thumb dir"
	while read image; do
		convert "$1/${image}" -auto-orient -resize 144x144 "$2/${image}" || die "can't convert file ${image}"
	done
}

parseArgs
checkConf
exit 0

cd "${TARGET_DIR}" || die "can't chdir to ${TARGET_DIR}"
putStart "${GALLERY_NAME}" "${HIGHSLIDE_PATH}" > index.html || die "can't put start of html file"
ls -1 "${IMAGE_PATH}" | xargs -n 1 basename | putList "${GALLERY_NAME}" "${IMAGE_PATH}" "${THUMB_PATH}" >> index.html
[ "$?" = 0 ] || die "can't put image list"
putEnd >> index.html

cd "${ORIGIN}"
exit 0

