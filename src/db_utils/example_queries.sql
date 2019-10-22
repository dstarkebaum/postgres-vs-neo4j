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



# Find an author with a name similar to 'x'
SELECT name, id FROM authors WHERE name ILIKE '%Altman%';

# Find a paper with a title similar to 'x'
SELECT title, id FROM papers
WHERE title ilike '%Preferred reporting items for systematic reviews%';

#id = 1436906225246299354080717389136457570294446097622

# possible alternative?
SELECT 1
WHERE to_tsvector('simple', 'Ozek') @@ to_tsquery('english', 'yor');


# Most Cited Author in small database:
# name: Douglas G. Altman, id: 144117798


# Count all papers by an author with id "a"
SELECT count(paper_id)
FROM has_author
WHERE has_author.author_id = 144117798;

# Find papers by an author with id "a"
SELECT papers.title, papers.id FROM papers, (
    SELECT paper_id FROM has_author
    WHERE has_author.author_id = 5160022
) AS z
WHERE papers.id = z.paper_id;

# Find the titles and ids of all papers by an author with id 'x' using join
SELECT papers.title, papers.id
  FROM papers
  JOIN has_author ON
    has_author.paper_id = papers.id
  WHERE has_author.author_id = 144117798;



# Count all papers that cite a paper with id 'b' using join
SELECT count(incit_id)
FROM is_cited_by
WHERE is_cited_by.id = 1436906225246299354080717389136457570294446097622;

# Find all papers that cite a paper with id "x"
SELECT papers.title, papers.id FROM papers, (
    select incit_id from is_cited_by
    where is_cited_by.id = 1436906225246299354080717389136457570294446097622
) as citations
where papers.id = citations.incit_id;

# Find the titles and ids of papers that cite a paper with id 'x' using join
SELECT papers.title, papers.id
  FROM papers
  JOIN is_cited_by ON
    papers.id = is_cited_by.incit_id
  WHERE is_cited_by.id = 1436906225246299354080717389136457570294446097622;


# what are the top ten most cited papers, and how many citations to they have?
SELECT papers.title, papers.id, count(is_cited_by.incit_id)
  FROM papers
  JOIN is_cited_by ON
    papers.id = is_cited_by.id
  GROUP BY papers.id
  ORDER BY count(is_cited_by.incit_id) DESC LIMIT 10;

# what are the top ten authors that have published the most papers
SELECT authors.name, authors.id, count(*)
    FROM authors
    JOIN has_author as papersByAuthor ON
        authors.id = papersByAuthor.author_id
GROUP BY authors.id
ORDER BY count(*) DESC LIMIT 10;

# what are the top ten authors that have published the most papers
SELECT authors.name, authors.id, count(has_author.paper_id)
    FROM authors
    JOIN has_author ON
        authors.id = has_author.author_id
GROUP BY authors.id
ORDER BY count(has_author.paper_id) DESC LIMIT 10;


# what are the top ten most cited papers?
SELECT papers.title, papers.id, count(*)
    FROM papers
    JOIN is_cited_by AS citingPapers ON
        authorsPapers.id = citingPapers.incit_id
GROUP BY papers.id
ORDER BY count(*) DESC LIMIT 10;


# what are the top ten most cited authors, and how many citations to they have?
SELECT authors.name, authors.id, count(*)
    FROM authors
    JOIN has_author as papersByAuthor ON
        authors.id = papersByAuthor.author_id
    JOIN is_cited_by AS citingPapers ON
        papersByAuthor.paper_id = citingPapers.id
GROUP BY authors.id
ORDER BY count(*) DESC LIMIT 10;


SELECT authors.name, authors.id, count(is_cited_by.incit_id)
    FROM authors
    JOIN has_author ON
        authors.id = has_author.author_id
    JOIN is_cited_by ON
        has_author.paper_id = is_cited_by.id
GROUP BY authors.id
ORDER BY count(is_cited_by.incit_id) DESC LIMIT 10;


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

# first join papers with is_cited_by
# get list of every title with the ids of every paper that cites it
# then join each id with the ids of all papers that are citing that paper
# recursively until you run out of papers.
# Finally, group by
WITH RECURSIVE citation_tree AS (
  SELECT papers.title AS title, is_cited_by.incit_id AS citingID
  FROM papers
  JOIN is_cited_by ON
    papers.id = is_cited_by.id
  UNION ALL
  select prev.title, prev.citingID FROM (
    is_cited_by prev
    JOIN citation_tree ON
      citation_tree.citingID = prev.id
  ) AS prev
) SELECT title, count(*) FROM citation_tree
 GROUP BY title ORDER BY count(*) DESC LIMIT 10;


