#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import os
from datetime import datetime
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class MangaDetail:
    title: str
    short_title: str
    url: str
    status: str
    genres: List[str]
    summary: str
    chapter_count: int
    image: str
    related_manga: List[Dict[str, str]] = None  # 設置默認值為 None

class MangaDetailScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        # 確保 docs 目錄存在
        self.docs_dir = Path('docs')
        self.docs_dir.mkdir(exist_ok=True)

    def fetch_and_save_html(self, url: str, filename: str = "test.html") -> Optional[str]:
        """Fetch HTML content and save it to a file."""
        try:
            logger.info(f"Fetching content from {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            # Save HTML content with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(filename)
            filename_with_timestamp = f"{base}{ext}"
            
            with open(filename_with_timestamp, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"Saved HTML content to {filename_with_timestamp}")
            
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch content: {e}")
            return None

    def parse_html(self, url: str, html_content: str) -> Optional[MangaDetail]:
        """Parse HTML content and extract manga details."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get chapter count from chapter-item
            chapter_items = soup.find_all('li', class_='chapter-item')
            chapter_count = len(chapter_items)
            logger.info(f"Found {chapter_count} chapters")

            # Extract basic information
            title = self._get_title(soup)
            status = self._get_status(soup)
            genres = self._get_genres(soup)
            summary = self._get_summary(soup)
            image = self._get_image(soup)
            
            # Get related manga and log the results
            related_manga = self.get_related_manga(html_content)
            logger.info(f"Related manga count: {len(related_manga)}")
            for manga in related_manga:
                logger.debug(f"Related manga found: {manga['title']}")

            return MangaDetail(
                title=title,
                short_title="",
                url=url,
                status=status,
                genres=genres,
                summary=summary,
                image=image,
                chapter_count=chapter_count,
                related_manga=related_manga
            )

        except Exception as e:
            logger.error(f"Failed to parse HTML content: {e}")
            return None

    def get_manga_detail(self, url: str) -> Optional[MangaDetail]:
        """Fetch and parse the manga detail page."""
        html_content = self.fetch_and_save_html(url)
        if html_content:
            return self.parse_html(url, html_content)
        return None

    def _get_title(self, detail_section: BeautifulSoup) -> str:
        """Extract the main title from detail section."""
        title_elem = detail_section.find('h2', class_='manga-name')
        return title_elem.get_text().strip() if title_elem else ""

    def _get_status(self, detail_section: BeautifulSoup) -> str:
        """Extract manga status from detail section."""
        return ""

    def _get_genres(self, detail_section: BeautifulSoup) -> List[str]:
        """Extract genres from detail section."""
        genres = []
        genre_section = detail_section.find('div', class_='genres')
        if genre_section:
            genre_links = genre_section.find_all('a')
            genres = [link.get_text().strip() for link in genre_links]
        return genres

    def _get_summary(self, detail_section: BeautifulSoup) -> str:
        """Extract manga summary from detail section."""
        summary_elem = detail_section.find('div', class_='description')
        return summary_elem.get_text().strip() if summary_elem else ""

    def _get_image(self, detail_section: BeautifulSoup) -> str:
        """Extract manga summary from detail section."""
        image_elem = detail_section.find('div', class_='manga-poster')
        image_elem = image_elem and image_elem.find('img')
        return image_elem.get('data-src', '').strip() if image_elem else ""

    def get_related_manga(self, html_content: str) -> List[Dict[str, str]]:
        """Extract related manga links and titles."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            related_items = []
            
            # 找到相關漫畫列表區域
            related_sections = soup.find_all('h3', class_='manga-name')
            for related_section in related_sections:
                manga_links = related_section.find('a')
                
                url = manga_links.get('href', '').strip()
                title = manga_links.get('title', '').strip()
                        
                if url and title:
                    related_items.append({
                        'url': url,
                        'title': title
                    })
    
            logger.info(f"Found {len(related_items)} related manga items")
            return related_items
            
        except Exception as e:
            logger.error(f"Failed to parse related manga: {e}")
            return []

    def save_to_json(self, manga_detail: MangaDetail) -> None:
        """Save manga detail to JSON file."""
        try:
            # 清理標題中的非法字符，以便用作文件名
            safe_title = "".join(c for c in manga_detail.title if c.isalnum() or c in (' ', '-', '_'))
            safe_title = safe_title.strip()
            
            # 構建完整的文件路徑
            file_path = self.docs_dir / f"{safe_title}.json"
            
            # 將 MangaDetail 對象轉換為字典
            manga_dict = {
                'title': manga_detail.title,
                'short_title': manga_detail.short_title,
                'chapter_count': manga_detail.chapter_count,
                'url': manga_detail.url,
                'genres': manga_detail.genres,
                'status': manga_detail.status,
                'summary': manga_detail.summary,
                'image': manga_detail.image,
                'related_manga': manga_detail.related_manga
            }
            
            # 寫入 JSON 文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(manga_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved manga detail to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save manga detail to JSON: {e}")

def main():
    scraper = MangaDetailScraper()
    url = "https://jmanga.se/read/ベタ惚れの婚約者が悪役令嬢にされそうなのでヒロイン側にはそれ相応の報いを受けてもらう-raw/"
    
    manga_detail = scraper.get_manga_detail(url)
    
    if manga_detail:
        # 保存到 JSON 文件
        scraper.save_to_json(manga_detail)
        
        # 打印信息
        print("\nManga Detail Information:")
        print(f"Title: {manga_detail.title}")
        print(f"URL: {manga_detail.url}")
        print(f"Status: {manga_detail.status}")
        print(f"Genres: {', '.join(manga_detail.genres)}")
        print(f"Image: {manga_detail.image}")
        print(f"Total Chapters: {manga_detail.chapter_count}")
        print("\nSummary:")
        print(manga_detail.summary)
        
        if manga_detail.related_manga:
            print("\nRelated Manga:")
            for manga in manga_detail.related_manga:
                print(f"- {manga['title']}: {manga['url']}")
    else:
        print("Failed to fetch manga details")

if __name__ == "__main__":
    main()
