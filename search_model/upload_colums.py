import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.system('chcp 65001 > nul') 

import pandas as pd 
import numpy as np
import requests
import asyncio
import aiohttp
import time
from config import API_KEY, PASSWORD_API, ADDRESS


BASE_URL = 'https://api.themoviedb.org/3/movie'

# Функция запроса данных по одному tmdb_id
async def fetch_movie_data(session, tmdb_id):
    try:
        # Запрос основной информации
        movie_url = f"{BASE_URL}/{tmdb_id}?api_key={API_KEY}&language=ru"
        credits_url = f"{BASE_URL}/{tmdb_id}/credits?api_key={API_KEY}"

        async with session.get(movie_url) as movie_resp:
            movie_data = await movie_resp.json()

        async with session.get(credits_url) as credits_resp:
            credits_data = await credits_resp.json()

        description = movie_data.get('overview', '')
        poster_path = movie_data.get('poster_path', '')
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ''
        director = next((p['name'] for p in credits_data.get('crew', []) if p['job'] == 'Director'), None)
        actors = ', '.join([a['name'] for a in credits_data.get('cast', [])[:5]])
        print(f"Обработан tmdb_id: {tmdb_id}")
        return {
            'tmdbId': tmdb_id,
            'description': description,
            'poster_url': poster_url,
            'director': director,
            'actors': actors
        }

    except Exception as e:
        print(f"Ошибка при обработке tmdb_id {tmdb_id}: {e}")
        return {
            'tmdbId': tmdb_id,
            'description': None,
            'poster_url': None,
            'director': None,
            'actors': None
        }

# Основной цикл с лимитом 20 запросов/сек
async def fetch_all(df):
    results = []
    connector = aiohttp.TCPConnector(limit=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i, tmdb_id in enumerate(df['tmdbId']):
            tasks.append(fetch_movie_data(session, tmdb_id))
            # Пауза каждые 20 запросов
            if (i + 1) % 20 == 0:
                results += await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)  # пауза 1 секунда

        # Завершение оставшихся задач
        if tasks:
            results += await asyncio.gather(*tasks)
    print("Запросы завершены")
    return results

# Загрузка CSV и обновление
def enrich_dataframe(df):
    results = asyncio.run(fetch_all(df))
    result_df = pd.DataFrame(results)
    enriched_df = df.merge(result_df, on='tmdbId', how='left')
    return enriched_df

# Пример использования
if __name__ == "__main__":
    df = pd.read_csv(ADDRESS + 'data/movies.csv', encoding='utf-8')
    df_links = pd.read_csv(ADDRESS + 'data/links.csv', encoding='utf-8')

    df['genres'] = df['genres'].str.split('|')
    df['year'] = df['title'].str.extract(r'\((\d{4})\)')
    df['title'] = df['title'].str[:-7]
    df['tmdbId'] = df_links['tmdbId']
       


         
    enriched_df = enrich_dataframe(df)
    enriched_df.to_csv(ADDRESS + 'data/movies_enriched.csv', index=False, encoding='utf-8')
    print("Готово: enriched_df сохранён в movies_enriched.csv")