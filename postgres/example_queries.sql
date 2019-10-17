
# Find an author
SELECT name, id FROM authors WHERE name ILIKE '%ozek%';

# possible alternative?
SELECT 1
WHERE to_tsvector('simple', 'Ozek') @@ to_tsquery('english', 'yor');


# Find papers by an author
SELECT papers.title, papers.id FROM papers, (
    SELECT paper_id FROM has_author
    WHERE has_author.author_id = 5160022
) AS z
WHERE papers.id = z.paper_id;




#========================== Cypher ================================


# Find an author
MATCH (a:Author) WHERE a.name =~ '.*az.*' RETURN a.name,a.id;

# Find papers by an author
MATCH (p:Paper)-[:HAS_AUTHOR]->(a:Author)
WHERE a.id = "2475639" RETURN p.title,p.id;

# Find papers that cite a paper
MATCH (p1:Paper)-[:CITES]->(p2:Paper)
WHERE p2.id = "af05f3bf27641bafd0e49f092a21bd5bc6b1843c" RETURN p1.title,p1.id;


# Go deep!! count all papers that cite papers that cite papers.... by an author
MATCH (pn:Paper)-[:CITES *1..]->(p:Paper)
RETURN count(pn);
