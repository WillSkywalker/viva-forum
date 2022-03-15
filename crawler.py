import re
import json
import requests
from bs4 import BeautifulSoup


HEADER_INFO = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2526.80 Safari/537.36',
    'Host': 'forum.viva.nl',
    'Origin': 'https://forum.viva.nl',
    }


class VivaSearch:

    def __init__(self):
        # self.keyword = keyword
        self.session = requests.session()


    def search(self, keyword, filename):
        url = 'https://search.snmmd.nl/search/?filters=www.viva.nl%2CViva+Forum&page={}&per_page=999&channel=viva&ks=0&r=1&q={}'
        # r = requests.get('https://search.snmmd.nl/search/?filters=www.viva.nl%2CViva+Forum&per_page=999&channel=viva&ks=0&r=1&q={}'.format(keyword))
        # res = r.json()

        with open(filename, 'w') as f:
            f.write('')

        for i in range(1, 11):
            r = requests.get(url.format(i, keyword))
            res = r.json()
            for item in res['data'][0]['links']:
                if item[0]['url'].startswith('https://forum.viva.nl'):
                    thread = self.save_thread(item[0]['url'])
                    if thread:
                        with open(filename, 'a') as f:
                            f.write(thread + '\n')


    def get_thread(self, url):
        '''returns a title and a list of comments'''
        url = 'https://forum.viva.nl' + url
        r = self.session.get(url, headers=HEADER_INFO)
        soup = BeautifulSoup(r.text, features="lxml")
        title = soup.find('div', {"class": 'thread__title'}).text.strip()
        comments = [c.text.strip() for c in soup.find_all('div', {"class": 'post__text'})]
        return title, comments

    def save_thread(self, url):
        '''returns one line containing both title and all comments'''
        if not url.startswith('https://forum.viva.nl'):
            url = 'https://forum.viva.nl' + url
        elif not url.startswith('http'):
            url = 'https:' + url
        r = self.session.get(url, headers=HEADER_INFO)
        soup = BeautifulSoup(r.text, features="lxml")
        try:
            title = self.clean_text(soup.find('div', {"class": 'thread__title'}).text.strip())
        except:
            return
        comments = ''
        # comments = [self.clean_text(c.strip()) for c in soup.find_all('div', {"class": 'post__text'})]
        for c in soup.find_all('div', {"class": 'post__text'}):
            comments += self.clean_text(c.text) + ' '
        return title + comments


    def get_by_topic(self, name, topic_id, filename):
        url = 'https://forum.viva.nl/{}/list_topics/{}'.format(name, topic_id)
        r = self.session.get(url, headers=HEADER_INFO)
        soup = BeautifulSoup(r.text, features="lxml")

        page_num = soup.find('ul', {'class': 'pagination__nav'}).find_all('a')[-2]
        page_num = int(page_num.text)

        with open(filename, 'w') as f:
            f.write('')

        for i in range(page_num):
            url = 'https://forum.viva.nl/{}/list_topics/{}/{}'.format(name, topic_id, i)
            r = self.session.get(url, headers=HEADER_INFO)
            soup = BeautifulSoup(r.text, features="lxml")

            for item in soup.find_all('div', {'class': 'topic__item'}):
                if item.find('a'):
                    thread = self.save_thread(item.find('a')['href'])
                    with open(filename, 'a') as f:
                        f.write(thread + '\n')


    def get_by_keywords(self, name, topic_id, filename):
        url = 'https://forum.viva.nl/{}/list_topics/{}'.format(name, topic_id)
        r = self.session.get(url, headers=HEADER_INFO)
        soup = BeautifulSoup(r.text, features="lxml")

        page_num = soup.find('ul', {'class': 'pagination__nav'}).find_all('a')[-2]
        page_num = int(page_num.text)

        with open(filename, 'w') as f:
            f.write('')

        for i in range(page_num):
            url = 'https://forum.viva.nl/{}/list_topics/{}/{}'.format(name, topic_id, i)
            r = self.session.get(url, headers=HEADER_INFO)
            soup = BeautifulSoup(r.text, features="lxml")

            for item in soup.find_all('div', {'class': 'topic__item'}):
                if item.find('a'):
                    thread = self.save_thread(item.find('a')['href'])
                    with open(filename, 'a') as f:
                        f.write(thread + '\n')


    @staticmethod
    def clean_text(text, strip_html=False, lower=True, keep_emails=False, keep_at_mentions=False):
        # remove html tags
        if strip_html:
            text = re.sub(r'<[^>]+>', '', text)
        else:
            # replace angle brackets
            text = re.sub(r'<', '(', text)
            text = re.sub(r'>', ')', text)
        # lower case
        if lower:
            text = text.lower()
        # eliminate email addresses
        if not keep_emails:
            text = re.sub(r'\S+@\S+', '', text)
        # eliminate @mentions
        if not keep_at_mentions:
            text = re.sub(r'\s@\S+', ' ', text)
        # replace underscores with spaces
        text = re.sub(r'_', ' ', text)
        # break off single quotes at the ends of words
        text = re.sub(r'\s\'', ' ', text)
        text = re.sub(r'\'\s', ' ', text)
        # replace single quotes with underscores
        text = re.sub(r'\'', '_', text)
        # remove periods
        text = re.sub(r'\.', ' ', text)
        # replace all other punctuation with spaces
        # text = replace.sub(' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        # replace all whitespace with a single space
        text = re.sub(r'\s+', ' ', text)
        # strip off spaces on either end
        text = text.strip()
        return text

def main():
    # VivaSearch().get_by_topic('zwanger', '28', 'zwanger.txt')
    VivaSearch().search('kinderwens', 'kinderwens.txt')


if __name__ == '__main__':
    main()
