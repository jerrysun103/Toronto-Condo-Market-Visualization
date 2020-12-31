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

    # attributes in output dataframe
    attributes_array = ['title', 'MLS ID', 'transaction_type', 'home_type', 'level', 
    'first day on market', 'final_price', 'list_price', 'bedrooms', 'bathrooms', 'den', 'sqft', 'exposure', 
    'parking', 'locker', 'maintanance fee', 'description', 'link', 'address']

    # attributes in realmaster name
    # MLS ID, home_type, level, bedrooms, bathrooms, den, exposure, parking, locker, maintanance fee
    realmaster_summary_dims = ["ID", "Ownership Type", "Level", "Rooms", "Exposure", "Parking Spots", 
    "Locker", "Maint Fee"]

    # mapping from realmaster name to output dataframe name
    mapping_dict = {"ID":'MLS ID', "Ownership Type":'home_type', "Level":'level', "Exposure":'exposure', 
    "Parking Spots":'parking', "Locker":'locker', "Maint Fee": 'maintanance fee'}

    res_df = pd.DataFrame(columns = attributes_array)
    for num in range(num_of_link):
        
        url = links_df.link[num]

        print(url)
        print("-----------------------------")

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

        # print(title_part_one + " | " + title_part_two)
        # populate others
        # MLS ID, home_type, level, bedrooms, bathrooms, den, exposure, parking, locker, maintanance fee
        raw_html_lables = list(soup.findAll("span", {"class": "summary-label"}))
        raw_html_values = list(soup.findAll("span", {"class": "summary-value"}))
        
        assert(len(raw_html_lables) == len(raw_html_values))

        html_lables, html_values = [], []
        
        for i in range(len(raw_html_lables)):
            # for lable
            raw_labe = str(raw_html_lables[i])
            start = raw_labe.find(">")
            end = raw_labe.find("</")
            lable = raw_labe[start+1:end]

            # for value
            raw_value = str(raw_html_values[i])
            start = raw_value.find(">")
            end = raw_value.find("</")
            value = raw_value[start+1:end]

            html_lables.append(lable)
            html_values.append(value)
        
        for i in range(len(html_lables)):
            lable = html_lables[i]
            value = html_values[i]

            if lable == "Rooms":
                # bedroom vs bathroom vs den
                bedrooms = value.split(',')
                
                # for bedroom & den
                if "+" in bedrooms[0]:
                    # case 1: den exist
                    plus_index = bedrooms[0].find("+")
                    bedroom_num = bedrooms[0][plus_index - 1:plus_index]
                    den_num = bedrooms[0][plus_index + 1:plus_index + 2]
                else:
                    # case 2: no den, all rooms are bedroom
                    start = bedrooms[0].find(":")
                    bedroom_num = bedrooms[0][start+1:]
                    res_df.loc[num, "bedrooms"] = bedroom_num
                    res_df.loc[num, "den"] = 0
                
                # for bathroom
                comma_index = bedrooms[2].find(":")
                bathroom_num = bedrooms[2][comma_index+1:]
                res_df.loc[num, "bathrooms"] = bathroom_num
            else:
                if lable in mapping_dict:
                    res_df.loc[num, mapping_dict[lable]] = value

        #TODO: check findAll return is None or not for following
        # Remaining: sqft, first day on market, final_price, list_price, address, description
        # sqft
        html_sqft = str(list(soup.findAll("span", {"class": "listing-prop-sqft"}))[0])
        sqft_num = html_sqft.split("|")[1].split(" ")[1]
        res_df.loc[num, 'sqft'] = sqft_num
      
        #first day on market
        # <p class="listing-prop-size"> <span class="listing-prop-dom"> 12 DOM </span>
        # <span>
        # (20201204 - 20201216)
        # </span>
        # </p>
        html_fdm = str(list(soup.findAll("p", {"class": "listing-prop-size"}))[0])
        first_day_on_market = html_fdm.split("<span>")[1].strip()[1:9]
        res_df.loc[num, 'first day on market'] = first_day_on_market

        # list price
        # <h6 class="detail-lp">
        #    $539,900 Asking price
        #   </h6>
        


        # final price
        # <span class="detail-price">
        #     $535,000 Sold
        #    </span>

        # <span class="listing-prop-address">
        #    44 Beverly Glen Blvd
        #   </span>
        #   <p class="listing-prop-address">
        #    Toronto, Ontario, M1W1W2
        #   </p>
        
        
        print(soup.prettify())
        
        counter += 1
        
        # try:
        # except:
        #     print("link No.{} is a bad link".format(num))
        if num == 0:
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