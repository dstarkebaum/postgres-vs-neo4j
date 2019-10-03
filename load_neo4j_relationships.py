import py2neo


LOAD CSV WITH HEADERS FROM 'file:///neo4j.com/docs/cypher-manual/3.5/csv/artists-with-headers.csv' AS line
CREATE (:Artist { name: line.Name, year: toInteger(line.Year)})
