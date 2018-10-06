# -*- coding: utf-8 -*-
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

class IMDBScraper:

    page_size = 100


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
    def scrape_full_cc(self, page):
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
    


page = "https://www.imdb.com/list/ls057823854/?sort=list_order,asc&st_dt=&mode=detail&page=1"
scarper = IMDBScraper()
full_cc_urls = scarper.scrape_full_cc(page)
for url in full_cc_urls:
    print(url)



        
        