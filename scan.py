#!/bin/python3

from ptyprocess import PtyProcessUnicode
import sys
p = PtyProcessUnicode.spawn(["deno","run","--unstable"]+ sys.argv[1:])

scan = []
scan.append("#" + sys.argv[1])
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

# write scan.out
with open('scan.out', 'w') as f:
    f.write('\n'.join(scan))
