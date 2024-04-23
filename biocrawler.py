from urllib.parse import urljoin, urlparse
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from collections import deque
from bs4 import BeautifulSoup
import pymongo

class BioCrawler:
    def __init__(self, seedURL):
        self.frontier = deque([seedURL])
        self.vis = set()

    def connectDB(self):
        DB_NAME = 'CPPBIO'
        DB_HOST = 'localhost'
        DB_PORT = 27017
        client = pymongo.MongoClient(DB_HOST, DB_PORT)
        db = client[DB_NAME]
        self.pages = db.pages

    #function to check if the page is a professor page with the correct format
    def target_page(self, bs):
        return bs.find('div', {'class': 'fac-info'})
    
    #function to store the page in the database
    def store_page(self, url, bs):
        self.pages.insert_one({'url': url, 'html': str(bs)})

    def crawlerThread(self, num_targets):
        #list of professor pages to be returned
        targets_found = []
        #add the seed url to visited since it is the first page to be visited
        self.vis.add(self.frontier[0])
        #while there are still pages to visit and we have not found the desired number of targets
        while self.frontier and len(targets_found) < num_targets:
            url = self.frontier.popleft()
            #print current page being visited in terminal
            print("Current page:", url)
            try:
                #open the page and parse the html
                html = urlopen(url)
                bs = BeautifulSoup(html, 'html.parser')
                self.store_page(url, bs)
                if self.target_page(bs):
                    targets_found.append(url)
                    continue
                #find all links on the page
                for links in bs.find_all('a', href=True):
                    #join the link to the base url
                    link = urljoin(url, links['href'].strip())
                    #check if the link is not already visited and is a cpp.edu link
                    if urlparse(link).netloc.endswith("cpp.edu") and link not in self.vis:
                        self.frontier.append(link)
                        self.vis.add(link)
            #if the page cannot be accessed, print page access failed along with the error type
            except (HTTPError, URLError) as e:
                print("Access failed:", url + " Error Type:", e)
                continue
        #return the list of professor pages 
        return targets_found

#main function to run the crawler
if __name__ == '__main__':
    crawler = BioCrawler('https://www.cpp.edu/sci/biological-sciences/index.shtml')
    crawler.connectDB()
    targets_found = crawler.crawlerThread(num_targets=10)
    print(targets_found)