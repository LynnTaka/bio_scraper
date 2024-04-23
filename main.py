from biocrawler import *

#main function to run the crawler
if __name__ == '__main__':
    crawler = BioCrawler('https://www.cpp.edu/sci/biological-sciences/index.shtml')
    crawler.connectDB()
    targets_found = crawler.crawlerThread(num_targets=10)
    print(targets_found)