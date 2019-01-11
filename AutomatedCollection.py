import os
import stat
import logging
from shutil import copyfile

EXTENSIONS = []
MATCH_IGNORE_CASE = False
COLLECTION_LOCATION = ''

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
    # Traverse file system and look for files that match extension
    # Look out for:
    #       - File permissions (both to search and copy)
    #       - case sensitivity
    #       - complex nested fs
    #       - performance of search
    # Copy matching files to some location
    search_filesystem(path)

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
                # Restore original permissions
                modify_permissions(d, original_permissions)

        for file in files:
            f = os.path.join(root, file)
            if file_matches_target_extension(f):
                logger.info("Target file found: %s", f)
                original_permissions = get_permissions(f)
                if original_permissions < OWNER_READ_PERMISSIONS:
                    logger.info(
                        "File does not have owner read permissions. Permissions will be temporarily modified. "
                        "File: %s, current permissions: %d", d, original_permissions)
                    modify_permissions(f, OWNER_READ_PERMISSIONS)
                copyfile(f, os.path.join(COLLECTION_LOCATION, file))


def file_matches_target_extension(f):
    ext = os.path.splitext(f)[1]
    return ext.lower() in EXTENSIONS if MATCH_IGNORE_CASE else ext in EXTENSIONS


def collect_file(src, dest):
    copyfile(src, dest)


def create_and_validate_collection_dir():
    if not os.path.exists(COLLECTION_LOCATION):
        os.makedirs(COLLECTION_LOCATION)
        modify_permissions(COLLECTION_LOCATION, OWNER_READ_EXECUTE_PERMISSIONS)


def get_permissions(f):
    return int(oct(os.stat(f)[stat.ST_MODE])[-3:])


def modify_permissions(f, perm):
    os.chmod(f, perm)


if __name__ == '__main__':
    EXTENSIONS.append('.txt')
    COLLECTION_LOCATION = '/Users/vince/Desktop/output'
    execute_automated_collection("/Users/vince/Desktop/test")
