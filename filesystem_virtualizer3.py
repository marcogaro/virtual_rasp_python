#!/usr/bin/env python3
import os
import sys
import configparser
import re
import subprocess
import shlex

basedir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), '..'))
if (os.path.exists(os.path.join(basedir, 'setup.py')) and
        os.path.exists(os.path.join(basedir, 'src', 'pyfuse3.pyx'))):
    sys.path.insert(0, os.path.join(basedir, 'src'))

import pyfuse3
from argparse import ArgumentParser
import errno
import logging
import stat as stat_m
from pyfuse3 import FUSEError
from os import fsencode, fsdecode
from collections import defaultdict
import trio

import faulthandler

faulthandler.enable()

log = logging.getLogger(__name__)

###########################################################################
export = 0
unexport = 0
direction = 0
value = 0
active = 0
edge = 0
last_path = ''


def set_export_to_one():
    global export  # Needed to modify global copy of globvar
    export = 1

def set_export_to_zero():
    global export  # Needed to modify global copy of globvar
    export = 0

def print_glob_export():
    print(export)  # No need for global declaration to read value of globvar


def set_unexport_to_one():
    global unexport  # Needed to modify global copy of globvar
    unexport = 1

def set_unexport_to_zero():
    global unexport  # Needed to modify global copy of globvar
    unexport = 0

def print_glob_unexport():
    print(unexport)  # No need for global declaration to read value of globvar


def set_direction_to_one():
    global direction  # Needed to modify global copy of globvar
    direction = 1

def set_direction_to_zero():
    global direction  # Needed to modify global copy of globvar
    direction = 0

def print_glob_direction():
    print(direction)  # No need for global declaration to read value of globvar


def set_value_to_one():
    global value  # Needed to modify global copy of globvar
    value = 1

def set_value_to_zero():
    global value  # Needed to modify global copy of globvar
    value = 0

def print_glob_value():
    print(value)  # No need for global declaration to read value of globvar


def set_active_to_one():
    global active  # Needed to modify global copy of globvar
    active = 1

def set_active_to_zero():
    global active  # Needed to modify global copy of globvar
    active = 0

def print_glob_active():
    print(active)  # No need for global declaration to read value of globvar


def set_edge_to_one():
    global edge  # Needed to modify global copy of globvar
    edge = 1

def set_edge_to_zero():
    global edge  # Needed to modify global copy of globvar
    edge = 0

def print_glob_edge():
    print(edge)  # No need for global declaration to read value of globvar


def set_lastpath_to_zero(path):
    global last_path  # Needed to modify global copy of globvar
    last_path = path

def print_glob_lastpath():
    print(last_path)  # No need for global declaration to read value of globvar


#########################


class Operations(pyfuse3.Operations):
    enable_writeback_cache = True

    def __init__(self, source):
        super().__init__()
        self._inode_path_map = {pyfuse3.ROOT_INODE: source}
        self._lookup_cnt = defaultdict(lambda: 0)
        self._fd_inode_map = dict()
        self._inode_fd_map = dict()
        self._fd_open_count = dict()

    def _inode_to_path(self, inode):
        try:
            val = self._inode_path_map[inode]
        except KeyError:
            raise FUSEError(errno.ENOENT)

        if isinstance(val, set):
            # In case of hardlinks, pick any path
            val = next(iter(val))
        return val

    #################################################################################################################

    def _add_path(self, inode, path):
        set_lastpath_to_zero(path)

        if __debug__:
            pass
        else:
            print("\nlast_path: ", last_path, "\n")
            print("\npath: ", path)
            print("la lista di gpio disponibili per istanza è: ", listgpio, "\n")

        if path == '/sys/class/gpio/export':
            set_export_to_one()
            set_unexport_to_zero()

            if inode not in self._inode_path_map:
                self._inode_path_map[inode] = path
                return

            val = self._inode_path_map[inode]

            if isinstance(val, set):
                val.add(path)
            elif val != path:
                self._inode_path_map[inode] = {path, val}


        elif path == '/sys/class/gpio/unexport':
            set_export_to_zero()
            set_unexport_to_one()

            if inode not in self._inode_path_map:
                self._inode_path_map[inode] = path
                return

            val = self._inode_path_map[inode]

            if isinstance(val, set):
                val.add(path)
            elif val != path:
                self._inode_path_map[inode] = {path, val}


        else:
            set_export_to_zero()
            set_unexport_to_zero()
            x = re.search("gpio\d{1,2}", path)

            if __debug__:
                pass
            else:
                print(x)  # this is an object

            if x:
                if __debug__:
                    # print('Debug OFF')
                    pass
                else:
                    print("\npath:", path)
                    print("sì, c'è gpio...")
                    print("il gpio presente nel path è:", x[0])

                gpio = x[0]

