#!/usr/bin/python3

import os
import hashlib

rand = os.urandom(20)
sha = hashlib.sha256()
sha.update(rand)
trimmed_digest = sha.digest()[:20]

with open("/home/flag.txt", "wb") as f:
    f.write(rand + trimmed_digest)
