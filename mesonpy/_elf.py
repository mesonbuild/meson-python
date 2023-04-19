# SPDX-FileCopyrightText: 2013-2016 The Meson development team
# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import typing


# if typing.TYPE_CHECKING:  # pragma: no cover
#     from typing import Optional

#     from mesonpy._compat import Collection, Path


import functools
import sys
import os
import stat
import struct
import shutil
import subprocess
import typing as T

def generate_list(func: T.Callable[..., T.Generator[_T, None, None]]) -> T.Callable[..., T.List[_T]]:
    @functools.wraps(func)
    def wrapper(*args: T.Any, **kwargs: T.Any) -> T.List[_T]:
        return list(func(*args, **kwargs))
    return wrapper


SHT_STRTAB = 3
DT_NEEDED = 1
DT_RPATH = 15
DT_RUNPATH = 29
DT_STRTAB = 5
DT_SONAME = 14
DT_MIPS_RLD_MAP_REL = 1879048245


class DataSizes:
    def __init__(self, ptrsize: int, is_le: bool) -> None:
        if is_le:
            p = '<'
        else:
            p = '>'
        self.Half = p + 'h'
        self.HalfSize = 2
        self.Word = p + 'I'
        self.WordSize = 4
        self.Sword = p + 'i'
        self.SwordSize = 4
        if ptrsize == 64:
            self.Addr = p + 'Q'
            self.AddrSize = 8
            self.Off = p + 'Q'
            self.OffSize = 8
            self.XWord = p + 'Q'
            self.XWordSize = 8
            self.Sxword = p + 'q'
            self.SxwordSize = 8
        else:
            self.Addr = p + 'I'
            self.AddrSize = 4
            self.Off = p + 'I'
            self.OffSize = 4


class DynamicEntry(DataSizes):
    def __init__(self, ifile: T.BinaryIO, ptrsize: int, is_le: bool) -> None:
        super().__init__(ptrsize, is_le)
        self.ptrsize = ptrsize
        if ptrsize == 64:
            self.d_tag = struct.unpack(self.Sxword, ifile.read(self.SxwordSize))[0]
            self.val = struct.unpack(self.XWord, ifile.read(self.XWordSize))[0]
        else:
            self.d_tag = struct.unpack(self.Sword, ifile.read(self.SwordSize))[0]
            self.val = struct.unpack(self.Word, ifile.read(self.WordSize))[0]

    def write(self, ofile: T.BinaryIO) -> None:
        if self.ptrsize == 64:
            ofile.write(struct.pack(self.Sxword, self.d_tag))
            ofile.write(struct.pack(self.XWord, self.val))
        else:
            ofile.write(struct.pack(self.Sword, self.d_tag))
            ofile.write(struct.pack(self.Word, self.val))


class SectionHeader(DataSizes):
    def __init__(self, ifile: T.BinaryIO, ptrsize: int, is_le: bool) -> None:
        super().__init__(ptrsize, is_le)
        is_64 = ptrsize == 64

        # Elf64_Word
        self.sh_name = struct.unpack(self.Word, ifile.read(self.WordSize))[0]
        # Elf64_Word
        self.sh_type = struct.unpack(self.Word, ifile.read(self.WordSize))[0]
        # Elf64_Xword
        if is_64:
            self.sh_flags = struct.unpack(self.XWord, ifile.read(self.XWordSize))[0]
        else:
            self.sh_flags = struct.unpack(self.Word, ifile.read(self.WordSize))[0]
        # Elf64_Addr
        self.sh_addr = struct.unpack(self.Addr, ifile.read(self.AddrSize))[0]
        # Elf64_Off
        self.sh_offset = struct.unpack(self.Off, ifile.read(self.OffSize))[0]
        # Elf64_Xword
        if is_64:
            self.sh_size = struct.unpack(self.XWord, ifile.read(self.XWordSize))[0]
        else:
            self.sh_size = struct.unpack(self.Word, ifile.read(self.WordSize))[0]
        # Elf64_Word
        self.sh_link = struct.unpack(self.Word, ifile.read(self.WordSize))[0]
        # Elf64_Word
        self.sh_info = struct.unpack(self.Word, ifile.read(self.WordSize))[0]
        # Elf64_Xword
        if is_64:
            self.sh_addralign = struct.unpack(self.XWord, ifile.read(self.XWordSize))[0]
        else:
            self.sh_addralign = struct.unpack(self.Word, ifile.read(self.WordSize))[0]
        # Elf64_Xword
        if is_64:
            self.sh_entsize = struct.unpack(self.XWord, ifile.read(self.XWordSize))[0]
        else:
            self.sh_entsize = struct.unpack(self.Word, ifile.read(self.WordSize))[0]


