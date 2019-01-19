import scrapy

# scrapy runspider -s DOWNLOAD_DELAY=5.0 comment.py

class CommentSpider(scrapy.Spider):
    name = 'comment-spider'
    login_url = 'https://society6.com/login?done=/'
    start_urls = [login_url]

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'email': 'xxxxx@yyy.com', 'password': '****'},
            callback=self.after_login
        )

    def after_login(self, response):
        if "The password must be at least 6 characters." in str(response.body) or "username or password is invalid" in str(response.body):
            self.logger.error("Login failed!")
            return
        else:
            # continue scraping with authenticated session...
            product_listings_url = 'https://society6.com/s?q=new+wall-art'
            return scrapy.Request(url = product_listings_url, callback = self.on_listing_page)
    
    def on_listing_page(self, response):
        product_baseurl = 'https://society6.com'        
        links = []

        a = response.xpath("//a[@class='link_product_3ebk3']")
        for i in a.xpath(".//@href"):
            if i.extract() not in links:
                links.append(i.extract())
        
        filename = 'product_links'
        with open(filename, 'w') as f:
            for item in links:
                f.write("{}\n".format(product_baseurl + item))
                yield scrapy.Request(url = product_baseurl + item, callback = self.action)
    
    def action(self, response):
        title = response.selector.xpath('//title/text()').extract_first()
        filename = 'product_names'
        with open(filename, 'a') as f:
            f.write("{}\n".format(title))
