
# Find an author with a name similar to "x"
SELECT name, id FROM authors WHERE name ILIKE '%ozek%';

# possible alternative?
SELECT 1
WHERE to_tsvector('simple', 'Ozek') @@ to_tsquery('english', 'yor');


# Find papers by an author with id "x"
SELECT papers.title, papers.id FROM papers, (
    SELECT paper_id FROM has_author
    WHERE has_author.author_id = 5160022
) AS z
WHERE papers.id = z.paper_id;


# Find all papers that cite a paper with id "x"
SELECT papers.title, papers.id FROM papers, (
    select incit_id from is_cited_by
    where is_cited_by.id = 1096691340917389300651417525314313012981369689808
) as citations
where papers.id = citations.incit_id;


# How many papers are there in the dataset?
select count(*) from papers
49000200

# How many total number of citations in the dataset?
select count(*) from cites;
157154026

# How many citations reference another paper that is actually in the loaded dataset
select count(*) from papers inner join cites on papers.id = cites.outcit_id;
42849667

# How many total references to papers in the dataset?
select count(*) from is_cited_by;
163516318

# How many of those total references come from another paper in the loaded dataset
select count(*) from papers inner join is_cited_by on papers.id = is_cited_by.incit_id;
42849667

# what are the top ten most cited papers, and how many citations to they have?
select papers.title, count(*), papers.id from
papers inner join cites on papers.id = cites.id
group by papers.id order by count(*) desc limit 10;


# Example recursive query to build a list of numbers from 1 to 5
# "with" generates a "common table expression (CTE)"
# which is defined by an initialization step (select 1 as n)
# followed by a recursive step after the union [all]
# the recurstive step refers to the table it is building
# and must include a terminating predicate (where n <  5)
# finally, you select the columns that you want from the
# table that you built in the CTE.
with recursive print_numbers as(
  select 1 as n
  union all
  select n + 1 from print_numbers where n < 5
) select n from print_numbers;

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




# How NOT to match:
match (p:Paper {id:"892cbd4fe56bd56cbdb69810631648e6f8d1e407"}),
  (q:Paper {id:"24c6fc7aa8968d0a6a7a7b8d3bb002c53a29df13"})
return p,q;
1 row available after 14 ms, consumed after another 1 ms

explain match (p:Paper {id:"892cbd4fe56bd56cbdb69810631648e6f8d1e407"}),
  (q:Paper {id:"24c6fc7aa8968d0a6a7a7b8d3bb002c53a29df13"}) return p,q;
+------------------------+----------------+-------------+------------+------------+
| Operator               | Estimated Rows | Identifiers | Ordered by | Other      |
+------------------------+----------------+-------------+------------+------------+
| +ProduceResults        |              1 | p, q        | p.id ASC   |            |
| |                      +----------------+-------------+------------+------------+
| +CartesianProduct      |              1 | p, q        | p.id ASC   |            |
| |\                     +----------------+-------------+------------+------------+
| | +NodeUniqueIndexSeek |              1 | q           | q.id ASC   | :Paper(id) |
| |                      +----------------+-------------+------------+------------+
| +NodeUniqueIndexSeek   |              1 | p           | p.id ASC   | :Paper(id) |
+------------------------+----------------+-------------+------------+------------+

# How to match correctly:
match (p:Paper {id:"892cbd4fe56bd56cbdb69810631648e6f8d1e407"})
match (q:Paper {id:"24c6fc7aa8968d0a6a7a7b8d3bb002c53a29df13"})
return p,q;
+------------------------+----------------+-------------+------------+------------+
| Operator               | Estimated Rows | Identifiers | Ordered by | Other      |
+------------------------+----------------+-------------+------------+------------+
| +ProduceResults        |              1 | p, q        | p.id ASC   |            |
| |                      +----------------+-------------+------------+------------+
| +CartesianProduct      |              1 | p, q        | p.id ASC   |            |
| |\                     +----------------+-------------+------------+------------+
| | +NodeUniqueIndexSeek |              1 | q           | q.id ASC   | :Paper(id) |
| |                      +----------------+-------------+------------+------------+
| +NodeUniqueIndexSeek   |              1 | p           | p.id ASC   | :Paper(id) |
+------------------------+----------------+-------------+------------+------------+



