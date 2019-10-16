
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