#############################################################


                if path.endswith('active_low'):
                    set_active_to_one()

                elif path.endswith('direction'):
                    set_direction_to_one()

                elif path.endswith('edge'):
                    set_edge_to_one()

                elif path.endswith('value'):
                    set_value_to_one()

                else:
                    set_active_to_zero()
                    set_direction_to_zero()
                    set_edge_to_zero()
                    set_value_to_zero()

#################################################








                # controlli
                if gpio in listgpio:
                    if inode not in self._inode_path_map:
                        self._inode_path_map[inode] = path
                        return

                    val = self._inode_path_map[inode]
                    if isinstance(val, set):
                        val.add(path)
                    elif val != path:
                        self._inode_path_map[inode] = {path, val}

                else:
                    if __debug__:
                        pass
                    else:
                        print("gpio non in lista, non copio")
                    pass


            else:
                if __debug__:
                    pass
                else:
                    print("\npath:", path)
                    print("No match\n")

                # copio tutto
                if inode not in self._inode_path_map:
                    self._inode_path_map[inode] = path
                    return

                val = self._inode_path_map[inode]

                if isinstance(val, set):
                    val.add(path)
                elif val != path:
                    self._inode_path_map[inode] = {path, val}

    async def forget(self, inode_list):
        for (inode, nlookup) in inode_list:
            if self._lookup_cnt[inode] > nlookup:
                self._lookup_cnt[inode] -= nlookup
                continue
            log.debug('forgetting about inode %d', inode)
            assert inode not in self._inode_fd_map
            del self._lookup_cnt[inode]
            try:
                del self._inode_path_map[inode]
            except KeyError:  # may have been deleted
                pass

    async def lookup(self, inode_p, name, ctx=None):
        name = fsdecode(name)
        log.debug('lookup for %s in %d', name, inode_p)
        path = os.path.join(self._inode_to_path(inode_p), name)
        attr = self._getattr(path=path)
        if name != '.' and name != '..':
            self._add_path(attr.st_ino, path)
        return attr

    async def getattr(self, inode, ctx=None):
        if inode in self._inode_fd_map:
            return self._getattr(fd=self._inode_fd_map[inode])
        else:
            return self._getattr(path=self._inode_to_path(inode))

    def _getattr(self, path=None, fd=None):
        assert fd is None or path is None
        assert not (fd is None and path is None)
        try:
            if fd is None:
                stat = os.lstat(path)
            else:
                stat = os.fstat(fd)
        except OSError as exc:
            raise FUSEError(exc.errno)

        entry = pyfuse3.EntryAttributes()
        for attr in ('st_ino', 'st_mode', 'st_nlink', 'st_uid', 'st_gid',
                     'st_rdev', 'st_size', 'st_atime_ns', 'st_mtime_ns',
                     'st_ctime_ns'):
            setattr(entry, attr, getattr(stat, attr))
        entry.generation = 0
        entry.entry_timeout = 0
        entry.attr_timeout = 0
        entry.st_blksize = 512
        entry.st_blocks = ((entry.st_size + entry.st_blksize - 1) // entry.st_blksize)

        return entry

    async def readlink(self, inode, ctx):
        path = self._inode_to_path(inode)
        try:
            target = os.readlink(path)
        except OSError as exc:
            raise FUSEError(exc.errno)
        return fsencode(target)

    async def opendir(self, inode, ctx):
        return inode

    async def readdir(self, inode, off, token):
        path = self._inode_to_path(inode)
        log.debug('reading %s', path)
        entries = []
        for name in os.listdir(path):
            if name == '.' or name == '..':
                continue
            attr = self._getattr(path=os.path.join(path, name))
            entries.append((attr.st_ino, name, attr))

        log.debug('read %d entries, starting at %d', len(entries), off)

        # This is not fully posix compatible. If there are hardlinks
        # (two names with the same inode), we don't have a unique
        # offset to start in between them. Note that we cannot simply
        # count entries, because then we would skip over entries
        # (or return them more than once) if the number of directory
        # entries changes between two calls to readdir().
        for (ino, name, attr) in sorted(entries):
            if ino <= off:
                continue
            if not pyfuse3.readdir_reply(
                    token, fsencode(name), attr, ino):
                break
            self._add_path(attr.st_ino, os.path.join(path, name))

    async def unlink(self, inode_p, name, ctx):
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("\nunlink\n\n")

        name = fsdecode(name)
        parent = self._inode_to_path(inode_p)
        path = os.path.join(parent, name)
        try:
            inode = os.lstat(path).st_ino
            os.unlink(path)
        except OSError as exc:
            raise FUSEError(exc.errno)
        if inode in self._lookup_cnt:
            self._forget_path(inode, path)

    async def rmdir(self, inode_p, name, ctx):
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("\nrmdir\n\n")

        name = fsdecode(name)
        parent = self._inode_to_path(inode_p)
        path = os.path.join(parent, name)
        try:
            inode = os.lstat(path).st_ino
            os.rmdir(path)
        except OSError as exc:
            raise FUSEError(exc.errno)
        if inode in self._lookup_cnt:
            self._forget_path(inode, path)

    def _forget_path(self, inode, path):
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("\nforgetpath\n")

        log.debug('forget %s for %d', path, inode)
        val = self._inode_path_map[inode]
        if isinstance(val, set):
            val.remove(path)
            if len(val) == 1:
                self._inode_path_map[inode] = next(iter(val))
        else:
            del self._inode_path_map[inode]

    async def symlink(self, inode_p, name, target, ctx):
        name = fsdecode(name)
        target = fsdecode(target)
        parent = self._inode_to_path(inode_p)
        path = os.path.join(parent, name)
        try:
            os.symlink(target, path)
            os.chown(path, ctx.uid, ctx.gid, follow_symlinks=False)
        except OSError as exc:
            raise FUSEError(exc.errno)
        stat = os.lstat(path)
        self._add_path(stat.st_ino, path)
        return await self.getattr(stat.st_ino)

    async def rename(self, inode_p_old, name_old, inode_p_new, name_new,
                     flags, ctx):
        if flags != 0:
            raise FUSEError(errno.EINVAL)

        name_old = fsdecode(name_old)
        name_new = fsdecode(name_new)
        parent_old = self._inode_to_path(inode_p_old)
        parent_new = self._inode_to_path(inode_p_new)
        path_old = os.path.join(parent_old, name_old)
        path_new = os.path.join(parent_new, name_new)
        try:
            os.rename(path_old, path_new)
            inode = os.lstat(path_new).st_ino
        except OSError as exc:
            raise FUSEError(exc.errno)
        if inode not in self._lookup_cnt:
            return

        val = self._inode_path_map[inode]
        if isinstance(val, set):
            assert len(val) > 1
            val.add(path_new)
            val.remove(path_old)
        else:
            assert val == path_old
            self._inode_path_map[inode] = path_new

    async def link(self, inode, new_inode_p, new_name, ctx):
        new_name = fsdecode(new_name)
        parent = self._inode_to_path(new_inode_p)
        path = os.path.join(parent, new_name)
        try:
            os.link(self._inode_to_path(inode), path, follow_symlinks=False)
        except OSError as exc:
            raise FUSEError(exc.errno)
        self._add_path(inode, path)
        return await self.getattr(inode)

    async def setattr(self, inode, attr, fields, fh, ctx):
        # We use the f* functions if possible so that we can handle
        # a setattr() call for an inode without associated directory
        # handle.
        if fh is None:
            path_or_fh = self._inode_to_path(inode)
            truncate = os.truncate
            chmod = os.chmod
            chown = os.chown
            stat = os.lstat
        else:
            path_or_fh = fh
            truncate = os.ftruncate
            chmod = os.fchmod
            chown = os.fchown
            stat = os.fstat

        try:
            if fields.update_size:
                truncate(path_or_fh, attr.st_size)

            if fields.update_mode:
                # Under Linux, chmod always resolves symlinks so we should
                # actually never get a setattr() request for a symbolic
                # link.
                assert not stat_m.S_ISLNK(attr.st_mode)
                chmod(path_or_fh, stat_m.S_IMODE(attr.st_mode))

            if fields.update_uid:
                chown(path_or_fh, attr.st_uid, -1, follow_symlinks=False)

            if fields.update_gid:
                chown(path_or_fh, -1, attr.st_gid, follow_symlinks=False)

            if fields.update_atime and fields.update_mtime:
                if fh is None:
                    os.utime(path_or_fh, None, follow_symlinks=False,
                             ns=(attr.st_atime_ns, attr.st_mtime_ns))
                else:
                    os.utime(path_or_fh, None,
                             ns=(attr.st_atime_ns, attr.st_mtime_ns))
            elif fields.update_atime or fields.update_mtime:
                # We can only set both values, so we first need to retrieve the
                # one that we shouldn't be changing.
                oldstat = stat(path_or_fh)
                if not fields.update_atime:
                    attr.st_atime_ns = oldstat.st_atime_ns
                else:
                    attr.st_mtime_ns = oldstat.st_mtime_ns
                if fh is None:
                    os.utime(path_or_fh, None, follow_symlinks=False,
                             ns=(attr.st_atime_ns, attr.st_mtime_ns))
                else:
                    os.utime(path_or_fh, None,
                             ns=(attr.st_atime_ns, attr.st_mtime_ns))

        except OSError as exc:
            raise FUSEError(exc.errno)

        return await self.getattr(inode)

    async def mknod(self, inode_p, name, mode, rdev, ctx):
        path = os.path.join(self._inode_to_path(inode_p), fsdecode(name))
        try:
            os.mknod(path, mode=(mode & ~ctx.umask), device=rdev)
            os.chown(path, ctx.uid, ctx.gid)
        except OSError as exc:
            raise FUSEError(exc.errno)
        attr = self._getattr(path=path)
        self._add_path(attr.st_ino, path)
        return attr

    ##########################################################################################################################################

    async def mkdir(self, inode_p, name, mode, ctx):
        path = os.path.join(self._inode_to_path(inode_p), fsdecode(name))
        try:
            os.mkdir(path, mode=(mode & ~ctx.umask))
            os.chown(path, ctx.uid, ctx.gid)
        except OSError as exc:
            raise FUSEError(exc.errno)
        attr = self._getattr(path=path)
        self._add_path(attr.st_ino, path)
        return attr

    async def statfs(self, ctx):
        root = self._inode_path_map[pyfuse3.ROOT_INODE]
        stat_ = pyfuse3.StatvfsData()
        try:
            statfs = os.statvfs(root)
        except OSError as exc:
            raise FUSEError(exc.errno)
        for attr in ('f_bsize', 'f_frsize', 'f_blocks', 'f_bfree', 'f_bavail',
                     'f_files', 'f_ffree', 'f_favail'):
            setattr(stat_, attr, getattr(statfs, attr))
        stat_.f_namemax = statfs.f_namemax - (len(root) + 1)
        return stat_

    async def open(self, inode, flags, ctx):
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("open")

        if inode in self._inode_fd_map:
            fd = self._inode_fd_map[inode]
            if __debug__:
                # print('Debug OFF')
                pass
            else:
                print('Debug ON')
                print("fd:", fd)

            self._fd_open_count[fd] += 1
            return pyfuse3.FileInfo(fh=fd)
        assert flags & os.O_CREAT == 0
        try:
            fd = os.open(self._inode_to_path(inode), flags)
            if __debug__:
                # print('Debug OFF')
                pass
            else:
                print('Debug ON')
                print("fd2:", fd)
        except OSError as exc:
            raise FUSEError(exc.errno)
        self._inode_fd_map[inode] = fd
        self._fd_inode_map[fd] = inode
        self._fd_open_count[fd] = 1
        return pyfuse3.FileInfo(fh=fd)

    async def create(self, inode_p, name, mode, flags, ctx):
        path = os.path.join(self._inode_to_path(inode_p), fsdecode(name))
        try:
            fd = os.open(path, flags | os.O_CREAT | os.O_TRUNC)
        except OSError as exc:
            raise FUSEError(exc.errno)
        attr = self._getattr(fd=fd)
        self._add_path(attr.st_ino, path)
        self._inode_fd_map[attr.st_ino] = fd
        self._fd_inode_map[fd] = attr.st_ino
        self._fd_open_count[fd] = 1
        return (pyfuse3.FileInfo(fh=fd), attr)

    async def read(self, fd, offset, length):
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("leggo", fd, length)
        os.lseek(fd, offset, os.SEEK_SET)
        return os.read(fd, length)

    ##########################################################################################

    async def write(self, fd, offset, buf):
        gpiobyte = buf.decode()

        print("export: ", export, "\nunexport: ", unexport, "\ndirection: ", direction, "\nvalue: ", value,
              "\nactivelow: ", active, "\nedge: ", edge)



        if __debug__:
            pass
        else:
            print("buf: ", buf, "gpiobyte: ", gpiobyte)
            print("self: ", self, "offset: ", offset)
            print("export: ", export, "\nunexport: ", unexport, "\ndirection: ", direction, "\nvalue: ", value,
                  "\nactivelow: ", active, "\nedge: ", edge)

        if export == 1 and unexport == 0:
            gpioint = int(gpiobyte)

            if __debug__:
                pass
            else:
                print("1export")
                print("write\n buf: ", buf, "fd: ", fd)
                print("numerogpiobyte: ", gpiobyte)
                print("numerogpiointero: ", gpioint)

            gpio = str(gpioint)
            listgpio = listgpio2

            if __debug__:
                pass
            else:
                print("la lista di gpio disponibili per test2 è: ", listgpio, "\n")
                print(os.path.exists('/sys/class/gpio/gpio' + gpio + '/'))

            if gpioint in listgpio and not os.path.exists('/sys/class/gpio/gpio' + gpio + '/'):
                os.lseek(fd, offset, os.SEEK_SET)
                return os.write(fd, buf)
            else:
                print("\n-bash: echo: write error: Device or resource busy")
                if __debug__:
                    pass
                else:
                    print("error Device or resource busy ")

            os.lseek(fd, offset, os.SEEK_SET)
            return 1


        elif export == 0 and unexport == 1:
            gpioint = int(gpiobyte)

            if __debug__:
                pass
            else:
                print("1unexport")
                print("write\n buf: ", buf, "fd: ", fd)
                print("numerogpiobyte: ", gpiobyte)
                print("numerogpiointero: ", gpioint)

            gpio = str(gpioint)
            listgpio = listgpio2

            if __debug__:
                pass
            else:
                print("la lista di gpio disponibili per" + nomecontainer + "  è: ", listgpio, "\n")
                print('/sys/class/gpio/gpio' + gpio + '/')
                print(os.path.exists('/sys/class/gpio/gpio' + gpio + '/'))

            if gpioint in listgpio and os.path.exists('/sys/class/gpio/gpio' + gpio + '/'):
                os.lseek(fd, offset, os.SEEK_SET)
                return os.write(fd, buf)
            else:
                print("\n-bash: echo: write error: Invalid argument")
                if __debug__:
                    pass
                else:
                    print("errore gpio non in lista")
                os.lseek(fd, offset, os.SEEK_SET)
                return 1


        else:
            if __debug__:
                pass
            else:
                print("buff:", buf)
                print("gpiobyte: ", gpiobyte)
                print("buf decodificato:", gpiobyte)

            gpiobyte = gpiobyte.strip('\n')

            if __debug__:
                pass
            else:
                print("buf decodificato senzsa\\n:", gpiobyte)

            if direction == 1:
                if __debug__:
                    pass
                else:
                    print("caso direction:")

                pathmod = os.path.relpath(last_path, '/sys/devices/platform/soc/3f200000.gpio/gpiochip0/gpio/')
                basename = os.path.basename(last_path)
                basename = '/' + basename

                if __debug__:
                    pass
                else:
                    print("\npathmod:", pathmod, "basename:", basename, "\n")

                gpio = os.path.dirname(pathmod)
                if __debug__:
                    pass
                else:
                    print("gpio:", gpio)

                valoredirezioneprima = os.popen('cat /sys/class/gpio/' + gpio + '/direction').read()
                valoredirezioneprima = valoredirezioneprima.strip('\n')

                if __debug__:
                    pass
                else:
                    print("valore direzione", valoredirezioneprima)

                stringa = '\n'

                if __debug__:
                    pass
                else:
                    print("il valore direzione prima di essere aggiornato è: ", valoredirezioneprima,
                          'b\'' + valoredirezioneprima + stringa)

                valoredirezioneprimabyte = valoredirezioneprima + stringa
                valoredirezioneprimabyte = valoredirezioneprima.encode()

                if __debug__:
                    pass
                else:
                    print("valoredirezioneprimabyte: ", valoredirezioneprimabyte)
                    print("buff:", buf, "fd:", fd)

                if gpiobyte == 'in' or gpiobyte == 'out':
                    if __debug__:
                        pass
                    else:
                        print("ok1")

                    os.lseek(fd, offset, os.SEEK_SET)
                    return os.write(fd, buf)
                else:
                    print("\n-bash: echo: write error: Invalid argument")
                    if __debug__:
                        pass
                    else:
                        print("errore carattere")

                    proc = subprocess.Popen(
                        'echo ' + valoredirezioneprima + ' > /gpio_mnt/' + nomecontainer + '/sys/class/gpio/' + gpio + '/direction',
                        shell=True, stdout=subprocess.PIPE)

                    os.lseek(fd, offset, os.SEEK_SET)
                    return 1



            elif value == 1:
                pathmod = os.path.relpath(last_path, '/sys/devices/platform/soc/3f200000.gpio/gpiochip0/gpio/')
                basename = os.path.basename(last_path)
                basename = '/' + basename
                gpio = os.path.dirname(pathmod)

                valueprecedente = os.popen('cat /sys/class/gpio/' + gpio + '/value').read()
                valueprecedente = valueprecedente.strip('\n')

                if __debug__:
                    pass
                else:
                    print("\npathmod:", pathmod, "basename:", basename, "\n\n\n")
                    print("gpio:", gpio)
                    print("value precedente: ", valueprecedente)

                valoredirezione = os.popen('cat /sys/class/gpio/' + gpio + '/direction').read()
                valoredirezione = valoredirezione.strip('\n')

                if valoredirezione == 'out':
                    if gpiobyte == '1' or gpiobyte == '0':
                        gpioint = int(gpiobyte)
                        if __debug__:
                            pass
                        else:
                            print("caso value:")
                            print("valore direzione: ", valoredirezione)

                        os.lseek(fd, offset, os.SEEK_SET)
                        return os.write(fd, buf)

                    else:
                        print("\n-bash: echo: write error: Invalid argument1")
                        if __debug__:
                            pass
                        else:
                            print("errore carattere")

                        proc2 = subprocess.Popen(
                            'echo ' + valueprecedente + ' > /gpio_mnt/' + nomecontainer + '/sys/class/gpio/' + gpio + '/value',
                            shell=True, stdout=subprocess.PIPE)

                        os.lseek(fd, offset, os.SEEK_SET)
                        return 1

                else:
                    # command = 'echo 1 > /gpio_mnt/test1/sys/class/gpio/gpio1/value'
                    print("\n-bash: echo: write error: Invalid argument2")
                    if __debug__:
                        pass
                    else:
                        print("errore carattere")

                    os.lseek(fd, offset, os.SEEK_SET)
                    return 1


            elif active == 1:
                if __debug__:
                    pass
                else:
                    print("caso active:")

                pathmod = os.path.relpath(last_path, '/sys/devices/platform/soc/3f200000.gpio/gpiochip0/gpio/')
                basename = os.path.basename(last_path)
                basename = '/' + basename
                gpio = os.path.dirname(pathmod)

                activeprecedente = os.popen('cat /sys/class/gpio/' + gpio + '/active_low').read()
                activeprecedente = activeprecedente.strip('\n')

                if __debug__:
                    pass
                else:
                    print("\npathmod:", pathmod, "basename:", basename, "\n")
                    print("\ngpio:", gpio)
                    print("active precedente: ", activeprecedente)

                if gpiobyte == '0' or gpiobyte == '1':
                    os.lseek(fd, offset, os.SEEK_SET)
                    return os.write(fd, buf)
                else:
                    print("\n-bash: echo: write error: Invalid argument")
                    if __debug__:
                        pass
                    else:
                        print("errore carattere")

                    proc2 = subprocess.Popen(
                        'echo ' + activeprecedente + ' > /gpio_mnt/' + nomecontainer + '/sys/class/gpio/' + gpio + '/active_low',
                        shell=True, stdout=subprocess.PIPE)

                    os.lseek(fd, offset, os.SEEK_SET)
                    return 1


            elif edge == 1:
                pathmod = os.path.relpath(last_path, '/sys/devices/platform/soc/3f200000.gpio/gpiochip0/gpio/')
                basename = os.path.basename(last_path)
                basename = '/' + basename

                gpio = os.path.dirname(pathmod)

                edgeprecedente = os.popen('cat /sys/class/gpio/' + gpio + '/edge').read()
                edgeprecedente = edgeprecedente.strip('\n')

                if gpiobyte == 'falling' or gpiobyte == 'rising' or gpiobyte == 'none':
                    os.lseek(fd, offset, os.SEEK_SET)
                    return os.write(fd, buf)
                else:
                    print("-bash: echo: write error: Invalid argument")
                    proc4 = subprocess.Popen(
                        'echo ' + edgeprecedente + ' > /gpio_mnt/' + nomecontainer + '/sys/class/gpio/' + gpio + '/edge',
                        shell=True, stdout=subprocess.PIPE)

                    os.lseek(fd, offset, os.SEEK_SET)
                    return 1


            else:
                if __debug__:
                    pass
                else:
                    print("errore2")
                os.lseek(fd, offset, os.SEEK_SET)
                return 1

    ##############################################################################################

    async def release(self, fd):
        if self._fd_open_count[fd] > 1:
            self._fd_open_count[fd] -= 1
            return

        del self._fd_open_count[fd]
        inode = self._fd_inode_map[fd]
        del self._inode_fd_map[inode]
        del self._fd_inode_map[fd]
        try:
            os.close(fd)
        except OSError as exc:
            raise FUSEError(exc.errno)


def init_logging(debug=False):
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(threadName)s: '
                                  '[%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if debug:
        handler.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


def parse_args(args):
    '''Parse command line'''

    parser = ArgumentParser()

    parser.add_argument('source', type=str,
                        help='Directory tree to mirror')
    parser.add_argument('mountpoint', type=str,
                        help='Where to mount the file system')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debugging output')
    parser.add_argument('--debug-fuse', action='store_true', default=False,
                        help='Enable FUSE debugging output')

    # parser.add_argument('nomecontainer', type=str,
    # help='nomecontainer')

    return parser.parse_args(args)


def main():
    options = parse_args(sys.argv[1:3])
    init_logging(options.debug)
    operations = Operations(options.source)

    log.debug('Mounting...')
    fuse_options = set(pyfuse3.default_options)
    fuse_options.add('fsname=passthroughfs')

    fuse_options.add('allow_other')

    if options.debug_fuse:
        fuse_options.add('debug')

    fuse_options.discard('default_permissions')
    pyfuse3.init(operations, options.mountpoint, fuse_options)

    try:
        log.debug('Entering main loop..')
        trio.run(pyfuse3.main)
    except:
        pyfuse3.close(unmount=False)
        raise

    log.debug('Unmounting..')
    pyfuse3.close()


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.sections()
    config.read('virtual_rasp.ini')
    config.sections()

    nomeconfigparser = 0

    if __debug__:
        # print('Debug OFF')
        pass
    else:
        print('Debug ON')
        print('Number of arguments:', len(sys.argv), 'arguments.')
        print('Argument List:', str(sys.argv))

    nomecontainer = sys.argv[3]
    if __debug__:
        # print('Debug OFF')
        pass
    else:
        print('Debug ON')
        print("nome container: ", nomecontainer)

    # listgpio = ["gpiochip0", "gpiochip504", "export"]
    listgpio = ["gpiochip0", "gpiochip504", "export", "unexport"]

    if nomecontainer in config.sections():
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("nome container presente nel file di configurazione")

        nomeconfigparser = 1
    else:
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("nome container non presente nel file di configurazione\n\n\n")

        nomeconfigparser = 0

    # listgpio = ["gpiochip0", "gpiochip504", "export", "unexport"]
    listgpio2 = []

    if nomeconfigparser == 1:
        for count in range(0, 28):
            # print(count, "gpio" + str(count))
            # print(config[nomecontainer]['gpio' + str(count)])
            if config[nomecontainer]['gpio' + str(count)] == 'yes':
                # print(count, "gpio" + str(count), "ok")
                listgpio.append("gpio" + str(count))

            if config[nomecontainer]['gpio' + str(count)] == 'yes':
                # print(count, "gpio" + str(count), "ok")
                listgpio2.append(count)


    else:
        if __debug__:
            # print('Debug OFF')
            pass
        else:
            print('Debug ON')
            print("il nome del container non è all'interno del file di configurazione")



    set_export_to_zero()
    set_unexport_to_zero()
    set_direction_to_zero()
    set_value_to_zero()
    set_active_to_zero()
    set_edge_to_zero()
    set_lastpath_to_zero('')



    main()
