#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# coding=utf-8
import requests 
from bs4 import BeautifulSoup
import pymysql
import time

def parse_html(r):
    if r.status_code == requests.codes.ok:
        r.encoding="big5-hkscs"
        soup=BeautifulSoup(r.text, "html.parser")
    else:
        print("http request error")
        soup=None
    return soup

def web_scraping_bot(url, clsname):
    soup=parse_html(requests.get(url))
    if soup:
        cls_count=str(soup.find_all("span", style="color:red;"))
        cls_count=int(cls_count[cls_count.index('>')+1:cls_count.index('/')-1])
        aft=get_articles(soup, "2", clsname)
        pagenum=3 #next next pagenum
        cls_count=cls_count-20 #one page has 20 qa
        while cls_count>0:
            time.sleep(5)
            soup=parse_html(requests.get(aft)) #next page
            aft=get_articles(soup, pagenum, clsname)
            cls_count=cls_count-20
            pagenum=pagenum+1

def get_articles(soup, pagenum, clsname):
    aft="https://sp1.hso.mohw.gov.tw/doctor/All/history.php?UrlClass="+clsname+"&SortBy=q_no&PageNo="+str(pagenum)
    tag_divs=soup.select('a[href^="Show"]') #all qa
    for tag in tag_divs:
        #文章網址
        url='https://sp1.hso.mohw.gov.tw/doctor/All/'+tag.get('href')
        time.sleep(5)
        soup=parse_html(requests.get(url))
        tmp=soup.select('li.doctor')

        if tmp:
           try:
               # 执行sql语句
               sql = "INSERT INTO qainfo (Q, A, DOCTOR, CLS) VALUES ('{}', '{}', '{}', '{}')".format(pymysql.escape_string(str(soup.find(class_="ask"))),pymysql.escape_string(str(soup.find(class_="ans"))), pymysql.escape_string(str(tmp[0].text[tmp[0].text.index(clsname)+len(clsname)+1:tmp[0].text.index(',')])), pymysql.escape_string(clsname))
               #print(str(i['DOCTOR']))
               cursor.execute(sql)
               db.commit()
           except:
                print(str(soup.find(class_="ask")))
                print(str(soup.find(class_="ans")))
                print(str(tmp[0].text[tmp[0].text.index(clsname)+len(clsname)+1:tmp[0].text.index(',')]))
                db.rollback()    

    return aft

if __name__ == "__main__":
    db = pymysql.connect(host='localhost', port=3306, user='root', passwd='team2', db='db', charset='utf8mb4')
    cursor = db.cursor()
    cls=['牙科','外科','兒科','骨科','眼科','漢生病','中醫科','皮膚科','泌尿科','家醫科'
         ,'高年科','婦產科','麻醉科','復健科','腫瘤科','精神科','體適能','營養教室','戒菸諮詢','藥物諮詢'
         ,'流感諮詢','耳鼻喉科','罕見疾病','放射線科','神經內科','神經外科','胸腔內科','整型外科','肝膽腸胃科','潛水醫學科'
         ,'心臟血管專科','乳房甲狀腺科','產後憂鬱諮詢']
    
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    print ("Database version : %s " % data)
    cursor.execute("TRUNCATE TABLE qainfo")
    for i in cls:
        url='https://sp1.hso.mohw.gov.tw/doctor/All/history.php?UrlClass='+i
        web_scraping_bot(url, i)
    
    
    # 关闭数据库连接
    db.close()

