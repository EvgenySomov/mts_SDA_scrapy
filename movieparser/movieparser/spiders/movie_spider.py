import scrapy

class MovieSpider(scrapy.Spider):
    name = 'wiki'
    start_urls = ["https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:"
                  "%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83"]

    def parse(self, response):
        for link in response.css('div.mw-category-group a::attr(href)'):
            yield response.follow(link, callback=self.parse_movie)

    def parse_movie(self, response):

        yield {"Название": response.css('table.infobox tbody tr th.infobox-above::text').get().strip(),
               "Жанр": response.css('table.infobox tbody tr th:contains("Жан") + td span.wikidata-snak a::text').getall(),
               "Режиссеры": response.css('table.infobox tbody tr th:contains("Реж") + td span::text').getall(),
               "Страны": response.css('table.infobox tbody tr th:contains("Стра") + td a ::text').getall()}


