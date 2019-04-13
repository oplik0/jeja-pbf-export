import requests
import json
from bs4 import BeautifulSoup
from config import parse_config

class scrape():
    def __init__(self):
        """
        Initialize class - load config options, urls, and create requests session
        """
        self.urls = parse_config("urls")
        # self.config = parse_config("config")
        self.session = requests.Session()
    def get_topic_urls(self):
        """
        Function used to get all not-ignored topic urls from group
        """
        self.urls["topics"] = {}
        group_url = self.urls["group_url"]
        group_page = self.session.get(group_url)
        if group_page.status_code != "200":
            raise RuntimeError("Error "+group_page.status_code)

        group_soup = BeautifulSoup(group_page.text, "html.parser")
        pages = group_soup.find_all("a", {"class":"pagination-number"})
        if len(pages)>0:
            max_page_url = pages[-1]
            max_page_number = int(max_page_url[max_page_url.rfind(",")+1:-5])
        else:
            max_page_number = 0
        tid = 0
        for i in range(max_page_number):
            self.urls["topics"][tid] = {}
            page = self.session.get(group_url[:-5]+",{}.html".format(i))
            page_soup = BeautifulSoup(page.text, "html.parser")
            topic_urls = page_soup.find_all("a", {"class":"topic-title"})
            for url in topic_urls:
                true_url="https://grupy.jeja.pl"+url["href"]
                if true_url not in set(self.urls["ignore_urls"]+self.urls["kp_urls"]+self.urls["topic_urls"]):
                    self.urls["topics"][tid]["url"] = true_url
                
                if len(url.contents)==3:
                    topic_title = url.contents[2]
                else:
                    topic_title = url.contents[0]
                topic_title = topic_title.replace("\n", "").replace("\t", "")
                urls["topics"][tid]["title"] = topic_title

            