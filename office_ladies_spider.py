import json
import os
import re
from urllib import parse

import requests
import scrapy
from requests.adapters import HTTPAdapter
from scrapy.loader.processors import Join
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from urllib3 import Retry


class Episode:
    title: str
    date: str
    excerpt: str
    href: str
    audio_href: str


def save_episode(episode: Episode):
    save_path = './episodes-1'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    audio_file = session.get(episode.audio_href, stream=True)
    normalized_title = re.sub(r'[^\w,|\s\']', '-', episode.title)
    open(os.path.join(save_path, f'{normalized_title}.mp3'), 'wb').write(audio_file.content)
    open(os.path.join(save_path, f'{normalized_title}.json'), 'wb').write(bytes(json.dumps(episode.__dict__), 'utf-8'))


class WaitForAudioLink(object):
    def __call__(self, driver):
        try:
            audio_link: str = driver.find_element(by=By.TAG_NAME, value='audio').get_attribute("src")
            return 'https://pdst.fm/e/stitcher.simplecastaudio.com/' in audio_link
        except Exception:
            return False


class OfficeLadiesSpider(scrapy.Spider):
    name = 'office ladies spider'
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_ITEMS': 1
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

            yield scrapy.Request(url=episode.href, callback=self.parse_episode, meta={'episode': episode})

            pagination_link_list = response.css('.BlogList-pagination-link')
            for pagination_link in pagination_link_list:
                if pagination_link.css('.BlogList-pagination-link-label::text').extract()[0] == 'Older':
                    next_page = pagination_link.css('::attr(href)').extract_first()
                    yield response.follow(next_page, self.parse)

    def parse_episode(self, response):
        iframe_href = response.css('iframe::attr(src)').extract_first()
        driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
        driver.get(iframe_href)
        WebDriverWait(driver=driver, timeout=20).until(WaitForAudioLink())
        audio_link = driver.find_element(by=By.TAG_NAME, value='audio').get_attribute("src")
        driver.close()
        if audio_link and audio_link != '':
            episode: Episode = response.meta['episode']
            episode.audio_href = audio_link
            yield episode.__dict__

            save_episode(episode=episode)
        else:
            yield response.follow(response.request.url, self.parse)
