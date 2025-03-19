from neo4j import GraphDatabase
from pathlib import Path
import html
import sys

class MangaQuery:
    def __init__(self, uri="bolt://solarsuna.com:37687", user="neo4j", password="jack1234"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_manga_by_genre(self, genre_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:Manga)-[:HAS_GENRE]->(g:Genre {name: $genre_name})
                OPTIONAL MATCH (m)-[:HAS_GENRE]->(og:Genre)
                WITH m, 
                     collect(DISTINCT og.name) as genres
                RETURN m.name as name,
                       m.title as title,
                       m.chapters as chapters,
                       m.image as image,
                       m.url as url,
                       genres
                ORDER BY m.chapters DESC
            """, genre_name=genre_name)
            
            return list(result)

    def generate_html(self, genre_name):
        manga_list = self.get_manga_by_genre(genre_name)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Manga List - {html.escape(genre_name)}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Manga List - {html.escape(genre_name)}</h1>
    <div class="manga-grid">
"""

        for manga in manga_list:
            genres_html = "".join(f'<span>{html.escape(g)}</span>' for g in manga["genres"])
            
            html_content += f"""
        <div class="manga-card">
            <div class="loading" data-img="{html.escape(manga['image'])}">Loading...</div>
            <div class="manga-title">
                <a href="{html.escape(manga['url'])}" target="mypage">{html.escape(manga['title'])}</a>
            </div>
            <div class="manga-info">
                Chapters: {manga['chapters'] or 0}
            </div>
            <div class="genres">
                {genres_html}
            </div>
        </div>
"""

        html_content += """
    </div>
    <button id="scroll-top">↑ Top</button>
    <script src="script.js"></script>
</body>
</html>
"""

        # Save HTML file
        output_dir = Path("html")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"{genre_name}.html"
        output_path.write_text(html_content, encoding="utf-8")
        return output_path

def main():
    query = MangaQuery()
    try:
        # 從命令行參數獲取 genre，如果沒有提供則使用默認值
        genre_name = sys.argv[1] if len(sys.argv) > 1 else "お色気"
        
        output_path = query.generate_html(genre_name)
        print(f"HTML file generated: {output_path}")
    finally:
        query.close()

if __name__ == "__main__":
    main()
