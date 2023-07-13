# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.


"""Image type detection based on magic bytes.

The following table shows which image types can be read by Qt natively, while the second
one shows which can be read when having the `qtimageformats` add-on module installed.

This module allows to detect images of these types based on the magic bytes of the file.

Native QT Support:
| ---    | ---                       | ---                                     |
| Format | Extension according to QT | Vimiv Supported                         |
| ---    | ---                       | ---                                     |
| BMP    | bmp                       | yes                                     |
| GIF    | gif                       | yes                                     |
| JPG    | jpeg, jpg                 | yes                                     |
| PNG    | png                       | yes                                     |
| PBM    | pbm                       | yes                                     |
| PGM    | pgm                       | yes                                     |
| PPM    | ppm                       | yes                                     |
| XBM    | xbm                       | yes (no distinct header, regex on file) |
| XPM    | xpm                       | yes                                     |
| SVG    | svg                       | yes                                     |
| SVG    | svgz                      | no (different from svg?)                |
| ---    | ---                       | ---                                     |

Extended QT Support:
| ---    | ---                       | ---                                             |
| Format | Extension according to QT | Vimiv Supported                                 |
| ---    | ---                       | ---                                             |
| ICNS   | ico                       | yes                                             |
| ICNS   | icns                      | yes                                             |
| ICNS   | cur                       | yes (TODO: is it really correct?)               |
| JP2    | TODO: ?                   | yes                                             |
| MNG    | TODO: ?                   | yes                                             |
| TGA    | tga                       | yes (only version 2, version 1 is undetectable) |
| TIFF   | tif, tiff                 | yes                                             |
| WBMP   | wbmp                      | no (is undetectable)                      |
| WEBP   | webp                      | yes                                             |
| ---    | ---                       | ---                                             |

A great list of magic bytes is provided here:
https://en.wikipedia.org/wiki/List_of_file_signatures
"""

import functools

from typing import Optional, List, Callable, Tuple, BinaryIO

from PyQt5.QtGui import QImageReader

from vimiv.utils import log, imagereader

_logger = log.module_logger(__name__)

CheckFuncT = Callable[[bytes, BinaryIO], bool]
# List containing all registered check functions
_registry: List[Tuple[str, CheckFuncT]] = []


def detect(filename: str) -> Optional[str]:
    """Determine type of image based on the magic bytes.

    Evaluates each registered check function in the order they were registered. If
    registered with `priority`, then that check is evaluated before all checks without
    `priority`.

    Args:
        filename: Name of file to determine type of.

    Returns:
        Filetype or None if unknown.
    """
    with open(filename, "rb") as f:
        header = f.read(32)

        for filetype, check in _registry:
            # Use try instead of contextlib.suppress due to zero-overhead.
            try:
                if check(header, f):
                    _logger.debug(f"Detected {filename} as {filetype}")
                    return filetype
            except IndexError:
                pass
    return None


def register(
    filetype: str, check: CheckFuncT, priority: bool = False, validate: bool = True
) -> None:
    """Register format test function.

    Args:
        filetype: Name of the format to register.
        check: Test function for that type.
        priority: Evaluate check before all previously registered checks if true.
        validate: Validate that the type is supported at runtime.
    """

    @functools.wraps(check)
    def check_verified(header: bytes, file: BinaryIO) -> bool:
        """Tests at runtime whether a filetype is actually supported.

        If not, then the filetype check is unregistered.
        """
        if check(header, file):
            if hasattr(check_verified, "checked"):
                return True
            if (
                filetype in QImageReader.supportedImageFormats()
                or filetype in imagereader.external_handler
            ):
                setattr(check_verified, "checked", True)
                return True
            _logger.warning(
                f"Check for {filetype} was register, but display is not supported."
                "Probably you need to install the required backend module."
            )
            _registry.remove((filetype, check_verified))
        return False

    check_register = check_verified if validate else check

    if priority:
        _registry.insert(0, (filetype, check_register))
    else:
        _registry.append((filetype, check_register))


