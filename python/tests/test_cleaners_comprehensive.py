"""Comprehensive tests for all document cleaning methods."""

from rs_document import Document


class TestCleanNonAsciiChars:
    """Tests for clean_non_ascii_chars method."""

    def test_removes_non_ascii_characters(self) -> None:
        doc = Document(
            page_content="\x88This text contains non-ascii characters!\x88",
            metadata={},
        )
        assert "\x88" in doc.page_content
        doc.clean_non_ascii_chars()
        assert doc.page_content == "This text contains non-ascii characters!"
        assert "\x88" not in doc.page_content

    def test_preserves_ascii_characters(self) -> None:
        doc = Document(page_content="Hello World 123!@#", metadata={})
        doc.clean_non_ascii_chars()
        assert doc.page_content == "Hello World 123!@#"

    def test_handles_empty_string(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.clean_non_ascii_chars()
        assert doc.page_content == ""

    def test_removes_unicode_characters(self) -> None:
        doc = Document(page_content="Hello 世界 World", metadata={})
        doc.clean_non_ascii_chars()
        assert doc.page_content == "Hello  World"

    def test_preserves_metadata(self) -> None:
        metadata = {"source": "test.txt", "page": "1"}
        doc = Document(page_content="\x88Test\x88", metadata=metadata)
        doc.clean_non_ascii_chars()
        assert doc.metadata == metadata


class TestCleanBullets:
    """Tests for clean_bullets method."""

    def test_removes_bullet_point(self) -> None:
        doc = Document(page_content="●  This is an excellent point!", metadata={})
        assert "●" in doc.page_content
        doc.clean_bullets()
        assert doc.page_content == "This is an excellent point!"
        assert "●" not in doc.page_content

    def test_removes_various_bullet_types(self) -> None:
        bullets = ["●", "•", "○", "◦", "▪", "▫", "–"]
        for bullet in bullets:
            doc = Document(page_content=f"{bullet} Test item", metadata={})
            doc.clean_bullets()
            # Should remove the bullet and clean up whitespace
            assert bullet not in doc.page_content

    def test_handles_no_bullets(self) -> None:
        doc = Document(page_content="This text has no bullets", metadata={})
        original = doc.page_content
        doc.clean_bullets()
        assert doc.page_content == original

    def test_handles_empty_string(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.clean_bullets()
        assert doc.page_content == ""

    def test_preserves_metadata(self) -> None:
        metadata = {"source": "test.txt"}
        doc = Document(page_content="● Test", metadata=metadata)
        doc.clean_bullets()
        assert doc.metadata == metadata


class TestCleanLigatures:
    """Tests for clean_ligatures method."""

    def test_replaces_ae_ligature(self) -> None:
        doc = Document(page_content="æ This is an excellent point!", metadata={})
        assert "æ" in doc.page_content
        doc.clean_ligatures()
        assert doc.page_content == "ae This is an excellent point!"
        assert "æ" not in doc.page_content

    def test_replaces_fi_ligature(self) -> None:
        doc = Document(page_content="The beneﬁts are clear", metadata={})
        doc.clean_ligatures()
        assert doc.page_content == "The benefits are clear"

    def test_replaces_fl_ligature(self) -> None:
        doc = Document(page_content="The ﬂower is beautiful", metadata={})
        doc.clean_ligatures()
        assert doc.page_content == "The flower is beautiful"

    def test_replaces_multiple_ligatures(self) -> None:
        doc = Document(page_content="ﬁnancial beneﬁts for æsthetics", metadata={})
        doc.clean_ligatures()
        assert doc.page_content == "financial benefits for aesthetics"

    def test_handles_no_ligatures(self) -> None:
        doc = Document(page_content="Normal text without ligatures", metadata={})
        original = doc.page_content
        doc.clean_ligatures()
        assert doc.page_content == original

    def test_handles_empty_string(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.clean_ligatures()
        assert doc.page_content == ""


class TestCleanExtraWhitespace:
    """Tests for clean_extra_whitespace method."""

    def test_removes_extra_spaces(self) -> None:
        doc = Document(page_content="ITEM 1.     BUSINESS ", metadata={})
        doc.clean_extra_whitespace()
        assert doc.page_content == "ITEM 1. BUSINESS"

    def test_replaces_newlines_with_spaces(self) -> None:
        doc = Document(page_content="Line 1\nLine 2\nLine 3", metadata={})
        doc.clean_extra_whitespace()
        assert doc.page_content == "Line 1 Line 2 Line 3"

    def test_removes_non_breaking_spaces(self) -> None:
        doc = Document(page_content=f"Word{chr(0xA0)}Word", metadata={})
        doc.clean_extra_whitespace()
        assert doc.page_content == "Word Word"

    def test_trims_leading_trailing_whitespace(self) -> None:
        doc = Document(page_content="  Test content  ", metadata={})
        doc.clean_extra_whitespace()
        assert doc.page_content == "Test content"

    def test_handles_multiple_whitespace_types(self) -> None:
        doc = Document(page_content=f"A    B\nC{chr(0xA0)}D", metadata={})
        doc.clean_extra_whitespace()
        assert doc.page_content == "A B C D"

    def test_handles_empty_string(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.clean_extra_whitespace()
        assert doc.page_content == ""


class TestGroupBrokenParagraphs:
    """Tests for group_broken_paragraphs method."""

    def test_groups_broken_paragraphs(self) -> None:
        text = """The big red fox
is walking down the lane.

At the end of the lane
the fox met a bear."""
        doc = Document(page_content=text, metadata={})
        doc.group_broken_paragraphs()
        # Should group line-broken paragraphs
        assert "\n\n" in doc.page_content
        lines = doc.page_content.split("\n\n")
        assert len(lines) == 2

    def test_handles_bullet_paragraphs(self) -> None:
        text = """● The big red fox
is walking down the lane.

● At the end of the lane
the fox met a friendly bear."""
        doc = Document(page_content=text, metadata={})
        doc.group_broken_paragraphs()
        # Should preserve bullet structure while grouping
        assert "●" in doc.page_content or "·" in doc.page_content

    def test_handles_empty_string(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.group_broken_paragraphs()
        assert doc.page_content == ""

    def test_preserves_short_lines(self) -> None:
        text = """One
Two
Three
Four"""
        doc = Document(page_content=text, metadata={})
        doc.group_broken_paragraphs()
        # Short lines (< 5 words) should be preserved separately
        assert "\n\n" in doc.page_content


class TestNewLineGrouper:
    """Tests for new_line_grouper method."""

    def test_groups_single_line_breaks(self) -> None:
        text = """Iwan Roberts
Roberts celebrating after scoring a goal for Norwich City
in 2004"""
        doc = Document(page_content=text, metadata={})
        doc.new_line_grouper()
        # Should convert single line breaks to double
        assert "\n\n" in doc.page_content

    def test_removes_empty_lines(self) -> None:
        text = """Line 1

Line 2


Line 3"""
        doc = Document(page_content=text, metadata={})
        doc.new_line_grouper()
        lines = [line for line in doc.page_content.split("\n\n") if line]
        assert len(lines) == 3

    def test_handles_empty_string(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.new_line_grouper()
        assert doc.page_content == ""


class TestAutoParagraphGrouper:
    """Tests for auto_paragraph_grouper method."""

    def test_handles_dense_text(self) -> None:
        # Text with few line breaks (< 10% empty lines)
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        doc = Document(page_content=text, metadata={})
        doc.auto_paragraph_grouper()
        # Should use new_line_grouper
        assert "\n\n" in doc.page_content

    def test_handles_sparse_text(self) -> None:
        # Text with many line breaks (>= 10% empty lines)
        text = """Paragraph 1

Paragraph 2

Paragraph 3"""
        doc = Document(page_content=text, metadata={})
        doc.auto_paragraph_grouper()
        # Should use group_broken_paragraphs
        assert "\n\n" in doc.page_content

    def test_handles_empty_string(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.auto_paragraph_grouper()
        assert doc.page_content == ""


class TestCleanMethod:
    """Tests for the combined clean() method."""

    def test_runs_all_cleaners(self) -> None:
        doc = Document(
            page_content="●  \x88Test    with\nall\nproblems æ",
            metadata={},
        )
        doc.clean()
        # Should have removed bullet, non-ascii, ligature, extra whitespace
        assert "●" not in doc.page_content
        assert "\x88" not in doc.page_content
        assert "æ" not in doc.page_content
        # Should have cleaned up whitespace and grouped paragraphs

    def test_preserves_metadata(self) -> None:
        metadata = {"source": "test.txt", "page": "42"}
        doc = Document(page_content="●  Test", metadata=metadata)
        doc.clean()
        assert doc.metadata == metadata

    def test_handles_empty_document(self) -> None:
        doc = Document(page_content="", metadata={})
        doc.clean()
        assert doc.page_content == ""

    def test_handles_clean_document(self) -> None:
        clean_text = "This is already clean text."
        doc = Document(page_content=clean_text, metadata={})
        doc.clean()
        # Should not damage already clean text
        assert "This is already clean text" in doc.page_content


class TestMetadataPreservation:
    """Tests to ensure metadata is preserved across all operations."""

    def test_metadata_preserved_through_all_cleaners(self) -> None:
        metadata = {"source": "test.pdf", "page": "1", "author": "Test"}
        doc = Document(page_content="● Test content æ", metadata=metadata)

        doc.clean_non_ascii_chars()
        assert doc.metadata == metadata

        doc.clean_bullets()
        assert doc.metadata == metadata

        doc.clean_ligatures()
        assert doc.metadata == metadata

        doc.clean_extra_whitespace()
        assert doc.metadata == metadata

    def test_empty_metadata_preserved(self) -> None:
        doc = Document(page_content="Test", metadata={})
        doc.clean()
        assert doc.metadata == {}
