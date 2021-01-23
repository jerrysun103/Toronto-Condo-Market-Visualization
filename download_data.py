import pandas as pd
import numpy as np
import urllib.request
import bs4 as bs
import time
import requests
from datetime import date
from random import random


def download_links(total_pages_num, url_prefix, start_offset, end_offset):
    links_done = 0
    links = pd.DataFrame(columns=['link'])  

    for page in range(1,total_pages_num + 1):
    
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        
        url = url_prefix + str(page)
        
        headers={'User-Agent':user_agent} 

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


def download_home_data(link_path, cookies):
    #read links 
    links_df = pd.read_csv(link_path, index_col = 0)
    num_of_link = links_df.shape[0]
    counter = 0
    #print(links_df.head(5))

    # attributes in output dataframe
    attributes_array = ['title', 'MLS ID', 'transaction_type', 'home_type', 'level', 
    'first day on market', 'last day on market', 'sold_price', 'list_price', 'bedrooms', 'bathrooms', 'den', 'sqft', 'exposure', 
    'parking', 'locker', 'maintanance fee', 'description', 'link', 'address']

    # attributes in realmaster name
    # MLS ID, home_type, level, bedrooms, bathrooms, den, exposure, parking, locker, maintanance fee
    realmaster_summary_dims = ["ID", "Type", "Level", "Rooms", "Exposure", "Parking Spots", 
    "Locker", "Maint Fee"]

    # mapping from realmaster name to output dataframe name
    mapping_dict = {"ID":'MLS ID', "Type":'home_type', "Level":'level', "Exposure":'exposure', 
    "Parking Spots":'parking', "Locker":'locker', "Maint Fee": 'maintanance fee'}

    res_df = pd.DataFrame(columns = attributes_array)

    for num in range(num_of_link):
        sleep_time = random()
        time.sleep(sleep_time)
        
        #below is for test
        # if num == 1:
        #     break
        try:
            url = links_df.link[num]

            # below for test
            # url = "https://www.realmaster.com/en/toronto-on/100-mornelle-crt/1016-morningside-TRBE5000585?d=https://www.realmaster.com/en/sold-price/Toronto-ON?page=79"
            

            headers={'User-Agent': 'Mozilla/5.0'} 

            response = requests.get(url, cookies=cookies, headers=headers)
            
            soup = bs.BeautifulSoup(response.text, 'html.parser')
            #print(soup.prettify())

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

            
            
            if len(raw_html_lables) != len(raw_html_values):
                print("Error: Line 131")
            if len(raw_html_lables) == 0:
                print("Error: Check cookies information")

        
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
                    # print(value)
                    bedrooms = value.split(',')
                    bedroom_index = [i for i, elem in enumerate(bedrooms) if 'Bed' in elem][0]
                    # for bedroom & den
                    if "+" in bedrooms[bedroom_index]:
                        # case 1: den exist
                        plus_index = bedrooms[bedroom_index].find("+")
                        bedroom_num = bedrooms[bedroom_index][plus_index - 1:plus_index]
                        den_num = bedrooms[bedroom_index][plus_index + 1:plus_index + 2]
                        res_df.loc[num, "bedrooms"] = bedroom_num
                        res_df.loc[num, "den"] = den_num
                    else:
                        # case 2: no den, all rooms are bedroom
                        start = bedrooms[bedroom_index].find(":")
                        bedroom_num = bedrooms[bedroom_index][start+1:]
                        res_df.loc[num, "bedrooms"] = bedroom_num
                        res_df.loc[num, "den"] = 0
                    
                    # for bathroom
                    bathroom_index = [i for i, elem in enumerate(bedrooms) if 'Bath' in elem][0]
                    comma_index = bedrooms[bathroom_index].find(":")
                    bathroom_num = bedrooms[bathroom_index][comma_index+1:]
                    res_df.loc[num, "bathrooms"] = bathroom_num
                else:
                    if lable in mapping_dict:
                        res_df.loc[num, mapping_dict[lable]] = value

            # TODO: check findAll return is None or not for following
            # Remaining: sqft, first day on market, sold_price, list_price, address, description
            # sqft
            if soup.findAll("span", {"class": "listing-prop-sqft"}) != []:
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

            # if sold, populate the last day on market
            if "Sold" in title_part_two:
                last_day_on_market = html_fdm.split("<span>")[1].strip()[12:20]
                res_df.loc[num, 'last day on market'] = last_day_on_market

            # list price and sold price
            # case one: for sale
            if "Sale" in title_part_two:
                html_sale_price = str(list(soup.findAll("span", {"class": "detail-price"}))[0])
                start = html_sale_price.find("$")
                end = html_sale_price.find(" |")
                sale_price = html_sale_price[start+1:end]
                res_df.loc[num, 'list_price'] = sale_price
                
            # case two: sold
            else:
                # list price
                # <h6 class="detail-lp">
                #    $539,900 Asking price
                #   </h6>
                html_list_price = str(list(soup.findAll("h6", {"class": "detail-lp"}))[0])
                start = html_list_price.find("$")
                end = html_list_price.find(" Asking")
                list_price = html_list_price[start+1:end]
                res_df.loc[num, 'list_price'] = list_price

                # final price
                # <span class="detail-price">
                #     $535,000 Sold
                #    </span>
                html_sold_price = str(list(soup.findAll("span", {"class": "detail-price"}))[0])
                start = html_sold_price.find("$")
                end = html_sold_price.find(" Sold")
                sold_price = html_sold_price[start+1:end]
                res_df.loc[num, 'sold_price'] = sold_price


            # address
            # <span class="listing-prop-address">
            #    44 Beverly Glen Blvd
            #   </span>
            #   <p class="listing-prop-address">
            #    Toronto, Ontario, M1W1W2
            #   </p>
            html_address_first_half = str(list(soup.findAll("span", {"class": "listing-prop-address"}))[0])
            start = html_address_first_half.find(">")
            end = html_address_first_half.find("</")
            address_first_half = html_address_first_half[start+1:end].strip()

            html_address_second_half = str(list(soup.findAll("p", {"class": "listing-prop-address"}))[0])
            s = html_address_second_half.find(">")
            e = html_address_second_half.find("</")
            address_second_half = html_address_second_half[s+1:e].strip()
            
            address = address_first_half + ", " + address_second_half
            res_df.loc[num, 'address'] = address
            
            # description
            # <meta content="19 Broadleaf Rd  Toronto Ontario, 3Bd 2Ba House For Sale, 
            # Asking Price: undefined. 
            # Fully Renovated Cozy Home Near Shop At Don Mills, $$$ Spent. 
            # ...
            # ...
            # All New Ceiling And Drywall." 
            # name="description"/>
            html_description = str(list(soup.findAll("meta", {"name": "description"}))[0])
            start = html_description.find(".")
            end = html_description.find("name=")
            description = html_description[start+1:end].strip()
            res_df.loc[num, 'description'] = description

            # print(description)
            # print("----- divide -----")
            
            
            print("download data for home {}".format(counter))
            counter += 1

        except:
            print("Error: link No.{} is a bad link, url: {}".format(num, url))

    # store the data frame

    t = date.today()
    d = today.strftime("%b-%d-%Y")

    if "sale" in link_path:
        res_df.to_csv('home_data/for_sale_data/home_for_sale_data_{}.csv'.format(d))
    elif "sold" in link_path:
        res_df.to_csv('home_data/sold_data/home_sold_data_{}.csv'.format(d))
    else:
        print("Error in link path") 

