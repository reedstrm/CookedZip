import string
from os import makedirs
from Spoon import Spoon
from subprocess import call
import os

"""
Some of this code was reused from Weston's Book Zip branch on cnx-epub
"""


def write_toc_element(html, json_tree):
    """
    Recursively write the html corresponding to the elements in json_tree to file
    """
    # If id is just subcol, there's no actual html associated w/ this page, so no link is required
    if json_tree["id"] == "subcol":
        html.write(spoon.beautify(json_tree["title"]))
        html.write("<ul>\n")
        contents = json_tree["contents"]
        # Write each member of this tree
        for elem in contents:
            html.write("<li>\n")
            write_toc_element(html, elem)
            html.write("</li>\n")
        html.write("</ul>\n")

    # Otherwise, it's an individual page, link to it directly
    else:
        setup_page(json_tree["id"], json_tree["title"])
        main_files_added.append(book_title + "/" + spoon.remove_version(json_tree["id"]) + ".html")
        linkstr = u'<a href="{}.html">{}</a>\n'.format(spoon.remove_version(json_tree["id"]), json_tree["title"]).encode('utf-8')
        html.write(linkstr)


def setup_page(page_id, title):
    page_html = spoon.load_page(page_id)
    page_html = page_html.encode('utf-8')
    new_page = string.replace(page_html, '/resources/', 'resources/')
    #print page_id
    if spoon.beautify(title) == "Index":
        fixed_links = new_page
    else:
        print "setup_page: " + title + " " + page_id
        fixed_links = spoon.fix_inner_link(new_page)

    f = open(book_title + "/" + spoon.remove_version(page_id) + ".html", "w")
    f.write(fixed_links)
    f.close()

    resources = spoon.get_resources(page_html)

    for resource in resources:
        resource_files_added.append(book_title + "/" + ("/".join(resource.split("/")[1:])))
        spoon.save_resource(spoon.domain + resource, book_title)

book_id = raw_input("Please enter book UUID: ")

main_files_added = []
resource_files_added = []
spoon = Spoon()

spoon.load_book_json(book_id)
book_title = spoon.get_book_name()
makedirs(book_title)
makedirs(book_title + "/resources")

"""
Create the html TOC
"""
print "Fetching book HTML..."
toc_html = open(book_title + '/toc.html', 'w')
main_files_added.append(book_title + '/toc.html')
toc_html.write("<html>\n")
toc_html.write("<body>\n")

toc_json = spoon.get_tree()
toc_html.write("<ul>")
for section in toc_json["contents"]:
    toc_html.write("<li>")
    write_toc_element(toc_html, section)
    toc_html.write("</li>")
toc_html.write("</ul>")

# Finish writing toc
toc_html.write("</body>\n")
toc_html.write("</html>\n")
toc_html.close()

print "Zipping..."

unique_dirs = []
zip_command = ["zip",  "-rm", book_title]
for filename in main_files_added + resource_files_added:
    #print "Adding file: " + filename + " to zip"
    zip_command.append(filename)
call(zip_command)

rm_command = ["rm", "-r", book_title]
call(rm_command)

print "Zip complete!"
