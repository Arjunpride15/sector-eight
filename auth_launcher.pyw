import subprocess
CREATE_NO_WINDOW = 0x08000000
subprocess.Popen(["auth_launch.cmd"], creationflags=CREATE_NO_WINDOW)