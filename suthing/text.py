"""Text helpers."""

from __future__ import annotations

import re
import unicodedata

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def slugify(
    text: str,
    *,
    sep: str = "-",
    fallback: str = "item",
    lower: bool = False,
    ascii_fold: bool = False,
    max_length: int | None = None,
) -> str:
    """Turn *text* into a token safe for file names and URL path segments.

    Every run of characters outside ``A-Za-z0-9._-`` becomes one *sep*, and
    *sep* is stripped from both ends.

    Args:
        text: Input text.
        sep: Replacement for each run of unsafe characters.
        fallback: Returned when nothing safe is left.
        lower: Lower-case the result.
        ascii_fold: Replace accented letters by their base letter (``"é"`` →
            ``"e"``) instead of treating them as unsafe.
        max_length: Cut the result to at most this many characters, then strip
            *sep* again.

    Returns:
        The slug, or *fallback*.

    Example:
        >>> slugify("  Person / Company ")
        'Person-Company'
        >>> slugify("Café Menü", sep="_", lower=True, ascii_fold=True)
        'cafe_menu'
    """
    if ascii_fold:
        text = (
            unicodedata.normalize("NFKD", text)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    slug = _UNSAFE.sub(sep, text.strip()).strip(sep)
    if lower:
        slug = slug.lower()
    if max_length is not None:
        slug = slug[:max_length].strip(sep)
    return slug or fallback
