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

    def merge_genre(self, target, alternatives):
        with self.driver.session() as session:
            result = session.run("""
                // 找出所有需要合併的 Genre 和相關的 Manga
                MATCH (m:Manga)-[r:HAS_GENRE]->(oldGenre:Genre)
                WHERE oldGenre.name IN $alternatives
                
                // 合併到目標 Genre
                MERGE (newGenre:Genre {name: $target})
                
                // 建立新關係
                MERGE (m)-[:HAS_GENRE]->(newGenre)
                
                // 刪除舊關係和舊 Genre
                DELETE r
                
                WITH oldGenre, oldGenre.name as oldName
                DETACH DELETE oldGenre
                RETURN oldName
            """, target=target, alternatives=alternatives)
            
            # 打印處理結果
            merges = list(result)
            for record in merges:
                print(f"Merged genre: {record['oldName']} -> {target}")
            
            print(f"\nTotal merges: {len(merges)}")

    def split_genre(self, source, new_genres):
        """
        將一個 genre 拆分成多個新的 genres
        
        Args:
            source (str): 要拆分的原始 genre 名稱
            new_genres (list): 新的 genre 名稱列表
        """
        with self.driver.session() as session:
            result = session.run("""
                // 找出所有有原始 Genre 的 Manga
                MATCH (m:Manga)-[r:HAS_GENRE]->(oldGenre:Genre {name: $source})
                
                // 對每個 Manga，創建到新 Genres 的關係
                WITH m, r, oldGenre
                UNWIND $new_genres AS new_genre_name
                
                // 創建或合併新的 Genre 節點
                MERGE (newGenre:Genre {name: new_genre_name})
                
                // 創建新關係
                MERGE (m)-[:HAS_GENRE]->(newGenre)
                
                // 刪除舊關係
                DELETE r
                
                WITH DISTINCT oldGenre
                DETACH DELETE oldGenre
                
                RETURN count(*) as affected_mangas
            """, source=source, new_genres=new_genres)
            
            affected = result.single()["affected_mangas"]
            print(f"Split genre: {source} -> {', '.join(new_genres)}")
            print(f"Affected manga count: {affected}")

def main():
    refiner = GenreRefiner()
    try:
        print("Starting genre refinement...")
        
        # 原有的處理
        refiner.split_genres_with_dot()
        refiner.merge_genre("コメディ", ["コメディー", "ラブコメ"])
        refiner.merge_genre("異世界", ["転生", "異世界モノ"])
        refiner.merge_genre("恋愛", ["ラブストーリー", "ロマンス", "恋愛ファンタジー", "純愛", "女子高生"])
        refiner.merge_genre("ドラマ", ["ヒューマンドラマ", "人間ドラマ", "ドラマ化"])
        refiner.merge_genre("オトナ", ["オトナコミック", "オトナ向け", "成人向け", "大人向け"])
        refiner.merge_genre("エッチ", ["Ecchi", "お色気", "エロい", "エロ", "巨乳", "爆乳", "むちむち"])
        refiner.merge_genre("学園", ["学校生活", "先生", "女子校生", "JK", "同級生",
                                   "女子大生", "学園モノ", "大学生", "高校生", "学生", "k高校生", "女教師"])
        refiner.merge_genre("SF", ["-SF-"])
        refiner.merge_genre("青年漫画", ["青年", "青年マンガ"])
        refiner.merge_genre("少年漫画", ["少年", "少年マンガ"])
        refiner.merge_genre("少女漫画", ["少女", "少女マンガ"])
        refiner.merge_genre("女性漫画", ["女性マンガ"])
        refiner.merge_genre("ミステリー", ["ミステリー/ホラー", "ホラー", "サスペンス", "吸血鬼"])
        refiner.merge_genre("歴史", ["ロマンスA 超自然的 / 歴史", "古代～飛鳥･奈良", "戦国", "三国志", "歴史的",
                                   "明治維新", "戦国･安土桃山時代", "幕末", "江戸時代(武士･時代劇)", "近代(明治以降)"])
        refiner.merge_genre("料理", ["料理･グルメ", "グルメ"])
        refiner.merge_genre("貴族", ["王様", "王女", "姫"])
        refiner.merge_genre("小説", ["小説家になろう", "なろう系", "WEB小説", "コミカライズ(小説", "ラノベ"])
        refiner.merge_genre("ゲーム", ["ゲームコミカライズ", "デスゲーム", "乙女ゲーム", "ゲーム)"])
        refiner.merge_genre("百合", ["GL"])
        refiner.merge_genre("アニメ化", ["映画化", "メディア化"])
        refiner.merge_genre("生活", ["くらし", "日常", "くらし。生活"])
        refiner.merge_genre("家族", ["妹", "義母", "浮気", "不倫", "姉", "人妻", "幼なじみ", "姉妹"])
        refiner.merge_genre("特典", ["シーモア限定特典付き", "電子特典付き", "独占配信"])
        refiner.merge_genre("大賞", ["電子コミック大賞2018", "電子コミック大賞2019", "電子コミック大賞2020", "電子コミック大賞2021", 
                                   "電子コミック大賞2022", "電子コミック大賞2023", "電子コミック大賞2024", "電子コミック大賞2025"])
        refiner.merge_genre("ハーレム", ["複数プレイ"])
        refiner.merge_genre("スポーツ", ["野球･ソフトボール"])
        refiner.merge_genre("動物", ["ペット"])
        
        # 使用新的 split_genre 函數
        refiner.split_genre("TL小説", ["TL", "小説"])
        refiner.split_genre("ロマンス小説", ["恋愛", "小説"])
        refiner.split_genre("BLドラマCD化", ["BL", "ドラマ"])
        refiner.split_genre("学園コメディ", ["学園", "コメディ"])

        print("Genre refinement completed.")
    finally:
        refiner.close()

if __name__ == "__main__":
    main()
