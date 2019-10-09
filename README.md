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
- Due to file-write permission, you will need to run the script
with `sudo` (or with `sudo -u neo4j`).

There are two versions of the script:
- One uses `neo4j-admin import`, which is adapted for large-scale bulk csv imports,
but it only works on an empty database, and all of the csv files are available
locally on disk.
- The other method uses Cypher queries `COPY FROM CSV WITH HEADERS AS row...`

For `neo4j-admin import`

You will need to delete (or backup) the current database before repopulating:
`sudo rm -r /var/lib/neo4j/data/databases/graph.db`


Troubleshooting:
Sometimes you try to start neo4j and it will not work:
`sudo neo4j start`

Start by checking:
`neo4j status`

If neo4j is not running, check the log file:
`sudo nano /var/log/neo4j/neo4j.log`

You may see an error like this:
```
ERROR Failed to start Neo4j: Starting Neo4j failed: Component 'org.neo4j.server.database.LifecycleManagingDatabase@xxxxxx'
was was successfully initialized, but failed to start.
Please see the attached cause exception
"Store and its lock file has been locked by another process:
/var/lib/neo4j/data/databases/store_lock.
Please ensure no other process is using this database,
and that the directory is writable (required even for read-only access)".
```
In this case, a store lock has been used to prevent racing conditions
(when multiple processes try to read/write from the same location).
You can double-check if another process is running neo4j by using htop:
`sudo apt-get install htop` (if its not already installed):
`sudo htop` --> F5 (to show tree-view) --> F4 (filter) --> type 'neo4j'
You can then kill the top neo4j process with F9:
`usr/bin/java -cp /var/lib/neo4j/plugins: ...`

You can also do this by command line:
(search for neo4j with pgrep, and kill whatever process is there)
`sudo kill $(pgrep -f neo4j)`

Then remove the store_lock
`sudo rm /var/lib/neo4j/data/databases/store_lock`

You may also need to modify the neo4j configuration file:
`sudo nano /etc/neo4j/neo4j.conf`

You can find (somewhat) detailed information about each parameter here:
https://neo4j.com/docs/operations-manual/current/reference/configuration-settings/

Paramaters to look for:
`dbms.security.auth_enabled=false`
- Disables authentication for user access...
Not ideal from a security standpoint, but this may help you just get it working

`#dbms.directories.import=/var/lib/neo4j/import`
- Commenting this out allows you to load csv files from anywhere,
not just from the neo4j/import directory.
`dbms.security.allow_csv_import_from_file_urls=true`
- This allows you to read CSV files from remote URL's (like S3), if you prefer

`dbms.memory.heap.max_size=512m`
`dbms.memory.pagecache.size=10g`
- See https://neo4j.com/docs/operations-manual/current/performance/memory-configuration/
for advice on memory allocation (depends on how much RAM you actually have available)

`dbms.connectors.default_listen_address=0.0.0.0`
- You can choose specific IP addresses to listen to, rather than all internet
But you will need to put something here to enable any access over a network

`dbms.db.timezone=SYSTEM`
- **NOTE**: This setting is not included in the default neo4j.conf file
But it is very helpful to get useful logs that actually record the local time
according to your system clock instead of UTC

Ex: import just one set of compressed csv files in data/csv/s2-corpus-000-[table].csv.gz:
`sudo python3 setup/populated_database.py --compress --start 0 --end 0`

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
