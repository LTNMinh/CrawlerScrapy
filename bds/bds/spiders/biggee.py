import scrapy
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging

logger = logging.getLogger('mycustomlogger')

class biggeeSpider(scrapy.Spider):
    name = 'biggee'
    start_urls = ['https://biggee.vn/mua-nha-dat']

    def __init__(self):
        self.base_url = 'https://batdongsan.com.vn'
        self.start_url = 'https://biggee.vn/mua-nha-dat'
        pass

    def __del__(self):
        pass

    def parse(self,response):
        logger.info("Parse Funtion Called on %s", response.url)
        current_url = response.request.url

        ITEM_SELECTOR = "a.btn-default::attr(href)"

        # page_number = current_url.split("/")[-1]
        logger.info("Parse Funtion Called on %s", response.url)
        logger.info(response.css(ITEM_SELECTOR).extract())

        for index,link in enumerate(response.css(ITEM_SELECTOR).extract()):
            logger.info("Parse Funtion Called on %s", link)
            # link = self.base_url + link
            page = current_url.split("=")[-1]
            yield scrapy.Request(url=link, callback=self.parse_inner_pages,meta={'page_number' :page })

        '/html/body/section[2]/div/div[5]/div[1]/div[12]/div/ul/li[3]/a'
        '/html/body/section[2]/div/div[5]/div[1]/div[11]/div/ul/li[6]/a'
        '/html/body/section[2]/div/div[5]/div[1]/div[9]/div/ul/li[6]/a'
        # if current_url == self.start_url:
        #     link = current_url + '/p2'
        #     yield scrapy.Request(url=link, callback=self.parse)
        # else :
        #     page = current_url.split("/")[-1]
        #     link = self.start_url + '/p' + str(int(page[1:]) + 1)
        #     try :
        #         yield scrapy.Request(url=link, callback=self.parse)
        #     except:
        #         pass


    def parse_inner_pages(self, response):
        re_latlong = r'[0-9]+.[0-9]+'

        logger.info("Parse Funtion Called on %s", response.url)
        # string_re = '(\\r|\\n)'

        # self.driver.get(response.url)
        # map = self.driver.find_element_by_xpath('//*[@id="liMap"]/a')
        # map.click()


        NAME_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[2]/div/p/text()'
        PRICE_SELECTOR = "/html/body/section[2]/div/div[3]/div[1]/div[2]/div/h3/text()"
        DETAIL_SELECTOR = "/html/body/section[2]/div/div[3]/div[1]/div[4]/div[2]/p/text()"
        DATE_SELECTOR = "/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[1]/p[2]/text()"
        AREA_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[1]/p[3]/text()'
        FLOOR_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[2]/p[1]/text()'
        ROOM_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[2]/p[2]/text()'
        TYPE_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[2]/p[3]/text()'
        CONTACT_SELECTOR = '/html/body/section[2]/div/div[3]/div[2]/div[1]/div[2]/p[1]/strong/text()'
        TEL_SELECTOR = '/html/body/section[2]/div/div[3]/div[2]/div[1]/div[2]/p[2]/text()'
        LAT_SELECTOR = "/html/body/script[3]/text()"

        # LONG_SELECTOR = '//*[@id="map"]/div/div/div[7]/div[2]/a/text()'

        # KEY_SELECTOR = '.prj-i .fl::text'
        # VALUE_SELECTOR = '.prj-i .fr::text'

        # key = response.css(KEY_SELECTOR).extract()
        # value = response.css(VALUE_SELECTOR).extract()
        # dictionary = dict(zip(key,value))

        name = response.xpath(NAME_SELECTOR).extract()
        price = response.xpath(PRICE_SELECTOR).extract()
        # owner = dictionary.get('Chủ đầu tư')
        # address = dictionary.get('Địa chỉ')
        date = response.xpath(DATE_SELECTOR).extract()[1]
        area = response.xpath(AREA_SELECTOR).extract()[1]
        floor = response.xpath(FLOOR_SELECTOR).extract()[1]
        room = response.xpath(ROOM_SELECTOR).extract()[1]
        type = response.xpath(TYPE_SELECTOR).extract()[1]
        detail = response.xpath(DETAIL_SELECTOR).extract()
        contact = response.xpath(CONTACT_SELECTOR).extract_first()
        tel = response.xpath(TEL_SELECTOR).extract()


        # project_url = response.meta.get('project_url')
        # try:
        latlong = response.xpath(LAT_SELECTOR).extract()
        latlong = " ".join(latlong)
        # if latlong is not None:
        latlong = re.findall(re_latlong,latlong)
        # latlong =  re.findall(re_latlong,latlong_)
        # except:
        # latlong = None

        # latlong = response.xpath(LONG_SELECTOR).extract()
        page_number = response.meta.get('page_number')
        # progress = response.meta.get('progress')

        yield {
                'name' : name  ,
                # 'project_link': project_url,
                # 'owner': owner,
                # 'address' : address,
                'date': date,
                'area' : area,
                'price': price,
                'floor' : floor,
                'room'  : room,
                'type'  : type,
                'detail' : detail,
                'latlong' : latlong,
                'contact_name' :  contact,
                'tel'    : str(tel),
                'page_number': page_number,
        }