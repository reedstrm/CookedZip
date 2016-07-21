from HTMLParser import HTMLParser


class CNXHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.resources = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for name, value in attrs:
                if name == "src":
                    if "/resources/" in value:
                        self.resources.append(value)

    def get_resources(self):
        return self.resources
