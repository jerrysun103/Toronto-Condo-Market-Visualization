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

        request=urllib.request.Request(url,None,headers) 
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
        print("Error in url prefix")


def download_home_data(link_path):
    #read links 
    links_df = pd.read_csv(link_path, index_col = 0)
    num_of_link = links_df.shape[0]
    counter = 0
    #print(links_df.head(5))

    attributes_array = ['title', 'MLS ID', 'transaction_type', 'home_type', 'unit', 'level', 
    'first day on market', 'final_price', 'list_price', 'bedrooms', 'bathrooms', 'den', 'sqft', 'exposure', 
    'parking', 'locker', 'maintanance fee', 'description', 'link', 'address']

    res_df = pd.DataFrame(columns = attributes_array)
    for num in range(num_of_link):
        
        url = links_df.link[num]
        print(url)
        # print("-----------------------------")
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        
        headers={'User-Agent':user_agent,} 

        request=urllib.request.Request(url, None, headers) 

        html_doc = urllib.request.urlopen(request).read()
                
        soup = bs.BeautifulSoup(html_doc, 'html.parser')

        # populate link url
        res_df.loc[num, 'link'] = url

        # populate title & transaction_type
        title_components_lst = soup.title.contents[0].split('|')
        title_part_one = title_components_lst[0].strip()
        title_part_two = title_components_lst[1].strip()
        res_df.loc[num, 'title'] = title_part_one + " | " + title_part_two

        if "Sale" in title_part_two:
            res_df.loc[num, 'transaction_type'] = "for sale"
        elif "Sold" in title_part_two:
            res_df.loc[num, 'transaction_type'] = "sold"
        else:
            print("Error,link No.{} 's title information is not expected".format(num))

        print(title_part_one + " | " + title_part_two)
        # populate others
        # MLS ID, home_type, unit, level, first day on market, final_price, list_price, 
        # bedrooms, bathrooms, den, sqft, exposure, parking, locker, 
        # maintanance fee, description, address

        # print(soup.prettify())
        counter += 1
            
        # try:
        # except:
        #     print("link No.{} is a bad link".format(num))
        if num == 100:
            exit()
        else:
            print("_________________")

if __name__ == '__main__':
    # Part One: download links data
    # for_sale_url_prefix = 'https://www.realmaster.com/en/for-sale/Toronto-ON?page='
    # sold_url_prefix = "https://www.realmaster.com/en/sold-price/Toronto-ON?page="
    # start_offset = 6
    # end_offset = 1

    # # hard code for these two number
    # # do automation in future
    # total_pages_num_for_sale = 170
    # total_pages_num_for_sold = 90

    # # download links for sale homes
    # download_links(total_pages_num_for_sale, for_sale_url_prefix, start_offset, end_offset)

    # # download links for sold homes
    # download_links(total_pages_num_for_sold, sold_url_prefix, start_offset, end_offset)

    # Part two: download homes data
    for_sale_link_path = "links_data/for_sale_links/house_for_sale_links_Dec-29-2020.csv"
    sold_link_path = "links_data/sold_links/house_sold_links_Dec-29-2020.csv"

    download_home_data(for_sale_link_path)