# Welcome to postgres-vs-neo4j!
## Prepared by David Starkebaum for Insight Data Engineering 2019 in Seattle!

The goal of this project is to compare two database engines:
**Postgres (Relational)** and **Neo4 (Graph)**
This benchmarking tool is designed to run on a small cluster of EC2 instances
on AWS using the Ubuntu 18.04 AMI,
although it could be run locally on a machine with sufficient resources.

## Initial Setup
### RAM Requirements
For the Postgres database, an m5.large (8GB RAM) may be sufficient, but an
r5.large (16GB RAM) is recommended.
For Neo4j, an r5.2xlarge is recommended for the initial import process,
which can then be downgraded to an r5.xlarge (32GB) for most of the benchmarking
The Dash front-end can run on a t2.micro with no trouble.

### Installing Dependencies
All of the necessary dependencies can be installed using either:
`dash_setup.sh`, `neo4j_setup.sh`, or `postgresql_setup.sh`
These scripts can be run using the "UserData" option while launching
the instances on AWS
Alternatively, they can be executed with bash after the instances are
up and running.
After launching each instance, clone this github repository into your home directory:
`git clone https://github.com/dstarkebaum/postgres-vs-neo4j.git`

### Disk Space Requirements
An Elastic Block Store (EBS) of at least 350GB for Postres and 200GB for Neo4j
is necessary for the database files.
However, an additional 160GB will also be necessary if you store the parsed CSV
files locally.  This necessity can be circumvented if the parsed CSV files
are stored on S3 instead.  These can be accessed by each instance using
S3fs
https://cloud.netapp.com/blog/amazon-s3-as-a-file-system
`sudo apt-get install s3fs`
**Note:** If you run out of disk space, you can increase it later.
See the section on "**Increasing EBS Volume Size**" below.

### Security Settings
For the purpose of this project, all instances were launched in a single VPC
with a private subnet. A single security group was used, which allowed
all ports to other computers within the same security group, and only allowed
SSH (port 22) from the local IP address
**Note:** You can determine your local IP address by using a free service from AWS:
`export MY_IP=$(curl checkip.amazonaws.com)`

### Downloading the data
The data used for this project is available for bulk download from
Semantic Scholar:
https://api.semanticscholar.org/corpus/download/
This project used the 2019-09-17 release, though newer version are released
on a regular basis.  This data can be downloaded using the AWS CLI as follows:
`aws s3 cp --no-sign-request --recursive s3://ai2-s2-research-public/open-corpus/2019-09-17/ destinationPath`
... where `desinationPath` can be the URI of your own S3 bucket.

## Setting up the databases

### Postgres Configuration
Before starting your database, you will need to modify the configuration files:
`sudo nano /etc/postgresql/10/main/postgresql.conf`
In particular, it is important to adjust the memory settings according to
available RAM in your instance.
**PGTune** provides a convenient tool to estimate the appropriate memory settings.
Just fill in the online form, and it will provide a list of settings to copy into
`postgresql.conf`:
https://pgtune.leopard.in.ua/
For this project, I used:
- **DB Version**: 10
- **OS Type**: Linux
- **DB Type**: Data Warehouse
- **Total Memory (RAM)**: 16GB RAM
- **Number of CPU's**: 4
- **Number of Connections**: 20
- **Data Storage**: SSD

In addition, it is necessary to specify a range of IP addresses that your
database will listen to, and the security settings for each connection.
In my case, I allowed connection from any instance in my private subnet,
which had IP addresses in the range of `10.0.0.0/26`.
I also added my local IP address.
Both used `md5` hashing for password authentication.
`sudo nano /etc/postgresql/10/main/pg_hba.conf`

### Postgres initialization
Once your settings are satisfactory, you can start the Postgres service:
`sudo service postgresql start`
The script 'reset_db.sh' in the postgres folder of this repository can be used
to create a user role and database based on your current username.
('ubuntu' in the case of the AWS instance).
From within this repository's home directory:
`sudo bash postgres/reset_db.sh`
This is necessary before you can login for the first time using `psql`
In addition, you will need to run one more script to define the database tables:
`sudo bash postgres/create_tables_int.sh`

