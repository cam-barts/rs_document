"""Vendored post processors from Unstructured.io"""

import re
import sys
import unicodedata
from collections.abc import Callable
from typing import Final

LINE_BREAK = r"(?<=\n)"
LINE_BREAK_RE = re.compile(LINE_BREAK)

UNICODE_BULLETS: Final[list[str]] = [
    "\u0095",
    "\u2022",
    "\u2023",
    "\u2043",
    "\u3164",
    "\u204c",
    "\u204d",
    "\u2219",
    "\u25cb",
    "\u25cf",
    "\u25d8",
    "\u25e6",
    "\u2619",
    "\u2765",
    "\u2767",
    "\u29be",
    "\u29bf",
    "\u002d",
    "",
    "\*",  # noqa: W605 NOTE(robinson) - skipping qa because we need the escape for the regex
    "\x95",
    "·",
]
BULLETS_PATTERN = "|".join(UNICODE_BULLETS)
UNICODE_BULLETS_RE = re.compile(f"(?:{BULLETS_PATTERN})(?!{BULLETS_PATTERN})")
# zero-width positive lookahead so bullet characters will not be removed when using .split()
UNICODE_BULLETS_RE_0W = re.compile(f"(?={BULLETS_PATTERN})(?<!{BULLETS_PATTERN})")
E_BULLET_PATTERN = re.compile(r"^e(?=\s)", re.MULTILINE)


PARAGRAPH_PATTERN = r"\s*\n\s*"

PARAGRAPH_PATTERN_RE = re.compile(
    f"((?:{BULLETS_PATTERN})|{PARAGRAPH_PATTERN})(?!{BULLETS_PATTERN}|$)",
)

DOUBLE_PARAGRAPH_PATTERN_RE = re.compile("(" + PARAGRAPH_PATTERN + "){2}")


def clean_non_ascii_chars(text: str) -> str:
    """Cleans non-ascii characters from unicode string.

    Example
    -------
    \x88This text contains non-ascii characters!\x88
        -> This text contains non-ascii characters!
    """
    en = text.encode("ascii", "ignore")
    return en.decode()


def clean_bullets(text: str) -> str:
    """Cleans unicode bullets from a section of text.

    Example
    -------
    ●  This is an excellent point! -> This is an excellent point!
    """
    search = UNICODE_BULLETS_RE.match(text)
    if search is None:
        return text

    cleaned_text = UNICODE_BULLETS_RE.sub("", text, 1)
    return cleaned_text.strip()


def clean_ligatures(text: str) -> str:
    """Replaces ligatures with their most likely equivalent characters.

    Example
    -------
    The beneﬁts -> The benefits
    High quality ﬁnancial -> High quality financial
    """
    ligatures_map = {
        "æ": "ae",
        "Æ": "AE",
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬅ": "ft",
        "ʪ": "ls",
        "œ": "oe",
        "Œ": "OE",
        "ȹ": "qp",
        "ﬆ": "st",
        "ʦ": "ts",
    }
    cleaned_text: str = text
    for k, v in ligatures_map.items():
        cleaned_text = cleaned_text.replace(k, v)

    return cleaned_text


def group_bullet_paragraph(paragraph: str) -> list:
    """Groups paragraphs with bullets that have line breaks for visual/formatting purposes.
    For example:

    '''○ The big red fox
    is walking down the lane.

    ○ At the end of the lane
    the fox met a friendly bear.'''

    Gets converted to

    '''○ The big red fox is walking down the lane.
    ○ At the end of the land the fox met a bear.'''
    """
    clean_paragraphs = []
    # pytesseract converts some bullet points to standalone "e" characters.
    # Substitute "e" with bullets since they are later used in partition_text
    # to determine list element type.
    paragraph = (re.sub(E_BULLET_PATTERN, "·", paragraph)).strip()

    bullet_paras = re.split(UNICODE_BULLETS_RE_0W, paragraph)
    for bullet in bullet_paras:
        if bullet:
            clean_paragraphs.append(re.sub(PARAGRAPH_PATTERN, " ", bullet))
    return clean_paragraphs


def group_broken_paragraphs(
    text: str,
    line_split: re.Pattern[str] = PARAGRAPH_PATTERN_RE,
    paragraph_split: re.Pattern[str] = DOUBLE_PARAGRAPH_PATTERN_RE,
) -> str:
    """Groups paragraphs that have line breaks for visual/formatting purposes.
    For example:

    '''The big red fox
    is walking down the lane.

    At the end of the lane
    the fox met a bear.'''

    Gets converted to

    '''The big red fox is walking down the lane.
    At the end of the land the fox met a bear.'''
    """
    paragraphs = paragraph_split.split(text)
    clean_paragraphs = []
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        # NOTE(robinson) - This block is to account for lines like the following that shouldn't be
        # grouped together, but aren't separated by a double line break.
        #     Apache License
        #     Version 2.0, January 2004
        #     http://www.apache.org/licenses/
        para_split = line_split.split(paragraph)
        all_lines_short = all(len(line.strip().split(" ")) < 5 for line in para_split)
        # pytesseract converts some bullet points to standalone "e" characters
        if UNICODE_BULLETS_RE.match(paragraph.strip()) or E_BULLET_PATTERN.match(
            paragraph.strip()
        ):
            clean_paragraphs.extend(group_bullet_paragraph(paragraph))
        elif all_lines_short:
            clean_paragraphs.extend([line for line in para_split if line.strip()])
        else:
            clean_paragraphs.append(re.sub(PARAGRAPH_PATTERN, " ", paragraph))

    return "\n\n".join(clean_paragraphs)