def valid_page_helper(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent} 

    request=urllib.request.Request(url, None, headers) 

    data_raw = urllib.request.urlopen(request).read().decode('utf-8')

    if "No result found" in data_raw:
        return False
    else:
        return True

def binary_search(link_prefix, num_lst):

    # print(num_lst)

    # base
    if len(num_lst) == 1:
        url = link_prefix + str(num_lst[0])
        assert(valid_page_helper(url) == True)
        return num_lst[0]

    elif len(num_lst) == 2:
        
        url_1 = link_prefix + str(num_lst[0])
        url_2 = link_prefix + str(num_lst[1])
        bool_1 = valid_page_helper(url_1)
        bool_2 = valid_page_helper(url_2)

        if bool_2:
            res = num_lst[1]
            return res
        elif bool_1:
            res = num_lst[0]
            return res
        else:
            exit("something uknown wrong")

    else:
        min_url = link_prefix + str(num_lst[0])
        max_url = link_prefix + str(num_lst[-1])

        left = valid_page_helper(min_url)
        right = valid_page_helper(max_url)

        if left and right:
            print(min_url)
            print(max_url)
            exit("Need to adjust the initial page number")
        else:
            if right:
                return binary_search(link_prefix, num_lst[-1:])
                
            middle_num = len(num_lst) // 2
            middle_url = link_prefix + str(num_lst[middle_num])
            middle = valid_page_helper(middle_url)
            
            if middle and not right:
                return binary_search(link_prefix, num_lst[middle_num:])
            elif not middle:
                return binary_search(link_prefix, num_lst[:middle_num+1])

        