def _test_jpg(h: bytes, _f: BinaryIO) -> bool:
    """Joint Photographic Experts Group (JPEG) in different kinds of "subtypes"(?).

    Extension: .jpeg, .jpg

    Magic bytes:
    - FF D8 FF DB
    - FF D8 FF E0 (only for JPG, but no need to differentiate)
    - FF D8 FF E0 00 10 4A 46 49 46 00 01 (covered be prior)
    - FF D8 FF EE
    - FF D8 FF E1 ?? ?? 45 78 69 66 00 00

    Support: native
    """
    return h[:3] == b"\xFF\xD8\xFF" and (
        h[3] in [0xDB, 0xE0, 0xEE]
        or (h[3] == 0xE1 and h[6:12] == b"\x45\x78\x69\x66\x00\x00")
    )


def _test_png(h: bytes, _f: BinaryIO) -> bool:
    """Portable Network Graphics (PNG).

    Extension: .png

    Magic bytes:
    - 89 50 4E 47 0D 0A 1A 0A

    Support: native
    """
    return h[:8] == b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"


def _test_gif(h: bytes, _f: BinaryIO) -> bool:
    """Graphics Interchange Format (GIF).

    Extension: .gif

    Magic bytes:
    - 47 49 46 38 37 61
    - 47 49 46 38 39 61

    Support: native
    """
    return h[:4] == b"\x47\x49\x46\x38" and h[4] in [0x37, 0x39] and h[5] == 0x61


def _test_svg(h: bytes, _f: BinaryIO) -> bool:
    """Scalable Vector Graphics (SVG).

    Extension: .svg (TODO: also svgz?)

    Magic bytes:
    - 3C 3F 78 6D 6C
    - 3C 3F 73 76 67

    Native QT support.
    """
    return h[:2] == b"\x3C\x3F" and (h[2:5] in [b"\x78\x6D\x6C", b"\x73\x76\x67"])


def _test_pbm(h: bytes, _f: BinaryIO) -> bool:
    """Portable Bitmap (PBM) in ASCII and Binary.

    Extension: .pbm

    Magic bytes:
    - 50 31 0A
    - 50 34 0A

    Support: native
    """
    return h[0] == 0x50 and h[1] in [0x31, 0x34] and h[2] == 0x0A


def _test_pgm(h: bytes, _f: BinaryIO) -> bool:
    """Portable Graymap (PGM) in ASCII and Binary.

    Extension: .pgm

    Magic bytes:
    - 50 32 0A
    - 50 35 0A

    Support: native
    """
    return h[0] == 0x50 and h[1] in [0x32, 0x35] and h[2] == 0x0A


def _test_ppm(h: bytes, _f: BinaryIO) -> bool:
    """Portable Pixmap (PPM) in ASCII and Binary.

    Extension: .ppm

    Magic bytes:
    - 50 33 0A
    - 50 36 0A

    Support: native
    """
    return h[0] == 0x50 and h[1] in [0x33, 0x36] and h[2] == 0x0A


def _test_bmp(h: bytes, _f: BinaryIO) -> bool:
    """Bitmap (BMP).

    Extension: .bmp, .dib

    Magic bytes:
    - 42 4D

    Support: native
    """
    return h[0:2] == b"\x42\x4D"


def _test_xbm(h: bytes, f: BinaryIO) -> bool:
    """X Bitmap (XBM).

    Are valid C source files.

    Extension: .xbm

    Magic Bytes:
    - None; Use regex on file

    Support: native
    """
    # Regex match is expensive, only do when likely to succeed
    if h[:7] == b"#define":
        import re

        f.seek(0, 0)
        h = f.read()
        pattern = (
            b"#define [a-zA-Z0-9]*_width [0-9]+\n#define [a-zA-Z0-9]*_height [0-9]+"
        )
        return re.search(pattern, h) is not None
    return False


def _test_xpm(h: bytes, _f: BinaryIO) -> bool:
    """X Pixmap (XPM).

    Extension: .xpm

    Magic Bytes:
    - 2F 2A 20 58 50 4D 20 2A 2F

    Support: native
    """
    return h[:9] == b"\x2F\x2A\x20\x58\x50\x4D\x20\x2A\x2F"


def _test_webp(h: bytes, _f: BinaryIO) -> bool:
    """Web Picture Format (WebP).

    Raster graphics format intended to replace JPEG, PNG, GIF.

    Extension: .webp

    Magic bytes:
    - 52 49 46 46 ?? ?? ?? ?? 57 45 42 50

    Support: extended
    """
    return h[:4] == b"\x52\x49\x46\x46" and h[8:12] == b"\x57\x45\x42\x50"


