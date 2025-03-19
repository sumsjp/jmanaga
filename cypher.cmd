# remove self loop
    MATCH (n)-[r:RELATED_TO]->(n)
    DELETE r

# handle {name1}({name2})
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
        WHERE g.name =~ '.*（.*）.*'  // Match Genres Containing Parentheses
        WITH g, m, g.name AS originalName,
            substring(g.name, 0, size(g.name) - size(split(g.name, '（')[-1]) - 1) AS name1, // Extract {name1}
            split(split(g.name, '（')[-1], '）')[0] AS name2 // Extract {name2}
    return g, m, originalName, name1, name2

##
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
    WHERE g.name =~ '.*\\(.*\\).*'  // Match Genres Containing Parentheses
        WITH g, m, g.name AS originalName,
            substring(g.name, 0, size(g.name) - size(split(g.name, '(')[-1]) - 1) AS name1, // Extract {name1}
            split(split(g.name, '(')[-1], ')')[0] AS name2 // Extract {name2}
    return g, m, originalName, name1, name2

# split {name1}({name2})
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
    WHERE g.name =~ '.*\\(.*\\).*'  // Match Genres Containing Parentheses
        WITH g, m, g.name AS originalName,
            substring(g.name, 0, size(g.name) - size(split(g.name, '(')[-1]) - 1) AS name1, // Extract {name1}
            split(split(g.name, '(')[-1], ')')[0] AS name2 // Extract {name2}
        
    // Create/Merge the {name1} genre
    MERGE (genre1:Genre {name: trim(name1)})

    // Create/Merge the {name2} genre
    MERGE (genre2:Genre {name: trim(name2)})

    // Create/Merge the relationships
    MERGE (m)-[:HAS_GENRE]->(genre1)
    MERGE (m)-[:HAS_GENRE]->(genre2)

    // Remove the old relationship
    DETACH DELETE g

##

    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
    WHERE g.name =~ '.*（.*）.*'  // Match Genres Containing Parentheses
      WITH g, m, g.name AS originalName,
        substring(g.name, 0, size(g.name) - size(split(g.name, '（')[-1]) - 1) AS name1, // Extract {name1}
        split(split(g.name, '（')[-1], '）')[0] AS name2 // Extract {name2}
        
    // Create/Merge the {name1} genre
    MERGE (genre1:Genre {name: trim(name1)})

    // Create/Merge the {name2} genre
    MERGE (genre2:Genre {name: trim(name2)})

    // Create/Merge the relationships
    MERGE (m)-[:HAS_GENRE]->(genre1)
    MERGE (m)-[:HAS_GENRE]->(genre2)

    // Remove the old relationship
    DETACH DELETE g

# merge Genre オトナ, オトナコミック, オトナ向け
    MATCH (m:Manga)-[r:HAS_GENRE]->(oldGenre)
            WHERE oldGenre.name IN ["オトナコミック", "オトナ向け"]
        MERGE (newGenre:Genre {name: "オトナ"})
        MERGE (m)-[:HAS_GENRE]->(newGenre)
        DELETE r // 删除旧的关系

# print all Genre and count of Manga HAS_GENRE on it
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
    RETURN g.name, count(m) AS mangaCount
    ORDER BY mangaCount DESC

# split Genre {name1}・{name2} into two Genre
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
    WHERE g.name =~ '.*・.*'  // Match Genres Containing Parentheses
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

    // Remove the old relationship
    DETACH DELETE g

###
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
    WHERE g.name =~ '.*･.*'  // Match Genres Containing Parentheses
        WITH g, m, g.name AS originalName,
            split(g.name, '･')[0] AS name1, // Extract {name1}
            split(g.name, '･')[1] AS name2 // Extract {name2}

    // Create/Merge the {name1} genre
    MERGE (genre1:Genre {name: trim(name1)})

    // Create/Merge the {name2} genre
    MERGE (genre2:Genre {name: trim(name2)})

    // Create/Merge the relationships
    MERGE (m)-[:HAS_GENRE]->(genre1)
    MERGE (m)-[:HAS_GENRE]->(genre2)

    // Remove the old relationship
    DETACH DELETE g

###
    MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga)
    WHERE g.name =~ 'SF.ファンタジー'  // Match Genres Containing Parentheses
        WITH g, m, g.name AS originalName,
            split(g.name, '.')[0] AS name1, // Extract {name1}
            split(g.name, '.')[1] AS name2 // Extract {name2}

    // Create/Merge the {name1} genre
    MERGE (genre1:Genre {name: trim(name1)})

    // Create/Merge the {name2} genre
    MERGE (genre2:Genre {name: trim(name2)})

    // Create/Merge the relationships
    MERGE (m)-[:HAS_GENRE]->(genre1)
    MERGE (m)-[:HAS_GENRE]->(genre2)

    // Remove the old relationship
    DETACH DELETE g

# MATCH (g:Genre)<-[:HAS_GENRE]-(m:Manga), 合併有相同 name 的 Genre
MATCH (g1:Genre)<-[:HAS_GENRE]-(m1:Manga), (g2:Genre)<-[:HAS_GENRE]-(m2:Manga)
WHERE g1.name = g2.name AND id(g1) < id(g2)
return g1.name, g2.name, m1.name, m2.name

MERGE (m2)-[:HAS_GENRE]->(g1)
DETACH DELETE g2
