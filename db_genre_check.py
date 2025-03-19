from neo4j import GraphDatabase
import csv
from pathlib import Path
import html

class GenreChecker:
    def __init__(self, uri="bolt://solarsuna.com:37687", user="neo4j", password="jack1234"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.major_genres = set()  # manga_count >= 100 的 genres
        self.load_genres()

    def close(self):
        self.driver.close()

    def load_genres(self):
        """從 genre.csv 讀取並分類 genres"""
        with open('genre.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if int(row['manga_count']) >= 100:
                    self.major_genres.add(row['genre'])

    def check_manga_without_major_genres(self):
        """檢查沒有主要 genre 的漫畫並生成 HTML 報告"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Manga)
                WITH m, [(m)-[:HAS_GENRE]->(g:Genre) | g.name] as genres
                WHERE NONE(genre IN genres WHERE genre IN $major_genres)
                RETURN m.name as manga_name, 
                       m.title as title,
                       m.image as image,
                       m.chapters as chapters,
                    
                       genres
                ORDER BY m.chapters DESC
            """, major_genres=list(self.major_genres))

            # 生成 HTML 內容
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Manga Without Major Genres</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Manga Without Major Genres</h1>
    <div class="info">
        <h2>Major Genres (manga_count >= 100):</h2>
        <div class="genres">
            {', '.join(sorted(list(self.major_genres)))}
        </div>
    </div>
    <div class="manga-grid">
"""
            count = 0
            for record in result:
                count += 1
                genres_html = "".join(f'<span>{html.escape(g)}</span>' for g in record['genres'])
                
                html_content += f"""
        <div class="manga-card">
            <div class="loading" data-img="{html.escape(record['image'])}">Loading...</div>
            <div class="manga-title">
                <a href="https://jmanga.se/read/{record['manga_name']}-raw/" target="mypage">{html.escape(record['title'])}</a>
            </div>
            <div class="manga-info">
                Chapters: {record['chapters'] or 0}
            </div>
            <div class="genres">
                {genres_html}
            </div>
        </div>
"""

            html_content += f"""
    </div>
    <div class="summary">
        Total: {count} manga without major genres
    </div>
    <button id="scroll-top">↑ Top</button>
    <script src="script.js"></script>
</body>
</html>
"""

            # 保存 HTML 文件
            output_dir = Path("docs")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "check.html"
            output_path.write_text(html_content, encoding="utf-8")
            
            print(f"Report generated: {output_path}")
            print(f"Total manga without major genres: {count}")

def main():
    checker = GenreChecker()
    try:
        checker.check_manga_without_major_genres()
    finally:
        checker.close()

if __name__ == "__main__":
    main()
