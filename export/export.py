import requests
import json
import re
from bs4 import BeautifulSoup
import sys
sys.path.append(".")
from config.config import parse_config

class scrape():
    def __init__(self):
        """
        Initialize class - load config options, urls, and create requests session
        """
        self.urls = parse_config("export_urls")
        # self.config = parse_config("config")
        self.session = requests.Session()
        
    
    def get_topic_urls(self):
        """
        Function used to get all not-ignored topic urls from group
        """
        self.urls["topics"] = []
        group_url = self.urls["group_url"]
        group_page = self.session.get(group_url)
        if group_page.status_code != 200:
            raise RuntimeError("Error "+str(group_page.status_code))

        group_soup = BeautifulSoup(group_page.text, "html.parser")
        max_page_number = self.get_page_count(group_soup)
        tid = 0
        for i in range(max_page_number):
            page = self.session.get(group_url[:-5]+",{}.html".format(i))
            page_soup = BeautifulSoup(page.text, "html.parser")
            topic_urls = page_soup.find_all("a", {"class":"topic-title"})
            for url in topic_urls:
                true_url="https://grupy.jeja.pl"+url["href"]
                if true_url not in set(self.urls["ignore_urls"]+[self.urls["kp_url"]]):
                    self.urls["topics"].append({})
                    self.urls["topics"][tid]["url"] = true_url
                    topic_title = url.contents[-1]
                    topic_title = topic_title.replace("\n", "").replace("\t", "")
                    self.urls["topics"][tid]["title"] = topic_title
                    tid+=1
        return self.urls
    def get_all_posts(self):
        for tid in enumerate(self.urls["topics"]):
            self.get_posts_from_topic(tid[0])

    def get_posts_from_topic(self, tid):
        self.urls["topics"][tid]["posts"] = []
        topic_url = self.urls["topics"][tid]["url"]
        
        page = self.session.get(topic_url)

        page_soup = BeautifulSoup(page.text, "html.parser")
        max_page_number = self.get_page_count(page_soup)
        pid = 0
        for i in range(max_page_number):
            page = self.session.get(topic_url[:-5]+",0,{}.html".format(i))
            page_soup = BeautifulSoup(page.text, "html.parser")
            posts = page_soup.find_all("div", {"class":"komentarz kom-mar"})
            for post in posts:
                self.urls["topics"][tid]["posts"].append({})
                nick_div = post.find("div", {"class":"nick"})
                try:
                    self.urls["topics"][tid]["posts"][pid]["username"] = nick_div.find("a").contents[0]
                except AttributeError:
                    self.urls["topics"][tid]["posts"][pid]["username"] = nick_div.contents[0]
                self.urls["topics"][tid]["posts"][pid]["avatar"] = post.find("img", {"class":"komentarz-foto"})["src"].replace("90x90", "small")
                post_contents = post.find("div", {"class":"text"})
                post_content = ""
                for content in post_contents:
                    post_content += str(content)
                post_content = self.jeja_to_markdown(post_content)
                
                self.urls["topics"][tid]["posts"][pid]["content"] = post_content
                pid+=1
        return self.urls
    def get_character_sheet_template(self):
        self.urls["character_sheet_template"] = {
            "title":"Wzór karty postaci",
            "content":""
        }

        page = self.session.get(self.urls["kp_url"])
        page_soup = BeautifulSoup(page.text, "html.parser")
        first_post = page_soup.find("div", {"class":"komentarz kom-mar"})
        post_contents = first_post.find("div", {"class":"text"})
        post_content = ""
        for content in post_contents:
            post_content += str(content)
        post_content = self.jeja_to_markdown(post_content)
        self.urls["character_sheet_template"]["content"] = post_content

    def get_page_count(self, soup):
        pages = soup.find_all("a", {"class":"pagination-number"})
        if len(pages)>0:
            max_page_url = pages[-1]
            max_page_number = int(max_page_url["href"][int(max_page_url['href'].rfind(","))+1:-5])
        else:
            max_page_number = 1
        return(max_page_number)

    def export(self):
        self.get_topic_urls()
        self.get_all_posts()
        self.get_character_sheet_template()
        return {"topics":self.urls["topics"], "character_sheet_template":self.urls["character_sheet_template"]}

    def export_to_file(self, filename):
        with open(filename, "w") as f:
            json.dump(self.export(), f, indent=2)

    def jeja_to_markdown(self, text):
        text = text.replace("<strong>", "**").replace("</strong>", "**")
        text = text.replace("<b>", "**").replace("</b>", "**")
        text = text.replace("<em>", "*").replace("</em>", "*")
        text = text.replace("<s>", "~~").replace("</s>", "~~")
        text = text.replace("<br/>", "")
        text = text.replace('blockquote class="quote">', ">").replace("</blockquote>", "")
        text = re.sub(r'\<a .*href\=\"(\S+)\"[^>]*\>(.*)\<\/a\>', r'[\2](\1)', text)
        text = re.sub(r'\<img.*src\=\"([^>"]*)\"[^>]*\>', r'![image](\1)', text)
        text = re.sub(r'\<iframe.*src\=\"\/\/www\.youtube\.com\/embed\/([\S]+)\"[^>]*\>\<\/iframe\>', r'https://youtu.be/\1', text)
        return str(text)

if __name__=="__main__":
    a = scrape()
    a.export_to_file("export_result.json")