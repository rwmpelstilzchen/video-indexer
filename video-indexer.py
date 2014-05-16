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
VIDEO_EXTS = ["avi", "flv", "mkv", "mov", "mp4", "m4v", "ogv"]
DIR_DESC_FN = "description.xml"


def process_root(root):
    rootname = root[path_length:]
    print ('<h3 id="' + rootname + '">' +
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
                print("קישור עבור ספריה זו: " +
                      "[" + dirxml.find("link").text + "]" +
                      "(" + dirxml.find("link").text + ")")


def process_dirs(dirs, root):
    for dirname in sorted(dirs):
        print("* **[" + dirname + "]" +
              "(#" + os.path.join(root[path_length:], dirname) + ")**")


def autolink(filename, pattern, prefix, suffix):
    autocode = re.search(pattern, filename)
    if autocode:
        stripped_filename = re.sub(pattern + ".*", "", filename)
        stripped_code = autocode.group(0)[1:-1]
        print("* [" + stripped_filename + "](" + prefix +
              stripped_code + suffix + ")")
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
        if filename_ext in VIDEO_EXTS:
            try:
                autolink(filename, "-\d{8}\.", "https://vimeo.com/", "")
            except:
                try:
                    autolink(filename, "-[^ ]{11}\.", "https://youtu.be/", "")
                except:  # not from Vimeo nor Youtube
                    if XMLed:  # maybe there is a link in the XML file
                        video_link = xmlroot.find('.//link/..[@filename="' +
                                                  filename + '"]')
                        if video_link:
                            print("* " +
                                  "[" + filename[:-len(filename_ext)-1] + "]" +
                                  "(" + video_link.find("link").text + ")")
                    else:  # if nothing is found, don't link
                        print("* " + filename[:-len(filename_ext)-1])
            if XMLed:
                video_description = xmlroot.find(
                    './/description/..[@filename="' +
                    filename + '"]')
                if video_description:
                    print("<br/>" + video_description.find("description").text)


for root, dirs, files in sorted(os.walk(path)):
    process_root(root)
    print()
    print("ספריות:\n")
    process_dirs(dirs, root)
    print()
    print("קבצים:\n")
    process_files(files, root)
    print("\n")