#
 WITH RECURSIVE citation_tree AS (
   SELECT papers.title AS title, is_cited_by.incit_id AS citingID
   FROM papers
   JOIN is_cited_by ON
     papers.id = is_cited_by.id
   UNION ALL
   select prev.title, prev.citingID FROM (
     is_cited_by prev
     JOIN citation_tree ON
       citation_tree.citingID = prev.id
   ) AS prev
 ) SELECT title, count(*) FROM citation_tree
  GROUP BY title ORDER BY count(*) DESC LIMIT 10;


WITH RECURSIVE subordinates AS (
   SELECT
      employee_id,
      manager_id,
      full_name
   FROM
      employees
   WHERE
      employee_id = 2
   UNION
      SELECT
         e.employee_id,
         e.manager_id,
         e.full_name
      FROM
         employees e
      INNER JOIN subordinates s ON s.employee_id = e.manager_id
) SELECT
   *
FROM
   subordinates;


select * from papers p
where (
  select count(*) from paper q
  where p.id = q.id
) > 1;

CREATE TABLE unique_authors AS
SELECT id, min(name) FROM authors
GROUP BY id;

#========================== Cypher ================================


# Find an author
MATCH (a:Author) WHERE a.name =~ '.*az.*' RETURN a.name,a.id;

# Find papers by an author
MATCH (p:Paper)-[:HAS_AUTHOR]->(a:Author)
WHERE a.id = "2475639" RETURN p.title,p.id;

# Find papers that cite a paper
MATCH (p1:Paper)-[:CITES]->(p2:Paper)
WHERE p2.id = "af05f3bf27641bafd0e49f092a21bd5bc6b1843c" RETURN p1.title,p1.id;


# Count all papers by an author with id 'x'
MATCH (p:Paper)-[:HAS_AUTHOR]->(a:Author)
WHERE a.id = "144117798"
RETURN count(p);


# Count all papers that cite a paper with id 'x'
MATCH (citing:Paper)-[:CITES]->(cited:Paper)
WHERE cited.id = "fbb11a841893d4b68fa2173226285ded4f7b04d6"
RETURN count(citing);

# Find the top ten papers with most citations
MATCH (:Paper)-[r:CITES]->(p:Paper)
RETURN p, COUNT(r)
ORDER BY COUNT(r) DESC
LIMIT 10;
| (:Paper {id: "fbb11a841893d4b68fa2173226285ded4f7b04d6", title: "Preferred reporting items for systematic reviews and meta-analyses: the PRISMA statement.", year: 2009, doi: "10.1136/bmj.b2535"})                                            | 1673     |
| (:Paper {id: "d2cd75e6defc26a4d343f5f3c4c214da8a2caf3b", title: "Cutoff criteria for fit indexes in covariance structure analysis: Conventional criteria versus new alternatives", year: 1999, doi: "10.1080/10705519909540118"})              | 1204     |
| (:Paper {id: "b7919bcfa38aa97514187501a23c983e8eb5482b", title: "Particle swarm optimization", year: 1995, doi: "10.1109/ICNN.1995.488968"})                                                                                                   | 1105     |
| (:Paper {id: "57e7a7323f58a35f5e2cc33bf17d4ac9cdcafdd4", title: "Systematic and integrative analysis of large gene lists using DAVID bioinformatics resources", year: 2008, doi: "10.1038/nprot.2008.211"})                                    | 823      |
| (:Paper {id: "458e20bfbc71a80902897ab684e324d3e5c3b2b0", title: "Random sample consensus: a paradigm for model fitting with applications to image analysis and automated cartography", year: 1987, doi: "10.1016/b978-0-08-051581-6.50070-2"}) | 764      |
| (:Paper {id: "fddb43681b965d0e566f8beb2ce3e057e4072909", title: "Multiple regression: Testing and interpreting interactions", year: 1993, doi: "10.1016/0886-1633(93)90008-d"})                                                                | 682      |
| (:Paper {id: "e985ac2e151903000cac310ffbc5b2cb4fbb9dd5", title: "Coefficient alpha and the internal structure of tests", year: 1951, doi: "10.1007/bf02310555"})                                                                               | 680      |
| (:Paper {id: "dc6ea0e30e46163b706f2f8bdc9c67ca87f83d63", title: "Rapid object detection using a boosted cascade of simple features", year: 2001, doi: "10.1109/CVPR.2001.990517"})                                                             | 665      |
| (:Paper {id: "465ecac8eddd2c362f0e10de2583a62a1a7c371a", title: "MRBAYES: Bayesian inference of phylogenetic trees", year: 2001, doi: "10.1093/bioinformatics/17.8.754"})                                                                      | 634      |
| (:Paper {id: "1805e19e9fa6a4c140c531bc0dca8016ee75257b", title: "A Tutorial on Support Vector Machines for Pattern Recognition", year: 1998, doi: "10.1023/A:1009715923555"})                                                                  | 555      |
11788 ms




