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
        max_page_number = self.get_page_count(group_soup)
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
                self.urls["topics"][tid]["title"] = topic_title

    def get_all_posts(self):
        pass


    def get_posts_from_topic(self, tid):
        self.urls["topics"][tid]["posts"] = {}
        topic_url = self.urls["topics"][tid]["url"]
        
        page = self.session.get(topic_url)

        page_soup = BeautifulSoup(page, "html.parser")
        max_page_number = self.get_page_count(page_soup)
        pid = 0
        for i in range(max_page_number):
            page = self.session.get(topic_url[:-5]+",0,{}.html".format(i))
            page_soup = BeautifulSoup(page, "html.parser")
            posts = page_soup.find_all("div", {"class":"komentarz kom-mar"})
            for post in posts:
                self.urls["topics"][tid]["posts"][pid]["username"] = post.find("div", {"class":"nick"}).find("a").contents[0]
                self.urls["topics"][tid]["posts"][pid]["avatar"] = post.find("img", {"class":"komentarz-foto"})["src"].replace("90x90", "small")
                post_contents = post.find("div", {"class":"text"})
                post_content = ""
                for content in post_contents:
                    post_content += str(content)
                replacable_list = ['<a class="fancybox" data-fancybox="grupy" data-fancybox-group="fancybox" href="', '</a>', 
                                   '">', '<img alt="" src="', '" style="max-width:510px"/>', '<a class="withUl" href="',
                                   '" rel="nofollow', '" target="_blank', '<strong>', '</strong>', '<em>', '</em>', '<u>', '</u>',
                                   '<iframe allowfullscreen="" frameborder="0" height="285" src="https://www.youtube.com/embed/',
                                   '" width="510]</iframe>', '<br/>', "<s>", "</s>"]
                to_replace_list = ['[url=', ']', '[/url]', '[img]', '[/img]', '[url=', '', '', '**', '**', '*', '*',
                                   '__', '__', '[youtube]', '[/youtube]', '', "~~", "~~"]

                for replacable, to_replace in replacable_list, to_replace_list:
                    post_content.replace(replacable, to_replace)
                
                self.urls["topics"][tid]["posts"][pid]["content"] = post_content



    def get_page_count(self, soup):
        pages = soup.find_all("a", {"class":"pagination-number"})
        if len(pages)>0:
            max_page_url = pages[-1]
            max_page_number = int(max_page_url[max_page_url.rfind(",")+1:-5])
        else:
            max_page_number = 0
        return(max_page_number)