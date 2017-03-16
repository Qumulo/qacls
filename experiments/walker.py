import multiprocessing
import os, sys
import time

from qumulo.rest_client import RestClient
import qumulo.lib
import qumulo.rest
import qumulo.rest.fs as fs

NUM_WORKERS = 4
API = {
    'host': '192.168.11.147',
    'port': '8000',
    'user': 'admin',
    'pass': 'a'
}


def login():
    """return connection and credentials object based on above settings"""
    try:
        connection = qumulo.lib.request.Connection(API['host'],
                                                   int(API['port']))
        login_results, _ = qumulo.rest.auth.login(connection, None,
                                                  API['user'], API['pass'])

        credentials = qumulo.lib.auth.Credentials.from_login_response(
            login_results)
        # print connection
        # print credentials
        return (connection, credentials)
    except Exception, e:
        print "Error connecting to the REST server: %s" % e
        #print __doc__
        sys.exit(1)


def walker_main(queue, count, lock):
    """Walker process, managed by a process pool, fed a queue
    1) consume a directory from the queue
    2) for each from the list of things in the directory
        if it's a file, print it (later we'll do something useful with it)
        if it's a directory, print it then add it to the queue
    """
    print os.getpid(), "working"

    connection, credentials = login()
    # print connection
    # print credentials

    while True:
        directory = queue.get(True, 10)
        with lock:
            count.value += 1

        print os.getpid(), "got directory", directory
        # 1) list the directory we got
        response = fs.read_entire_directory(connection, credentials,
                                            page_size=5000, path=directory)

        # 2) for each item in 'files' that is "type": "FS_FILE_TYPE_DIRECTORY"
        #    add to the queue
        #    set the ACL, inherited, inheritance
        dir_list = []
        file_list = []
        # print response
        # count = 0
        for r in response:
            # count = count + 1
            # print "Item %s from response: " % str(count)
            dir_list = [i['path'] for i in r.data['files']
                        if i['type'] == 'FS_FILE_TYPE_DIRECTORY']
            file_list = [i['name'] for i in r.data['files']
                         if i['type'] == 'FS_FILE_TYPE_FILE']
            # print dir(r)
            # print r
            # print r.data
            # dir_list.extend([i['name'] for i in r.data['files']
            #                  if i['type'] == 'FS_FILE_TYPE_DIRECTORY'])
        print os.getpid(), "dir_list", dir_list
        print os.getpid(), "file_list", file_list
        for d in dir_list:
            #target_dir = os.path.join(directory, d) + '/'
            # print "target_dir to put on queue: %s" % target_dir
            print os.getpid(), "putting %s on queue" % d
            queue.put(d)

        #3) For each item in 'files' that is "type": "FS_FILE_TYPE_FILE"
        #    set the ACL, inherited"""
        # print os.getpid(), "got", directory
        #time.sleep(1) # simulate a "long" operation


if __name__ == '__main__':
    dir_count = multiprocessing.Value('i',0)
    lock = multiprocessing.Lock()
    the_queue = multiprocessing.Queue()
    the_pool = multiprocessing.Pool(NUM_WORKERS,
                                    walker_main,
                                    (the_queue, dir_count, lock,))
    the_queue.put("/")
    time.sleep(10) # horrible hack to make the queue persist long enough for
                   # walkers to add more directories to it
    with lock:
        print "Finished: %i directories processed" % dir_count.value
