import scrapy
from bs4 import BeautifulSoup
import json
from scrapy.selector import Selector

class GetData(scrapy.Spider):
    name = "geturldata"
    def start_requests(self):
        urls = 'https://www.getmyuni.com/engineering-colleges'
 
        yield scrapy.Request(url=urls, callback=self.parse)

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

                    print(feeAndExam.find_all('div')[0].contents[2])


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
