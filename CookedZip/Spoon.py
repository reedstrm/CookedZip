import json
import urllib2
from CNXHTMLParser import CNXHTMLParser
from urllib import urlretrieve
import os
import lxml.html
from bs4 import BeautifulSoup


def _walk_content(tree, pages=None):
    if pages is None:
        pages = []
    if 'contents' in tree:
        for child in tree['contents']:
            if 'contents' in child:
                _walk_content(child, pages)
            else:
                id = child['id']
                pages.append(id[:id.find('@')])
    return pages


class Spoon:
    def __init__(self):
        self.json = []
        self._page_ids = []
        self.page_json = []
        self.domain = 'http://archive-dev00.cnx.org'
        self.pages = {}

    def load_book_json(self, page_id):
        """
        Load the table of contents (TOC) page of the page whose id is page_id
        """
        req = urllib2.Request(u'{}/contents/{}.json'.format(self.domain,
                                                            page_id))
        opener = urllib2.build_opener()
        f = opener.open(req)
        self.json = json.loads(f.read())
        self._page_ids = _walk_content(self.json['tree'])

    def get_tree(self):
        """
        Returns the content tree (in json) of the currently loaded TOC page
        """
        return self.json["tree"]

    def get_page_ids(self):
        """
        Returns a list of pageids that exist in the currently loaded TOC page
        """
        return self._page_ids

    def get_book_name(self):
        """
        Returns the title string of the currently loaded TOC page
        """
        return self.beautify(self.json["title"])

    def get_book_id(self):
        """
        Returns the id string of the currently loaded TOC page
        """
        return u'{}@{}'.format(self.json["id"], self.json['version'])

    def load_page(self, page_id):
        """
        fetches page json and returns content HTML
        :param page_id: UUID of page
        :return: content stanza (page html)
        """
        try:
            url = u'{}/contents/{}:{}.json'.format(self.domain,
                                                   self.get_book_id(),
                                                   page_id)
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            page_json = json.loads(f.read())
        except:
            url = u'{}/contents/{}.json'.format(self.domain, page_id)
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            page_json = json.loads(f.read())

        self.page_json = page_json
        return self.page_json["content"]

    def get_resources(self, page_html):
        """
        returns list of resources found in the given page HTML
        :param page_html: HTML of page
        :return: list of resources
        """
        parser = CNXHTMLParser()
        parser.feed(page_html)
        return parser.get_resources()

    def save_resource(self, resource_url, book_title):
        """
        Saves the given resource URL to a local resources directory.
        Can handle resources that are a UUID and Resources inside
        a UUID directory
        :param resource_url: URL of resource to fetch
        """
        directory = "/".join(resource_url.split("/")[3:5])
        filename = "/".join(resource_url.split("/")[3:])
        # print directory
        # print filename
        if (filename != directory
                and not os.path.exists(book_title + "/" + directory)
                and not os.path.exists(book_title + "/" + filename)):
            os.makedirs(book_title + "/" + directory)
        urlretrieve(resource_url, book_title + "/" + filename)

    def fix_inner_link(self, page_html):
        """
        Changes inner book links to point to the saved HML file rather than the
        URL on CNX
        :param page_html: HTML that could contain page links
        :return: HTML with corrected links
        """
        html = lxml.html.document_fromstring(page_html)
        for element, attribute, link, pos in html.iterlinks():
            if '/contents/' in link and element.text is not None:
                print "fix_link: " + link
                content_index = link.find('/contents/')
                pound_index = link.find('#')
                id = ''
                if pound_index == -1:
                    id = link[content_index + 10:]
                else:
                    id = link[content_index + 10:pound_index]
                anchor = ''
                if pound_index > -1:
                    anchor = link[pound_index:]

                if self.remove_version(id) in self.get_page_ids():
                    print "fix_inner_link: " + id
                    page = self.get_page_json(id)
                    title = page['id'] + ".html"
                    link_text = title + anchor
                    element.attrib['href'] = link_text
        return lxml.html.tostring(html)

    def local_url_format(self, page_name):
        """
        Removes numbering from page name, removes punctuation
        and replaces spaces with _
        :param page_name: page name to fix
        :return: updated page name
        """
        index = page_name.find("|")
        if index > 0:
            shortened_name = page_name[index + 2:]
        else:
            shortened_name = page_name
        temp = shortened_name.encode('utf-8').replace(' ', '_') + ".html"
        punclist = ':,-\''
        for c in punclist:
            temp = temp.replace(c, "")
        return temp

    def beautify(self, title):
        """
        Removes HTML tags from title if they exist
        :param title: title to remove HML tags from
        :return: updated title
        """
        soup = BeautifulSoup(title, 'html.parser')
        return soup.get_text().strip()

    def get_page_json(self, page_id):
        """
        Retrieves json for the given page id
        :param page_id: page id to fetch json for
        :return: page json
        """
        p_id = self.remove_version(page_id)
        if p_id in self.pages:
            return self.pages[p_id]

        page_json = None
        try:
            url = u'{}/contents/{}:{}.json'.format(self.domain,
                                                   self.get_book_id(),
                                                   p_id)
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            page_json = json.loads(f.read())
        except:
            url = u'{}/contents/{}.json'.format(self.domain, page_id)
            req = urllib2.Request(url)
            opener = urllib2.build_opener()
            f = opener.open(req)
            page_json = json.loads(f.read())

        self.pages[p_id] = page_json
        return page_json

    def remove_version(self, page_id):
        """
        removes version (@X.X) from page id
        :param page_id: page id to modify
        :return: page id minus version
        """
        index = page_id.find('@')
        return page_id[:index]
