import subprocess
import os
import distutils.log
import distutils.dir_util
from scctool import __version__ as version

if __name__ == "__main__":
    subprocess.run(f".\.venv\Scripts\pyupdater.exe pkg --process", shell=True, check=True)
    subprocess.run(f".\.venv\Scripts\pyupdater.exe pkg --sign", shell=True, check=True)
    archive = '../SCCT-archive'
    distutils.log.set_verbosity(distutils.log.DEBUG)
    distutils.dir_util.copy_tree(
        'pyu-data/deploy',
        archive,
        update=1,
        verbose=1,
    )
    #os.chdir(archive)
    #subprocess.run(f"git add .", shell=True, check=True)
    #subprocess.run(f"git commit -a -m 'Updated to v{version}'", shell=True, check=True)
    #subprocess.run(f"git push'", shell=True, check=True)