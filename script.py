import os
import re
import logging
import argparse

# email modules
import smtplib
from email.mime.text import MIMEText

# default configurations
DEFAULT_SHELLS = ['bash', 'zsh']
DEFAULT_KEYWORDS = ['username', 'password',
                    'secret', 'rsa', 'key', 'host']

# setup log output
logging.basicConfig(filename='cred.log', level=logging.INFO)
logger = logging.getLogger('logs')


class CredentialReader(object):

    def __init__(self, **props):
        # get list of file paths
        self.__fps = props.get('fps')
        # get list of keywords
        self.__keywords = props.get('keywords')
        # read file contents
        self.__files = self.__get_file_content()
        # flag for finding credentials
        self.__cred_found = False

    def __get_file_content(self):
        """

          Returns each file content as an array of strings

        """
        result = []
        for fp in self.__fps:
            with open(os.path.expanduser(fp)) as f:
                # remove extra newline from end of line
                file = [line.strip('\n') for line in f.readlines()]
                result.append(file)
        return result

    def __find_credentials(self):
        """

          Searches the file content for keywords
          and returns a dictionary of keywords and their matched values

        """

        # initialize container
        credentials = dict()

        # search for words appearing after keywords
        kw_pattern = [
            '.*(' + kw + '=?\s*(?P<' + kw + '>[^ ]+))\s*' for kw in self.__keywords]

        for (i, pat) in enumerate(kw_pattern):
            # compile pattern for each keyword
            regex = re.compile(pat, re.IGNORECASE)

            # get keyword
            kw = self.__keywords[i]

            # iterate through all files
            for file in self.__files:
                for line in file:
                    obj = regex.match(line)
                    if obj:
                        try:
                            # if a match is captured, store in dictionary
                            credentials[kw] = str(obj.group(kw)) if not credentials.get(kw) else '{0},{1}'.format(
                                credentials[kw], obj.group(kw))
                            # turn flag to True
                            if not self.__cred_found:
                                self.__cred_found = True
                        except Exception as e:
                            # handle exception if match is captured but cannot
                            # be added as a string
                            logger.exception(
                                "Error parsing credential file: {}".format(e))

        return credentials

    def log_results(self):
        """

        output results to cred.log

        """
        credentials = self.__find_credentials()
        if not self.__cred_found:

            # no keywords found
            logger.info('No sensitive data found.')
            return  # exit log writing

        # summary
        logger.warn('{total} potential credentials discovered'.format(
            total=len(credentials)))

        # output keywords and matched values
        for k in credentials:
            v = credentials[k]
            logger.warn('CREDENTIAL type {k}: {v}'.format(k=k, v=v))


if __name__ == '__main__':
    # parse command line args
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '-s', '--shells',
        help='File containing searchable info'
    )

    arg_parser.add_argument(
        '-k', '--keywords',
        help='Keywords to search within shell history files'
    )

    arg_parser.add_argument(
        '--cleanup',
        help='Indicates whether to remove log after script'
    )

    arg_parser.add_argument(
        '-fp', '--filepath',
        help='Manually define filepath for shell history file'
    )

    args = arg_parser.parse_args()

    # parse input
    keywords = args.keywords.split(',') if args.keywords else DEFAULT_KEYWORDS
    shells = args.shells.split(',') if args.shells else DEFAULT_SHELLS
    cleanup = args.cleanup

    # format file path location
    fps = ['~/.{}_history'.format(sh) for sh in shells]

    # allow manually defined file paths
    filepath = [args.filepath] if args.filepath else fps

    # read and parse credentials
    cr = CredentialReader(keywords=keywords, fps=filepath)

    # write log
    cr.log_results()

    # remove log file if requested
    if cleanup == 'yes' and os.path.exists('cred.log'):
        os.remove('cred.log')
