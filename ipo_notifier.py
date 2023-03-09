import scrapy
import datetime

from typing import Tuple

from scrapy.crawler import CrawlerProcess

from utilities import EmailService

class IpoNotifierSpider(scrapy.Spider):
    name = 'Ipo_Notifier'
    base_url = "https://www.sharesansar.com/"
    current_date = str(datetime.date.today())

    # custom headers
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    # crawler's entry point
    def start_requests(self):
        yield scrapy.Request(
            url = self.base_url,
            headers = self.headers,
            callback = self.parse
        )
    
    def get_ipo_data(self, response):
        return {
        'Company' : response.xpath(".//td/a/@title").get(),
        'Symbol' : response.xpath(".//td/a/text()").get(),
        'Units' : response.xpath(".//td[@class= 'text-center'][1]/text()").get(),
        'Unit_Price' : response.xpath(".//td[@class= 'text-center'][2]/text()").get(),
        'Opening_Date' : response.xpath(".//td[6]/text()").get().strip(),
        'Closing_Date' : response.xpath(".//td[7]/text()").get().strip()
        }

    
    def create_ipo_message(self, info:str) -> Tuple[dict,str]:
        ipo_data = self.get_ipo_data(info)
        ipo_str = '\n'.join([f'{key}: {value}' for key, value in ipo_data.items()])
        return ipo_data,ipo_str

    def send_mail_on_opening_date(self, info:str, opening_date: str):

        if (opening_date == str(datetime.date.today() + datetime.timedelta(days = 1))) or (self.current_date == opening_date):
            ipo_data,ipo_str = self.create_ipo_message(info=info)
            yield ipo_data
            email_service = EmailService(ipo_str)
            email_service.send_mail_to_users()
        
    def parse(self, response):
        """
        This function scrapes allprocess.start() the required information about the IPOs
        """
        for i in range(1,6):
            for info in response.xpath(
                f"//div[@id='myTableEip']/table/tbody/tr[{i}]"
            ):
                opening_date = info.xpath(".//td[6]/text()").get().strip()

                yield from self.send_mail_on_opening_date(
                    info=info, opening_date=opening_date
                )

if __name__=='__main__':
    process = CrawlerProcess()
    process.crawl(IpoNotifierSpider)
    process.start()