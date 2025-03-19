from neo4j import GraphDatabase

class GenreRefiner:
    def __init__(self, uri="bolt://solarsuna.com:37687", user="neo4j", password="jack1234"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def split_genres_with_dot(self):
        with self.driver.session() as session:
            # 首先找出所有包含 "・" 的 Genre
            result = session.run("""
                MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
                WHERE g.name =~ '.*・.*'  // Match Genres Containing ・
                WITH g, m, g.name AS originalName,
                    split(g.name, '・')[0] AS name1, // Extract {name1}
                    split(g.name, '・')[1] AS name2 // Extract {name2}
                
                // Create/Merge the {name1} genre
                MERGE (genre1:Genre {name: trim(name1)})

                // Create/Merge the {name2} genre
                MERGE (genre2:Genre {name: trim(name2)})

                // Create/Merge the relationships
                MERGE (m)-[:HAS_GENRE]->(genre1)
                MERGE (m)-[:HAS_GENRE]->(genre2)

                // Remove the old relationship and genre
                DETACH DELETE g

                RETURN originalName, name1, name2
            """)
            
            # 打印處理結果
            splits = list(result)
            # for record in splits:
            #    print(f"Split genre: {record['originalName']} -> {record['name1']} and {record['name2']}")
            
            print(f"\nTotal splits: {len(splits)}")

def main():
    refiner = GenreRefiner()
    try:
        print("Starting genre refinement...")
        refiner.split_genres_with_dot()
        print("Genre refinement completed.")
    finally:
        refiner.close()

if __name__ == "__main__":
    main()
