

# create tables with all primary keys, and foreign value constraints
psql -c "CREATE TABLE papers (id NUMERIC PRIMARY KEY, title TEXT, year SMALLINT, doi TEXT);"
psql -c "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);"
psql -c "CREATE TABLE is_cited_by (id NUMERIC REFERENCES papers(id), incit_id NUMERIC REFERENCES papers(id), PRIMARY KEY (id, incit_id));"
psql -c "CREATE TABLE cites (id NUMERIC REFERENCES papers(id), outcit_id NUMERIC REFERENCES papers(id), PRIMARY KEY (id,outcit_id));"
psql -c "CREATE TABLE paper_authors (paper_id NUMERIC REFERENCES papers(id), author_id INTEGER REFERENCES authors(id), PRIMARY KEY (author_id,paper_id));"