EXPLAIN LOAD CSV WITH HEADERS
FROM "file:///home/ubuntu/postgres-vs-neo4j/data/csv/s2-corpus-090-cites.csv" AS row
FIELDTERMINATOR "|"
MATCH (p1:Paper {id:row.id})
MATCH (p2:Paper {id:row.outcit_id})
MERGE (p1)-[:CITES]->(p2);

+-----------------------------------+----------------+------------------------+------------------------------+
| Operator                          | Estimated Rows | Identifiers            | Other                        |
+-----------------------------------+----------------+------------------------+------------------------------+
| +ProduceResults                   |              1 | anon[204], p1, p2, row |                              |
| |                                 +----------------+------------------------+------------------------------+
| +EmptyResult                      |              1 | anon[204], p1, p2, row |                              |
| |                                 +----------------+------------------------+------------------------------+
| +Apply                            |              1 | anon[204], p1, p2, row |                              |
| |\                                +----------------+------------------------+------------------------------+
| | +AntiConditionalApply           |              1 | anon[204], p1, p2      |                              |
| | |\                              +----------------+------------------------+------------------------------+
| | | +MergeCreateRelationship      |              1 | anon[204], p1, p2      |                              |
| | | |                             +----------------+------------------------+------------------------------+
| | | +Argument                     |              1 | p1, p2                 |                              |
| | |                               +----------------+------------------------+------------------------------+
| | +AntiConditionalApply           |              1 | anon[204], p1, p2      |                              |
| | |\                              +----------------+------------------------+------------------------------+
| | | +Optional                     |              1 | anon[204], p1, p2      |                              |
| | | |                             +----------------+------------------------+------------------------------+
| | | +ActiveRead                   |              0 | anon[204], p1, p2      |                              |
| | | |                             +----------------+------------------------+------------------------------+
| | | +Expand(Into)                 |              0 | anon[204], p1, p2      | (p1)-[anon[204]:CITES]->(p2) |
| | | |                             +----------------+------------------------+------------------------------+
| | | +LockNodes                    |              1 | p1, p2                 | p1, p2                       |
| | | |                             +----------------+------------------------+------------------------------+
| | | +Argument                     |              1 | p1, p2                 |                              |
| | |                               +----------------+------------------------+------------------------------+
| | +Optional                       |              1 | anon[204], p1, p2      |                              |
| | |                               +----------------+------------------------+------------------------------+
| | +ActiveRead                     |              0 | anon[204], p1, p2      |                              |
| | |                               +----------------+------------------------+------------------------------+
| | +Expand(Into)                   |              0 | anon[204], p1, p2      | (p1)-[anon[204]:CITES]->(p2) |
| | |                               +----------------+------------------------+------------------------------+
| | +Argument                       |              1 | p1, p2                 |                              |
| |                                 +----------------+------------------------+------------------------------+
| +Apply                            |              1 | p1, p2, row            |                              |
| |\                                +----------------+------------------------+------------------------------+
| | +ValueHashJoin                  |              1 | p1, p2, row            | p2.id = row.outcit_id        |
| | |\                              +----------------+------------------------+------------------------------+
| | | +NodeUniqueIndexSeek(Locking) |              1 | p1, row                | :Paper(id)                   |
| | |                               +----------------+------------------------+------------------------------+
| | +NodeUniqueIndexSeek(Locking)   |              1 | p2, row                | :Paper(id)                   |
| |                                 +----------------+------------------------+------------------------------+
| +LoadCSV                          |              1 | row                    |                              |
+-----------------------------------+----------------+------------------------+------------------------------+