def new_line_grouper(
    text: str,
    paragraph_split: re.Pattern[str] = LINE_BREAK_RE,
) -> str:
    """
    Concatenates text document that has one-line paragraph break pattern

    For example,

    Iwan Roberts
    Roberts celebrating after scoring a goal for Norwich City
    in 2004

    Will be returned as:

    Iwan Roberts\n\nRoberts celebrating after scoring a goal for Norwich City\n\nin 2004
    """
    paragraphs = paragraph_split.split(text)
    clean_paragraphs = []
    for paragraph in paragraphs:
        if not paragraph.strip():
            continue
        clean_paragraphs.append(paragraph)
    return "\n\n".join(clean_paragraphs)


def blank_line_grouper(
    text: str,
    paragraph_split: re.Pattern = DOUBLE_PARAGRAPH_PATTERN_RE,
) -> str:
    """
    Concatenates text document that has blank-line paragraph break pattern

    For example,

    Vestibulum auctor dapibus neque.

    Nunc dignissim risus id metus.

    Will be returned as:

    Vestibulum auctor dapibus neque.\n\nNunc dignissim risus id metus.\n\n

    """
    return group_broken_paragraphs(text)


def auto_paragraph_grouper(
    text: str,
    line_split: re.Pattern[str] = LINE_BREAK_RE,
    max_line_count: int = 2000,
    threshold: float = 0.1,
) -> str:
    """
    Checks the ratio of new line (\n) over the total max_line_count

    If the ratio of new line is less than the threshold,
    the document is considered a new-line grouping type
    and return the original text

    If the ratio of new line is greater than or equal to the threshold,
    the document is considered a blank-line grouping type
    and passed on to blank_line_grouper function
    """
    lines = line_split.split(text)
    max_line_count = min(len(lines), max_line_count)
    line_count, empty_line_count = 0, 0
    for line in lines[:max_line_count]:
        line_count += 1
        if not line.strip():
            empty_line_count += 1
    ratio = empty_line_count / line_count

    if ratio < threshold:
        return new_line_grouper(text)
    else:
        return blank_line_grouper(text)


def replace_unicode_quotes(text: str) -> str:
    """Replaces unicode bullets in text with the expected character

    Example
    -------
    \x93What a lovely quote!\x94 -> “What a lovely quote!”
    """
    # NOTE(robinson) - We should probably make this something more sane like a regex
    # instead of a whole big series of replaces
    text = text.replace("\x91", "‘")
    text = text.replace("\x92", "’")
    text = text.replace("\x93", "“")
    text = text.replace("\x94", "”")
    text = text.replace("&apos;", "'")
    text = text.replace("\xe2\x80\x99", "'")
    text = text.replace("\xe2\x80\x94", "—")
    text = text.replace("\xe2\x80\x93", "–")
    text = text.replace("\xe2\x80\x98", "‘")
    text = text.replace("\xe2\x80\xa6", "…")
    text = text.replace("\xe2\x80\x99", "’")
    text = text.replace("\xe2\x80œ", "“")
    text = text.replace("\xe2\x80?", "”")
    text = text.replace("\xe2\x80ť", "”")
    text = text.replace("\xe2\x80ś", "“")
    text = text.replace("\xe2\x80¨", "—")
    text = text.replace("\xe2\x80ł", "″")
    text = text.replace("\xe2\x80Ž", "")
    text = text.replace("\xe2\x80‚", "")
    text = text.replace("\xe2\x80‰", "")
    text = text.replace("\xe2\x80‹", "")
    text = text.replace("\xe2\x80", "")
    text = text.replace("\xe2\x80s'", "")
    return text


tbl = dict.fromkeys(
    i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith("P")
)


def clean_extra_whitespace(text: str) -> str:
    """Cleans extra whitespace characters that appear between words.

    Example
    -------
    ITEM 1.     BUSINESS -> ITEM 1. BUSINESS
    """
    cleaned_text = re.sub(r"[\xa0\n]", " ", text)
    cleaned_text = re.sub(r"([ ]{2,})", " ", cleaned_text)
    return cleaned_text.strip()


UNSTRUCTURED_POST_PROCESSORS: list[Callable[[str], str]] = [
    clean_extra_whitespace,
    clean_ligatures,
    clean_non_ascii_chars,
    blank_line_grouper,
    new_line_grouper,
    group_broken_paragraphs,
    auto_paragraph_grouper,
]
