# vim: ft=python fileencoding=utf-8 sw=4 et sts=4


"""Recognize image file formats based on their first few bytes."""

from typing import Optional, BinaryIO, List, Callable

# List containing all testing functions
tests: List[Callable[[bytes, Optional[BinaryIO]], Optional[str]]] = []


def what(filename: str) -> Optional[str]:
    """Determine type of image based on the magic bytes.

    Args:
        filename: Name of file to determine type of.

    Returns:
        Filetype or None if unknown.
    """
    f = None
    with open(filename, "rb") as f:
        h = f.read(32)

        for tf in tests:
            res = tf(h, f)
            if res:
                return res
    return None


def _test_jpeg(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """JPEG data with JFIF or Exif markers; and raw JPEG."""
    if h[6:10] in (b"JFIF", b"Exif"):
        return "jpeg"
    if h[:4] == b"\xff\xd8\xff\xdb":
        return "jpeg"
    return None


tests.append(_test_jpeg)


def _test_png(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """PNG."""
    if h.startswith(b"\211PNG\r\n\032\n"):
        return "png"
    return None


tests.append(_test_png)


def _test_gif(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """GIF ('87 and '89 variants)."""
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    return None


tests.append(_test_gif)


def _test_tiff(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """TIFF (can be in Motorola or Intel byte order)."""
    if h[:2] in (b"MM", b"II"):
        return "tiff"
    return None


tests.append(_test_tiff)


def _test_rgb(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """SGI image library."""
    if h.startswith(b"\001\332"):
        return "rgb"
    return None


tests.append(_test_rgb)


def _test_pbm(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """PBM (portable bitmap)."""
    if len(h) >= 3 and h[0] == ord(b"P") and h[1] in b"14" and h[2] in b" \t\n\r":
        return "pbm"
    return None


tests.append(_test_pbm)


def _test_pgm(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """PGM (portable graymap)."""
    if len(h) >= 3 and h[0] == ord(b"P") and h[1] in b"25" and h[2] in b" \t\n\r":
        return "pgm"
    return None


tests.append(_test_pgm)


def _test_ppm(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """PPM (portable pixmap)."""
    if len(h) >= 3 and h[0] == ord(b"P") and h[1] in b"36" and h[2] in b" \t\n\r":
        return "ppm"
    return None


tests.append(_test_ppm)


def _test_rast(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """Sun raster file."""
    if h.startswith(b"\x59\xA6\x6A\x95"):
        return "rast"
    return None


tests.append(_test_rast)


def _test_xbm(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """X bitmap (X10 or X11)."""
    if h.startswith(b"#define "):
        return "xbm"
    return None


tests.append(_test_xbm)


def _test_bmp(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """BMP."""
    if h.startswith(b"BM"):
        return "bmp"
    return None


tests.append(_test_bmp)


def _test_webp(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """WEBP."""
    if h.startswith(b"RIFF") and h[8:12] == b"WEBP":
        return "webp"
    return None


tests.append(_test_webp)


def _test_exr(h: bytes, _f: Optional[BinaryIO]) -> Optional[str]:
    """EXR."""
    if h.startswith(b"\x76\x2f\x31\x01"):
        return "exr"
    return None


tests.append(_test_exr)