### Initial Testing of import script
The main importing tool can be called using `load.py` in the home directory
of this repository.
Before proceeding further, it is recommended to start by testing that the import
process can process with a small subset of the data.
This module accepts several command line arguments.  To see a list of arguments, try:
`python3 load.py --help`
To run the initial test, you can use:
```
python3 load.py \
  --s3_bucket <YOUR_BUCKET_NAME> \
  --s3_path <PATH_TO_JSON_FILES_IN_BUCKET> \
  --start 0 --end 1 \
  --engine psql \
  --make_int --testing --cache
```
This will download the first two JSON files from your S3 bucket, and load them into your Progres database.
- The `--testing` flag causes only the first 100 records from each JSON file to be parsed to CSV (instead of 1M)
- The `--cache` flag will keep the compressed JSON files on the local disk, so they can be re-used.
Without it, the files will be deleted after import, and will need to be downloaded again.
- The `make_int` flag will convert the hexadecimal ID's from Semantic Scholar
into large integers (~10^49), which should be faster to sort and index by Postgres
If the test was successful, you must reset the database again to prepare for the full import:
`sudo bash postgres/reset_db.sh`
`sudo bash postgres/create_tables_int.sh`

### Installing Postgres Extensions
For this project, I used 'trigram' and 'binary-tree generalized inverted index'
for text search of authors and titles.
https://www.postgresql.org/docs/10/pgtrgm.html
https://www.postgresql.org/docs/10/btree-gin.html
These extensions must be installed manually, using `psql`:
- To see a list of available extensions:
`SELECT * FROM pg_available_extensions;`
- To install the needed extensions:
`create extension btree_gin;`
`create extension pg_trgm;`
- In addition to the indexing extension above, it can be handy to install
one additional extension to enhance the logging functionality of postgres:
https://www.postgresql.org/docs/10/pgstatstatements.html
`create extension pg_stat_statements;`
- To confirm which extensions are installed:
`\dx`

### Postgres full import
To run the full import, you can use:
```
python3 load.py \
  --s3_bucket <YOUR_BUCKET_NAME> \
  --s3_path <PATH_TO_JSON_FILES_IN_BUCKET> \
  --start 0 --end 176 \
  --engine psql \
  --make_int
```
- **Note**: Using the `--cache` flag will keep a copy of all of the compressed
JSON files locally on disk.  This can make things smoother if you run into problems,
but add an extra ~100GB to the disk space requirements.
Refer to **Increasing EBS Volume size** to allocate additional space as needed.
- This process can take several hours, so it is recommended to run in the background
so it does not abort if you lose a connection to your server.
You can either do this by wrapping the above command in a 'no-hangup' subrouting:
`nohup <my_command> &`
Or, you can push a running process into the background in 3 steps:
1. Press CTRL+z to pause the process
2. Type `bg` (+Enter) to move the process to the background
3. Type `disown` (+Enter) to disassociate the process from your terminal

You can check that the import completed by logging into `psql`, then:
`SELECT count(*) from papers;`
`SELECT count(*) from authors;`

