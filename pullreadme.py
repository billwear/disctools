#!/usr/bin/python3
# retrieve a file from github
## what github?  specify on command line or in config file
## hardcode everything to start, then parameterize it
# import urllib.request
# import json
# import ssl
# import os
# import time
# import sys

from git import Repo
import glob
import os
import shutil
import re

# remove /tmp/packer-maas if it exists; it could be stale
import os
if os.path.exists("/tmp/packer-maas"):
    shutil.rmtree("/tmp/packer-maas")

if os.path.exists("/tmp/readme-output.md"):
    os.remove("/tmp/readme-output.md")
  
# clone the packer-maas repo into /tmp
Repo.clone_from("https://github.com/canonical/packer-maas","/tmp/packer-maas")

# (re)create the markdown buffer
rmo = open("/tmp/readme-output.md", "a")
markdown = []

# loop through all the subdir README.md files
for name in glob.glob(r'/tmp/packer-maas/*/README.md'):
    # read in the README.md file
    with open(name) as f:
        lines = f.readlines()
        for line in lines:
            markdown.append(re.sub(r'^\# (.*)$', r'<h1>\1</h1>',line))
        rmo.writelines(markdown)
        rmo.write("\n")
