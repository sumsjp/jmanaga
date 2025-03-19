from pathlib import Path
import csv
from db_genre_list import list_genres
from html_genre import MangaQuery
import html

def get_genre_list():
    # 調用 list_genres() 函數獲取 genre 列表
    csv_path = list_genres()
    
    genres = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            count = int(row['manga_count'])
            if count < 100:
                continue
            genres.append((row['genre'], count))
    
    return genres

def generate_genre_pages(genres):
    query = MangaQuery()
    try:
        for genre, _ in genres:
            print(f"Generating HTML for genre: {genre}")
            query.generate_html([genre])
    finally:
        query.close()

def generate_main_html(genres):
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Manga Genres</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Manga Genres</h1>
    <div class="genre-grid">
"""

    for genre, count in genres:
        safe_genre = genre.replace("/", "_").replace("\\", "_")
        html_content += f"""
        <div class="genre-card" onclick="window.open('{html.escape(safe_genre)}.html', '_self')">
            <div class="genre-name">{html.escape(genre)}</div>
            <div class="manga-count">{count} manga</div>
        </div>
"""

    html_content += """
    </div>
    <button id="scroll-top">↑ Top</button>
    <script src="script.js"></script>
</body>
</html>
"""

    output_dir = Path("html")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "index.html"
    output_path.write_text(html_content, encoding="utf-8")
    return output_path

def main():
    print("Getting genre list...")
    genres = get_genre_list()
    
    print("Generating individual genre pages...")
    generate_genre_pages(genres)
    
    print("Generating main page...")
    output_path = generate_main_html(genres)
    print(f"Main page generated: {output_path}")

if __name__ == "__main__":
    main()
