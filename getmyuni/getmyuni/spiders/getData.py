import scrapy
from bs4 import BeautifulSoup
import json
import pymongo
from scrapy.selector import Selector
from pymongo import MongoClient
client_db = MongoClient("mongodb://test:7101904a@ds157723.mlab.com:57723/shreyanshu")


class GetData(scrapy.Spider):
    name = "geturldata"

    def start_requests(self):
        urls = 'https://www.getmyuni.com/engineering-colleges' 
        yield scrapy.Request(url = urls, callback = self.parse)


    def pushDataToDb(self, values):        
        print(client_db['shreyanshu'].list_collection_names())
        collection = client_db["shreyanshu"].scraper
        try:
            res = collection.insert_one(values).inserted_id
            print(res)
        except Exception as e :
            print("key already exists")
            pass
        


    def parse(self, response):
        data = response.body
        #info-card college  bg_color
        #print(response.body)
        val = response.css("div.info-card")
        for i in val:
            data = i.css("div.table-cell")
            values = dict()
            #print(data.css("p::text").get())
            #print(data.css("p.no-margin ").get())
            #data = i.css("div.table-cell")
            values['url_info'] = data.xpath('*/a/@href').get()
            values['college_name'] = data.xpath("*/a/b/text()").get()

            #hm = data.css("/p/text()").get()
            #print(hm)
            trunc_val = data.xpath(".//p").getall()
            #print(trunc_val, len(trunc_val))
            if trunc_val:
                #print(trunc_val[1])
                #print(trunc_val)
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
            #print(values)
            degree = i.css("div.pnm")
            pnm = str(degree.extract()).split("\\n")
            #print(pnm[0])
            if len(pnm)> 1:
                pnm1 = str(pnm[1]).split('</b>')
                pnm1 = [x.strip() for x in pnm1]
                course = str(pnm1[1]).split('     ')[0]
                if course:
                    values["Degree"] = course
                else: 
                    values["Degree"] = None
            #print(values)
            #Rank = i.xpath("//div[1]//div[1]/div/*")
            #print(Rank.css("div.col-lg-6").get()) clearfix info-course-detail
            soup = BeautifulSoup(str(i.get()),)
            #print(soup.find_all('div', class_ = ['col-md-6', 'no-padding']))
            for x in soup.find_all('div', class_ = ['clearfix', 'info-course-detail']):
                rankAndDuration = soup.find_all('div', class_ = ['col-md-6', 'col-md-6', 'no-padding'])[2]
                #print(rankAndDuration.find_all('div')[0].contents)
                if len(rankAndDuration.find_all('div')[0].contents) <= 2:
                    
                    values["Rank"] = None
                    values["Duration"] = rankAndDuration.find_all('div')[0].contents[1].strip()
                    #print(values)
                else:
                    values["Duration"] = rankAndDuration.find_all('div')[1].contents[1].strip()
                    values["Rank"] = rankAndDuration.find_all('div')[0].contents[1].strip()
                    #print(values)
                feeAndExam = soup.find_all('div', class_ = ['col-md-6', 'col-md-6', 'no-padding'])[3]
                #print(soup.find_all('div', class_ = ['col-md-6', 'col-md-6', 'no-padding'])[3])
                #print(feeAndExam.find_all('div'))
                if len(feeAndExam.find_all('div')) > 1:
                    values["Fees"] = feeAndExam.find_all('div')[1].contents[1]
                    values["ExamLinks"] = BeautifulSoup(str(feeAndExam.find_all('div')[0].contents[2])).find('a').get('href')
                    values["ExamName"] = BeautifulSoup(str(feeAndExam.find_all('div')[0].contents[2])).find('a').get_text()
                    #print(values)
                else:
                    values["Fees"] = feeAndExam.find_all('div')[0].contents[1].strip()
                    #print(values)
                #text-center card-icon-div
                links = soup.find_all('div', class_ = ["text-center", "card-icon-div"])
                #print(links)
                for link in links:
                    #print(len(link))
                    #PLACEMENTS = 1
                    #print(link.find_all('a')[0].get('href'))
                    #print(len(link.find_all("a", class_ = "menu-menu-items-a")))
                    if len(link.find_all("a", class_ = "menu-menu-items-a")) > 0:
                        #print(link.find_all("a", class_ = "menu-menu-items-a")[1])
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
                #print(values)

                self.pushDataToDb(values)
                print("###################")



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
