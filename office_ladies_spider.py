import json
import os
import re
import time
from urllib import parse

import requests
import scrapy
from scrapy.loader.processors import Join
from selenium import webdriver
from selenium.webdriver.common.by import By


class Episode:
    title: str
    date: str
    excerpt: str
    href: str
    audio_href: str


def save_episode(episode: Episode):
    save_path = './episodes'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    normalized_title = re.sub(r'[^\w]', episode.title, '-')
    audio_file = requests.get(episode.audio_href, stream=True)
    open(os.path.join(save_path, f'{normalized_title}.mp3'), 'wb').write(audio_file.content)
    open(os.path.join(save_path, f'{normalized_title}.json'), 'wb').write(bytes(json.dumps(episode.__dict__), 'utf-8'))


def parse_episode(response):
    iframe_href = response.css('iframe::attr(src)').extract_first()
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
    driver.get(iframe_href)
    time.sleep(10)
    audio_link = driver.find_element(by=By.TAG_NAME, value='audio').get_attribute("src")

    episode: Episode = response.meta['episode']
    episode.audio_href = audio_link
    yield episode.__dict__

    save_episode(episode=episode)


class OfficeLadiesSpider(scrapy.Spider):
    name = 'office ladies spider'
    custom_settings = {
        'DOWNLOAD_DELAY': 10,
    }
    start_urls = ['https://officeladies.com/episodes']

    def parse(self, response):
        for episode_article in response.css('.BlogList-item'):
            episode = Episode()
            episode.title = episode_article.css('.BlogList-item-title::text').extract()[0]
            episode.date = episode_article.css('.Blog-meta-item--date::text').extract()[0]
            episode.excerpt = Join()(episode_article.css('.BlogList-item-excerpt p::text').extract())

            href = episode_article.css('.BlogList-item-title::attr(href)').extract()[0]
            episode.href = parse.urljoin('https://officeladies.com', href)

            yield scrapy.Request(url=episode.href, callback=parse_episode, meta={'episode': episode})

            pagination_link_list = response.css('.BlogList-pagination-link')
            print(pagination_link_list)
            for pagination_link in pagination_link_list:
                if pagination_link.css('.BlogList-pagination-link-label::text').extract()[0] == 'Older':
                    next_page = pagination_link.css('::attr(href)').extract_first()
                    yield response.follow(next_page, self.parse)
