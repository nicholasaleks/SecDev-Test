# Credential Access - Brute Force - Timing Attack

## Remarks

This exploit works by using a timing attack to determine a secret required by
the vulnerable application. This is the Credential Access tactic under MITRE
ATT&CK, exploited by the Brute Force technique.

The choice of this technique was inspired by one of the challenges
at the DEFCON Toronto CTF in December 2017, which no team was able to crack
until it was announced that it used a timing attack. Now I'll never forget to
try timing attacks.

To be extra sterile and ultra portable, the real dependencies, exploit and
vulnerable binary are run in Docker. This is quite nice for running manual
testing on other systems, because even python varies across Linux distributions
and even more greatly across operating systems. I chose this approach over an
Ansible playbook because of the difficulty for end-users in getting Ansible to
work by setting up SSH keys and the host inventory, especially the variables
`ansible_ssh_user` and `ansible_become_pass.` Although not always practical,
Docker is much more portable, and easier to deploy on new systems, even
Windows.

## Instructions

### 0. Operating System and Network

Any operating system that will run docker-compose and docker should be
sufficient. Debian GNU/Linux stretch (presently stable) is recommended.

The system will require access to the Internet at least until the attack is complete.

### 1. Required State Setup

On Debian stretch, you may complete this step by cloning the repo unto the host
system and running `./1_debian_setup.sh`.

OR you may complete the scripts' actions manually:

Git and Docker must be installed on the host system. They are freely available
in Debian, however the docker.io package needs to be installed from the
unstable archive. Installation and use of git is out of scope because this is
a git repository.

The Debian package names and required versions are as follows:
- docker.io >= 1.13.1
- docker-compose >= 1.8.0
- git >= 2.11 (`./4_debian_cleanup` needs roughly git >= 1.8, but only >= 2.11
  has been tested)

Under the Debian unstable docker.io package, it's necessary to add your user to
the `docker` group and then login to again. Alternatively you can run as root.

Docker variants are available for [macOS](https://www.docker.com/docker-mac) and
[Windows](https://www.docker.com/docker-windows).

### 2. Prepare the attack

On Debian stretch, macOS and other Unix-likes, you can complete this step by
running `./2_prepare.sh`.

OR you may complete the scripts' actions manually:

First you'll want to walk the directory tree of the git repository to the
location of this readme
file.

Next run `docker-compose build` to build the Docker image.

Finally run `docker compose run attack make -B` to compile the vulnerable
program. It is safe to ignore the pedantic warnings.


### 3. Run

On Debian stretch, macOS and other Unix-likes, you can complete this step by
running `./3_attack.sh`.

OR you may complete the scripts' actions manually:

```bash
docker-compose run attack
```

This command will output the secret once it is found. In the unlikely event
that the script does not find the secret, simply run the script again.

The script is sucessful if and only if it prints a message to stdout of the
form: `The credentials are user : pass`.

### 4. Cleanup

On Debian stretch, you can complete this step by running `./4_debian_cleanup.sh`.

OR you may complete the scripts' actions manually:

- You may now uninstall Docker. If running Debian, it can be removed using APT
  as shown in the script.

- You may also delete the directory in which you cloned this repository.

As git is out of scope, the script does not uninstall it.
