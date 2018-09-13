# SecDev-Solution
# Technique: Remote File Copy
# ID: T1105
# Tactic: Command and Control, Lateral Movement

# Objective
- Transfer a local file to remote server using SMB
- Provide evidence of efficient coding and documentation skills to TD Security Engineering Team

# Run
`python attack.py`

# Resources
- [MITRE ATT&CK](https://attack.mitre.org/)

# Requirements
- python 2.7
- Windows 64bit

# Post Condition
- There will be a test.exe file in this folder

# Limitations
- Text is displayed on command prompt (no graphical user interactive)
- Requires seperate server-side handling to receive file

# Personal Comments
- I tried creating an automated system with GUI (like Caldera) using HTML and JavaScript, but failed miserably and was unable to resolve many issues arising due to the complicated structure and access permissions
- Thus, the script that I’ve uploaded is extremely simple and refers several existing Python attack automation scripts
- However, I’ve developed a genuine interest in the MITRE ATT&CK framework and will continue working on the GUI, until I get it right

