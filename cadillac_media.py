import requests
from bs4 import BeautifulSoup
import os
import csv
import time
import pprint


def write_csv(lines, file_name):
    with open(file=file_name, encoding='utf-8', mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(lines)


def send_request(url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0'
        }
        res = requests.request('GET', url=url, headers=headers)
        if res.status_code == 200:
            return res
        return send_request(url=url)
    except ConnectionError as e:
        time.sleep(5)
        return send_request(url=url)


def parse_soup(html):
    return BeautifulSoup(html.content, 'html5lib')


def middleware(year):
    if year == 2020:
        url = 'https://media.cadillac.com/media/us/en/cadillac/vehicles.html'
    else:
        url = 'https://media.cadillac.com/media/us/en/cadillac/archive/{}.html'.format(year)
    res = send_request(url=url)
    soup = parse_soup(res)
    thumbnails = soup.find_all(attrs={'class': 'thumb_nail_caption'})
    for thumbnail in thumbnails:
        thumbnail_url = 'https://media.cadillac.com' + thumbnail.a['href']
        model = thumbnail.text.strip()
        thumbnail_soup = parse_soup(send_request(thumbnail_url))
        more_buttons = thumbnail_soup.find_all(attrs={'class': 'more'})
        for more_button in more_buttons:
            if more_button.a and more_button.a.has_attr('href') and 'galleryphotogrid' in more_button.a['href']:
                button_link = 'https://media.cadillac.com' + more_button.a['href']
                button_link_soup = parse_soup(send_request(button_link))
                image_cards = button_link_soup.find_all(attrs={'class': 'image_container'})
                for image_card in image_cards:
                    image_url = 'https://media.cadillac.com' + image_card.img['src'].replace('w_140.maxw_140', 'w_1120.maxw_1120')
                    line = [year, 'Cadillac', model, '', image_url]
                    print(line)
                    write_csv(lines=[line], file_name=file_name)


def main():
    for year in range(2015, 2021):
        middleware(year=year)


if __name__ == '__main__':
    file_name = 'Cadillac_Images_From_Media.csv'
    head = [['YEAR', 'MAKE', 'MODEL', 'SECTION', 'IMAGE_URL']]
    write_csv(lines=head, file_name=file_name)
    main()