import scrapy
from bs4 import BeautifulSoup
import json
import pymongo
from scrapy.selector import Selector
from pymongo import MongoClient
client_db = MongoClient("mongodb://test:7101904a@ds157723.mlab.com:57723/shreyanshu")


class GetData(scrapy.Spider):
    name = "ScrapeData"

    def start_requests(self):
        urls = 'https://www.getmyuni.com/engineering-colleges' 
        yield scrapy.Request(url = urls, callback = self.parse)


    def pushDataToDb(self, values):        
        collection = client_db["shreyanshu"].scraper
        try:
            res = collection.insert_one(values).inserted_id
            print(res)
        except Exception as e :
            pass
        


    def parse(self, response):
        data = response.body
        val = response.css("div.info-card")
        for i in val:
            data = i.css("div.table-cell")
            values = dict()
            values['url_info'] = data.xpath('*/a/@href').get()
            values['college_name'] = data.xpath("*/a/b/text()").get()
            trunc_val = data.xpath(".//p").getall()
            if trunc_val:
                if trunc_val[1]:
                    values['location'] = Selector(text=trunc_val[1]).css('p::text').get()
                else:
                    values['location'] = None
                if trunc_val[2]:
                    rating = Selector(text=trunc_val[2]).xpath('(.//p/text())[2]').get()
                    if rating:
                        values['rating'] = rating.strip() 
                    else:
                        values['rating'] = rating
                else:
                    values['rating'] = None
            degree = i.css("div.pnm")
            pnm = str(degree.extract()).split("\\n")
            if len(pnm)> 1:
                pnm1 = str(pnm[1]).split('</b>')
                pnm1 = [x.strip() for x in pnm1]
                course = str(pnm1[1]).split('     ')[0]
                if course:
                    values["Degree"] = course
                else: 
                    values["Degree"] = None
            soup = BeautifulSoup(str(i.get()),)
            for x in soup.find_all('div', class_ = ['clearfix', 'info-course-detail']):
                rankAndDuration = soup.find_all('div', class_ = ['col-md-6', 'col-md-6', 'no-padding'])[2]
                if len(rankAndDuration.find_all('div')[0].contents) <= 2:
                    
                    values["Rank"] = None
                    values["Duration"] = rankAndDuration.find_all('div')[0].contents[1].strip()
                else:
                    values["Duration"] = rankAndDuration.find_all('div')[1].contents[1].strip()
                    values["Rank"] = rankAndDuration.find_all('div')[0].contents[1].strip()
                feeAndExam = soup.find_all('div', class_ = ['col-md-6', 'col-md-6', 'no-padding'])[3]
                if len(feeAndExam.find_all('div')) > 1:
                    values["Fees"] = feeAndExam.find_all('div')[1].contents[1]
                    values["ExamLinks"] = BeautifulSoup(str(feeAndExam.find_all('div')[0].contents[2])).find('a').get('href')

                else:
                    values["Fees"] = feeAndExam.find_all('div')[0].contents[1].strip()
                links = soup.find_all('div', class_ = ["text-center", "card-icon-div"])
                for link in links:
                    if len(link.find_all("a", class_ = "menu-menu-items-a")) > 0:
                        try:
                            if link.find_all("a", class_ = "menu-menu-items-a")[0].get('href'):
                                values["Info_link"] = link.find_all("a", class_ = "menu-menu-items-a")[0].get('href')
                            if link.find_all("a", class_ = "menu-menu-items-a")[1].get('href'):
                                values["Placements_link"] = link.find_all("a", class_ = "menu-menu-items-a")[1].get('href')
                            if link.find_all("a", class_ = "menu-menu-items-a")[2].get('href'):
                                values["FeeandCourses_link"] = link.find_all("a", class_ = "menu-menu-items-a")[2].get('href')
                            if link.find_all("a", class_ = "menu-menu-items-a")[3].get('href'):
                                values["Infrastructure_link"] = link.find_all("a", class_ = "menu-menu-items-a")[3].get('href')
                            if link.find_all("a", class_ = "menu-menu-items-a")[4].get('href'):
                                values["Addmision_link"] = link.find_all("a", class_ = "menu-menu-items-a")[4].get('href')
                            if link.find_all("a", class_ = "menu-menu-items-a")[5].get('href'):
                                values["Review_link"] = link.find_all("a", class_ = "menu-menu-items-a")[5].get('href')
                        except Exception as e:
                            pass
                self.pushDataToDb(values)




"""
            for j in data:
                print(j.css("p.b::text").getall())
1. College Name.
2. College Link/URL
3. College Location.
4. College Rating.
5. Degree
6. Rank
7. Duration
8. Course Fees
9. Exams Required
10. Bottom Links (Info, Placement, Fees & Courses etc.)"""
