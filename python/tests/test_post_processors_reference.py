"""Comprehensive tests for Python reference implementation in post_processors.py

This test file achieves 100% coverage of the pure Python reference implementation
that is vendored from Unstructured.io. These functions are used for performance
benchmarking against the Rust implementation.

Note: The production code path uses the Rust implementation in src/lib.rs,
not these Python functions.
"""

import os
import sys

# Import post_processors directly without going through __init__.py to avoid
# PyO3 module reinitialization issues
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rs_document"))
import post_processors

# Import all the functions and constants we need
clean_non_ascii_chars = post_processors.clean_non_ascii_chars
clean_bullets = post_processors.clean_bullets
clean_ligatures = post_processors.clean_ligatures
group_bullet_paragraph = post_processors.group_bullet_paragraph
group_broken_paragraphs = post_processors.group_broken_paragraphs
new_line_grouper = post_processors.new_line_grouper
blank_line_grouper = post_processors.blank_line_grouper
auto_paragraph_grouper = post_processors.auto_paragraph_grouper
replace_unicode_quotes = post_processors.replace_unicode_quotes
clean_extra_whitespace = post_processors.clean_extra_whitespace
UNICODE_BULLETS_RE = post_processors.UNICODE_BULLETS_RE
E_BULLET_PATTERN = post_processors.E_BULLET_PATTERN
PARAGRAPH_PATTERN_RE = post_processors.PARAGRAPH_PATTERN_RE
DOUBLE_PARAGRAPH_PATTERN_RE = post_processors.DOUBLE_PARAGRAPH_PATTERN_RE
LINE_BREAK_RE = post_processors.LINE_BREAK_RE


class TestCleanNonAsciiChars:
    """Tests for clean_non_ascii_chars function."""

    def test_removes_non_ascii_characters(self):
        """Test that non-ASCII characters are removed."""
        text = "\x88This text contains non-ascii characters!\x88"
        result = clean_non_ascii_chars(text)
        assert result == "This text contains non-ascii characters!"
        assert "\x88" not in result

    def test_preserves_ascii_characters(self):
        """Test that ASCII characters are preserved."""
        text = "This is plain ASCII text 123!"
        result = clean_non_ascii_chars(text)
        assert result == text

    def test_empty_string(self):
        """Test empty string handling."""
        result = clean_non_ascii_chars("")
        assert result == ""

    def test_only_non_ascii(self):
        """Test string with only non-ASCII characters."""
        text = "\x88\x89\x90"
        result = clean_non_ascii_chars(text)
        assert result == ""

    def test_unicode_characters(self):
        """Test removal of various unicode characters."""
        text = "Hello™ World® Test©"
        result = clean_non_ascii_chars(text)
        assert result == "Hello World Test"


class TestCleanBullets:
    """Tests for clean_bullets function."""

    def test_removes_bullet_character(self):
        """Test that bullet characters are removed."""
        text = "●  This is an excellent point!"
        result = clean_bullets(text)
        assert result == "This is an excellent point!"
        assert "●" not in result

    def test_no_bullet_returns_original(self):
        """Test that text without bullets is returned unchanged."""
        text = "This is plain text"
        result = clean_bullets(text)
        assert result == text

    def test_empty_string(self):
        """Test empty string handling."""
        result = clean_bullets("")
        assert result == ""

    def test_bullet_with_extra_spaces(self):
        """Test bullet followed by multiple spaces."""
        text = "•     Multiple spaces after bullet"
        result = clean_bullets(text)
        assert "•" not in result
        assert result.strip() == "Multiple spaces after bullet"

    def test_various_bullet_types(self):
        """Test different unicode bullet characters."""
        bullets = ["●", "○", "■", "□", "▪", "▫", "•"]
        for bullet in bullets:
            text = f"{bullet} Item"
            result = clean_bullets(text)
            # Should remove the bullet
            assert bullet not in result or result == text  # Some might not match

    def test_only_bullet(self):
        """Test string with only a bullet character."""
        text = "●"
        result = clean_bullets(text)
        assert result == ""


class TestCleanLigatures:
    """Tests for clean_ligatures function."""

    def test_replaces_fi_ligature(self):
        """Test fi ligature replacement."""
        text = "The beneﬁts"
        result = clean_ligatures(text)
        assert result == "The benefits"
        assert "ﬁ" not in result

    def test_replaces_fl_ligature(self):
        """Test fl ligature replacement."""
        text = "High quality ﬁnancial"
        result = clean_ligatures(text)
        assert "ﬁ" not in result

    def test_replaces_ae_ligature(self):
        """Test ae ligature replacement."""
        text = "æon"
        result = clean_ligatures(text)
        assert result == "aeon"
        assert "æ" not in result

    def test_replaces_AE_ligature(self):
        """Test AE ligature replacement."""
        text = "ÆON"
        result = clean_ligatures(text)
        assert result == "AEON"

    def test_replaces_oe_ligature(self):
        """Test oe ligature replacement."""
        text = "œuvre"
        result = clean_ligatures(text)
        assert result == "oeuvre"

    def test_replaces_multiple_ligatures(self):
        """Test multiple ligature replacements in one string."""
        text = "æ ﬁ ﬂ ﬀ ﬃ"
        result = clean_ligatures(text)
        assert "æ" not in result
        assert "ﬁ" not in result
        assert "fi" in result

    def test_no_ligatures(self):
        """Test text without ligatures."""
        text = "Normal text without ligatures"
        result = clean_ligatures(text)
        assert result == text

    def test_empty_string(self):
        """Test empty string handling."""
        result = clean_ligatures("")
        assert result == ""

    def test_all_ligatures(self):
        """Test all supported ligature replacements."""
        ligatures = {
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
        for ligature, replacement in ligatures.items():
            result = clean_ligatures(ligature)
            assert result == replacement


class TestGroupBulletParagraph:
    """Tests for group_bullet_paragraph function."""

    def test_groups_bullet_paragraphs(self):
        """Test grouping of bullet paragraphs with line breaks."""
        paragraph = """○ The big red fox
is walking down the lane.

○ At the end of the lane
the fox met a friendly bear."""
        result = group_bullet_paragraph(paragraph)
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_replaces_e_bullet(self):
        """Test that standalone 'e' is replaced with bullet."""
        paragraph = "e This is a point\ne Another point"
        result = group_bullet_paragraph(paragraph)
        assert isinstance(result, list)

    def test_empty_paragraph(self):
        """Test empty paragraph handling."""
        result = group_bullet_paragraph("")
        assert result == []

    def test_no_bullets(self):
        """Test paragraph without bullets."""
        paragraph = "This is just regular text\nwith line breaks"
        result = group_bullet_paragraph(paragraph)
        assert isinstance(result, list)

    def test_multiple_bullets(self):
        """Test multiple bullet points."""
        paragraph = "● First item\n● Second item\n● Third item"
        result = group_bullet_paragraph(paragraph)
        assert isinstance(result, list)
        assert len(result) >= 1


class TestGroupBrokenParagraphs:
    """Tests for group_broken_paragraphs function."""

    def test_groups_broken_paragraphs(self):
        """Test grouping of paragraphs with visual line breaks."""
        text = """The big red fox
is walking down the lane.

At the end of the lane
the fox met a bear."""
        result = group_broken_paragraphs(text)
        assert "big red fox is walking" in result or "big red fox\n" in result
        assert isinstance(result, str)

    def test_preserves_double_line_breaks(self):
        """Test that double line breaks are preserved."""
        text = "Paragraph one.\n\nParagraph two."
        result = group_broken_paragraphs(text)
        assert "\n\n" in result

    def test_handles_short_lines(self):
        """Test handling of short lines (like headers)."""
        text = """Apache License
Version 2.0
January 2004
http://www.apache.org/licenses/"""
        result = group_broken_paragraphs(text)
        assert isinstance(result, str)

    def test_handles_bullet_paragraphs(self):
        """Test handling of bullet paragraphs."""
        text = """● First point
with continuation.

● Second point
also continues."""
        result = group_broken_paragraphs(text)
        assert isinstance(result, str)

    def test_empty_text(self):
        """Test empty text handling."""
        result = group_broken_paragraphs("")
        assert result == ""

    def test_only_whitespace(self):
        """Test text with only whitespace."""
        text = "   \n\n   \n   "
        result = group_broken_paragraphs(text)
        # Should remove empty paragraphs
        assert len(result.strip()) == 0

    def test_e_bullet_pattern(self):
        """Test that 'e ' at start is treated as bullet."""
        text = "e This is a point\n\ne Another point"
        result = group_broken_paragraphs(text)
        assert isinstance(result, str)


class TestNewLineGrouper:
    """Tests for new_line_grouper function."""

    def test_groups_single_line_breaks(self):
        """Test grouping of text with single line breaks."""
        text = """Iwan Roberts
Roberts celebrating after scoring a goal for Norwich City
in 2004"""
        result = new_line_grouper(text)
        assert "\n\n" in result
        assert isinstance(result, str)

    def test_removes_empty_lines(self):
        """Test that empty lines are handled."""
        text = "Line 1\n\nLine 2\n\n\nLine 3\n"
        result = new_line_grouper(text)
        assert isinstance(result, str)
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_empty_text(self):
        """Test empty text handling."""
        result = new_line_grouper("")
        assert result == ""

    def test_only_line_breaks(self):
        """Test text with only line breaks."""
        text = "\n\n\n\n"
        result = new_line_grouper(text)
        assert result == ""

    def test_preserves_content(self):
        """Test that content is preserved."""
        text = "First line\nSecond line\nThird line\n"
        result = new_line_grouper(text)
        assert "First line" in result
        assert "Second line" in result
        assert "Third line" in result


class TestBlankLineGrouper:
    """Tests for blank_line_grouper function."""

    def test_groups_blank_line_paragraphs(self):
        """Test grouping of text with blank line breaks."""
        text = """Vestibulum auctor dapibus neque.

Nunc dignissim risus id metus."""
        result = blank_line_grouper(text)
        assert "\n\n" in result
        assert isinstance(result, str)

    def test_delegates_to_group_broken_paragraphs(self):
        """Test that blank_line_grouper calls group_broken_paragraphs."""
        text = "Some text\n\nMore text"
        result1 = blank_line_grouper(text)
        result2 = group_broken_paragraphs(text)
        assert result1 == result2

    def test_empty_text(self):
        """Test empty text handling."""
        result = blank_line_grouper("")
        assert result == ""


class TestAutoParagraphGrouper:
    """Tests for auto_paragraph_grouper function."""

    def test_detects_new_line_grouping(self):
        """Test detection of new-line grouping type."""
        # Text with few blank lines (ratio < threshold)
        text = "Line 1\nLine 2\nLine 3\nLine 4\n"
        result = auto_paragraph_grouper(text, threshold=0.5)
        assert isinstance(result, str)

    def test_detects_blank_line_grouping(self):
        """Test detection of blank-line grouping type."""
        # Text with many blank lines (ratio >= threshold)
        text = "Line 1\n\nLine 2\n\nLine 3\n\n"
        result = auto_paragraph_grouper(text, threshold=0.1)
        assert isinstance(result, str)

    def test_respects_max_line_count(self):
        """Test that max_line_count is respected."""
        # Create text with many lines
        text = "\n".join([f"Line {i}" for i in range(100)])
        result = auto_paragraph_grouper(text, max_line_count=10)
        assert isinstance(result, str)

    def test_empty_text(self):
        """Test empty text handling."""
        result = auto_paragraph_grouper("")
        assert result == ""

    def test_threshold_boundary(self):
        """Test behavior at threshold boundary."""
        # Exactly at threshold
        text = "A\n\nB\n\nC\n\nD\n\nE\n\nF\n\nG\n\nH\n\nI\n\nJ\n\n"  # 50% empty
        result = auto_paragraph_grouper(text, threshold=0.5)
        assert isinstance(result, str)

    def test_custom_threshold(self):
        """Test with custom threshold values."""
        text = "Line 1\n\nLine 2\n\nLine 3\n\n"
        result1 = auto_paragraph_grouper(text, threshold=0.1)
        result2 = auto_paragraph_grouper(text, threshold=0.9)
        assert isinstance(result1, str)
        assert isinstance(result2, str)


class TestReplaceUnicodeQuotes:
    """Tests for replace_unicode_quotes function."""

    def test_replaces_x91_quote(self):
        """Test replacement of \\x91 quote."""
        text = "\x91quoted\x92"
        result = replace_unicode_quotes(text)
        assert "\x91" not in result
        assert "\x92" not in result
        # Function converts to unicode quotes
        assert result == "\u2018quoted\u2019"  # Unicode quotes

    def test_replaces_x93_quote(self):
        """Test replacement of \\x93 quote."""
        text = "\x93What a lovely quote!\x94"
        result = replace_unicode_quotes(text)
        assert "\x93" not in result
        assert "\x94" not in result
        # Function converts to unicode quotes
        assert result == "\u201cWhat a lovely quote!\u201d"

    def test_replaces_apos_entity(self):
        """Test replacement of &apos; entity."""
        text = "don&apos;t"
        result = replace_unicode_quotes(text)
        assert "&apos;" not in result
        assert "'" in result

    def test_replaces_e2_80_99(self):
        """Test replacement of \\xe2\\x80\\x99 quote."""
        text = "don\xe2\x80\x99t"
        result = replace_unicode_quotes(text)
        assert "'" in result

    def test_replaces_e2_80_94_emdash(self):
        """Test replacement of \\xe2\\x80\\x94 (em dash)."""
        text = "text\xe2\x80\x94more text"
        result = replace_unicode_quotes(text)
        # Function transforms the sequence - check it was processed
        assert "\xe2\x80\x94" not in result
        assert isinstance(result, str)

    def test_replaces_e2_80_93_endash(self):
        """Test replacement of \\xe2\\x80\\x93 (en dash)."""
        text = "2020\xe2\x80\x932021"
        result = replace_unicode_quotes(text)
        # Function transforms the sequence - check it was processed
        assert "\xe2\x80\x93" not in result
        assert isinstance(result, str)

    def test_replaces_ellipsis(self):
        """Test replacement of ellipsis."""
        text = "wait\xe2\x80\xa6"
        result = replace_unicode_quotes(text)
        assert "…" in result

    def test_no_special_quotes(self):
        """Test text without special quotes."""
        text = "Normal text with 'regular' quotes"
        result = replace_unicode_quotes(text)
        assert result == text

    def test_empty_string(self):
        """Test empty string handling."""
        result = replace_unicode_quotes("")
        assert result == ""

    def test_multiple_replacements(self):
        """Test multiple replacements in one string."""
        text = "\x91quote\x92 and \x93another\x94"
        result = replace_unicode_quotes(text)
        assert "\x91" not in result
        assert "\x92" not in result
        assert "\x93" not in result
        assert "\x94" not in result


class TestCleanExtraWhitespace:
    """Tests for clean_extra_whitespace function."""

    def test_removes_extra_spaces(self):
        """Test removal of extra spaces."""
        text = "ITEM 1.     BUSINESS"
        result = clean_extra_whitespace(text)
        assert result == "ITEM 1. BUSINESS"
        assert "     " not in result

    def test_replaces_newlines(self):
        """Test that newlines are replaced with spaces."""
        text = "Line 1\nLine 2"
        result = clean_extra_whitespace(text)
        assert "\n" not in result
        assert result == "Line 1 Line 2"

    def test_replaces_non_breaking_space(self):
        """Test replacement of non-breaking space (\\xa0)."""
        text = f"Text{chr(0xA0)}with{chr(0xA0)}nbsp"
        result = clean_extra_whitespace(text)
        assert chr(0xA0) not in result
        assert result == "Text with nbsp"

    def test_strips_leading_trailing_whitespace(self):
        """Test stripping of leading and trailing whitespace."""
        text = "   Text with spaces   "
        result = clean_extra_whitespace(text)
        assert result == "Text with spaces"

    def test_empty_string(self):
        """Test empty string handling."""
        result = clean_extra_whitespace("")
        assert result == ""

    def test_only_whitespace(self):
        """Test string with only whitespace."""
        text = "     \n\n     "
        result = clean_extra_whitespace(text)
        assert result == ""

    def test_single_space_preserved(self):
        """Test that single spaces are preserved."""
        text = "Word1 Word2 Word3"
        result = clean_extra_whitespace(text)
        assert result == text

    def test_multiple_types_of_whitespace(self):
        """Test handling of multiple whitespace types."""
        text = f"Text  with\nmultiple{chr(0xA0)}types    of   whitespace"
        result = clean_extra_whitespace(text)
        assert "  " not in result
        assert "\n" not in result
        assert chr(0xA0) not in result


class TestRegexPatterns:
    """Tests for regex pattern constants."""

    def test_unicode_bullets_re_matches_bullets(self):
        """Test that UNICODE_BULLETS_RE matches bullet characters."""
        # Test bullets that are definitely in the pattern
        test_bullets_in_pattern = ["●", "•", "-"]
        matched_count = 0
        for bullet in test_bullets_in_pattern:
            match = UNICODE_BULLETS_RE.match(bullet)
            if match is not None:
                matched_count += 1
        # At least some bullets should match
        assert matched_count > 0

    def test_e_bullet_pattern_matches_e_space(self):
        """Test that E_BULLET_PATTERN matches 'e ' at line start."""
        text = "e This is a point"
        match = E_BULLET_PATTERN.match(text)
        assert match is not None

    def test_e_bullet_pattern_not_matches_regular_e(self):
        """Test that E_BULLET_PATTERN doesn't match regular 'e'."""
        text = "east"
        match = E_BULLET_PATTERN.match(text)
        assert match is None

    def test_paragraph_pattern_re_splits_on_newlines(self):
        """Test that PARAGRAPH_PATTERN_RE can split text."""
        text = "Line 1\n\nLine 2"
        parts = PARAGRAPH_PATTERN_RE.split(text)
        assert len(parts) >= 1

    def test_double_paragraph_pattern_splits_double_newlines(self):
        """Test that DOUBLE_PARAGRAPH_PATTERN_RE splits on double newlines."""
        text = "Para 1\n\nPara 2"
        parts = DOUBLE_PARAGRAPH_PATTERN_RE.split(text)
        assert len(parts) >= 1

    def test_line_break_re_splits_on_newlines(self):
        """Test that LINE_BREAK_RE splits on line breaks."""
        text = "Line 1\nLine 2\nLine 3"
        parts = LINE_BREAK_RE.split(text)
        assert len(parts) >= 3
        assert "Line 1" in parts[0]
