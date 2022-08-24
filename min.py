#!/bin/python3

from ptyprocess import PtyProcessUnicode
import sys
import os
import subprocess

file = sys.argv[1]

p = PtyProcessUnicode.spawn(["deno", "run", "--unstable", file])

scan = []
scan.append("#" + file)
try:
    while True:
        try:
            line = p.read()
        except EOFError:
            break

        # if env NO_OUTPUT is set, don't print anything
        if os.getenv("NO_OUTPUT") is None:
            print(line)

        if '⚠️ ' in line:
            permission_type = line.split(' ')[4]
            permission = line.split(' ')[7]
            scan.append(permission_type + ' ' + permission)
            p.write('y\n')
except KeyboardInterrupt:
    print("")

with open('/tmp/scan.out', 'w') as f:
    f.write('\n'.join(scan))

######
######
######

# read file
out = open("/tmp/scan.out", "r").read()

"""
Create deno permission flag based on the above output
"""


class Permission:
    read = []
    write = []
    net = []
    run = []
    env = []
    ffi = []

    def toDeno(self):
        result = ""
        if len(self.read) > 0:
            result += "--allow-read=" + ",".join(self.read) + " "
        if len(self.write) > 0:
            result += "--allow-write=" + ",".join(self.write) + " "
        if len(self.net) > 0:
            result += "--allow-net=" + ",".join(self.net) + " "
        if len(self.run) > 0:
            result += "--allow-run=" + ",".join(self.run) + " "
        if len(self.env) > 0:
            result += "--allow-env=" + ",".join(self.env) + " "
        if len(self.ffi) > 0:
            result += "--allow-ffi=" + ",".join(self.ffi) + " "

        return result


def parse(out) -> str:
    permissions = Permission()
    for line in out.split("\n"):
        if not line or line.startswith("#"):
            continue
        permission_type = line.split(" ")[0].strip()
        # remove '.' at the end
        permission = line.split(" ")[1].strip()[:-1]

        # handle builtin permissions
        if permission == '<CWD>':
            permission = permission.replace('<CWD>', '$PWD')
        if permission == '<exec_path>':
            permission = permission.replace('<exec_path>',
                                            subprocess.check_output(['deno', 'eval', 'console.log(Deno.execPath())']).decode("utf-8").strip())
        if permission.startswith('<'):
            permission = permission.replace('<', '\\<').replace('>', '\\>')

        match permission_type:
            case "read":
                if permission not in permissions.read:
                    permissions.read.append(permission)
            case "write":
                if permission not in permissions.write:
                    permissions.write.append(permission)
            case "net":
                if permission not in permissions.net:
                    permissions.net.append(permission)
            case "run":
                if permission not in permissions.run:
                    permissions.run.append(permission)
            case "env":
                if permission not in permissions.env:
                    permissions.env.append(permission)
            case "ffi":
                if permission not in permissions.ffi:
                    permissions.ffi.append(permission)

    return permissions.toDeno()


argv = out.split("\n")[0][1:]
print("deno run --unstable " + parse(out) + argv)
