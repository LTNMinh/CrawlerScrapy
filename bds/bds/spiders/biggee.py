import scrapy
import re
import logging

logger = logging.getLogger('mycustomlogger')
logging.basicConfig(
    filename='log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.ERROR,
)



class biggeeSpider(scrapy.Spider):
    name = 'biggee'
    start_urls = ['https://biggee.vn/mua-nha-dat']

    def __init__(self):
        self.base_url = 'https://biggee.vn/'
        self.start_url = 'https://biggee.vn/mua-nha-dat'
        pass

    def __del__(self):
        pass

    def parse(self,response):
        logger.info("Parse Funtion Called on %s", response.url)
        current_url = response.request.url

        ITEM_SELECTOR = "a.btn-default::attr(href)"
        PAGE_NEXT_1 = '/html/body/section[2]/div/div[5]/div[1]/div[12]/div/ul/li[3]/a/@href'
        PAGE_NEXT_2 = 'li:nth-child(6) a::attr(href)'

        logger.info("Parse Funtion Called on %s", response.url)
        logger.info(response.css(ITEM_SELECTOR).extract())

        for index,link in enumerate(response.css(ITEM_SELECTOR).extract()):
            logger.info("Parse Funtion Called on %s", link)
            page = current_url.split("=")[-1]
            yield scrapy.Request(url=link, callback=self.parse_inner_pages,meta={'page_number' :page })

        if current_url == self.start_url:
            link = response.xpath(PAGE_NEXT_1).extract_first()
            yield scrapy.Request(url=link, callback=self.parse)
        else :
            link = response.css(PAGE_NEXT_2).extract_first()
            try :
                yield scrapy.Request(url=link, callback=self.parse)
            except:
                pass

    def parse_inner_pages(self, response):
        re_latlong = r'[0-9]+.[0-9]+'
        # re_area = r'[0'
        page_number = response.meta.get('page_number')

        logger.info("Parse Funtion Called on {} Pages: {}".format(response.url,page_number))
        # string_re = '(\\r|\\n)'

        # self.driver.get(response.url)
        # map = self.driver.find_element_by_xpath('//*[@id="liMap"]/a')
        # map.click()


        NAME_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[2]/div/p/text()'
        PRICE_SELECTOR = "/html/body/section[2]/div/div[3]/div[1]/div[2]/div/h3/text()"
        DETAIL_SELECTOR = "/html/body/section[2]/div/div[3]/div[1]/div[4]/div[2]/p/text()"
        DATE_SELECTOR = '.col-md-6:nth-child(1) p:nth-child(2)::text'
        # DATE_SELECTOR = "/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[1]/p[2]/text()"
        AREA_SELECTOR = '.col-md-6:nth-child(1) p~ p+ p::text'

        # AREA_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[1]/p[3]/text()'
        FLOOR_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[2]/p[1]/text()'
        ROOM_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[2]/p[2]/text()'
        TYPE_SELECTOR = '/html/body/section[2]/div/div[3]/div[1]/div[4]/div[3]/div/div[2]/p[3]/text()'
        CONTACT_SELECTOR = '/html/body/section[2]/div/div[3]/div[2]/div[1]/div[2]/p[1]/strong/text()'
        TEL_SELECTOR = '/html/body/section[2]/div/div[3]/div[2]/div[1]/div[2]/p[2]/text()'
        LAT_SELECTOR = "/html/body/script[3]/text()"

        name = response.xpath(NAME_SELECTOR).extract()
        price = response.xpath(PRICE_SELECTOR).extract()
        date = response.css(DATE_SELECTOR).extract()
        area = response.css(AREA_SELECTOR).extract()
        floor = response.xpath(FLOOR_SELECTOR).extract()
        room = response.xpath(ROOM_SELECTOR).extract()
        type = response.xpath(TYPE_SELECTOR).extract()
        detail = response.xpath(DETAIL_SELECTOR).extract()
        contact = response.xpath(CONTACT_SELECTOR).extract_first()
        tel = response.xpath(TEL_SELECTOR).extract()

        try:
            latlong = response.xpath(LAT_SELECTOR).extract()
            latlong = " ".join(latlong)
            latlong = re.findall(re_latlong,latlong)
        except:
            latlong = None


        yield {
                'name' : name  ,
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
                'url'  : response.url,
                'page_number': page_number, }