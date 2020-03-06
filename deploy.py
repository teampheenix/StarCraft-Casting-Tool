import subprocess
from scctool import __version__ as version

if __name__ == "__main__":
    subprocess.run(f"pyupdater pkg --process", shell=True, check=True)
    subprocess.run(f"pyupdater pkg --sign", shell=True, check=True)
    #copy to SCCT-archive
    #git add new files
    #git push