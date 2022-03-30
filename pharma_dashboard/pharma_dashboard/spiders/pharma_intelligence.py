#%%
from turtle import Screen
import scrapy
from lib2to3.pgen2.token import OP
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from shutil import which
from scrapy.selector import Selector
import os 
import string

class PharmaIntelligenceSpider(scrapy.Spider):
    name = 'pharma_intelligence'
    #allowed_domains = ['duckduckgo.com']
    #start_urls = ['http://duckduckgo.com/']

    def __init__(self):
        #super().__init__()

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        print("Spider path" + os.getcwd())

        #driver = webdriver.Chrome(executable_path="../chromedriver",
        #        keep_alive=True)
        driver = webdriver.Chrome(executable_path="/Users/architdatar_1/Software/pharma_dashboard/pharma_dashboard/pharma_dashboard/chromedriver",
                keep_alive=True)

        driver.get("https://duckduckgo.com")

        search_input = driver.find_element_by_xpath("(//input[contains(@class, 'js-search-input')])[1]")

        #Things we can search. 
        #search_input.send_keys("COVID news latest")
        #search_input.send_keys("pfizer news latest")
        search_input.send_keys("pfizer abc news")
        search_input.send_keys(Keys.ENTER)

        #First, we will load the page completely for the browser and then scrape. 
        #this strategy could change for other websites we use like Google. 
        for _ in range(2):
            search_btn = driver.find_element_by_xpath("//a[@class='result--more__btn btn btn--full']")
            #search_btn = driver.find_element_by_xpath("//input[@id='search_button_homepage']")
            search_btn.click()

        self.html = driver.page_source
        self.driver = driver

        #self.parse(self.html)
        driver.close()

        #Assumption: we can scrape articles from certain web domains in a pre-defined way. 
        self.scrapable_domain_list = ["abcnews.go.com", 
        "washingtonpost.com", "foxnews.com", "finance.yahoo.com"
        ]

    def start_requests(self):
        """"""
        resp = Selector(text=self.html)

        site_links_on_page = resp.xpath('//a[@class="result__a js-result-title-link"]/@href').getall()

        site_link_index = 0

        #for site_link in ["https://abcnews.go.com/Politics/pfizer-asks-fda-authorization-covid-19-vaccine-children/story?id=82598025"]:    
        for site_link in site_links_on_page:    
            print(f"Site link index: {site_link_index}")
            domain = site_link.split("/")[2]
            try:
                if domain in self.scrapable_domain_list:
                    yield scrapy.Request(url=site_link, callback=self.parse_link, 
                    meta={"site_link_index": site_link_index, "url": site_link,
                    "domain": domain}) #errback=self.log_error)                                
                else:
                    yield {"site_link_index": site_link_index, "url": site_link,
                "domain": domain}
            except Exception as e:
                print("Failed")
                continue

            site_link_index += 1

    def parse_link(self, response):
        """
        """
        site_link_index = response.meta.get("site_link_index")
        print("Entered parse link.")
        print(f"Parse link: {site_link_index}")
        
        site_link = response.meta.get("site_link")
        domain = response.meta.get("domain")

        article_text = self.scrape_text(domain, response)

        yield {"site_link_index": site_link_index, "url": site_link,
                "domain": domain, "text": article_text}


    def scrape_text(self, domain, response):
        """
        """

        print("Entered scrape text")

        if domain == "foxnews.com":
            x_path_string = "//div[@class='article-body']/p//text()"
        elif domain == "usatoday.com":
            x_path_string = "//p[@class='gnt_ar_b_p']//text()"
        elif domain == "washingtonpost.com":
            x_path_string = '//div[@class="article-body"]//p[@class="font--body font-copy gray-darkest ma-0 pb-md "]//text()'
        elif domain == "nytimes.com":
            x_path_string = '//section[@name="articleBody"]//p[@class="css-axufdj evys1bk0"]//text()'
        elif domain == "abcnews.go.com":
            x_path_string = '//section[@class="Article__Content story"]/p//text()'
        elif domain == "buzzfeed.com":
            x_path_string = '//div[@class=" buzz--long"]//p//text()'
        elif domain == "finance.yahoo.com":
            x_path_string = '//div[@class="caas-body"]//p'

        article_text_string = " ".join(response.xpath(x_path_string).getall())        
        article_text = article_text_string.translate(str.maketrans('', '', string.punctuation))

        return article_text

    def log_error(self, failure):
        """"""
        self.logger.error(repr(failure))


#if __name__ == "__main__":
#    pis = PharmaIntelligenceSpider()
# %%
