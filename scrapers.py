# -*- coding: utf-8 -*-
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


class IMDBScraper:

    page_size = 10
    movie_index = 0
    movie_list = []

    def simple_get(self, url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None


    def is_good_response(self, resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 and content_type is not None 
                and content_type.find('html') > -1)
        

    def log_error(self, e):
        """
        It is always a good idea to log errors. 
        This function just prints them, but you can
        make it do anything.
        """
        print(e)
        
    # get list of movie full cast and crew list urls
    def get_cast_and_crew_urls(self, page):
        raw_html = self.simple_get(page)
        html = BeautifulSoup(raw_html, 'html.parser')
        url_count = 0
        full_cc_urls = []
        root_path = 'https://imdb.com/title/'
        tail_path = '/fullcredits/?ref_=tt_ov_st_sm'
        for h3 in html.select('h3'):
            for a in h3.select('a'):
                url_count += 1
                if url_count <= self.page_size:
                    path_elements = a['href'].split("/")
                    full_cc_urls.append(root_path + path_elements[2] + tail_path)
        return full_cc_urls

    def get_imdb_page(self, num):
        return 'https://www.imdb.com/list/ls057823854/?sort=list_order,asc&st_dt=&mode=detail&page=' + str(num)


    #creates Movie object with title and cast/crew list as objects
    def scrape_movie(self, url):
        raw_html = scarper.simple_get(url) #might be an issue? can I use scarper to call a function inside the class that it's the type of?
        html = BeautifulSoup(raw_html, 'html.parser')

        personnel_list = []
        num_cast_members = 20

        movie_title = html.find('div', class_='parent').h3.a.text

        # gets all crew members in first ten tables (all crew personnel down to makeup
        for crew_table in html.find_all(class_="simpleTable simpleCreditsTable")[:10]:
            for a in crew_table.find_all('a'):
                if a.text[1:-1] not in personnel_list:
                    personnel_list.append(a.text[1:-1])

        # gets specific number oc cast members, and adds to the personnel list
        for tr in html.find_all('tr'):
            for td in tr.find_all('td', class_='primary_photo'):
                if num_cast_members > 0:
                    personnel_list.append(td.a.img['title'])
                num_cast_members -= 1

        #CREATE MOVIE OBJECT
        self.movie_list.append(Film(movie_title, self.movie_index, personnel_list))

        #Add to movie_list
        self.movie_index += 1



class Film:
    title = ""
    index = 0
    personnel_list = []
    similarity_list = []
    
    def __init__(self, title, index, personnel_list):
        self.title = title
        self.index = index
        self.personnel_list = personnel_list
        
    def getTitle(self):
        return self.title
    
    def getIndex(self):
        return self.index
    
    def getPersonnelList(self):
        return self.personnel_list
    
    def getSimilarityList(self):
        return self.similarity_list



scarper = IMDBScraper()

f = Film("golf film", 0, [1, 2, 3])
print(f.getTitle())
print(f.getIndex())
print(f.getPersonnelList())

for i in range(1, 2):  # (i = 0: i < X; i++)
    cast_and_crew_url_list = scarper.get_cast_and_crew_urls(scarper.get_imdb_page(i))

    #for the 100 movies on the current page
    for url in cast_and_crew_url_list:

        #create movie object
        scarper.scrape_movie(url)

#for movie1 in scarper.movie_list:
