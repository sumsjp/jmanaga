from neo4j import GraphDatabase
from pathlib import Path
import csv

class GenreCounter:
    def __init__(self, uri="bolt://solarsuna.com:37687", user="neo4j", password="jack1234"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_genre_counts(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
                WITH g.name as genre, count(m) as manga_count
                RETURN genre, manga_count
                ORDER BY manga_count DESC
            """)
            return [(record["genre"], record["manga_count"]) for record in result]

    def save_to_csv(self, filename="genre.csv"):
        genre_counts = self.get_genre_counts()
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['genre', 'manga_count'])
            writer.writerows(genre_counts)
        
        return Path(filename).absolute()

def list_genres():
    """
    獲取所有 genre 並保存到 CSV 文件
    返回: Path 對象，指向生成的 CSV 文件
    """
    counter = GenreCounter()
    try:
        output_path = counter.save_to_csv()
        print(f"Genre counts saved to: {output_path}")
        return output_path
    finally:
        counter.close()

def main():
    return list_genres()

if __name__ == "__main__":
    main()
