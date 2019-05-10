import requests
import json
import sys
sys.path.append(".")
from config.config import parse_config
from time import sleep

class nodebb_import():
    def __init__(self):
        """
        Initialize class - load config options, urls, and create requests session
        """
        self.urls = parse_config("import_urls")
        self.config = parse_config("config")
        self.data = parse_config("export_result")
        self.session = requests.Session()
        self.headers = {"Authorization":"Bearer {}".format(self.config["token"])}
        self.tids = []
        if self.config["create_new"]:
            self.create_user()
            self.create_categories()
    def create_user(self):
        data = {"username":self.urls["PBF_name"], "_uid":1}
        response = self.session.post(self.urls["forum_url"]+"/api/v2/users", data=data, headers=self.headers)
        self.config["_uid"] = response.json()['payload']['uid']
        input("confirm email")
        self.session.put(self.urls["forum_url"]+"/api/v2/groups/PBF/membership/{}".format(self.config["_uid"]), data={"_uid":1}, headers=self.headers)
        self.session.post(self.urls["forum_url"]+"/api/v2/groups/", data = {"name":"Mistrzowie Gry {}".format(self.urls["PBF_name"]), "ownerUid":self.config["_uid"], "_uid":1})
        sleep(1)

    def create_categories(self):
        data = {"name":self.urls["PBF_name"], "_uid":1}
        response = self.session.post(self.urls["forum_url"]+"/api/v2/categories", data=data, headers=self.headers)
        top_cid = response.json()['payload']['cid']
        names = ["Karty Postaci", "Czat", "Najważniejsze Informacje", "Lokacje"]
        data["parentCid"] = top_cid
        for name in names:
            data["name"] = name
            response = self.session.post(self.urls["forum_url"]+"/api/v2/categories", data=data, headers=self.headers)
            if name == "Karty Postaci":
                self.urls["character_sheet_category_id"] = response['payload']['cid']
            elif name == "Lokacje":
                self.urls["post_category_id"] = response['payload']['cid']
            elif name == "Czat":
                cid = response.json()['payload']['cid']
                self.session.post(self.urls["forum_url"]+"/api/v2/topics", data={"cid":cid, "title":"Czat", "content":"Miejsce do pisania o wszystkim i o niczym"}, headers=self.headers)

    def import_topics(self):
        for topic in self.data["topics"]:
            title = topic["title"]
            content = topic["posts"][0]["content"]

            data = {"_uid":self.config["_uid"], "cid":self.urls["post_category_id"], "title":title, "content":content}
            response = self.session.post(self.urls["forum_url"]+"/api/v2/topics", data=data, headers=self.headers)
            response = response.json()
            if response["code"] == "ok":
                self.tids.append(response["payload"]["topicData"]["tid"])
            else:
                raise RuntimeError("Error "+response["code"]+"\n"+str(response))
            sleep(0.01)
    def import_posts(self):
        for i, tid in reversed(list(enumerate(self.tids))):
            posts = self.data["topics"][i]["posts"]
            for post in posts[1:]:
                data = {"_uid":self.config["_uid"], "content":self.parse_post(post)}
                self.session.post(self.urls["forum_url"]+"/api/v2/topics/"+str(tid), data=data, headers=self.headers)
                sleep(0.01)
    def parse_post(self, post):
        post["content"] = post["content"].replace("\n", "\n> ")
        content = """#### ![avatar {0}]({1}) %(#344576)[{0}]
>{2}""".format(post["username"], post["avatar"], post["content"])
        return content
    
    def import_character_sheet_template(self):
        title = "Wzór karty postaci"
        content = self.data["character_sheet_template"]["content"]
        data = {"_uid":self.config["_uid"], "cid":self.urls["character_sheet_category_id"], "title":title, "content":content}
        self.session.post(self.urls["forum_url"]+"/api/v2/topics", data=data, headers=self.headers)

if __name__=="__main__":
    a = nodebb_import()
    a.import_topics()
    a.import_posts()
    a.import_character_sheet_template()
    print("done!")