Also, you can check the indexes:
```
SELECT tablename, indexname, indexdef
FROM pg_indexes WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### Postgres Logfiles
You can view the Postgres logs in Ubuntu here:
`less /var/log/postgresql/postgresql-10-main.log`
You can measure the the size of the database like so:
`sudo du -sh /var/lib/postgresql/10/main`


### Making a Backup of the Postgres Database
https://www.postgresql.org/docs/10/backup-file.html
- First *stop the database* (This is critical!):
`sudo service postgresql stop`
- Navigate to the directory containing your database:
`cd /var/lib/postgresql/10`
- Put the whole database into a tar file:
`sudo tar -cf main_backup.tar main`
- Restart the database when you are finished:
`sudo service postgresql start`

### Restoring a Postgres Backup
- Again make sure to *stop the database* (This is critical!)
`sudo service postgresql stop`
- Navigate to the directory containing your database:
`cd /var/lib/postgresql/10`
- For safety sake you can first just rename your current database:
`sudo mv main main_original`
- Then extract your tar file (it should automatically be named "main", and have the correct permissions as before):
`sudo tar -xvf main_backup.tar`
- Finally, restart the database:
`sudo service postgresql start`


## Setting up Neo4j:
There are two versions of the script:
- One uses `neo4j-admin import`, which is adapted for large-scale bulk csv imports,
but it only works on an empty database, and all of the csv files are available
locally on disk.
- The other method uses Cypher queries `COPY FROM CSV WITH HEADERS AS row...`
- For anything larger than 10 million records, it is strongly recommended to use
the `neo4j-admin import` method, as the `COPY FROM CSV` method gets very slow for large datasets.

### Neo4j Configuration
Before you begin the import process, it is necessary to update the configuration file.
In particular, you will need to allocate sufficient RAM to prevent Neo4j crashing.
There is a convenient command-line too to estimate appropriate settings on your machine:
`neo4j-admin memrec`
This should give you appropriate recommendations for the following settings:
`dbms.memory.heap.max_size=<...>g`
`dbms.memory.pagecache.size=<...>g`
See https://neo4j.com/docs/operations-manual/current/performance/memory-configuration/
for further advice on memory allocation (depends on how much RAM you actually have available)
Before you modify the settings, make sure Neo4j is not running:
`sudo neo4j stop`

You can find the configuration file here:
`sudo nano /etc/neo4j/neo4j.conf`
There are a number of parameters that can be modified.
You can find (somewhat) detailed information about each parameter here:
https://neo4j.com/docs/operations-manual/current/reference/configuration-settings/

Parameters to look for:
`dbms.security.auth_enabled=false`
- Disables authentication for user access...
Not ideal from a security standpoint, but this may help you if you having trouble logging in.

`#dbms.directories.import=/var/lib/neo4j/import`
- Commenting this out allows you to load csv files from anywhere, not just from the neo4j/import directory.
`dbms.security.allow_csv_import_from_file_urls=true`
- This allows you to read CSV files from remote URL's (like S3), if you prefer. However, using s3fs is recommended instead.

`dbms.connectors.default_listen_address=0.0.0.0`
- You can choose specific IP addresses to listen to. The above setting listens
to incoming connections from any IP address.
For greater security, you can list specific IP addresses as needed.

`dbms.db.timezone=SYSTEM`
- **NOTE**: This setting is not included in the default neo4j.conf file
But it is very helpful to get useful logs that actually record the local time
according to your system clock instead of UTC

### Setting up a password:
If you haven't started your server yet, you can pre-configure neo4j
with a default password using neo4j-admin:
`sudo neo4j-admin set-initial-password <initial_password>`

If you have already started your database you can login to it
with cypher-shell, (default user:`neo4j`, default password: `neo4j`)
`CALL dbms.security.changePassword("<new_password>")`

### Testing Neo4j import:
To run the initial test, you can use:
```
python3 load.py \
  --s3_bucket <YOUR_BUCKET_NAME> \
  --s3_path <PATH_TO_JSON_FILES_IN_BUCKET> \
  --start 0 --end 1 \
  --engine neo4j-admin \
  --testing --cache
```

If the test was successful, you can proceed to the full import.
You will need to delete (or backup) the current database before repopulating:
`sudo rm -r /var/lib/neo4j/data/databases/graph.db`

### Neo4j Full Import
```
python3 load.py \
  --s3_bucket <YOUR_BUCKET_NAME> \
  --s3_path <PATH_TO_JSON_FILES_IN_BUCKET> \
  --start 0 --end 176 \
  --engine neo4j-import \
  --cache
```
- As with with Postgres full import, this process can take several hours,
so it is recommended to run in the background so it does not abort if you lose a connection to your server.
You can either do this by wrapping the above command in a 'no-hangup' subrouting:
`nohup <my_command> &`
Or, you can push a running process into the background in 3 steps:
1. Press CTRL+z to pause the process
2. Type `bg` (+Enter) to move the process to the background
3. Type `disown` (+Enter) to disassociate the process from your terminal

Once the import is complete, you can restart Neo4j as follows:
`sudo neo4j start`

You can then test that the database is populated with `cypher-shell`:
`MATCH (p:Paper) RETURN count(p)`
`MATCH (a:Author) RETURN count(a)`

Check that indexes are built:
`CALL db.indexes();`
Make the indexes if needed:
`CREATE CONSTRAINT ON (p:Paper) ASSERT p.id IS UNIQUE;`
`CREATE CONSTRAINT ON (a:Author) ASSERT a.id IS UNIQUE;`
Note: the process above can take some time if it was not completed already,
so it may be better to execute it from the bash command line so you can disown the process:
`cypher-shell --non-interactive 'CREATE CONSTRAINT ON (a:Author) ASSERT a.id IS UNIQUE;'`
Then `CTRL+z`, `bg`, `disown` to move to background.

