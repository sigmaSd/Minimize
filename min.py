#!/bin/python3

import sys
import os
import subprocess
import re
import sys
import semver
from ptyprocess import PtyProcessUnicode

if sys.version_info < (3, 10, 0):
    raise Exception("minimize requires python >= 3.10 version")


def sanitize(s):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', s).replace('"', '')


p = PtyProcessUnicode.spawn(["deno", "run"] + sys.argv[1:])

scan = []
scan.append("#" + sys.argv[1])

deno_version = subprocess.check_output(
    ["deno", "--version"]).decode("utf-8").splitlines()[0]
# consider canary like latest parsing method
is_canary = semver.VersionInfo.parse(deno_version.split()[1]).build != ""
is_gte_1_25_4 = semver.compare(deno_version.split()[1], "1.25.4") >= 0


def parse_line(line):
    if is_canary or is_gte_1_25_4:
        if 'access' in line:
            line_split = line.split()
            mark = line_split.index("access")
            permission_type = sanitize(line_split[mark - 1])
            permission = sanitize(line_split[mark + 2])
            scan.append(permission_type + ' ' + permission)
        if 'Allow?' in line:
            p.write('y\n')
    else:
        if '⚠️ ' in line:
            permission_type = line.split()[4]
            permission = line.split()[7]
            scan.append(permission_type + ' ' + permission)
            p.write('y\n')


try:
    while True:
        try:
            line = p.read()
        except EOFError:
            break

        # if env NO_OUTPUT is set, don't print anything
        if os.getenv("NO_OUTPUT") is None:
            print(line)

        parse_line(line)
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

    def allow_all(self, permission):
        return "all" in permission

    def toDeno(self):
        result = ""
        if self.allow_all(self.read):
            result += "--allow-read "
        elif len(self.read) > 0:
            result += "--allow-read=" + ",".join(self.read) + " "
        if self.allow_all(self.write):
            result += "--allow-write "
        elif len(self.write) > 0:
            result += "--allow-write=" + ",".join(self.write) + " "
        if self.allow_all(self.net):
            result += "--allow-net "
        elif len(self.net) > 0:
            result += "--allow-net=" + ",".join(self.net) + " "
        if self.allow_all(self.run):
            result += "--allow-run "
        elif len(self.run) > 0:
            result += "--allow-run=" + ",".join(self.run) + " "
        if self.allow_all(self.env):
            result += "--allow-env "
        elif len(self.env) > 0:
            result += "--allow-env=" + ",".join(self.env) + " "
        if self.allow_all(self.ffi):
            result += "--allow-ffi "
        elif len(self.ffi) > 0:
            result += "--allow-ffi=" + ",".join(self.ffi) + " "

        return result


def parse(out) -> str:
    permissions = Permission()
    for line in out.split("\n"):
        if not line or line.startswith("#"):
            continue
        permission_type = line.split(" ")[0].strip()
        permission = line.split(" ")[1].strip()
        # remove '.' at the end
        if permission.endswith("."):
            permission = permission[:-1]

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
print("deno run " + parse(out) + argv)