class ELF(DataSizes):
    def __init__(self, bfile: str, verbose: bool = True) -> None:
        self.bfile = bfile
        self.verbose = verbose
        self.sections = []  # type: T.List[SectionHeader]
        self.dynamic = []   # type: T.List[DynamicEntry]
        self.bf = open(bfile, 'r+b')
        self.ptrsize, self.is_le = self.detect_elf_type()
        super().__init__(self.ptrsize, self.is_le)
        self.parse_header()
        self.parse_sections()
        self.parse_dynamic()

    def __enter__(self) -> ELF:
        return self

    def __del__(self) -> None:
        self.bf.close()

    def __exit__(self, exc_type: T.Any, exc_value: T.Any, traceback: T.Any) -> None:
        self.bf.close()

    def detect_elf_type(self) -> T.Tuple[int, bool]:
        self.bf.seek(0)
        data = self.bf.read(6)
        if data[1:4] != b'ELF':
            # This script gets called to non-elf targets too
            # so just ignore them.
            raise ValueError(f'File {self.bfile!r} is not an ELF file')
        if data[4] == 1:
            ptrsize = 32
        elif data[4] == 2:
            ptrsize = 64
        else:
            raise ValueError(f'File {self.bfile!r} has unknown ELF class')
        if data[5] == 1:
            is_le = True
        elif data[5] == 2:
            is_le = False
        else:
            raise ValueError(f'File {self.bfile!r} has unknown ELF endianness')
        return ptrsize, is_le

    def parse_header(self) -> None:
        self.bf.seek(0)
        self.e_ident = struct.unpack('16s', self.bf.read(16))[0]
        self.e_type = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]
        self.e_machine = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]
        self.e_version = struct.unpack(self.Word, self.bf.read(self.WordSize))[0]
        self.e_entry = struct.unpack(self.Addr, self.bf.read(self.AddrSize))[0]
        self.e_phoff = struct.unpack(self.Off, self.bf.read(self.OffSize))[0]
        self.e_shoff = struct.unpack(self.Off, self.bf.read(self.OffSize))[0]
        self.e_flags = struct.unpack(self.Word, self.bf.read(self.WordSize))[0]
        self.e_ehsize = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]
        self.e_phentsize = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]
        self.e_phnum = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]
        self.e_shentsize = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]
        self.e_shnum = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]
        self.e_shstrndx = struct.unpack(self.Half, self.bf.read(self.HalfSize))[0]

    def parse_sections(self) -> None:
        self.bf.seek(self.e_shoff)
        for _ in range(self.e_shnum):
            self.sections.append(SectionHeader(self.bf, self.ptrsize, self.is_le))

    def read_str(self) -> bytes:
        arr = []
        x = self.bf.read(1)
        while x != b'\0':
            arr.append(x)
            x = self.bf.read(1)
            if x == b'':
                raise RuntimeError('Tried to read past the end of the file')
        return b''.join(arr)

    def find_section(self, target_name: bytes) -> T.Optional[SectionHeader]:
        section_names = self.sections[self.e_shstrndx]
        for i in self.sections:
            self.bf.seek(section_names.sh_offset + i.sh_name)
            name = self.read_str()
            if name == target_name:
                return i
        return None

    def parse_dynamic(self) -> None:
        sec = self.find_section(b'.dynamic')
        if sec is None:
            return
        self.bf.seek(sec.sh_offset)
        while True:
            e = DynamicEntry(self.bf, self.ptrsize, self.is_le)
            self.dynamic.append(e)
            if e.d_tag == 0:
                break

    @generate_list
    def get_section_names(self) -> T.Generator[str, None, None]:
        section_names = self.sections[self.e_shstrndx]
        for i in self.sections:
            self.bf.seek(section_names.sh_offset + i.sh_name)
            yield self.read_str().decode()

    def get_soname(self) -> T.Optional[str]:
        soname = None
        strtab = None
        for i in self.dynamic:
            if i.d_tag == DT_SONAME:
                soname = i
            if i.d_tag == DT_STRTAB:
                strtab = i
        if soname is None or strtab is None:
            return None
        self.bf.seek(strtab.val + soname.val)
        return self.read_str().decode()

    def get_entry_offset(self, entrynum: int) -> T.Optional[int]:
        sec = self.find_section(b'.dynstr')
        for i in self.dynamic:
            if i.d_tag == entrynum:
                res = sec.sh_offset + i.val
                assert isinstance(res, int)
                return res
        return None

    def get_rpath(self) -> T.Optional[str]:
        offset = self.get_entry_offset(DT_RPATH)
        if offset is None:
            return None
        self.bf.seek(offset)
        return self.read_str().decode()

    def get_runpath(self) -> T.Optional[str]:
        offset = self.get_entry_offset(DT_RUNPATH)
        if offset is None:
            return None
        self.bf.seek(offset)
        return self.read_str().decode()

    @generate_list
    def get_deps(self) -> T.Generator[str, None, None]:
        sec = self.find_section(b'.dynstr')
        for i in self.dynamic:
            if i.d_tag == DT_NEEDED:
                offset = sec.sh_offset + i.val
                self.bf.seek(offset)
                yield self.read_str().decode()

    def fix_deps(self, prefix: bytes) -> None:
        sec = self.find_section(b'.dynstr')
        deps = []
        for i in self.dynamic:
            if i.d_tag == DT_NEEDED:
                deps.append(i)
        for i in deps:
            offset = sec.sh_offset + i.val
            self.bf.seek(offset)
            name = self.read_str()
            if name.startswith(prefix):
                basename = name.rsplit(b'/', maxsplit=1)[-1]
                padding = b'\0' * (len(name) - len(basename))
                newname = basename + padding
                assert len(newname) == len(name)
                self.bf.seek(offset)
                self.bf.write(newname)

    def fix_rpath(self, fname: str, rpath_dirs_to_remove: T.Set[bytes], new_rpath: bytes) -> None:
        # The path to search for can be either rpath or runpath. Fix both of them to be sure.
        self.fix_rpathtype_entry(fname, rpath_dirs_to_remove, new_rpath, DT_RPATH)
        self.fix_rpathtype_entry(fname, rpath_dirs_to_remove, new_rpath, DT_RUNPATH)

    def fix_rpathtype_entry(self, fname: str, rpath_dirs_to_remove: T.Set[bytes], new_rpath: bytes, entrynum: int) -> None:
        rp_off = self.get_entry_offset(entrynum)
        if rp_off is None:
            if self.verbose:
                print(f'File {fname!r} does not have an rpath. It should be a fully static executable.')
            return
        self.bf.seek(rp_off)

        old_rpath = self.read_str()
        new_rpaths = []  # type: List[bytes]
        if new_rpath:
            new_rpaths.extend(new_rpath.split(b':'))
        if old_rpath:
            # Filter out build-only rpath entries
            # added by get_link_dep_subdirs() or
            # specified by user with build_rpath.
            for rpath_dir in old_rpath.split(b':'):
                if not (rpath_dir in rpath_dirs_to_remove or
                        rpath_dir == (b'X' * len(rpath_dir))):
                    if rpath_dir:
                        new_rpaths.append(rpath_dir)

        # Some rpath entries may come from multiple sources. Only add each one once.
        new_rpaths = list(dict.fromkeys(new_rpaths))

        # Prepend user-specified new entries while preserving the ones that came from pkgconfig etc.
        new_rpath = b':'.join(new_rpaths)

        if len(old_rpath) < len(new_rpath):
            msg = "New rpath must not be longer than the old one.\n Old: {}\n New: {}".format(old_rpath.decode('utf-8'), new_rpath.decode('utf-8'))
            raise ValueError(msg)
        # The linker does read-only string deduplication. If there is a
        # string that shares a suffix with the rpath, they might get
        # dedupped. This means changing the rpath string might break something
        # completely unrelated. This has already happened once with X.org.
        # Thus we want to keep this change as small as possible to minimize
        # the chance of obliterating other strings. It might still happen
        # but our behavior is identical to what chrpath does and it has
        # been in use for ages so based on that this should be rare.
        if not new_rpath:
            self.remove_rpath_entry(entrynum)
        else:
            self.bf.seek(rp_off)
            self.bf.write(new_rpath)
            self.bf.write(b'\0')

    def remove_rpath_entry(self, entrynum: int) -> None:
        sec = self.find_section(b'.dynamic')
        if sec is None:
            return None
        for i, entry in enumerate(self.dynamic):
            if entry.d_tag == entrynum:
                rpentry = self.dynamic[i]
                rpentry.d_tag = 0
                self.dynamic = self.dynamic[:i] + self.dynamic[i + 1:] + [rpentry]
                break
        # DT_MIPS_RLD_MAP_REL is relative to the offset of the tag. Adjust it consequently.
        for entry in self.dynamic[i:]:
            if entry.d_tag == DT_MIPS_RLD_MAP_REL:
                entry.val += 2 * (self.ptrsize // 8)
                break
        self.bf.seek(sec.sh_offset)
        for entry in self.dynamic:
            entry.write(self.bf)
        return None

    @property
    def rpath(self) -> Collection[str]:
        rpath = self.get_rpath()
        if rpath:
            return frozenset(rpath.split(':'))
        return frozenset()

    @rpath.setter
    def rpath(self, value: Collection[str]) -> None:
        self.fix_rpath(self.bfile, set(), ':'.join(value).encode('utf-8'))