### Backing up Neo4j:
Make sure Neo4j is not running:
`sudo neo4j stop`
`tar -cf neo4j_backup.tar /var/lib/neo4j/data/databases/graph.db`
"tar -c" = create archive
"tar -f" = choose filename for the archive (next argument)
Then you can restart Neo4j:
`sudo neo4j start`

## Setting up Dash
1. Clone this repository on your front-end server:
`git clone https://github.com/dstarkebaum/postgres-vs-neo4j.git`
2. Run the dash_setup.sh script (if you didn't already do that through "UserData"):
`bash aws/dash_setup.sh`
3. See this page for information on registering your own domain name, and linking it to AWS:
http://techgenix.com/namecheap-aws-ec2-linux/
4. See this page for information on setting up NGINX and gunicorn to handle multiple users of your Dash app:
https://github.com/OXPHOS/GeneMiner/wiki/Setup-front-end-with-plotly-dash,-flask,-gunicorn-and-nginx
5. Once all of that is complete, you should be able to start the dash app with gunicorn:
`gunicorn src/dash_app/index:server`
As before, you probably want to run this in the background:
`CTRL+z`, `bg`, `disown`

### Clearing the Cache Prior to Benchmarking
If you want to simulate a cold start, you can SSH into each each database
and clear the Linux OS Cache before running the tests:
`sudo service postgresql stop` / `sudo neo4j stop`
`sync && echo 3 | sudo tee /proc/sys/vm/drop_caches`
`sudo service postgresql start` / `sudo neo4j start`

### Running the tests
You can initiate the tests from you dash server, since you will need to have access
to the test results locally to populate the graphs in the front-end.
This doesn't require much system resources, since all of the processing
will occur on the database servers.
However, in order to login to the databases, you will need to add a file called
`credentials.py` to the `src/db_utils` directory.
This file should contain two dictionaries, which hold the login information
for each of your database instances.  See the following for a template:
```
#!/usr/bin/env python3
neo4j = {
        'large': {
            'host': '<IP_ADDRESS_OF_LARGE_NEO4J_DATABASE>',
            'user': 'neo4j',
            'pass': '<NEO4J_PASSWORD>',
            },
        }
postgres = {
        'large': {
            'host': '<IP_ADDRESS_OF_LARGE_POSTGRES_DATABASE>',
            'database': 'ubuntu',
            'user': 'ubuntu',
            'pass': '<POSTGRES_PASSWORD>',
            },
        }
```
With that file setup, you can run the tests from this repository's home directory using:
`python3 run_tests.py --repeat 3 --database postgres --size large`
`python3 run_tests.py --repeat 3 --database neo4j --size large`
As before, you will likely want to run in the background: `CTRL+z`, `bg`, `disown`
See the run_tests.py help for an explanation of parameters:
`python3 run_tests.py --help`
Note that `--size` must refer to one of the entries in `credentials.py`


## Troubleshooting:
Sometimes you try to start neo4j and it will not work:
`sudo neo4j start`

Start by checking:
`neo4j status`

If neo4j is not running, check the log file:
`sudo nano /var/log/neo4j/neo4j.log`

You may see an error like this:
```
ERROR Failed to start Neo4j: Starting Neo4j failed:
Component 'org.neo4j.server.database.LifecycleManagingDatabase@xxxxxx'
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

### Increasing EBS Volume size
https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modify-volume.html

You can increase the volumne through the EC2 Console,
but then you have to tell your linux OS that things have changed.
After increaseing the volume size, check the current partitions:
`lsblk`

You should see something like this:
```
nvme0n1
└─nvme0n1p1
```

You can also check the filesystem with:
`df -Th`

You can extend the partition (even while it is mounted) with:
`sudo growpart /dev/nvme0n1 1`
Note: nvme0n1 is the drive name, and nvme0n1p1 is partition 1 on that drive

Then you extend the file system (usually Ext4) with:
`sudo resize2fs /dev/nvme0n1p1`

Done!

[Data Atsume website](http://www.data-atsu.me)
