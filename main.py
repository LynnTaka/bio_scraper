from biocrawler import *
from bioparser import *

#main function to run the crawler/parser
if __name__ == '__main__':
    #Crawler portion
    crawler = BioCrawler('https://www.cpp.edu/sci/biological-sciences/index.shtml')
    crawler.connectDB()
    targets_found = crawler.crawlerThread(num_targets=10)
    print(targets_found)

    #Parser portion
    parser = BioParser()
    parser.connectDB()
    parser.index_faculty_homepages()
    parser.process_text()
