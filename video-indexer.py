#!/usr/bin/python3

# This isn't anything worthy of releasing yet.
# TODO:
# * make fixed strings (now in Hebrew) flexible, translatable
# * make use of flexible command line arguments
# * make use of a config file


import os
import re
import xml.etree.ElementTree as ET
import sys


path = sys.argv[1]  # TODO: ugly, to be bettered; TODO: add simple help
path_length = len(path)
VIDEO_EXTS = ('avi', 'flv', 'mkv', 'mov', 'mp4', 'm4v', 'ogv', 'ogg')
DIR_DESC_FN = 'description.xml'


def process_root(root):
    rootname = root[path_length:]
    if rootname != "/":
        print('<h3 id="' + rootname + '">' +
              re.sub("/", " ◁ ", rootname) + '</h3>')

    dir_description_filename = root + "/" + DIR_DESC_FN
    if os.path.isfile(dir_description_filename):
        tree = ET.parse(dir_description_filename)
        xmlroot = tree.getroot()
        for dirxml in xmlroot.findall("dir"):
            link = dirxml.find("link")
            description = dirxml.find("description")
            if description is not None:
                print(dirxml.find("description").text)
            if link is not None:
                print("<a href=\"" + dirxml.find("link").text + "\">" +
                      "קישור עבור ספריה זו" +
                      "</a>.")


def process_dirs(dirs, root):
    for dirname in sorted(dirs):
        print("<li>" +
              "<a href=\"#" +
              os.path.join(root[path_length:], dirname) +
              "\">" +
              dirname +
              "</a>" +
              "</li>")


def autolink(filename, pattern, prefix, suffix):
    autocode = re.search(pattern, filename)
    if autocode:
        stripped_filename = re.sub(pattern + ".*", "", filename)
        stripped_code = autocode.group(0)[1:-1]
        print('<a href="' + prefix + stripped_code + suffix + '">' +
              stripped_filename +
              '</a>')
    else:
        raise Exception


def process_files(files, root):
    dir_description_filename = root + "/" + DIR_DESC_FN
    XMLed = False
    if os.path.isfile(dir_description_filename):
        tree = ET.parse(dir_description_filename)
        xmlroot = tree.getroot()
        XMLed = True
    for filename in sorted(files):
        filename_ext = re.search("\.[^\.]*$", filename).group(0)[1:]
        print("<li>", end="")
        try:
            autolink(filename, "-\d*\.", "https://vimeo.com/", "")
        except:
            try:
                autolink(filename, "-[^ ]{11}\.", "https://youtu.be/", "")
            except:  # not from Vimeo nor Youtube
                XMLlinked = False
                if XMLed:  # maybe there is a link in the XML file
                    video_link = xmlroot.find('.//link/..[@filename="' +
                                              filename + '"]')
                    if video_link:
                        print('<a href="' +
                              video_link.find("link").text +
                              '">' +
                              filename[:-len(filename_ext)-1] +
                              '</a>', end="")
                        XMLlinked = True
                if not XMLlinked:  # if nothing is found, don't link
                    print(filename[:-len(filename_ext)-1], end="")
        if XMLed:
            video_description = xmlroot.find(
                './/description/..[@filename="' +
                filename + '"]')
            if video_description:
                print('<div style="direction: RTL">' +
                      video_description.find("description").text +
                      '</div>', end="")
        print('</li>')


print("""
<style media="screen" type="text/css">
.videodirs li {
display: inline;
margin-left: 0.75em;
}

.videodirs li:before {
 content: "◁ ";
}

.videodirs li:last-child{
display: inline;
margin-left: 0em;
}

.videofiles {
      direction: LTR;
}
</style>
      """)

for root, dirs, files in sorted(os.walk(path + "/")):
    process_root(root)
    print()
    if dirs:
        print('<ul class="videodirs">')
        process_dirs(dirs, root)
        print("</ul>")
        print()
    video_files = [file for file in files if file.endswith(VIDEO_EXTS)]
    if video_files:
        print('<ul class="videofiles">')
        process_files(video_files, root)
        print("</ul>")
