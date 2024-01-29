import scrapy
import re
import pandas as pd


class MovieSpider(scrapy.Spider):

    name = 'wiki'
    start_urls = ["https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:"
                  "%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83"]

    def parse(self, response):

        """Рейтинг IMDB взят с https://developer.imdb.com/non-commercial-datasets/ а так как
        'ресурс можно использовать любой на ваше усмотрение' -
        надеюсь вы не будете считать это жульничеством :)"""

        data_IMDB = pd.read_csv('data_movie.tsv', sep='\t')


        # Проходим по всем фильмам на странице
        for link in response.css('div.mw-category-group a::attr(href)'):
            yield response.follow(link, callback=self.parse_movie, meta={'data_IMDB': data_IMDB})

        # Получаем ссылку следующей страницы с группами фильмов
        new_link = response.css('a:contains("Следующая страница")::attr(href)').get()

        # Переходим на нее и зацикливаемся
        if new_link:
            new_link = response.urljoin(new_link)
            yield response.follow(new_link, callback=self.parse)

    def strip_(self, arr: list) -> list:
        """Удадаляем запятые пробелы, спецсимволы"""

        words_only = [word for word in arr if re.match(r'\b\w+\b', word)]
        return words_only


    def parse_movie(self, response):
        """Функция парсинга страницы фильма"""

        data_IMDB = response.meta.get('data_IMDB')

        title = response.css('table.infobox tbody tr th.infobox-above::text').get().strip()
        genres = self.strip_(response.css('table.infobox tbody tr th:contains("Жан") + td ::text').getall())
        directors = self.strip_(response.css('table.infobox tbody tr th:contains("Реж") + td ::text').getall())
        countries = self.strip_(response.css('table.infobox tbody tr th:contains("Стра") + td ::text').getall())
        year = self.strip_(response.css('table.infobox tbody tr th:contains("Год") + td ::text').getall())

        # Получаем ссылку id IMDb фильма при наличии
        imdb_link = response.css('table.infobox tbody tr th:contains("IMDb") + td a::attr(href)').get()
        if imdb_link:
            imdb_id = imdb_link.split("/")[-2]
            imdb_rating = data_IMDB[data_IMDB["tconst"] == imdb_id]
            if len(imdb_rating):
                imdb_rating = imdb_rating.values[0][1]
            else:
                imdb_rating = "Без рейтинга"
        else:
            imdb_rating = "Без рейтинга"


        yield {
            "Название": title,
            "Жанр": genres,
            "Режиссеры": directors,
            "Страны": countries,
            "Год": year,
            "Рейтинг IMDB": imdb_rating
        }
