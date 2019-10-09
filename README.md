# Welcome to postgres-vs-neo4j!

## Prepared by David Starkebaum for
## Insight Data Engineering 2019 in Seattle!

The goal of this project is to compare two database engines:
**Postgres (Relational)** and **Neo4 (Graph)**


`setup/populate_database.py` contains the main code,
which will download a specified subset of json files from S3,
send them to `setup/json_to_csv.py` to parse into csv files,
then send those files to either `postgres_util.py`
or `neo4j_utils.py` to be loaded into the database.

From there it may be necessary to call additional functions
to remove duplicates and add indexes as needed.


## For neo4j import:
- Due to file-write permission, You may need to run the script
with `sudo` (or with `sudo -u neo4j`).
- It will not work if your database is already populated and/or running
Start by checking:
`neo4j status`
If it is running:
`sudo neo4j stop`
Then delete (or backup) the current database:
`sudo rm -r /var/lib/neo4j/data/databases/graph.db`
You may also need to modify the neo4j configuration file:
`sudo nano /etc/neo4j/neo4j.conf`
Check the log files for problems:
`sudo nano /var/log/neo4j/neo4j.log`

Ex: import just one set of compressed csv files in data/csv/s2-corpus-000-[table].csv.gz:
`sudo python3 setup/populated_database.py --compress --start 0 --end 0`

If you have any troubles with importing, check the logfiles:
`nano /var/log/neo4j/neo4j.log`
Also, check the logfiles for this script at:
`nano logs/import_csv.stderr`
`nano logs/import_csv.stdout`
`nano logs/import_csv.timer`

Once everything is complete, you may need to start neo4j using systemctl:
`sudo systemctl start neo4j`

## For postgres import
- More to come soon


[Data Atsume website](http://www.data-atsu.me)



[x] test `inline code` as well as ~~mistakes~~

[ ] Add actual readme text based on project idea

```
multi-line
blocks
of
code
```

> quotations

- unordered
- lists

1. ordered
   1. and nested
      - within nested
2. lists

emoji's :+1:
