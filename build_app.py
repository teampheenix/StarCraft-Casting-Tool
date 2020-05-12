import subprocess
import fileinput
from scctool import __version__ as version

if __name__ == "__main__":
    subprocess.run(f'git tag --force -a v{version} -m \'v{version}\'')
    subprocess.run("gitchangelog > CHANGELOG.md", shell=True, check=True)
    with open('CHANGELOG.md', 'r') as fh:
        text = fh.read()
    with open('CHANGELOG.md', 'w', encoding='utf-8') as fh:
        fh.write(text)
    subprocess.run(f".\.venv\Scripts\pyupdater.exe build --app-version {version} win.spec", shell=True, check=True)