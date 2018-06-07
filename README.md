BASH HISTORY EXPLOIT
--------------------------------------------------------------------
1) Set config file parameters in config.json:

Sample settings

	{

  	"CONFIG": {

    	"EXPLOIT_HOME":     "/Users/fahadk/GithubProjects/SecDev-Test/",

    	"EXPLOIT_TAGS":     "password|pwd|login|secure|credentials",

    	"LOG_FILENAME":     "exploit.log",

    	"OUTPUT_FILENAME":  "results.txt"

  	}

	}

2) To run:

	set +o history

	python exploit.py [--config-file <filename>] [--log-level <DEBUG", "INFO", "WARN", "ERROR>]

	set -o history

By default, log level is set to DEBUG
config file is set to config.json


Before running this script, we disable users history itself so no one else can track this user. And enable it after the exploit is complete.

This exploit tries to get the /Users/<username>/.bash_history file from all users and saves it locally for Exfiltration in bash_history_files folder.

I am particularly proud of the part that after copying all files, it looks for usernames, passwords and other credential information, which users may have typed as command line parameters to their applications. It does this by searching for the tags defined in the config file in all files. Not just credential tags, other kind oftags can be added in the config file to detect other keywords. The found tags are stored in OUTPUT_FILENAME.
This script is easily configurable to run in any MacOS environment. It may actually work in Linux environemtn as well (althoough not tested). THe logs are informational enough to tell us what wnet wrong or what steps where successful in the exploit.


We assume that this user running this exploit has read access to all the bash history files. Typically we would run this as root user.



# The SecDev Challenge
Applicants for the SecDev Engineer career must complete the following challenge, and submit a solution prior to the interviewing process. This will help the interviewers assess your strengths, and frame the conversation through the interview process. Take as much time as you need, however we ask that you not spend more than a few hours. 

We prefer that you use Python; however, this is not a hard requirement. Please contact us if you'd like to use something else.

## Submission Instructions
1. Fork this project on github. You will need to create an account if you don't already have one
1. Complete the project as described below within your fork
1. Push all of your changes to your fork on github and submit a pull request. 
1. You should also email your recruiter to let them know you have submitted a solution. Make sure to include your github username in your email (so we can match applicants with pull requests).

## Project Description
Leverage the [MITRE ATT&CK framework](https://attack.mitre.org/wiki/Main_Page) and pick 1 attack technique. MITRE's Adversarial Tactics, Techniques and Common Knowledge (ATT&CK) is a curated knowledge base and model for cyber adversary behavior, reflecting the various phases of an adversary's lifecycle and the platforms they are known to target.

We request that you write a Python exploit that will automate the attack technique you picked. (You may decide to write the exploit in powershell/bash)
1. Your exploit should clearly define attack preconditions (For Example: [Operating System = "Windows", Software Installed = "Office 2007"])
2. Your exploit should clearly define attack action (Execution of the attack)
3. Your exploit should clearly define postconditions (This will act as a validation check if your exploit was either successfully/failed)
4. Your exploit should finally contain a comprehensive clean-up method which will remove any files, directories and reset configurations changed/added by the attack action

Your exploit should be easy to set up, and should run on either Linux or Mac OS X. It should not require any non open-source software. The exploit will be tested in a virtual machine lab based on the clearly defined preconditions.

There are many ways that this exploit could be built; we ask that you build it in a way that showcases one of your strengths. If you you enjoy documentation, do something interesting with defining the preconditions. If you like object-oriented design, feel free to dive deeper into the model of this problem. We're happy to tweak the requirements slightly if it helps you show off one of your strengths.

## Bonus Points
Using orchestration software (Salt, Ansible, Puppet, Chef, and/or deployment scripts) to provision attack target machine state (meeting attack preconditions)

Once you're done, please submit a paragraph or two in your `README` about what you are particularly proud of in your implementation, and why.

## Evaluation
Evaluation of your submission will be based on the following criteria. 

1. Did your exploit fulfill the basic requirements?
2. Did you document the method for setting up and running your exploit?
3. Did you follow the instructions for submission?
4. Does your exploit work


