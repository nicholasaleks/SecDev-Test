import os

EXTENSIONS = []

def get_file_permissions(f):
    pass

def modify_file_permissions(f, p):
    pass

def copy_file(src, dest):
    # Look out for:
    #    - name collisions
    #    - permissions
    pass

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
    pass
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            d = os.path.join(root, dir)
            print(d)
        for file in files:
            f = os.path.join(root, file)
            print(f)

if __name__ == '__main__':
    execute_automated_collection("/Users/vince/Desktop/test")