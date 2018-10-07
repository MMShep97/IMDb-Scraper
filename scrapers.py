# -*- coding: utf-8 -*-
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time

class IMDBScraper:

    page_size = 100
    num_pages = 10
    num_movies = num_pages * page_size
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
        self.movie_list.append(Film(movie_title, self.movie_index, personnel_list, [None]*self.num_movies))

        print(self.movie_index)

        #Add to movie_list
        self.movie_index += 1



class Film:
    title = ""
    index = 0
    personnel_list = []
    similarity_list = []
    
    def __init__(self, title, index, personnel_list, similarity_list):
        self.title = title
        self.index = index
        self.personnel_list = personnel_list
        self.similarity_list = similarity_list
        
    def getTitle(self):
        return self.title
    
    def getIndex(self):
        return self.index
    
    def getPersonnelList(self):
        return self.personnel_list
    
    def getSimilarityList(self):
        return self.similarity_list





# Main

start = time.time()
        
def compareMovies(movie1, movie2):
    num_similarities = 0
    for person1 in movie1.personnel_list:
        for person2 in movie2.personnel_list:
            if person1 == person2:
                num_similarities += 1

    movie1.similarity_list[movie2.index] = num_similarities
    movie2.similarity_list[movie1.index] = num_similarities


scarper = IMDBScraper()

for i in range(1, 1+scarper.num_pages):  # (i = 0: i < X; i++)
    cast_and_crew_url_list = scarper.get_cast_and_crew_urls(scarper.get_imdb_page(i))

    #for the 100 movies on the current page
    for url in cast_and_crew_url_list:

        #create movie object
        scarper.scrape_movie(url)


for mov1 in range(0, len(scarper.movie_list)):
    for mov2 in range(mov1, len(scarper.movie_list)):
        compareMovies(scarper.movie_list[mov1], scarper.movie_list[mov2])


#prints matrix
# for movie in scarper.movie_list:
#     print(movie.similarity_list)

pair_list = [0]

for row in range(0, scarper.num_movies):

    # for some movie
    for sim_sum_spot in range(row, scarper.num_movies):

        # sim_sum_spot starts at the self-referential sim_sum and moves right for each movie
        if scarper.movie_list[row].similarity_list[sim_sum_spot] > len(pair_list):
            for i in range(len(pair_list)-1, scarper.movie_list[row].similarity_list[sim_sum_spot]):
                pair_list.append(0)
        pair_list[scarper.movie_list[row].similarity_list[sim_sum_spot]] += 1

for i in range(0, len(pair_list)):
    print(i, end=" ")
    print(pair_list[i])

end = time.time()
print(end-start)

# stop self-comparing - throws off connection count