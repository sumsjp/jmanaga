#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import List
from dataclasses import dataclass
from pathlib import Path
from detail import MangaDetailScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MangaItem:
    title: str
    url: str
    genres: List[str]

class JMangaScraper:
    BASE_URL = "https://jmanga.se"
    RAW_MANGA_URL = f"{BASE_URL}/raw-manga/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })

    def get_manga_list(self) -> List[MangaItem]:
        """Fetch and parse the manga list from the website."""
        try:
            logger.info(f"Fetching manga list from {self.RAW_MANGA_URL}")
            response = self.session.get(self.RAW_MANGA_URL)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            manga_items = []
            
            # Find all manga detail divs
            manga_details = soup.find_all('div', class_='manga-detail')
            logger.info(f"Found {len(manga_details)} manga entries")
            
            for detail in manga_details:
                try:
                    # Get title and URL from the manga-name section
                    title_element = detail.find('h3', class_='manga-name').find('a')
                    title = title_element.get('title', '').strip()
                    url = title_element.get('href', '').strip()
                    
                    # Get genres from fd-infor section
                    genres = []
                    genre_elements = detail.find('div', class_='fd-infor').find_all('a')
                    for genre in genre_elements:
                        genre_text = genre.get_text().strip()
                        if genre_text:
                            genres.append(genre_text)
                    
                    manga_items.append(MangaItem(
                        title=title,
                        url=url,
                        genres=genres
                    ))
                    
                except Exception as e:
                    logger.error(f"Error parsing manga entry: {e}")
                    continue
            
            return manga_items
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch manga list: {e}")
            return []

    def save_to_json(self, manga_items: List[MangaItem], filename: str = "manga_list.json"):
        """Save the manga list to a JSON file."""
        try:
            data = [{
                'title': item.title,
                'url': item.url,
                'genres': item.genres
            } for item in manga_items]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved manga list to {filename}")
        except Exception as e:
            logger.error(f"Failed to save manga list to JSON: {e}")

def main():
    scraper = JMangaScraper()
    manga_list = scraper.get_manga_list()
    
    if manga_list:
        logger.info(f"Successfully scraped {len(manga_list)} manga titles")
        
        # 確保 docs 目錄存在
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)
        
        # 初始化 detail scraper
        detail_scraper = MangaDetailScraper()
        
        # 處理每個漫畫
        for manga in manga_list:
            # 創建安全的文件名
            safe_title = "".join(c for c in manga.title if c.isalnum() or c in (' ', '-', '_'))
            safe_title = safe_title.strip()
            json_path = docs_dir / f"{safe_title}.json"
            
            # 檢查文件是否存在
            if not json_path.exists():
                logger.info(f"Fetching details for: {manga.title}")
                try:
                    # 獲取並保存詳細信息
                    manga_detail = detail_scraper.get_manga_detail(manga.url)
                    if manga_detail:
                        detail_scraper.save_to_json(manga_detail)
                    else:
                        logger.warning(f"Failed to get details for: {manga.title}")
                except Exception as e:
                    logger.error(f"Error processing {manga.title}: {e}")
            else:
                logger.info(f"Details already exist for: {manga.title}")
        
        # 打印樣本信息
        print("\nSample of manga list:")
        for manga in manga_list[:5]:  # 只顯示前5個
            print(f"\nTitle: {manga.title}")
            print(f"URL: {manga.url}")
            print(f"Genres: {', '.join(manga.genres)}")
    else:
        logger.warning("No manga found")

if __name__ == "__main__":
    main()
