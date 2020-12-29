import pandas as pd
import numpy as np
import urllib.request
import time

def download_links(total_pages_num):
    links_done = 0
    links = pd.DataFrame(columns=['link'])  

    for page in range(1,total_pages_num + 1):
    
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        url = "https://www.realmaster.com/en/for-sale/Toronto-ON?page=" + str(page)
        headers={'User-Agent':user_agent,} 

        request=urllib.request.Request(url,None,headers) #The assembled request
        data_raw = urllib.request.urlopen(request).read()
        
        print(data_raw)
        

        # data_split = data_raw.split(b'/listing-status>')[1:]
        # time.sleep(1)
        
        # for post in range(24): 

        #     try:
        #         start = data_split[post].find(b'href="/')
        #         end = data_split[post].find(b'-vow"')
        #         links.loc[links_done] = data_split[post][(start+7):(end+4)]

        #         links_done += 1
        #     except:
        #         print("An exception occurred")
                
    links.to_csv('house_links.csv')

if __name__ == '__main__':
    download_links(1)