from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.spider import BaseSpider
from scrapy.http import Request
import time
import sys
from indeed.items import IndeedItem


class IndeedSpider(CrawlSpider):
	name = "indeed"
	allowed_domains = ["indeed.com"]
	start_urls = [
		"http://www.indeed.com/jobs?q=linux&l=Chicago&sort=date?",
	]


	rules = ( 
		Rule(SgmlLinkExtractor(allow=('/jobs.q=linux&l=Chicago&sort=date$','q=linux&l=Chicago&sort=date&start=[0-9]+$',),deny=('/my/mysearches', '/preferences', '/advanced_search','/my/myjobs')), callback='parse_item', follow=True),

    	)

	def parse_next_site(self, response):

        	item = response.request.meta['item']
            	item['source_url'] = response.url
            	item['source_page_body'] = response.body
		item['crawl_timestamp'] =  time.strftime('%Y-%m-%d %H:%M:%S')

        	return item 


	def parse_item(self, response):
	        self.log('\n Crawling  %s\n' % response.url)
		hxs = HtmlXPathSelector(response)
		sites = hxs.select("//div[@class='row ' or @class='row lastRow']")
		#sites = hxs.select("//div[@class='row ']")
		items = []
		for site in sites:
			item = IndeedItem(company='none')
			
			item['job_title'] = site.select('h2/a/@title').extract()
			link_url= site.select('h2/a/@href').extract()
			item['link_url'] = link_url
			item['crawl_url'] = response.url
			item['location'] = site.select("span[@class='location']/text()").extract()

			# Not all entries have a company
			if  site.select("span[@class='company']/text()").extract() == []:
				item['company'] = [u'']
			else:
				item['company'] = site.select("span[@class='company']/text()").extract()

			item['summary'] = site.select("//table/tr/td/span[@class='summary']").extract()
			item['source'] = site.select("table/tr/td/span[@class='source']/text()").extract()
			item['found_date'] = site.select("table/tr/td/span[@class='date']/text()").extract()
			#item['source_url'] = self.get_source(link_url)
			request = Request("http://www.indeed.com" + item['link_url'][0], callback=self.parse_next_site)
            		request.meta['item'] = item
			yield request

			items.append(item)
		return


			
SPIDER=IndeedSpider()