# Find the top ten papers with most citations of citations of citations...
MATCH (:Paper)-[r:CITES *1..]->(p:Paper)
RETURN p, COUNT(r)
ORDER BY COUNT(r) DESC
LIMIT 10;

| (:Paper {id: "bc4c1ad3a9ca9e3528059f4e1ebea1ef312ea168", title: "Virus resistance and gene silencing in plants can be induced by simultaneous expression of sense and antisense RNA.", year: 1998, doi: "10.1073/pnas.95.23.13959"})                                              | 21637    |
| (:Paper {id: "930249e3410a49483bd417941decca4717a34a0b", title: "Arabidopsis thaliana DNA methylation mutants.", year: 1993, doi: "10.1126/science.8316832"})                                                                                                                     | 20329    |
| (:Paper {id: "0f80b26ed4b4391e38c23d90fd09ad529fa524bc", title: "Silencing of developmental genes in Hydra.", year: 1999, doi: "10.1006/dbio.1999.9407"})                                                                                                                         | 18943    |
| (:Paper {id: "180799ac36c7f0ad2e4803fc466974baffdadfba", title: "Cortical projection to hand-arm motor area from post-arcuate area in macaque monkeys: A histological study of retrograde transport of horseradish peroxidase", year: 1979, doi: "10.1016/0304-3940(79)90001-6"}) | 18408    |
| (:Paper {id: "8573bbb55112c1f06c43211daedacc1578e69a92", title: "Cluster analysis and display of genome-wide expression patterns", year: 1999})                                                                                                                                   | 18075    |
| (:Paper {id: "2628f715db49272aaf16689355b7f473be57608d", title: "Extending Particle Swarms with Self-Organized Criticality", year: 2002})                                                                                                                                         | 16621    |
| (:Paper {id: "b7919bcfa38aa97514187501a23c983e8eb5482b", title: "Particle swarm optimization", year: 1995, doi: "10.1109/ICNN.1995.488968"})                                                                                                                                      | 16592    |
| (:Paper {id: "94b3ebb0555dc0c4d802986571457067300b2ba7", title: "Deficits in attention and movement following the removal of postarcuate (area 6) and prearcuate (area 8) cortex in macaque monkeys.", year: 1983, doi: "10.1093/brain/106.3.655"})                               | 14019    |
| (:Paper {id: "7612ecf4e0b646e199bf65da1edf848ecf87dd90", title: "Systemic spread of sequence-specific transgene RNA degradation in plants is initiated by localized introduction of ectopic promoterless DNA.", year: 1998, doi: "10.1016/s0092-8674(00)81749-3"})                | 13955    |
| (:Paper {id: "19290ec16407327287ef9328611f2f5c94e764f7", title: "Neuronal activity in the cortical supplementary motor area related with distal and proximal forelimb movements", year: 1979, doi: "10.1016/0304-3940(79)96062-2"})                                               | 13926    |
57417 ms

# Find the top ten authors with the most papers
MATCH (:Paper)-[r:HAS_AUTHOR]->(a:Author)
RETURN a,COUNT(r)
ORDER BY COUNT(r) DESC
LIMIT 10;


Find the top ten authors whose papers have the most direct citations
MATCH (:Paper)-[r:CITES]-(:Paper)-[HAS_AUTHOR]-(a:Author)
RETURN a, COUNT(r)
ORDER BY COUNT(r) DESC
LIMIT 10;


# Go deep!! count all papers that cite papers that cite papers.... by an author
MATCH (:Paper)-[r:CITES *1..]->(:Paper)-[:HAS_AUTHOR]->(a:Author)
RETURN a, COUNT(r)
ORDER BY COUNT(r) DESC
LIMIT 10;

| (:Author {name: "Giacomo Rizzolatti", id: "2460061"}) | 30343    |
| (:Author {name: "Jun Tanji", id: "2436887"})          | 29052    |
| (:Author {name: "Corey S. Goodman", id: "2419211"})   | 28918    |
| (:Author {name: "Kiyoshi Kurata", id: "48726588"})    | 27851    |
| (:Author {name: "Raymond J Deshaies", id: "5684169"}) | 26449    |
| (:Author {name: "Gordon H. Guyatt", id: "1954106"})   | 25305    |
| (:Author {name: "Solomon H Snyder", id: "2153925"})   | 25156    |
| (:Author {name: "Randy Schekman", id: "6205592"})     | 23765    |
| (:Author {name: "Thiemo Krink", id: "2773576"})       | 23338    |
| (:Author {name: "David O. Morgan", id: "35719273"})   | 22794    |
139630 ms

MATCH (:Paper)-[r:CITES *1..]->(p:Paper)-[:HAS_AUTHOR]->(a:Author)
WHERE a.name IS "Giacomo Rizzolatti"
RETURN p.title, COUNT(r)
ORDER BY COUNT(r) DESC
LIMIT 10;


# How to match:
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

# How another way to match (equivalent):
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
