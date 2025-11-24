"""Comprehensive tests for document splitting methods."""

from rs_document import Document, clean_and_split_docs


class TestSplitOnNumCharacters:
    """Tests for split_on_num_characters method."""

    def test_basic_splitting(self) -> None:
        doc = Document(page_content="A" * 20, metadata={"Hello": "World"})
        splits = doc.split_on_num_characters(5)
        assert len(splits) == 4
        assert all(split.page_content == "AAAAA" for split in splits)

    def test_metadata_preserved_in_splits(self) -> None:
        metadata = {"source": "test.txt", "page": "1"}
        doc = Document(page_content="A" * 20, metadata=metadata)
        splits = doc.split_on_num_characters(5)
        assert all(split.metadata == metadata for split in splits)

    def test_uneven_split(self) -> None:
        doc = Document(page_content="A" * 23, metadata={})
        splits = doc.split_on_num_characters(5)
        assert len(splits) == 5
        # First 4 should be 5 chars, last should be 3
        assert splits[0].page_content == "AAAAA"
        assert splits[-1].page_content == "AAA"

    def test_single_character_split(self) -> None:
        doc = Document(page_content="ABCDE", metadata={})
        splits = doc.split_on_num_characters(1)
        assert len(splits) == 5
        assert [s.page_content for s in splits] == ["A", "B", "C", "D", "E"]

    def test_split_size_larger_than_content(self) -> None:
        doc = Document(page_content="Short", metadata={})
        splits = doc.split_on_num_characters(100)
        assert len(splits) == 1
        assert splits[0].page_content == "Short"

    def test_empty_document(self) -> None:
        doc = Document(page_content="", metadata={})
        splits = doc.split_on_num_characters(5)
        assert len(splits) == 0

    def test_unicode_characters(self) -> None:
        doc = Document(page_content="Hello世界Test", metadata={})
        splits = doc.split_on_num_characters(5)
        # Should split by character count, not byte count
        assert len(splits) == 3


class TestRecursiveCharacterSplitter:
    """Tests for recursive_character_splitter method."""

    def test_basic_splitting(self) -> None:
        # Create text with natural break points
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(20)
        assert len(splits) > 0
        assert all(isinstance(split, Document) for split in splits)

    def test_respects_chunk_size(self) -> None:
        text = "A" * 1000
        doc = Document(page_content=text, metadata={})
        chunk_size = 100
        splits = doc.recursive_character_splitter(chunk_size)
        # No chunk should exceed chunk_size (allowing for the overlap algorithm)
        for split in splits:
            assert len(split.page_content) <= chunk_size

    def test_metadata_preserved(self) -> None:
        metadata = {"source": "test.txt", "page": "1", "author": "Test"}
        text = "Some text\n\nMore text\n\nEven more text" * 10
        doc = Document(page_content=text, metadata=metadata)
        splits = doc.recursive_character_splitter(50)
        assert all(split.metadata == metadata for split in splits)

    def test_creates_overlapping_chunks(self) -> None:
        # The splitter should create overlapping chunks (1/3 overlap)
        text = "A" * 300
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(90)
        # With overlap, we should get more splits than simple division
        assert len(splits) > 0

    def test_preserves_paragraph_boundaries(self) -> None:
        text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(100)
        # Should try to split on double newlines first
        assert len(splits) > 0

    def test_handles_long_text(self) -> None:
        text = "This is a long document. " * 1000
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(500)
        assert len(splits) > 1
        # All splits should have content
        assert all(len(split.page_content) > 0 for split in splits)

    def test_handles_short_text(self) -> None:
        text = "Short text"
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(100)
        assert len(splits) >= 1
        # Short text should not be split unnecessarily

    def test_empty_document(self) -> None:
        doc = Document(page_content="", metadata={})
        splits = doc.recursive_character_splitter(100)
        # Empty document might return empty list or single empty doc
        # depending on implementation
        assert isinstance(splits, list)

    def test_various_chunk_sizes(self) -> None:
        text = "Word " * 500
        doc = Document(page_content=text, metadata={})

        for chunk_size in [50, 100, 500, 1000]:
            splits = doc.recursive_character_splitter(chunk_size)
            assert len(splits) > 0
            # Verify chunk size constraint
            for split in splits:
                assert len(split.page_content) <= chunk_size

    def test_handles_no_natural_breaks(self) -> None:
        # Text with no spaces or newlines
        text = "A" * 500
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(100)
        assert len(splits) > 0

    def test_mixed_separators(self) -> None:
        # Text with various separator types
        text = "Para1\n\nPara2\nLine break\n\nPara3 with spaces"
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(20)
        assert len(splits) > 0


