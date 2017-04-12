import multiprocessing
from Queue import Empty
import os, sys
import time

import qumulo.lib
import qumulo.lib.auth
import qumulo.rest
import qumulo.rest.fs as fs

START_PATH = '/'
NUM_WALKERS = 1
NUM_SETTERS = 10
API = {
    'host': '192.168.11.147',
    'port': '8000',
    'user': 'admin',
    'pass': 'a'
}
POLLING_INTERVAL = 2
QUEUE_TIMEOUT = 2
QUEUE_WAIT = 2

connection = None
credentials = None


class Counter(object):
    def __init__(self, initial_value=0):
        self.val = multiprocessing.Value('i', initial_value)
        self.lock = multiprocessing.Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def decrement(self):
        with self.lock:
            self.val.value -= 1

    def value(self):
        with self.lock:
            return self.val.value


def login():
    """return connection and credentials object based on above settings"""
    try:
        connection = qumulo.lib.request.Connection(API['host'],
                                                   int(API['port']))
        login_results, _ = qumulo.rest.auth.login(connection, None,
                                                  API['user'], API['pass'])

        credentials = qumulo.lib.auth.Credentials.from_login_response(
            login_results)
        return connection, credentials
    except Exception, e:
        print "Error connecting to the REST server: %s" % e
        sys.exit(1)


def walker_main(walker_q, setter_q, walker_ql, setter_ql):
    """Walker process, managed by a process pool, fed a walker_q
    1) consume a directory from the walker_q
    2) for each from the list of things in the directory
        if it's a file, print it (later we'll do something useful with it)
        if it's a directory, print it then add it to the walker_q
    """
    print os.getpid(), "walker()"

    while True:
        while True:
            try:
                directory = walker_q.get(True, QUEUE_TIMEOUT)
                walker_ql.decrement()
                break
            except Empty:
                print os.getpid(), "Timed out waiting on walker queue get"
                time.sleep(QUEUE_WAIT)
                pass

        response = fs.read_entire_directory(connection, credentials,
                                            page_size=5000, path=directory)

        dir_list = []
        file_list = []

        for r in response:
            dir_list = [i for i in r.data['files']
                        if i['type'] == 'FS_FILE_TYPE_DIRECTORY']
            file_list = [i for i in r.data['files']
                         if i['type'] == 'FS_FILE_TYPE_FILE']

        for d in dir_list:
            print os.getpid(), "Putting %s on walker queue" % d['path']
            setter_q.put(d)
            setter_ql.increment()
            walker_q.put(d['path'])
            walker_ql.increment()

        for f in file_list:
            while True:
                try:
                    setter_q.put(f, QUEUE_TIMEOUT)
                    setter_ql.increment()
                    break
                except Empty:
                    print os.getpid(), "Timed out waiting on setter queue put"
                    time.sleep(QUEUE_WAIT)
                    pass


def get_attr(setter_queue, dirs_processed, files_processed,
             setter_qlength):
    print os.getpid(), "setter()"
    while True:
        file_info = setter_queue.get(True)
        setter_qlength.decrement()
        if file_info['type'] == 'FS_FILE_TYPE_DIRECTORY':
            path = file_info['path']
            fs.get_attr(connection, credentials, path=path)
            dirs_processed.increment()
        elif file_info['type'] == 'FS_FILE_TYPE_FILE':
            path = file_info['path']
            fs.get_attr(connection, credentials, path=path)
            files_processed.increment()


if __name__ == '__main__':
    start_time = time.time()
    connection, credentials = login()
    agg_result, _ = fs.read_dir_aggregates(connection, credentials, START_PATH)

    dir_count = int(agg_result['total_directories']) + 1
    file_count = int(agg_result['total_files'])

    print "total directories to process:", dir_count
    print "total files to process:", file_count

    # Synced counters for progress and determining done-ness
    dirs_processed = Counter()
    files_processed = Counter()
    walker_qlen = Counter()
    setter_qlen = Counter()

    # Set up queues and worker pools
    setter_queue = multiprocessing.Queue()
    walker_queue = multiprocessing.Queue()
    setter_pool = multiprocessing.Pool(NUM_SETTERS, get_attr,
                                       (setter_queue,
                                        dirs_processed, files_processed,
                                        setter_qlen,))
    walker_pool = multiprocessing.Pool(NUM_WALKERS, walker_main,
                                       (walker_queue, setter_queue,
                                        walker_qlen, setter_qlen,))

    # Initialize walker queue with a path, setter queue with a fileinfo JSON
    walker_queue.put(START_PATH)
    walker_qlen.increment()

    root_info, _ = fs.get_attr(connection, credentials, path=START_PATH)

    setter_queue.put(root_info)
    setter_qlen.increment()

    # performance counters
    last_files_processed = 0
    last_directories_processed = 0

    # once dirs_processed and files_processed reach their goals we break and
    # this will exit once the queues are empty and the worker pools are blocked
    while True:
        time.sleep(POLLING_INTERVAL)
        if dirs_processed.value() >= dir_count and files_processed.value() >= file_count:
            break
        fp = files_processed.value()
        fps = (fp - last_files_processed) / POLLING_INTERVAL
        last_files_processed = fp
        dp = dirs_processed.value()
        dps = (dp - last_directories_processed) / POLLING_INTERVAL
        last_directories_processed = dp
        print "f:%i/%i d:%i/%i fps:%i dps:%i wql:%i sql:%i" % (files_processed.value(),
                                                  file_count,
                                                  dirs_processed.value(),
                                                  dir_count,
                                                  fps, dps,
                                                  walker_qlen.value(),
                                                  setter_qlen.value())

    print "Finished: %i directories and %i files processed" % (dirs_processed.value(), files_processed.value())
    print "%f seconds elapsed" % (time.time() - start_time)
