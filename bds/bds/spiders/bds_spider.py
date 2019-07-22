import scrapy
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import logging

logger = logging.getLogger('mycustomlogger')


class bdsSpider(scrapy.Spider):
    name = 'bds'
    start_urls = ['https://batdongsan.com.vn/ban-can-ho-chung-cu']

    def __init__(self):
        # cap = DesiredCapabilities().FIREFOX
        # cap["marionette"] = False
        self.driver = webdriver.Firefox()
        self.base_url = 'https://batdongsan.com.vn'
        self.start_url = 'https://batdongsan.com.vn/ban-can-ho-chung-cu'
        pass

    def __del__(self):
        self.driver.close()

    def parse(self,response):
        ITEM_SELECTOR = ".vip0.search-productItem .p-title a::attr(href)"

        for link in  response.css(ITEM_SELECTOR).extract():
            link = self.base_url + link
            yield scrapy.Request(url=link, callback=self.parse_inner_pages)

        current_url = response.request.url

        if current_url == self.start_url:
            link = current_url + '/p2'
            yield scrapy.Request(url=link, callback=self.parse)

        # else :
        #     page = current_url.split("/")[:-1]
        #     link = self.start_url + '/p' + str(int(page[1:]) + 1)
        #     try :
        #         yield scrapy.Request(url=link, callback=self.parse)
        #     except:
        #         pass


    def parse_inner_pages(self, response):
        latlong_re = r'q=(-?[\d\.]*),([-?\d\.]*)'
        string_re = '(\\r|\\n)'

        self.driver.get(response.url)
        map = self.driver.find_element_by_xpath('//*[@id="liMap"]/a')
        map.click()


        TITLE_SELECTOR = 'title::text'
        PRICE_SELECTOR = "span.gia-title.mar-right-15 strong::text"
        AREA_SELECTOR = '//*[@id="product-detail"]/div[2]/span[2]/span[2]/strong/text()'
        DETAIL_SELECTOR =  ".pm-desc::text"
        ADDRESS_SELECTOR = '//*[@id="product-detail"]/div[8]/div/div[1]/div/div[2]/div[2]/div[2]/text()'
        LOCATION_SELECTOR = '//*[@id="maputility"]/iframe'
        PROJECT_SELECTOR = '//*[@id="LeftMainContent__productDetail_linkProject"]/@href'
        CONTACT_NAME_SELECTOR = '//*[@id="LeftMainContent__productDetail_contactName"]/div[2]/text()'
        CONTACT_MOBILE_SELECTOR = '//*[@id="LeftMainContent__productDetail_contactMobile"]/div[2]/text()'
        CONTACT_EMAIL_SELECTOR = '//*[@id="contactEmail"]/div[2]/a'
        CONTACT_ADDRESS_SELECTOR = '//*[@id="LeftMainContent__productDetail_contactAddress"]/div[2]/text()'

        title = response.css(TITLE_SELECTOR).extract_first()
        price = response.css(PRICE_SELECTOR).extract_first()
        area = response.xpath(AREA_SELECTOR).extract_first()
        address = response.xpath(ADDRESS_SELECTOR).extract_first()
        detail = response.css(DETAIL_SELECTOR).extract()
        location_url = self.driver.find_element_by_xpath(LOCATION_SELECTOR).get_attribute("src")
        project_url =  self.base_url + response.xpath(PROJECT_SELECTOR).extract_first()

        contact_name   = response.xpath(CONTACT_NAME_SELECTOR).extract_first()
        contact_mobile = response.xpath(CONTACT_MOBILE_SELECTOR).extract_first()

        contact_email = None
        contact_address = response.xpath(CONTACT_ADDRESS_SELECTOR).extract_first()

        try :
            contact_email  = self.driver.find_element_by_xpath(CONTACT_EMAIL_SELECTOR).text
        except:
            pass

        title   = re.sub(string_re,'',title)
        price   = re.sub(string_re, '', price)
        area    = re.sub(string_re, '', area)
        # address = re.sub(string_re, '', address)
        detail  = ' '.join(detail)
        # contact_name = re.sub(string_re,'',contact_name)
        # contact_address = re.sub(string_re, '', contact_address)

        latlong = re.search(latlong_re, location_url).group()[2:]


        yield { 'title' : title ,
                'price' : price,
                'address' : address,
                'area' : area ,
                'detail' : detail,
                'latlong' : latlong,
                'project_link' : project_url,
                'contact_name': contact_name,
                'contact_mobile': contact_mobile,
                'contact_email':contact_email ,
                'contact_address' : contact_address}