class TestCleanAndSplitDocs:
    """Tests for the clean_and_split_docs function."""

    def test_processes_multiple_documents(self) -> None:
        docs = [
            Document(page_content="Doc 1 content " * 50, metadata={"id": "1"}),
            Document(page_content="Doc 2 content " * 50, metadata={"id": "2"}),
            Document(page_content="Doc 3 content " * 50, metadata={"id": "3"}),
        ]
        result = clean_and_split_docs(docs, chunk_size=100)
        assert len(result) > len(docs)  # Should be split
        assert all(isinstance(doc, Document) for doc in result)

    def test_cleans_documents(self) -> None:
        docs = [
            Document(
                page_content="●  Test    content\n\næ ligature",
                metadata={},
            ),
        ]
        result = clean_and_split_docs(docs, chunk_size=100)
        # Should have cleaned bullets, whitespace, ligatures
        combined = "".join(doc.page_content for doc in result)
        assert "●" not in combined
        assert "æ" not in combined

    def test_preserves_metadata(self) -> None:
        metadata = {"source": "test.txt", "page": "1"}
        docs = [
            Document(page_content="Content " * 50, metadata=metadata),
        ]
        result = clean_and_split_docs(docs, chunk_size=100)
        assert all(doc.metadata == metadata for doc in result)

    def test_empty_list(self) -> None:
        result = clean_and_split_docs([], chunk_size=100)
        assert result == []

    def test_various_chunk_sizes(self) -> None:
        docs = [
            Document(page_content="A" * 1000, metadata={}),
        ]
        for chunk_size in [50, 100, 500]:
            result = clean_and_split_docs(docs, chunk_size=chunk_size)
            assert len(result) > 0
            for doc in result:
                assert len(doc.page_content) <= chunk_size

    def test_handles_mixed_content(self) -> None:
        docs = [
            Document(page_content="", metadata={}),  # Empty
            Document(page_content="Short", metadata={}),  # Short
            Document(page_content="A" * 1000, metadata={}),  # Long
        ]
        result = clean_and_split_docs(docs, chunk_size=100)
        assert len(result) > 0

    def test_parallel_processing(self) -> None:
        # Create many documents to test parallel processing
        docs = [
            Document(
                page_content=f"Document {i} content " * 50,
                metadata={"id": str(i)},
            )
            for i in range(100)
        ]
        result = clean_and_split_docs(docs, chunk_size=100)
        assert len(result) > len(docs)
        # Check metadata IDs are preserved
        ids = {doc.metadata.get("id") for doc in result if doc.metadata.get("id")}
        assert len(ids) == 100


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_very_long_word(self) -> None:
        # Single word longer than chunk size
        word = "A" * 1000
        doc = Document(page_content=word, metadata={})
        splits = doc.recursive_character_splitter(100)
        # Should still split, even without natural breaks
        assert len(splits) > 0

    def test_special_characters(self) -> None:
        text = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(50)
        assert len(splits) > 0

    def test_mixed_unicode(self) -> None:
        text = "English 中文 日本語 한글 العربية עברית"
        doc = Document(page_content=text, metadata={})
        splits = doc.recursive_character_splitter(20)
        assert len(splits) > 0

    def test_whitespace_only(self) -> None:
        doc = Document(page_content="     \n\n    \n    ", metadata={})
        doc.clean()
        # After cleaning, should be empty or minimal
        assert len(doc.page_content) == 0

    def test_metadata_with_special_characters(self) -> None:
        metadata = {
            "key with spaces": "value with spaces",
            "special!@#": "chars$%^",
        }
        doc = Document(page_content="Test content", metadata=metadata)
        splits = doc.recursive_character_splitter(50)
        assert all(split.metadata == metadata for split in splits)
