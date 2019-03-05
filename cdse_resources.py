import requests
from os import getcwd, makedirs, chdir
from os.path import join, isdir, isfile
import importlib

url_root = "https://raw.githubusercontent.com/bbadzioch/CDSE-Workshop/master/"
flist = ["cdse_copy_cells.py",
         "CDSE_Python_Test.ipynb",
         "CDSE_Python1.ipynb",
         "CDSE_Python2.ipynb",
         "CDSE_Python3.ipynb",
         "CDSE_Python4.ipynb",
         "__init__.py"
        ]

local_dir = "CDSE2019_Python_Files"

def get_resources():

    global url_root
    global flist
    global local_dir

    cwd = getcwd()
    local_path = join(cwd,  local_dir)
    file_missing = False

    if not isdir(local_path):
        print(f"Creating directory {local_dir:25}", end="")
        try:
            makedirs(local_path)
            print("Done.")
        except:
            print("FAILED")
            file_missing = True
            return file_missing


    for fname in flist:
        print(f"Downloading {fname:32}", end="")
        try:
            r = requests.get(url_root + fname)
        except requests.ConnectionError:
            print("\n\nCONNECTION ERROR. Check your internet connection.")
            file_missing = True
            return file_missing
        if not r.status_code == requests.codes.ok:
            if r.status_code == 404:
                print("FILE NOT FOUND 404")
                file_missing = True
            else:
                print(f"Status code: {r.status_code}.")
            continue

        with open(join(local_dir, fname) , "wb") as f:
            f.write(r.content)
        print("Done.")

    print("Resources download finished.")
    return file_missing


file_missing = get_resources()

if file_missing:
    print('''

Some files could not be downloaded. Please check your internet
connection and try again. If this problem persists please post
a message with a screenshot of this notebook on the CDSE Python
workshop Piazza page:

piazza.com/buffalo/spring2019/cdsepython''')
else:
    chdir(local_dir)
    cc = importlib.import_module("cdse_copy_cells")
    cc.C("0 -f0")
