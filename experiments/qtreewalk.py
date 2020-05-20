import os
import sys
import glob
import time
import argparse
import pprint
import datetime
import multiprocessing
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf8')
from qumulo.rest_client import RestClient
from qumulo.lib.request import RequestError


class Gvars:
    def __init__(self, h, u, p):
        self.QHOST = h
        self.QUSER = u
        self.QPASS = p
        self.the_queue = multiprocessing.Queue()
        self.the_queue_len = multiprocessing.Value('i', 0)
        self.done_queue_len = multiprocessing.Value('i', 0)

args = None


def log(msg):
    t = datetime.datetime.utcnow()
    print("%s - %s" % (t.strftime('%Y-%m-%dT%H:%M:%SZ'), msg))


def add_to_queue(d):
    global gvars
    with gvars.the_queue_len.get_lock():
        gvars.the_queue_len.value += 1
    gvars.the_queue.put(d)


def list_dir(rc, d, out_file=None):
    global gvars
    next_page = "first"
    while next_page != "":
        if next_page == "first":
            try:
                r = rc.fs.read_directory(path=d["path"], page_size=1000)
            except RequestError as e:
                # Need to catch login timeouts
                if "Need to log in first to establish credentials." in str(e):
                    rc.login('admin', args.p)
                    r = rc.fs.read_directory(path=d["path"], page_size=1000)
                log("Error reading directory: %s" % d["path"])
                next
        else:
            r = rc.request("GET", r['paging']['next'])
        next_page = r['paging']['next']
        for ent in r["files"]:
            with gvars.done_queue_len.get_lock():
                gvars.done_queue_len.value += 1
            try:
                if args.l:
                    out_file.write("%s\t%s\t%s\t%s\n" % (d["path"], ent["name"], ent["size"], ent["type"]))
            except AttributeError as e:
                if "'NoneType' object has no attribute 'l'" in str(e):
                    pass
                else:
                    raise
            # This is the call that gets run against each file and directory
            do_per_file(ent, d, out_file, rc)
            if ent["type"] == "FS_FILE_TYPE_DIRECTORY" and int(ent["child_count"]) > 0:
                add_to_queue({"path": d["path"] + ent["name"] + "/", "max_depth": d["max_depth"]})


def do_per_file(ent, d, out_file=None, rc=None):
    """This does nothing by default. It should be monkey-patched by the user of
    qtreewalk"""
    pass


def worker_main():
    try:
        global gvars
        proc = multiprocessing.current_process()
        rc = RestClient(gvars.QHOST, 8000)
        rc.login(gvars.QUSER, gvars.QPASS)
        # this is terrible need to deal with args more gracefully
        try:
            if args.l:
                out_file = open("out-%s.txt" % proc.pid, "w")
            else:
                out_file = None
        except AttributeError as e:
            if "'NoneType' object has no attribute 'l'" in str(e):
                out_file = None
                pass
            else:
                raise
        while True:
            item = gvars.the_queue.get(True)
            list_dir(rc, item, out_file)
            try:
                if args.l:
                    out_file.flush()
            except AttributeError as e:
                if "'NoneType' object has no attribute 'l'" in str(e):
                    pass
                else:
                    raise
            with gvars.the_queue_len.get_lock():
                gvars.the_queue_len.value -= 1
    except KeyboardInterrupt:
        print(multiprocessing.current_process().name,
              "received KeyboardInterrupt")
        sys.exit(1)


def walk_tree(QHOST, QUSER, QPASS, start_path):
    global gvars
    if start_path[-1] != "/":
        start_path = start_path + "/"
    log("Tree walk on Qumulo cluster %s starting at path %s" % (QHOST, start_path))
    gvars = Gvars(QHOST, QUSER, QPASS)
    the_pool = multiprocessing.Pool(16, worker_main)
    rc = RestClient(gvars.QHOST, 8000)
    rc.login(gvars.QUSER, gvars.QPASS)
    root = rc.fs.read_dir_aggregates(path=start_path, max_depth=0)
    log("Directories to walk: %12s" % "{:,}".format(int(root["total_directories"])))
    log("      Files to walk: %12s" % "{:,}".format(int(root["total_files"])))
    add_to_queue({"path": start_path, "max_depth": 5})
    time.sleep(0.1) # wait a bit for the queue to get build up.
    wait_count = 0
    while gvars.the_queue_len.value > 0:
        wait_count += 1
        if (wait_count % 50) == 0: # show status every ~5 seconds
            log("Processed %s entries. Queue length: %s" % (gvars.done_queue_len.value, gvars.the_queue_len.value))
        time.sleep(0.1)
    the_pool.terminate()
    log("Processed %s entries." % gvars.done_queue_len.value)
    log("Done with tree walk.")
    # this is terrible need to deal with args more gracefully
    try:
        if args.l:
            log("Combining results.")
            fw = open("file-list.txt", "w")
            for f in glob.glob('out-*.txt'):
                fr = open(f, "r")
                fw.write(fr.read())
                fr.close()
                os.remove(f)
            log("Results save to file: file-list.txt")
    except AttributeError as e:
        if "'NoneType' object has no attribute 'l'" in str(e):
            pass
        else:
            raise
    del gvars


def parse_args():
    usage_msg = "\nExample: python api-tree-walk.py -s qumulo -p password123 -d /home/\nSpecify -h for list of arguments."
    parser = argparse.ArgumentParser(description='Recursive parallel tree walk with Qumulo API', usage=usage_msg)
    parser.add_argument('-s', required=True, help='Qumulo cluster ip/hostname')
    parser.add_argument('-p', required=True, help='Qumulo api *admin* password')
    parser.add_argument('-d', required=False, help='Starting directory', default='/')
    parser.add_argument('-l', required=False, help='Log all files', action='store_true')
    global args
    args = parser.parse_args()
    return args

