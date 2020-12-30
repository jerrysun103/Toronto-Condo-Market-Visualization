import pandas as pd
import numpy as np
import urllib.request
import bs4 as bs
import time
from datetime import date
from random import random


def download_links(total_pages_num, url_prefix, start_offset, end_offset):
    links_done = 0
    links = pd.DataFrame(columns=['link'])  

    for page in range(1,total_pages_num + 1):
    
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        
        url = url_prefix + str(page)
        
        headers={'User-Agent':user_agent,} 

        request=urllib.request.Request(url,None,headers) #The assembled request
        data_raw = urllib.request.urlopen(request).read().decode('utf-8')
        
        # print(data_raw)

        data_split = data_raw.split('<a class="listing-prop')[1:]

        sleep_time = random()
        time.sleep(sleep_time)

        one_page_homes_num = len(data_split)

        # print("there are {} homes in one page".format(one_page_homes_num))

        for post in range(one_page_homes_num): 

            try:
                start = data_split[post].find('href=')
                end = data_split[post].find(' target=')
                links.loc[links_done] = data_split[post][(start + start_offset):(end - end_offset)]
                links_done += 1
            except:
                print("An exception occurred")
        
        print("download links on page {}".format(page))

    today = date.today()
    day = today.strftime("%b-%d-%Y")

    if "sale" in url_prefix:
        links.to_csv('links_data/for_sale_links/house_for_sale_links_{}.csv'.format(day))
    elif "sold" in url_prefix:
        links.to_csv('links_data/sold_links/house_sold_links_{}.csv'.format(day))
    else:
        print("error in url prefix")


def download_home_data(link_path):
    #read links 
    links_df = pd.read_csv(link_path, index_col='Unnamed: 0')
    res_df = data = pd.DataFrame(columns=['title', 'final_price', 'list_price', 'bedrooms','bathrooms','den','sqft','parking','description','Unit No','type',
    'full_link','full_address'])

if __name__ == '__main__':
    for_sale_url_prefix = 'https://www.realmaster.com/en/for-sale/Toronto-ON?page='
    sold_url_prefix = "https://www.realmaster.com/en/sold-price/Toronto-ON?page="
    start_offset = 6
    end_offset = 1

    # hard code for these two number
    # do automation in future
    total_pages_num_for_sale = 170
    total_pages_num_for_sold = 90

    # download links for sale homes
    download_links(total_pages_num_for_sale, for_sale_url_prefix, start_offset, end_offset)

    # download links for sold homes
    download_links(total_pages_num_for_sold, sold_url_prefix, start_offset, end_offset)