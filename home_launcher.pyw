import subprocess
CREATE_NO_WINDOW = 0x08000000
subprocess.Popen(["home_launch.cmd"], creationflags=CREATE_NO_WINDOW)