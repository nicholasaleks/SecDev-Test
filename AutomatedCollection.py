import os
import stat
import logging
import hashlib
import re
from datetime import datetime
from shutil import copyfile

TARGET_EXTENSIONS = []
TARGET_REGEX_PATTERNS = []
MATCH_IGNORE_CASE = False
COLLECTION_LOCATION = ''
MD5 = hashlib.md5()

OWNER_READ_PERMISSIONS = stat.S_IRUSR
OWNER_READ_EXECUTE_PERMISSIONS = stat.S_IRUSR | stat.S_IXUSR
OWNER_WRITE_EXECUTE_PERMISSIONS = stat.S_IWUSR | stat.S_IXUSR

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)4s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def execute_automated_collection(path='/'):
    """
    Traverses all files and folders from path, looking for files with an extension that matches one in EXTENSIONS.
    Read and execute permissions for directories will be temporarily granted to the user to continue traversal.
    Read permissions for files will be temporarily granted to copy files.
    :param path: An absolute path in the filesystem (optional)
    :return:
    """
    # TODO: Pause bash history
    create_and_validate_dir(COLLECTION_LOCATION)
    search_filesystem(path)
    # TODO: Resume bash history

def search_filesystem(path):
    for root, dirs, files in os.walk(path):
        # Check for directories that can't be accessed
        for dir in dirs:
            d = os.path.join(root, dir)
            original_permissions = get_permissions(d)
            if original_permissions < OWNER_READ_EXECUTE_PERMISSIONS:
                logger.info(
                    "File does not have owner read execute permissions. Permissions will be temporarily modified."
                    " File: %s, current permissions: %d",
                    d,
                    original_permissions)

                modify_permissions(d, OWNER_READ_EXECUTE_PERMISSIONS)
                search_filesystem(d)
                modify_permissions(d, original_permissions)

        for file in files:
            f = os.path.join(root, file)
            if file_matches_target_extension(file) or file_matches_target_regex_patterns(file):
                logger.info("Target file found: %s", f)
                original_permissions = get_permissions(f)
                if original_permissions < OWNER_READ_PERMISSIONS:
                    logger.info(
                        "File does not have owner read permissions. Permissions will be temporarily modified. "
                        "File: %s, current permissions: %d", d, original_permissions)
                    modify_permissions(f, OWNER_READ_PERMISSIONS)
                MD5.update(str(datetime.now()).encode("utf-8"))
                name, ext = os.path.splitext(file)
                unique_filename = ''.join([name, '-', MD5.hexdigest(), ext])

                copyfile(f, os.path.join(COLLECTION_LOCATION, unique_filename))


def file_matches_target_extension(f):
    ext = os.path.splitext(f)[1]
    return ext.lower() in TARGET_EXTENSIONS if MATCH_IGNORE_CASE else ext in TARGET_EXTENSIONS


def file_matches_target_regex_patterns(f):
    return True in [p.match(f) != None for p in TARGET_REGEX_PATTERNS]


def collect_file(src, dest):
    copyfile(src, dest)


def create_and_validate_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)
        modify_permissions(d, OWNER_READ_EXECUTE_PERMISSIONS)


def get_permissions(f):
    return int(oct(os.stat(f)[stat.ST_MODE])[-3:])


def modify_permissions(f, perm):
    os.chmod(f, perm)


def upload_collections():
    pass


def clean_up():
    pass


if __name__ == '__main__':
    TARGET_EXTENSIONS.append('.txt')
    TARGET_REGEX_PATTERNS.append(re.compile("test.*"))
    COLLECTION_LOCATION = '/Users/vince/Desktop/output'
    execute_automated_collection("/Users/vince/Desktop/test")
