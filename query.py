from neo4j import GraphDatabase
from pathlib import Path
import html

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
                OPTIONAL MATCH (m)-[:RELATED_TO]->(rm:Manga)
                WITH m, 
                     collect(DISTINCT og.name) as genres,
                     collect(DISTINCT {title: rm.title, url: rm.url}) as related
                RETURN m.name as name,
                       m.title as title,
                       m.chapters as chapters,
                       m.image as image,
                       m.url as url,
                       genres,
                       related
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
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .manga-grid {{ 
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .manga-card {{
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }}
        .manga-card img {{
            max-width: 100%;
            height: auto;
        }}
        .manga-title {{
            font-weight: bold;
            margin: 10px 0;
        }}
        .manga-info {{
            font-size: 0.9em;
            color: #666;
        }}
        .genres {{
            margin-top: 5px;
            font-size: 0.8em;
        }}
        .genres span {{
            background: #eee;
            padding: 2px 5px;
            border-radius: 3px;
            margin-right: 5px;
        }}
        .related {{
            margin-top: 5px;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <h1>Manga List - {html.escape(genre_name)}</h1>
    <div class="manga-grid">
"""

        for manga in manga_list:
            genres_html = "".join(f'<span>{html.escape(g)}</span>' for g in manga["genres"])
            related_html = "".join(
                f'<div><a href="{html.escape(r["url"])}">{html.escape(r["title"])}</a></div>'
                for r in manga["related"]
            )
            
            html_content += f"""
        <div class="manga-card">
            <img src="{html.escape(manga['image'])}" alt="{html.escape(manga['title'])}">
            <div class="manga-title">
                <a href="{html.escape(manga['url'])}">{html.escape(manga['title'])}</a>
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
        genre_name = "お色気"
        output_path = query.generate_html(genre_name)
        print(f"HTML file generated: {output_path}")
    finally:
        query.close()

if __name__ == "__main__":
    main()