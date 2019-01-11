import argparse
import os
import stat
import logging
import hashlib
import re
import subprocess
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
    Traverses recursively through the src directory and copies any files that match at least one pattern in
     TARGET_REGEX_PATTERNS or with an extension listed in TARGET_EXTENSIONS. Files are copied into the dest directory.
     If archive is True, a tarball will be created with the name archive_name in the dest directory. If clean_dest is
     True, all collected documents will be deleted at the end of the script.
    :param src: Path to directory to traverse
    :param dest: Path of directory to save files in
    :param archive: If True, dest will be tarballed
    :param archive_name: The name of the tarball
    :param upload: If True, files will be uploaded to docker container. Only the tarball will be uploaded if archived.
    :param container: The name of the container to copy files to
    :param clean_dest: If True, deletes all collected files at the end of the script
    :return:
    """
    pause_bash_history_command = "set +o history"
    run_bash_command(pause_bash_history_command)

    create_and_validate_permissions(dest)
    search_filesystem(src, dest)

    if archive:
        archive_files(dest, os.path.join(dest, archive_name))

    if upload:
        print("uploading")

    if clean_dest:
        clean_files(dest)

    resume_bash_history_command = "set -o history"
    run_bash_command(resume_bash_history_command)


def run_bash_command(command):
    process = subprocess.Popen(command.split(), shell=True, stdout=subprocess.DEVNULL)
    process.communicate()


def search_filesystem(src, dest):
    for root, dirs, files in os.walk(src):

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

                copyfile(f, os.path.join(dest, unique_filename))


def file_matches_target_extension(f):
    ext = os.path.splitext(f)[1]
    return ext.lower() in TARGET_EXTENSIONS if MATCH_IGNORE_CASE else ext in TARGET_EXTENSIONS


def file_matches_target_regex_patterns(f):
    return True in [p.match(f) is not None for p in TARGET_REGEX_PATTERNS]


def collect_file(src, dest):
    copyfile(src, dest)


def create_and_validate_permissions(d):
    if not os.path.exists(d):
        os.makedirs(d)
    modify_permissions(d, OWNER_RWX_PERMISSIONS)


def get_permissions(f):
    return int(oct(os.stat(f)[stat.ST_MODE])[-3:])


def modify_permissions(f, perm):
    os.chmod(f, perm)


def archive_files(src, dest):
    with tarfile.open(dest, "w:gz") as tar:
        tar.add(src, arcname=os.path.basename(src))


def upload_collections(container, src, dest):
    docker_upload_command = 'docker cp %s %s:%s'.format(container, src, dest)
    run_bash_command(docker_upload_command)


def clean_files(dest):
    rmtree(dest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automated Collection.')
    parser.add_argument('--src', type=str, default='/', help='An absolute path to the directory to begin traversing in')
    parser.add_argument('--dest', type=str, default='/collect', help='An absolute path to the directory files will '
                                                                     'be collected in')
    parser.add_argument('--target_extensions', nargs='*', help='A list of one or more extensions of files to collect')
    parser.add_argument('--target_regex', nargs='*', help='A list of one or more regex patterns. Files matching any of '
                                                          'these patterns will be collected')
    parser.add_argument('--archive', type=bool, default=True, help='Creates a tar ball after all the files have been '
                                                                   'collected')
    parser.add_argument('--archive_name', type=str, default='collection.tar.gz', help='The name of the archive if '
                                                                                      'created')
    parser.add_argument('--upload', type=bool, default=False, help='Uploads collection to a docker container. '
                                                                   'A container name must be provided with '
                                                                   'the --container_name argument')
    parser.add_argument('--container_name', type=str, help='The name of the docker container to upload files to')
    parser.add_argument('--clean_up', type=bool, default=False, help='Removes all files saved to the collection')
    args = parser.parse_args()
    TARGET_EXTENSIONS = args.target_extensions
    TARGET_REGEX_PATTERNS = [re.compile(p) for p in args.target_regex]
    if TARGET_EXTENSIONS is None and TARGET_REGEX_PATTERNS is None:
        print("At least one extension or regex pattern must be provided")
    else:
        execute_automated_collection(args.src, args.dest, args.archive, args.archive_name, args.upload, args.container_name, args.clean_up)
