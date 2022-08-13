#!/bin/python3

from ptyprocess import PtyProcessUnicode
import sys
import os

file = sys.argv[1]
# change cwd to file cwd
cwd = file.rsplit('/', 1)[0]
os.chdir(cwd)

p = PtyProcessUnicode.spawn(["deno", "run", "--unstable", file])

scan = []
scan.append("#" + file)
try:
    while True:
        try:
            line = p.read()
        except EOFError:
            break

        print(line)

        if '⚠️ ' in line:
            permission_type = line.split(' ')[4]
            permission = line.split(' ')[7]
            scan.append(permission_type + ' ' + permission)
            p.write('y\n')
except KeyboardInterrupt:
    pass

# write scan.out
with open('scan.out', 'w') as f:
    f.write('\n'.join(scan))
