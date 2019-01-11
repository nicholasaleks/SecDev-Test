
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

def execute_automated_collection():
    # Traverse file system and look for files that match extension
    # Look out for:
    #       - File permissions (both to search and copy)
    #       - case sensitivity
    #       - complex nested fs
    #       - performance of search
    # Copy matching files to some location
    pass

if __name__ == '__main__':
    execute_automated_collection()