class bdsProjectSpider(scrapy.Spider):
    name = 'bds_project'
    start_urls = ['https://batdongsan.com.vn/can-ho-chung-cu']

    def __init__(self):
        self.base_url = 'https://batdongsan.com.vn'
        self.start_url = 'https://batdongsan.com.vn/can-ho-chung-cu'
        pass

    def __del__(self):
        pass

    def parse(self,response):
        logger.info("Parse Funtion Called on %s", response.url)
        current_url = response.request.url

        ITEM_SELECTOR = "div.detail > div.bigfont > h3 > a::attr(href)"
        LAT_SELECTOR = ".list-view > li::attr(lat)"
        LONG_SELECTOR = ".list-view > li::attr(lon)"
        PROGRESS_SELECTOR = '.prgrs::text'

        lat =  response.css(LAT_SELECTOR).extract()
        long = response.css(LONG_SELECTOR).extract()
        progress = response.css(PROGRESS_SELECTOR).extract()
        progress = [x for x in progress if x != '\r\n']
        # logger.info(progress)
        page_number = current_url.split("/")[-1]
        for index,link in enumerate(response.css(ITEM_SELECTOR).extract()):
            link = self.base_url + link
            latlong = lat[index] + ',' + long[index]
            progress_cur = progress[index]
            yield scrapy.Request(url=link, callback=self.parse_inner_pages, meta={'progress' : progress_cur,
                                                                                  'page_number':page_number ,
                                                                                  'project_url' : link ,                                                                     'latlong': latlong})

        if current_url == self.start_url:
            link = current_url + '/p2'
            yield scrapy.Request(url=link, callback=self.parse)
        else :
            page = current_url.split("/")[-1]
            link = self.start_url + '/p' + str(int(page[1:]) + 1)
            try :
                yield scrapy.Request(url=link, callback=self.parse)
            except:
                pass


    def parse_inner_pages(self, response):
        logger.info("Parse Funtion Called on %s", response.url)
        # string_re = '(\\r|\\n)'

        # self.driver.get(response.url)
        # map = self.driver.find_element_by_xpath('//*[@id="liMap"]/a')
        # map.click()

        KEY_SELECTOR = '.prj-i .fl::text'
        VALUE_SELECTOR = '.prj-i .fr::text'

        key = response.css(KEY_SELECTOR).extract()
        value = response.css(VALUE_SELECTOR).extract()
        dictionary = dict(zip(key,value))

        name = dictionary.get('Tên dự án')
        owner = dictionary.get('Chủ đầu tư')
        address = dictionary.get('Địa chỉ')
        area = dictionary.get('Tổng diện tích')
        selldate = dictionary.get('Bàn giao nhà')
        price = dictionary.get('Giá bán')
        scale = dictionary.get('Quy mô dự án')
        # detail = response.xpath(DETAIL_SELECTOR).extract()


        project_url = response.meta.get('project_url')
        latlong = response.meta.get('latlong')
        page_number = response.meta.get('page_number')
        progress = response.meta.get('progress')

        yield {
                'name' : name  ,
                'project_link': project_url,
                'owner': owner,
                'address' : address,
                'area' : area,
                'sell_date' : selldate,
                'progress' : progress,
                'price': price,
                'scale': scale,
                # 'detail' : detail,
                'latlong' : latlong,
                'page_number': page_number}

