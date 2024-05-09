from biocrawler import *
from bioparser import *
from cosine_similarity import *

def menu():
    print()
    print("===================================================")
    print("             BIOLOGY DEPARTMENT SEARCH ENGINE       ")
    print("===================================================")
    print("1. SEARCH")
    print("2. EXIT")
    choice = input(f'Enter your choice (1/2): ')
    return choice

def search_menu():
    print()
    print("===================================================")
    print("                     SEARCH MENU                   ")
    print("===================================================")
    print()
    query = input('Enter your search query: ').strip()
    return query

#main function to run the crawler/parser
if __name__ == '__main__':
    # #Crawler portion
    # crawler = BioCrawler('https://www.cpp.edu/sci/biological-sciences/index.shtml')
    # crawler.connectDB()
    # targets_found = crawler.crawlerThread(num_targets=10)
    # print(targets_found)
    #
    # #Parser and index portion
    # parser = BioParser()
    # parser.connectDB()
    # parser.index_faculty_homepages()
    # parser.process_text()

    # searching
    index = load()

    while (1):
        choice = menu()
        if choice == '2':
            break
        elif choice != '1':
            print('INVALID')
            print()
            continue
        query = search_menu()
        search(query, index)

