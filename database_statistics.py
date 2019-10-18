
import textwrap as txt



tooltips = {

    dbms.memory.heap.initial_size=txt.dedent('''\
        Java Heap Size: by default the Java heap size is dynamically
        calculated based on available system resources.
        Set specific initial and maximum heap size for more reliable performance.
        ''')

    dbms.memory.heap.max_size=txt.dedent('''\
        Java Heap Size: by default the Java heap size is dynamically
        calculated based on available system resources.
        Set specific initial and maximum heap size for more reliable performance.
        ''')

    dbms.memory.pagecache.size=txt.dedent('''\
        The amount of memory to use for mapping the store files.
        If Neo4j is running on a dedicated server, then it is generally recommended
        to leave about 2-4 gigabytes for the operating system, give the JVM enough
        heap to hold all your transaction state and query context, and then leave the
        rest for the page cache.
        The default page cache memory assumes the machine is dedicated to running
        Neo4j, and is heuristically set to 50% of RAM minus the max Java heap size.
        ''')

    dbms.jvm.additional=txt.dedent('''\
        G1GC generally strikes a good balance between throughput and tail
        latency, without too much tuning.
        ''')

    dbms.jvm.additional=txt.dedent('''\
        Make sure that `initmemory` is not only allocated, but committed to
        the process, before starting the database. This reduces memory
        fragmentation, increasing the effectiveness of transparent huge
        pages. It also reduces the possibility of seeing performance drop
        due to heap-growing GC events, where a decrease in available page
        cache leads to an increase in mean IO response time.
        Try reducing the heap memory, if this flag degrades performance.
        ''')
    }


ec2 = {
    'm5.large':dict(
        ram='8 GB',
        vCPU='2',
        ECU='8',
        cost='$0.096 / hr',
    ),
    'm5.xlarge':dict(
        ram='16 GB',
        vCPU='4',
        ECU='16',
        cost='$0.096 / hr',
    ),
    'r5.large':dict(
        ram='16 GB',
        vCPU='2',
        ECU='9',
        cost='$0.126 / hr',
    ),
    'r5.xlarge':dict(
        ram='32 GB',
        vCPU='4',
        ECU='19',
        cost='$0.252 / hr',
    ),
    'r5.2xlarge':dict(
        ram='64 GB',
        vCPU='8',
        ECU='38',
        cost='$0.504 / hr',
    ),
}

settings = {

    'postgres-small':dict(

        instance.type='m5.large',

        ),

    'postgres-medium':dict(

        instance.type='r5.xlarge',

        max_connections = '20',
        shared_buffers = '7680 MB',
        work_mem = '96 MB',
        maintenance_work_mem = '2 GB',

        effective_io_concurrency = '200',
        max_worker_processes = '4',
        max_parallel_workers_per_gather = '2',
        max_parallel_workers = '4',

        effective_cache_size = '23040 MB',
        checkpoint_completion_target = '0.9',
        wal_buffers = '16 MB',
        min_wal_size = '4 GB',
        max_wal_size = '8 GB',

        default_statistics_target = '500',
        random_page_cost = '1.1',
        ),

    'postgres-large':dict(

        instance.type='r5.xlarge',

        max_connections = '20',
        shared_buffers = '1500 MB',
        work_mem = '40 MB',
        maintenance_work_mem = '760 MB',

        effective_io_concurrency = '200',		# 1-1000; 0 disables prefetching
        max_worker_processes = '2',		# (change requires restart)
        max_parallel_workers_per_gather = '1',	# taken from max_parallel_workers
        max_parallel_workers = '2',		# maximum number of max_worker_processes that
        					            # can be used in parallel queries
        wal_level='minimal',
        wal_buffers = '16 MB',
        max_wal_size = '8 GB',# - Checkpoints -
        min_wal_size = '4 GB',# - Checkpoints -

        checkpoint_completion_target = 0.9,	# checkpoint target duration, 0.0 - 1.0
        random_page_cost = '1.1',# - Planner Cost Constants -# measured on an arbitrary scale
        effective_cache_size = '4 GB',
        default_statistics_target = '500' # - Other Planner Options - # range 1-10000

        ),

    'neo4j-small': dict(

        instance.type='r5.large', # too small, may need to resize to xlarge!

        ),

    'neo4j-medium' : dict (

        instance.type='r5.xlarge'

        dbms.memory.heap.initial_size='11800 MB'
        dbms.memory.heap.max_size='11800 MB'
        dbms.memory.pagecache.size='12 GB'
        dbms.jvm.additional='-XX:+UseG1GC'
        dbms.jvm.additional='-XX:+AlwaysPreTouch'

        ),
}
