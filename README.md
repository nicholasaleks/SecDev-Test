## Challenge solution by Naor N.
## Exploit Name: Credentials in Files (https://attack.mitre.org/wiki/Technique/T1081)

# Summary
This exploit is looking for credentials / sensitive data on machine.
It detects hosting OS type and executed proper command if supported, otherwise does not executes logic.
It looks for files that are matching the pattern and looks for sensitive data inside according to predefined keywords,
If sensitive data is found, then this data is being captures and later on transmitted to C2 server.
Additional functionallity is to send the whole file with the match to C2 server if this features is toggled on (obfuscated/compressed).
The Exploit is working with any user according his to permissions, therefore is better to executed as root/administrator

# Exploit Usage

1. Execution preconditions: OS = "Windows" or "Linux", machine is connected to Internet
							If OS == "Linux" - bash history should be turnned on before execution with "set +o history"
2. Attack action: Read summary. 
	Usage: python main.py [--log-level <"DEBUG", "INFO", "WARN", "ERROR", "CRITICAL">] [--pattern <file_search_pattern] [--keywords <comma_seperated_keywords>] [--case-sensitive <True/False>] [--send-files <True/False>] [--obfuscate <True/False>] [--compress <True/False>] [--send-logs <True/False>]
	
	Default parameters values:
		--log-level = DEBUG
		--pattern = "*.yaml"
		--keywords = ['user', 'pass', 'host', 'pwd', 'key', 'credetials', 'login', 'secret', 'url']
		--send-files = False (send matching pattern files with matching keywords to c2 server)
		--send-log = False (send log to c2 server)
		--case-sensitive = False
		--obfuscate = True
		--compress = False

3. Attack postconditions: attack considered as successful if there is at least one match
4. Exploit is removing log file and transmit the data to c2 server obfuscated to avoid monitoring/automatic rules that capture sensitive data leakage

I'm particularly proud of the dynamically of the exploit, it can be executed on several os (and other os can be added easily), 
it has lot of configurated exposed to the executing user and it should be safe and 'quiet', 
it means that no information is printed to the screen, exceptions are captured and data is transmitted obfuscated to c2.
can be orchestration ansible playbook

-----------------------------------


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