def _test_tiff(h: bytes, _f: BinaryIO) -> bool:
    """Tagged Image File Format (TIFF).

    Raster graphics format often used by professionals.

    Extension: .tiff, .tif

    Magic Bytes:
    - 49 49 2A 00
    - 4D 4D 00 2A

    Support: extended
    """
    return h[:4] in [b"\x49\x49\x2A\x00", b"\x4D\x4D\x00\x2A"]


def _test_ico(h: bytes, _f: BinaryIO) -> bool:
    """Icon (ICO).

    Windows' ICON format. Extended to CUR.

    Extension: .ico

    Magic Bytes:
    - 00 00 01 00

    Support: extended
    """
    return h[:4] == b"\x00\x00\x01\x00"


def _test_icns(h: bytes, _f: BinaryIO) -> bool:
    """Icon Container (ICNS).

    Apple's ICON format.

    Extension: .icns

    Magic Bytes:
    - 69 63 6e 73

    Support: extended
    """
    return h[:4] == b"\x69\x63\x6e\x73"


def _test_jp2(h: bytes, _f: BinaryIO) -> bool:
    """JPEP 2000.

    Extension: .jp2 (TODO: maybe also others)

    Magic Bytes:
    - 00 00 00 0C 6A 50 20 20 0D 0A 87 0A

    Support: extended
    """
    return h[:12] == b"\x00\x00\x00\x0C\x6A\x50\x20\x20\x0D\x0A\x87\x0A"


def _test_cur(h: bytes, _f: BinaryIO) -> bool:
    """Cursor (CUR).

    Windows' ICON format. Extended from ICO.

    TODO: not sure if the bytes are correct, but should be according to
    http://www.daubnet.com/en/file-format-cur

    Extension: .cur

    Magic Bytes:
    - 00 00 02 00

    Support: extended
    """
    return h[:4] == b"\x00\x00\x02\x00"


def _test_mng(h: bytes, _f: BinaryIO) -> bool:
    """Multiple-image Network Graphics (MNG).

    Like PNG but supports animations.

    Extension: .mng

    Magic Bytes:
    - 8A 4D 4E 47 0D 0A 1A 0A

    Support: extended
    """
    return h[:8] == b"\x8A\x4D\x4E\x47\x0D\x0A\x1A\x0A"


def _test_tga(_h: bytes, f: BinaryIO) -> bool:
    """Truevision Graphics Adapter (TGA).

    There are two versions of this file. Version 1 has no signature, and hence, is
    undetectable, while Version 2 has one at the end of the file.

    Extension: .tga, .icb, .vda, .vst

    Magic Bytes:
    - impossible to detect (Version 1)
    - 54 52 55 45 56 49 53 49 4F 4E 2D 58 46 49 4C 45 (Version 2; footer at end of file)

    Support: extended
    """
    # Get signature located at end of file
    # Seek relative to end of file for some files
    try:
        f.seek(-18, 2)
        h = f.read(16)
        return h == b"\x54\x52\x55\x45\x56\x49\x53\x49\x4F\x4E\x2D\x58\x46\x49\x4C\x45"
    except OSError:
        return False


def _test_wbmp(h: bytes, _f: BinaryIO) -> bool:
    """Wireless Bitmap (WBMP).

    Extension: .wbmp

    Magic Bytes:
    - impossible to detect

    Support: extended
    """
    raise NotImplementedError


# Register all check functions. Check functions of more frequently used types should be
# registered first, to make the detection more efficient.
# No need to validate natively supported type, but validate extended supported types.
register("jpg", _test_jpg, validate=False)
register("png", _test_png, validate=False)
register("gif", _test_gif, validate=False)
register("jp2", _test_jp2)
register("webp", _test_webp)
register("tiff", _test_tiff)
register("svg", _test_svg, validate=False)
register("ico", _test_ico)
register("icns", _test_icns)
register("tga", _test_tga, validate=False)
register("pbm", _test_pbm, validate=False)
register("pgm", _test_pgm, validate=False)
register("ppm", _test_ppm, validate=False)
register("bmp", _test_bmp, validate=False)
register("xbm", _test_xbm, validate=False)
register("xpm", _test_xpm, validate=False)
register("mng", _test_mng)
register("cur", _test_cur)