class muabanSpider(scrapy.Spider):
    name = 'muaban'
    start_urls = ['https://muaban.net/can-ho-chung-cu-tap-the-toan-quoc-l0-c3204']

    def __init__(self):
        pass

    def __del__(self):
        pass

    def parse(self,response):
        logger.info("Parse Funtion Called on %s", response.url)
        # urls = ['https://muaban.net/ban-nha-can-ho-quan-1-l5906-c32',  # district 1
        #         'https://muaban.net/ban-nha-can-ho-quan-2-l5910-c32',  # district 2
        #         'https://muaban.net/ban-nha-can-ho-quan-3-l5911-c32',  # district 3
        #         'https://muaban.net/ban-nha-can-ho-quan-4-l5912-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-5-l5913-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-6-l5914-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-7-l5915-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-8-l5916-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-9-l5917-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-10-l5907-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-11-l5908-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-12-l5909-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-binh-tan-l5918-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-binh-thanh-l5919-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-go-vap-l5920-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-phu-nhuan-l5921-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-tan-binh-l5922-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-tan-phu-l5923-c32',
        #         'https://muaban.net/ban-nha-can-ho-quan-thu-duc-l5924-c32',
        #         'https://muaban.net/ban-nha-can-ho-huyen-binh-chanh-l5901-c32',
        #         'https://muaban.net/ban-nha-can-ho-huyen-can-gio-l5902-c32',
        #         'https://muaban.net/ban-nha-can-ho-huyen-cu-chi-l5903-c32',
        #         'https://muaban.net/ban-nha-can-ho-huyen-hoc-mon-l5904-c32',
        #         'https://muaban.net/ban-nha-can-ho-huyen-nha-be-l5905-c32',
        #         ]
        # districts = ['1','2','3','4','5',
        #              '6','7','8','9','10',
        #              '11','12','Bình Tân','Bình Thạnh',
        #              'Gò Vấp','Phú Nhuận','Tân Bình',
        #              'Tân Phú','Thủ Đức','Bình Chánh',
        #              'Cần Giờ','Củ Chi','Hóc Môn','Nhà Bè']

        urls = ['https://muaban.net/ban-nha-can-ho-quan-ba-dinh-l2406-c32',
                'https://muaban.net/ban-nha-can-ho-quan-bac-tu-liem-l2430-c32',
                'https://muaban.net/ban-nha-can-ho-quan-cau-giay-l2407-c32',
                'https://muaban.net/ban-nha-can-ho-quan-dong-da-l2408-c32',
                'https://muaban.net/ban-nha-can-ho-quan-ha-dong-l2415-c32',
                'https://muaban.net/ban-nha-can-ho-quan-hai-ba-trung-l2409-c32',
                'https://muaban.net/ban-nha-can-ho-quan-hoan-kiem-l2410-c32',
                'https://muaban.net/ban-nha-can-ho-quan-hoang-mai-l2411-c32',
                'https://muaban.net/ban-nha-can-ho-quan-long-bien-l2412-c32',
                'https://muaban.net/ban-nha-can-ho-quan-nam-tu-liem-l2431-c32',
                'https://muaban.net/ban-nha-can-ho-quan-tay-ho-l2413-c32',
                'https://muaban.net/ban-nha-can-ho-quan-thanh-xuan-l2414-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-ba-vi-l2416-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-chuong-my-l2417-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-dan-phuong-l2418-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-dong-anh-l2401-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-gia-lam-l2402-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-hoai-duc-l2419-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-me-linh-l2429-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-phuc-tho-l2422-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-quoc-oai-l2423-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-soc-son-l2403-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-thach-that-l2424-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-thanh-oai-l2425-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-thanh-tri-ha-noi-l2404-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-thuong-tin-l2426-c32',
                'https://muaban.net/ban-nha-can-ho-huyen-ung-hoa-l2427-c32',
                'https://muaban.net/ban-nha-can-ho-thi-xa-son-tay-l2428-c32']

        districts = ['Ba Đình','Bắc Từ Liêm','Cầu Giấy',
                     'Đống Đa','Hà Đông','Hai Bà Trưng',
                     'Hoàn Kiếm','Hoàng Mai','Long Biên',
                     'Nam Từ Liêm','Tây Hồ','Thanh Xuân',
                     'Ba Vì','Chương Mỹ','Đan Phượng',
                     'Đông Anh','Gia Lâm','Hoài Đức',
                     'Mê Linh','Phúc Thọ','Quốc Oai',
                     'Sóc Sơn','Thạch Thất','Thanh Oai',
                     'Thanh Trì','Thường Tín','Ứng Hòa',
                     'Thị xã Sơn Tây']

        for index,link in enumerate(urls):
            district = districts[index]
            yield scrapy.Request(url=link, callback=self.parse_district, meta={ 'district' : district})


    def parse_district(self,response):
        logger.info("Parse Funtion Called on %s", response.url)

        current_url = response.url
        page_number = current_url.split('=')[-1]

        ITEM_SELECTOR = ".mbn-box-list .mbn-box-list-content a.mbn-image::attr(href)"

        district = response.meta.get('district')
        for link in response.css(ITEM_SELECTOR).extract():
            yield scrapy.Request(url=link, callback=self.parse_inner_pages, meta={'page_number': page_number,
                                                                                  'district' : district})
        page = current_url.split("=")[-1]
        if len(page) > 4:
            link = current_url + '?cp=2'
            yield scrapy.Request(url=link, callback=self.parse_district, meta={'district' : district})
        else:
            page = current_url.split("=")[-1]
            if (int(page) + 1) <= 3:
                link = current_url.split("=")[0] + "=" + str(int(page) + 1)
                try:
                    yield scrapy.Request(url=link, callback=self.parse_district,meta={'district' : district})
                except:
                    pass



    def parse_inner_pages(self, response):
        logger.info("Parse Funtion Called on %s", response.url)


        TITLE_SELECTOR = 'title::text'
        PRICE_SELECTOR = '.ct-price span::text'
        AREA_SELECTOR = '//*[@id="dvContent"]/div[7]/ul[1]/li[8]/div/div[2]/text()'
        DETAIL_SELECTOR =  '.ct-body::text'
        ADDRESS_SELECTOR = '//*[@id="dvContent"]/div[7]/ul[1]/li[1]/div/div[2]/text()'
        PROJECT_SELECTOR = '//*[@id="dvContent"]/div[7]/ul[1]/li[2]/div/div[2]/text()'
        CONTACT_NAME_SELECTOR = '.ct-contact .col-md-10.col-sm-10.col-xs-9::text'
        CONTACT_MOBILE_SELECTOR = '.contactmobile-desktop b::text'

        title = response.css(TITLE_SELECTOR).extract_first()
        price = response.css(PRICE_SELECTOR).extract_first()
        area = response.xpath(AREA_SELECTOR).extract_first()
        address = response.xpath(ADDRESS_SELECTOR).extract_first()
        detail = response.css(DETAIL_SELECTOR).extract()

        project_name = response.xpath(PROJECT_SELECTOR).extract_first()
        contact_name   = response.css(CONTACT_NAME_SELECTOR).extract_first()
        contact_mobile = response.css(CONTACT_MOBILE_SELECTOR).extract_first()

        detail  = ' '.join(detail)
        page_number = response.meta.get('page_number')
        district = response.meta.get('district')

        yield { 'title' : title ,
                'price' : price,
                'address' : address,
                'district' : district,
                'area' : area ,
                'detail' : detail,
                'project_name' : project_name,
                'contact_name': contact_name,
                'contact_mobile': contact_mobile,
                'page_number' : page_number,
                }