# -*- coding: utf-8 -*-
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time
import csv


class IMDBScraper:
    page_size = 1
    num_pages = 1
    num_movies = num_pages * page_size
    movie_index = 0
    movie_list = []
    master_personnel_list = []
    master_personnel_label_list = []

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

    # creates Movie object with title and cast/crew list as objects
    def scrape_movie(self, url):
        raw_html = scarper.simple_get(
            url)  # might be an issue? can I use scarper to call a function inside the class that it's the type of?
        html = BeautifulSoup(raw_html, 'html.parser')

        personnel_list = []
        num_cast_members = 50  # formerly 20. no danger in going higher: if movie only has 10 cast members, just gets them all

        movie_title = html.find('div', class_='parent').h3.a.text

        # gets all crew members in first X tables (all crew personnel down to makeup
        for crew_table in html.find_all(class_="simpleTable simpleCreditsTable")[:25]:  # formerly [:10], now goes down to music dep (ish)
            for a in crew_table.find_all('a'):
                if a.text[1:-1] not in personnel_list:  # add to movie personnel list
                    personnel_list.append(a.text[1:-1])
                if a.text[1:-1] not in self.master_personnel_list:  # add to master personnel list
                    self.master_personnel_list.append(a.text[1:-1])

        print("------------------------------------------------------------------------")

        for header_index in range(0,25):
            if header_index > 2:
                table_index = header_index -1
            else:
                table_index = header_index
            header = html.find_all(class_="dataHeaderWithBorder")[header_index]
            if not header_index == 2:  # skip cast
                header_text = header.text[0:-1].rstrip()
                table = html.find_all(class_="simpleTable simpleCreditsTable")[table_index]
                for a in table.find_all('a'):
                    print(header_text + ": " + a.text[1:-1])
        print("------------------------------------------------------------------------")


        # gets specific number oc cast members, and adds to the personnel list
        for tr in html.find_all('tr'):
            for td in tr.find_all('td', class_='primary_photo'):
                if num_cast_members > 0:
                    if td.a.img['title'] not in personnel_list:
                        personnel_list.append(td.a.img['title'])  # add to movie personnel list
                    if td.a.img['title'] not in self.master_personnel_list:
                        self.master_personnel_list.append(td.a.img['title'])  # add to master list if not already there
                        self.master_personnel_label_list.append("cast")
                        print("cast: " + td.a.img['title'])

                num_cast_members -= 1

        print(movie_title, end=" ")
        print(len(personnel_list))

        # CREATE MOVIE OBJECT
        self.movie_list.append(Film(movie_title, self.movie_index, personnel_list, [None] * self.num_movies))

        # Add to movie_list
        self.movie_index += 1


class Film:
    title = ""
    index = 0
    personnel_list = []
    similarity_list = []
    bin_list = []

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
    if (movie1 == movie2):
        movie1.similarity_list[movie1.index] = 0  # self-comparing slot = 0
    else:
        num_similarities = 0
        for person1 in movie1.personnel_list:
            for person2 in movie2.personnel_list:
                if person1 == person2:
                    num_similarities += 1

        movie1.similarity_list[movie2.index] = num_similarities
        movie2.similarity_list[movie1.index] = num_similarities


scarper = IMDBScraper()

for i in range(1, 1 + scarper.num_pages):  # (i = 0: i < X; i++)

    cast_and_crew_url_list = scarper.get_cast_and_crew_urls(scarper.get_imdb_page(i))

    # for the 100 movies on the current page
    for url in cast_and_crew_url_list:
        # get cast and crew, create movie object
        scarper.scrape_movie(url)

for mov1 in range(0, len(scarper.movie_list)):
    for mov2 in range(mov1, len(scarper.movie_list)):
        compareMovies(scarper.movie_list[mov1], scarper.movie_list[mov2])

# prints matrix
# for movie in scarper.movie_list:
#      print(movie.similarity_list)


# creates pair_list: number of pairs of movies with *index* number of connections
pair_list = [0]

# for some movie
for row in range(0, scarper.num_movies):

    # sim_sum_spot starts at the self-referential sim_sum and moves right for each movie
    for sim_sum_spot in range(row, scarper.num_movies):

        num_similarities = scarper.movie_list[row].similarity_list[sim_sum_spot]
        if num_similarities > (len(pair_list) - 1):
            for i in range(len(pair_list) - 1, num_similarities):
                pair_list.append(0)
        pair_list[num_similarities] += 1

# for i in range(0, len(pair_list)):
#     print(i, end=" ")
#     print(pair_list[i])

total_num_personnel = len(scarper.master_personnel_list)
print("length of master personnel list: " + str(total_num_personnel))
master_bin_list = []  # list of each movies binary list. Used to write to CSV

# create binary list of for each movie: length = length of master personnel list, each element is 1 or 0 if they have that person or not
for movie in scarper.movie_list:
    b_list = [0] * total_num_personnel
    for current_movie_mem in movie.personnel_list:
        b_list[(scarper.master_personnel_list).index(current_movie_mem)] = 1
    movie.bin_list = b_list
    master_bin_list.append(b_list)
    print(b_list)


with open("label_test.csv", "w", newline="") as f:
    mov_index = 0
    f.write("" + ', ')
    for item in scarper.master_personnel_label_list:
        f.write(item + ',')
    for sublist in master_bin_list:  # each sublist is a movie's bin_list
        f.write(scarper.movie_list[mov_index].title + ',')
        for item in sublist:
            f.write(str(item) + ',')
        f.write('\n')
        mov_index += 1

