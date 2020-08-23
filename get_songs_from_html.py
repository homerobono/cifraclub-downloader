import argparse
import re
import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('base_url', nargs='?')
arg_parser.add_argument('artist', nargs='?')

base_url = arg_parser.parse_args().base_url
artist = arg_parser.parse_args().artist

async def get(song_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=song_url) as response:
                song_raw_html = await response.read()
                song_soup = BeautifulSoup(song_raw_html, features="html.parser")
                try:
                    versions_urls = song_soup.find('div', {"data-v":"cifra"}).find('div', class_='list-versions').find_all('a', class_='vers-r')
                except Exception as e:
                    print(song_url, e)
                    return

                [print(a_tag.get('href').strip('/')) for a_tag in versions_urls if a_tag.get('href')]

    except Exception as e:
        await get(song_url)
        pass


async def get_songs_paths(songs_urls):
    await asyncio.gather(*[get(song_url) for song_url in songs_urls])


if __name__ == '__main__':
    raw_html = requests.get('/'.join([base_url, artist]))
    soup = BeautifulSoup(raw_html.content, features="html.parser")

    try:
        songs = soup.find('ul', id='js-a-songs').find_all('li')
    except AttributeError:
        songs = soup.find('ol', id='js-a-t').find_all('li')
    except TypeError:
        exit(1)
    except:
        exit(2)
    
    songs_urls = []
    for song in songs:
        try:
            song_path = song.span.find('a', {"data-title": re.compile(".*guitarra")})['href']
        except TypeError as e:
            continue
        except Exception as e:
            continue
        songs_urls.append('/'.join([base_url.strip('/'), song_path.strip('/')]))

    asyncio.run(get_songs_paths(songs_urls))

