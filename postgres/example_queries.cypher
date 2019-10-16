select papers.title from papers, (
    select paper_id from has_author
    where has_author.author_id = 5160022
) as z
where papers.id = z.paper_id;



SELECT * FROM authors WHERE name ILIKE '%ozek%';


SELECT 1
WHERE to_tsvector('simple', 'Ozek') @@ to_tsquery('english', 'yor');