# with open("movie_personnel.csv", "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerows(master_bin_list)


# save the binary lists in csv or something so we don't have to scrape every time we try to learn on it
# cluster movies using long ass binary lists
# ideally - each column of the csv would have a title like actor, director, writer, editor, makeup, etc.
# to eventually be able to say where the movie connections came from (same team of writers, etc.)


end = time.time()
print("run time in seconds: " + str(end - start))

# -*- coding: utf-8 -*-
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time
import csv


class IMDBScraper:
    page_size = 10
    num_pages = 1
    num_movies = num_pages * page_size
    movie_index = 0
    movie_list = []
    master_personnel_list = []

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

    # creates Movie object with title and cast/crew list as objects
    def scrape_movie(self, url):
        raw_html = scarper.simple_get(
            url)  # might be an issue? can I use scarper to call a function inside the class that it's the type of?
        html = BeautifulSoup(raw_html, 'html.parser')

        personnel_list = []
        num_cast_members = 50  # formerly 20. no danger in going higher: if movie only has 10 cast members, just gets them all

        movie_title = html.find('div', class_='parent').h3.a.text

        # gets all crew members in first ten tables (all crew personnel down to makeup
        for crew_table in html.find_all(class_="simpleTable simpleCreditsTable")[
                          :25]:  # formerly [:10], now goes down to music dep (ish)
            for a in crew_table.find_all('a'):
                if a.text[1:-1] not in personnel_list:  # add to movie personnel list
                    personnel_list.append(a.text[1:-1])
                if a.text[1:-1] not in self.master_personnel_list:  # add to master personnel list
                    self.master_personnel_list.append(a.text[1:-1])

        # gets specific number oc cast members, and adds to the personnel list
        for tr in html.find_all('tr'):
            for td in tr.find_all('td', class_='primary_photo'):
                if num_cast_members > 0:
                    if td.a.img['title'] not in personnel_list:
                        personnel_list.append(td.a.img['title'])  # add to movie personnel list
                    if td.a.img['title'] not in self.master_personnel_list:
                        self.master_personnel_list.append(td.a.img['title'])  # add to master list if not already there

                num_cast_members -= 1

        print(movie_title, end=" ")
        print(len(personnel_list))

        # CREATE MOVIE OBJECT
        self.movie_list.append(Film(movie_title, self.movie_index, personnel_list, [None] * self.num_movies))

        # Add to movie_list
        self.movie_index += 1


class Film:
    title = ""
    index = 0
    personnel_list = []
    similarity_list = []
    bin_list = []

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
    if (movie1 == movie2):
        movie1.similarity_list[movie1.index] = 0  # self-comparing slot = 0
    else:
        num_similarities = 0
        for person1 in movie1.personnel_list:
            for person2 in movie2.personnel_list:
                if person1 == person2:
                    num_similarities += 1

        movie1.similarity_list[movie2.index] = num_similarities
        movie2.similarity_list[movie1.index] = num_similarities


scarper = IMDBScraper()

for i in range(1, 1 + scarper.num_pages):  # (i = 0: i < X; i++)

    cast_and_crew_url_list = scarper.get_cast_and_crew_urls(scarper.get_imdb_page(i))

    # for the 100 movies on the current page
    for url in cast_and_crew_url_list:
        # get cast and crew, create movie object
        scarper.scrape_movie(url)

for mov1 in range(0, len(scarper.movie_list)):
    for mov2 in range(mov1, len(scarper.movie_list)):
        compareMovies(scarper.movie_list[mov1], scarper.movie_list[mov2])

# prints matrix
# for movie in scarper.movie_list:
#      print(movie.similarity_list)


# creates pair_list: number of pairs of movies with *index* number of connections
pair_list = [0]

# for some movie
for row in range(0, scarper.num_movies):

    # sim_sum_spot starts at the self-referential sim_sum and moves right for each movie
    for sim_sum_spot in range(row, scarper.num_movies):

        num_similarities = scarper.movie_list[row].similarity_list[sim_sum_spot]
        if num_similarities > (len(pair_list) - 1):
            for i in range(len(pair_list) - 1, num_similarities):
                pair_list.append(0)
        pair_list[num_similarities] += 1

# for i in range(0, len(pair_list)):
#     print(i, end=" ")
#     print(pair_list[i])

total_num_personnel = len(scarper.master_personnel_list)
print("length of master personnel list: " + str(total_num_personnel))
master_bin_list = []  # list of each movies binary list. Used to write to CSV

# create binary list of for each movie: length = length of master personnel list, each element is 1 or 0 if they have that person or not
for movie in scarper.movie_list:
    b_list = [0] * total_num_personnel
    for current_movie_mem in movie.personnel_list:
        b_list[(scarper.master_personnel_list).index(current_movie_mem)] = 1
    movie.bin_list = b_list
    master_bin_list.append(b_list)
    print(b_list)

with open("movie_personnel1.csv", "w", newline="") as f:
    mov_index = 0
    for sublist in master_bin_list:  # each sublist is a movie's bin_list
        f.write(scarper.movie_list[mov_index].title + ',')
        for item in sublist:
            f.write(str(item) + ',')
        f.write('\n')
        mov_index += 1

# with open("movie_personnel.csv", "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerows(master_bin_list)


# save the binary lists in csv or something so we don't have to scrape every time we try to learn on it
# cluster movies using long ass binary lists
# ideally - each column of the csv would have a title like actor, director, writer, editor, makeup, etc.
# to eventually be able to say where the movie connections came from (same team of writers, etc.)


end = time.time()
print("run time in seconds: " + str(end - start))