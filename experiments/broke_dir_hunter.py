import qumulo.lib
import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest
import qumulo.rest.fs as fs

from walker import login
from walker_config import START_PATH, API


connection = None
credentials = None


def walk_dir(directory):
    try:
        response = fs.read_entire_directory(connection, credentials,
                                            page_size=5000, path=directory)
    except qumulo.lib.request.RequestError:  # token is broke, login again
        global connection, credentials
        connection, credentials = login()
        response = fs.read_entire_directory(connection, credentials,
                                            page_size=5000, path=directory)
    print "Walking", directory
    for r in response:
        dir_list = (i for i in r.data['files']
                    if i['type'] == 'FS_FILE_TYPE_DIRECTORY')
        for d in dir_list:
            walk_dir(d['path'])


if __name__ == '__main__':
    connection, credentials = login()
    response = fs.read_entire_directory(connection, credentials,
                                        page_size=5000, path=START_PATH)
    print "dir", START_PATH
    walk_dir(START_PATH)
