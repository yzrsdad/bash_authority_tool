from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os, sys

if sys.version_info > (3, 0):
    from six.moves import xrange

regularOperations = {
    "ssh": {"superuser": False, "read": True, "write": False, "execute": True},
    "cd": {"superuser": False, "read": True, "write": False, "execute": False},
    "scp": {"superuser": False, "read": True, "write": False, "execute": True},
    "rsync": {"superuser": False, "read": True, "write": False, "execute": True},
    "exit": {"superuser": False, "read": False, "write": False, "execute": True},
    "shopt": {"superuser": False, "read": False, "write": False, "execute": True},
    "find": {"superuser": False, "read": True, "write": False, "execute": False},
    "wc": {"superuser": False, "read": True, "write": False, "execute": False},
    "sort": {"superuser": False, "read": True, "write": False, "execute": False},
    "readlink": {"superuser": False, "read": True, "write": False, "execute": False},
    "cat": {"superuser": False, "read": True, "write": False, "execute": False},
    "tac": {"superuser": False, "read": True, "write": False, "execute": False},
    "head": {"superuser": False, "read": True, "write": False, "execute": False},
    "tail": {"superuser": False, "read": True, "write": False, "execute": False},
    "less": {"superuser": False, "read": True, "write": False, "execute": False},
    "zless": {"superuser": False, "read": True, "write": False, "execute": False},
    "more": {"superuser": False, "read": True, "write": False, "execute": False},
    "grep": {"superuser": False, "read": True, "write": False, "execute": False},
    "egrep": {"superuser": False, "read": True, "write": False, "execute": False},
    "fgrep": {"superuser": False, "read": True, "write": False, "execute": False},
    "sed": {"superuser": False, "read": True, "write": False, "execute": False},
    "cut": {"superuser": False, "read": True, "write": False, "execute": False},
    "paste": {"superuser": False, "read": True, "write": False, "execute": False},
    "locate": {"superuser": False, "read": True, "write": False, "execute": False},
    "vim": {"superuser": False, "read": True, "write": True, "execute": True}
}

dangerousOperations = {
    "chmod": {"superuser": False, "read": False, "write": True, "execute": False},
    "chown": {"superuser": True, "read": False, "write": False, "execute": True},
    "sudo": {"superuser": True, "read": False, "write": False, "execute": True},
    "su": {"superuser": True, "read": False, "write": False, "execute": True},
    "kill": {"superuser": False, "read": False, "write": False, "execute": True},
    "bg": {"superuser": False, "read": False, "write": False, "execute": True},
    "fg": {"superuser": False, "read": False, "write": False, "execute": True},
    "apt-get": {"superuser": True, "read": False, "write": False, "execute": True},
    "brew": {"superuser": False, "read": False, "write": False, "execute": True},
    "yum": {"superuser": True, "read": False, "write": False, "execute": True},
    "mount": {"superuser": True, "read": False, "write": False, "execute": True},
    "umount": {"superuser": True, "read": False, "write": False, "execute": True},
    "ifconfig": {"superuser": True, "read": False, "write": False, "execute": True},
    "chgrp": {"superuser": False, "read": False, "write": True, "execute": False},
    "rm": {"superuser": False, "read": False, "write": True, "execute": False},
    "mv": {"superuser": False, "read": False, "write": True, "execute": False},
    "cp": {"superuser": False, "read": True, "write": True, "execute": False},
    "shred": {"superuser": False, "read": False, "write": True, "execute": False},
    "setfacl": {"superuser": False, "read": True, "write": True, "execute": False},
    "getfacl": {"superuser": False, "read": True, "write": False, "execute": False},
    "tar": {"superuser": False, "read": True, "write": True, "execute": False},
    "ln": {"superuser": False, "read": False, "write": True, "execute": False},
    "mkdir": {"superuser": False, "read": False, "write": True, "execute": False},
    "rename": {"superuser": False, "read": False, "write": True, "execute": False},
    "touch": {"superuser": False, "read": False, "write": True, "execute": False},
    "gzip": {"superuser": False, "read": True, "write": True, "execute": False},
    "gunzip": {"superuser": False, "read": True, "write": True, "execute": False}
}


class AuthorityTable:
    def __init__(self):
        self.table = {}

    def add_entry(self, argument, is_dangerous, superuser, read, write, execute,own):
        self.table[argument] = {
            "is_dangerous": is_dangerous,
            "superuser": superuser,
            "read": read,
            "write": write,
            "execute": execute,
            "own": own
        }

    def remove_entry(self, argument):
        if argument in self.table:
            del self.table[argument]

    def get_entry(self, argument):
        return self.table.get(argument, None)

    def check_permissions(self, argument, permission):
        entry = self.get_entry(argument)
        if entry:
            return entry.get(permission, False)
        return False

    def is_dangerous(self, argument):
        entry = self.get_entry(argument)
        if entry:
            return entry.get("is_dangerous", False)
        return False

    def print_table(self):
        print(
            f"{'Argument':<15} {'Dangerous':<10} {'Superuser':<10} {'Read':<5} {'Write':<5} {'Execute':<7} {'Own':<5}")
        print("=" * 80)
        for argument, details in self.table.items():
            print(
                f"{argument:<15} {str(details['is_dangerous']):<10} {str(details['superuser']):<10} {str(details['read']):<5} {str(details['write']):<5} {str(details['execute']):<7} {str(details['own']):<5}")

    def load_from_json(self, user_data):
        # 从JSON加载数据并添加到权限表
        superuser_global = user_data.get("superuser", False)
        table = user_data.get("table", {})

        for argument, permissions in table.items():
            self.add_entry(
                argument.strip('"'),
                False,
                superuser_global,
                permissions.get("read", False),
                permissions.get("write", False),
                permissions.get("execute", False),
                permissions.get("own", False)
            )
