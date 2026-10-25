import shutil,subprocess,sys,unittest
from pathlib import Path

def build_fixture(root,code=0):
    if not sys.platform.startswith('linux') or not shutil.which('cc'):
        raise unittest.SkipTest('Linux cc fixture unavailable; Windows native launch remains pending')
    folder=Path(root)/'controlled app with spaces';folder.mkdir(exist_ok=True)
    target=folder/'ORVEX controlled app'
    subprocess.run(['cc','-DEXIT_CODE='+str(code),str(Path(__file__).parent/'fixtures/controlled_app.c'),'-o',str(target)],check=True,capture_output=True)
    return target
