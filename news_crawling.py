import datetime
from tqdm import tqdm_notebook
from tqdm import trange
import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time, random
from pprint import pprint
import pandas as pd


days_range = []

start = datetime.datetime.strptime("2020-06-01", "%Y-%m-%d")
end = datetime.datetime.strptime("2020-06-03", "%Y-%m-%d")

date_generated = [start+datetime.timedelta(days=x) for x in range(0, (end-start).days)]

for date in date_generated:
    days_range.append(date.strftime("%Y-%m-%d"))

print(days_range)

def get_bs_obj(url):
    results = requests.get(url)
    bs_obj = BeautifulSoup(results.content, "html.parser")

    return bs_obj

test = ["2015-03-01"]
main_news_list = []

#for date in tqdm_notebook(test):
total_photo_news_count = 0
total_text_news_count = 0
date_str = "?date="
page_str = "&page="

for i in trange(len(days_range)):
    news_arrange_url = "https://news.naver.com/main/history/mainnews/list.nhn"
    news_list_date_page_url = news_arrange_url + date_str + days_range[i]

    bs_obj = get_bs_obj(news_list_date_page_url)

    photo_news_count = int(bs_obj.find("div", {"class": "eh_page"}).text.split('/')[1])
    text_news_count = int(bs_obj.find("div", {"class": "mtype_list_wide"}).find("div", {"class": "eh_page"}).text.split('/')[1])

    total_photo_news_count += photo_news_count
    total_text_news_count += text_news_count

    print(news_list_date_page_url, photo_news_count, text_news_count)

    # 포토 뉴스 부분 링크 크롤링
    for page in trange(1, photo_news_count+1):
        news_list_photo_url = 'http://news.naver.com/main/history/mainnews/photoTv.nhn'
        news_list_photo_full_url = news_list_photo_url + date_str + days_range[i] + page_str + str(page)

        photo_bs_obj = get_bs_obj(news_list_photo_full_url)

        ul = photo_bs_obj.find("ul", {"class": "edit_history_lst"})
        lis = ul.find_all("li")

        for item in lis:
            title = item.find("a")["title"]
            press = item.find("span", {"class" : "eh_by"}).text

            # link
            link = item.find("a")["href"]
            
            sid1 = link.split('&')[-3].split('=')[1]
            oid = link.split('&')[-2].split('=')[1]
            aid = link.split('&')[-1].split('=')[1]            
            
            # 연예 TV 기사 제외
            if sid1 == "shm":
                continue
                
            article_type = "pic"
            
            pic_list = [days_range[i], article_type, title, press, sid1, link, aid]
            
            main_news_list.append(pic_list)

    # 텍스트 뉴스 부분 링크 크롤링
    for page in trange(1, text_news_count+1):
        # 텍스트 뉴스 링크
        news_list_text_url = 'http://news.naver.com/main/history/mainnews/text.nhn'
        news_list_text_full_url = news_list_text_url + date_str + days_range[i] + page_str + str(page)

        # get bs obj
        text_bs_obj = get_bs_obj(news_list_text_full_url)

        # 링크 내 정보 수집
        uls = text_bs_obj.find_all("ul")
        for ul in uls:
            lis = ul.find_all("li")
            for item in lis:
                title = item.find("a").text
                press = item.find("span", {"class" : "writing"}).text
                
                # link
                link = item.find("a")["href"]

                sid1 = link.split('&')[-3].split('=')[1]
                oid = link.split('&')[-2].split('=')[1]
                aid = link.split('&')[-1].split('=')[1]
                
                # 연예 TV 기사 제외
                if sid1 == "shm":
                    continue

                article_type = "text"
                
                text_list = [date, article_type, title, press, sid1, link, aid]
                
                main_news_list.append(text_list)



pprint(main_news_list, width=20)

naver_news_df = pd.DataFrame(main_news_list, columns=["date", "type", "title", "press", "category", "link", "aid"])
naver_news_df.to_csv("naver_main_news_202006.csv", index=False)

print("total_photo_news_count:", total_photo_news_count)
print("total_text_news_count:", total_text_news_count)
