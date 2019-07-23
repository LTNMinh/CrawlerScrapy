import scrapy
import re
import logging

logger = logging.getLogger('mycustomlogger')
logging.basicConfig(
    filename='log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.ERROR,
)

def changeValue(value):
    if 'check' in value:
        value = 1
    elif 'none' in value:
        value = 0
    else:
        value = re.sub(r'<p.*>(.*)<\/p>', r'\1', value)
    return value

class reverSpider(scrapy.Spider):
    name = 'rever'
    start_urls = ['https://rever.vn/s/ho-chi-minh/mua']

    def __init__(self):
        self.base_url = 'https://rever.vn'
        self.start_url = 'https://rever.vn/s/ho-chi-minh/mua'
        pass

    def __del__(self):
        pass

    def parse(self,response):
        logger.info("Parse Funtion Called on %s", response.url)
        current_url = response.request.url

        ITEM_SELECTOR = ".listing-name::attr(href)"
        PRICE_SELECTOR = ".listing-price::text"
        # PAGE_NEXT_1 = '/html/body/section[2]/div/div[5]/div[1]/div[12]/div/ul/li[3]/a/@href'
        # PAGE_NEXT_2 = 'li:nth-child(6) a::attr(href)'

        logger.info("Parse Funtion Called on %s", response.url)
        logger.info(response.css(ITEM_SELECTOR).extract())

        links = response.css(ITEM_SELECTOR).extract()
        prices = response.css(PRICE_SELECTOR).extract()

        for index,link in enumerate(links):
            if current_url != self.start_url:
                page = current_url.split("=")[-1]
            else:
                page = 1

            price = prices[index]
            link = self.base_url + link
            yield scrapy.Request(url=link, callback=self.parse_inner_pages,meta={ 'price' : price,
                                                                                  'page_number' :page })

        for i in range(2,95+1):
            link = self.start_url + '?page=' + str(i)
            yield scrapy.Request(url=link, callback=self.parse)

        # if current_url == self.start_url:
        #     link = self.start_url + '?page=' + i
        #     yield scrapy.Request(url=link, callback=self.parse)
        # else :
        #     link = response.css(PAGE_NEXT_2).extract_first()
        #     try :
        #         yield scrapy.Request(url=link, callback=self.parse)
        #     except:
        #         pass

    def parse_inner_pages(self, response):
        # re_value = r'<p.*>(.*)<\/p>'
        re_latlong = 'center=(\d*.\d*,\d*.\d*)'
        page_number = response.meta.get('page_number')

        logger.info("Parse Funtion Called on {} Pages: {}".format(response.url,page_number))

        NAME_SELECTOR = 'h1::text'
        KEY_SELECTOR = 'li p.left::text'
        VALUE_SELECTOR = 'li p.right'
        DETAIL_SELECTOR = ".summary::text"
        CONTACT_SELECTOR = ".infoagent h4::text"
        TEL_SELECTOR = ".infoagent a::text"
        MAP_SELECTOR = '//*[@id="sticky"]/section/div[1]/section/div[1]/@style'
        ADDRESS = '//*[@id="sticky"]/section/div[1]/section/div[1]/div[2]/div/div/strong/text()'

        name = response.css(NAME_SELECTOR).extract()
        price = response.meta.get('price')
        key = response.css(KEY_SELECTOR).extract()
        value = response.css(VALUE_SELECTOR).extract()
        gmap = response.xpath(MAP_SELECTOR).extract_first()
        address = response.xpath(ADDRESS).extract_first()


        value = list(map(changeValue,value))
        dictionary = dict(zip(key,value))

        bedroom = dictionary.get('Phòng ngủ')
        bathroom = dictionary.get('Phòng tắm')
        area = dictionary.get('Diện tích')
        purpose = dictionary.get('Mục đích sử dụng')
        project = dictionary.get('Dự án')
        tower = dictionary.get('Tháp')
        startdate = dictionary.get('Thời gian bắt đầu bán')
        sofa = dictionary.get('Sofa')
        table = dictionary.get('Bàn ăn')
        kitchen = dictionary.get('Nhà bếp')
        kitchen_cabinet = dictionary.get('Tủ bếp')
        kitchen_equipment = dictionary.get('Thiết bị bếp')
        wardrobe = dictionary.get('Tủ quần áo')
        makeup_table = dictionary.get('Bàn trang điểm')
        work_table = dictionary.get('Bàn làm việc')
        tivi = dictionary.get('Tivi')
        washing_machine = dictionary.get('Máy giặt')
        fridge = dictionary.get('Tủ lạnh')
        air_conditioner = dictionary.get('Máy lạnh')
        microwave = dictionary.get('Lò vi sóng')
        heater = dictionary.get('Máy nước nóng')
        bed = dictionary.get('Giường')
        fireplace = dictionary.get('Máy sưởi')
        audio = dictionary.get('Thiết bị âm thanh')
        internet = dictionary.get('Internet')
        tv_cable = dictionary.get('Truyền hình cable')
        pet_allowance = dictionary.get('Cho phép thú cưng')
        elevator = dictionary.get('Thang máy')
        pool = dictionary.get('Hồ bơi')
        gym = dictionary.get('Gym')
        working_place = dictionary.get('Khu vực làm việc')
        allday = dictionary.get('Mở cửa 24h')
        car_parking = dictionary.get('Bãi để ôtô')
        balcony = dictionary.get('Ban công')
        dry_sauna = dictionary.get('Phòng xông hơi khô')
        steam_room = dictionary.get('Phòng xông hơi ướt')
        entertainment_room = dictionary.get('Phòng giải trí')

        detail = response.css(DETAIL_SELECTOR).extract()
        contact = response.css(CONTACT_SELECTOR).extract_first()
        tel = response.css(TEL_SELECTOR).extract_first()


        try:
            lat, long = re.findall(re_latlong, gmap)[0].split(',')
        except:
            lat,long = None,None


        yield { 'name' : name  ,
                'address' : address,
                'price': price,
                'detail' : detail,
                'bedroom' : bedroom,
                'bathroom' : bathroom,
                'area' : area,
                'purpose' : purpose,
                'project' : project,
                'tower' : tower,
                'startdate' : startdate,
                'sofa' : sofa ,
                'table' : table ,
                'kitchen' : kitchen,
                'kitchen_cabinet' : kitchen_cabinet,
                'kitchen_equipment' : kitchen_equipment,
                'wardrobe' : wardrobe,
                'makeup_table' : makeup_table,
                'work_table' : work_table,
                'tivi' : tivi,
                'washing_machine' : washing_machine,
                'fridge' : fridge,
                'air_conditioner' : air_conditioner,
                'microwave' : microwave,
                'heater' : heater,
                'bed' : bed,
                'fireplace' : fireplace,
                'audio' : audio,
                'internet' : internet,
                'tv_cable' : tv_cable,
                'pet_allowance' :  pet_allowance,
                'elevator' : elevator,
                'pool' : pool,
                'gym' : gym,
                'working_place' : working_place,
                'allday' : allday,
                'car_parking' : car_parking,
                'balcony' : balcony,
                'dry_sauna' : dry_sauna,
                'steam_room' : steam_room,
                'entertainment_room' : entertainment_room,
                'lat' : lat,
                'long' : long,
                'contact' : contact,
                'tel' : tel,
                'url'  : response.url,
                'page_number': page_number, }