def find_the_valid_page_numbers(sale_link_prefix, sold_link_prefix):
    # initial numbers
    pages_num_for_sale = 140
    pages_num_for_sold = 80
    multiple = 2

    sale_page_num_lst = list(range(1, pages_num_for_sale * multiple))
    sold_page_num_lst = list(range(1, pages_num_for_sold * multiple))
    
    # Part one: extract the vilid page number for sale
    pages_num_for_sale = binary_search(sale_link_prefix, sale_page_num_lst)
    

    # Part two: extract the vilid page number for sold
    pages_num_for_sold = binary_search(sold_link_prefix, sold_page_num_lst)

    return pages_num_for_sale, pages_num_for_sold

if __name__ == '__main__':
    # Part One: download links data
    for_sale_url_prefix = 'https://www.realmaster.com/en/for-sale/Toronto-ON?page='
    sold_url_prefix = "https://www.realmaster.com/en/sold-price/Toronto-ON?page="
    start_offset = 6
    end_offset = 1

    # find max valid pages 
    
    total_pages_num_for_sale, total_pages_num_for_sold = find_the_valid_page_numbers(for_sale_url_prefix, sold_url_prefix)
    print("Find max valid pages, sale:{}, sold:{}".format(total_pages_num_for_sale, total_pages_num_for_sold))

    # download links for sale homes
    download_links(total_pages_num_for_sale, for_sale_url_prefix, start_offset, end_offset)

    # download links for sold homes
    download_links(total_pages_num_for_sold, sold_url_prefix, start_offset, end_offset)

    #----------------------------------------------------------------------------------------

    #Part two: download homes data
    # today = date.today()
    # today_date = today.strftime("%b-%d-%Y")

    # for_sale_link_path = "links_data/for_sale_links/house_for_sale_links_{}.csv".format(today_date)
    # sold_link_path = "links_data/sold_links/house_sold_links_{}.csv".format(today_date)

    # cookies={'locale':'en',
    #         'cmate.sid':'6Eu3WrqKaeJjspMiqbedWod6H7ER5NJxXEGtlVJShdmKPbFEdPmfTBDZkjxq5qce',
    #         'k': '1eef099d41e1ce2f40c6cba924d7a89cd5dcb515'}

    # # print("Start: Download home data for all homes for sale\n")
    # # download_home_data(link_path=for_sale_link_path, cookies=cookies)
    # # print("Completed: Download home data for all homes for sale\n")

    # print("Start: Download home data for all homes sold\n")
    # download_home_data(link_path=sold_link_path, cookies=cookies)
    # print("Completed: Download home data for all homes sold\n")
