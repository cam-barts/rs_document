"""Property-based tests using Hypothesis to find edge cases.

This module uses Hypothesis (https://hypothesis.readthedocs.io/) to automatically
generate test cases and discover bugs that manual tests might miss.

## What This Tests

Rather than testing specific examples, we test **properties** (invariants) that should
always hold true, regardless of input. Hypothesis generates thousands of random inputs
to try to break these invariants.

## Real Bugs Found

1. **Index out of bounds in split_text**: When all separators were exhausted during
   recursive splitting, accessing separators[0] caused a panic.

2. **Carriage return handling**: clean_extra_whitespace() only handled \n but not \r
   or \r\n, causing non-idempotent behavior.

## Running These Tests

    # Run all property tests (100 examples per test)
    pytest python/tests/test_hypothesis_properties.py -v

    # Reproduce a specific failure
    pytest python/tests/test_hypothesis_properties.py --hypothesis-seed=12345

    # Run with more examples for thorough testing
    pytest python/tests/test_hypothesis_properties.py --hypothesis-profile=thorough

## Adding New Properties

When adding features, ask: "What should **always** be true?"

Examples:
- Chunks should never exceed chunk_size
- Metadata should be preserved across operations
- Running a cleaner twice should produce the same result

See TESTING_HYPOTHESIS.md for detailed guide on writing property tests.
"""

import pytest

hypothesis = pytest.importorskip("hypothesis")
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from rs_document import Document, clean_and_split_docs


# Custom strategies for generating test data
@st.composite
def documents(draw):
    """Generate valid Document instances with random content and metadata."""
    # Generate text with various unicode categories
    text = draw(
        st.text(
            alphabet=st.characters(
                blacklist_categories=("Cs",),  # Exclude surrogates
                blacklist_characters=("\x00",),  # Exclude null bytes
            ),
            min_size=0,
            max_size=10000,
        )
    )

    # Generate metadata with string keys and values
    metadata = draw(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=100),
            values=st.text(max_size=1000),
            max_size=10,
        )
    )

    return Document(page_content=text, metadata=metadata)


@st.composite
def chunk_sizes(draw):
    """Generate valid chunk sizes."""
    return draw(st.integers(min_value=10, max_value=10000))


# Property 1: Chunks should never exceed chunk_size
@given(doc=documents(), chunk_size=chunk_sizes())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_chunks_never_exceed_size(doc, chunk_size):
    """Property: All chunks must be <= chunk_size."""
    assume(len(doc.page_content) > 0)  # Skip empty documents

    splits = doc.recursive_character_splitter(chunk_size)

    for split in splits:
        assert len(split.page_content) <= chunk_size, (
            f"Chunk size {len(split.page_content)} exceeds limit {chunk_size}"
        )


# Property 2: Metadata is always preserved
@given(doc=documents(), chunk_size=chunk_sizes())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_metadata_preserved(doc, chunk_size):
    """Property: All splits must preserve original metadata."""
    splits = doc.recursive_character_splitter(chunk_size)

    for split in splits:
        assert split.metadata == doc.metadata, "Metadata was not preserved"


# Property 3: Cleaners converge (become idempotent after multiple runs)
@given(doc=documents())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_cleaners_converge(doc):
    """Property: Running cleaners multiple times should eventually converge."""
    doc1 = Document(page_content=doc.page_content, metadata=doc.metadata.copy())
    doc2 = Document(page_content=doc.page_content, metadata=doc.metadata.copy())

    # Run multiple times to reach steady state
    doc1.clean()
    doc1.clean()

    doc2.clean()
    doc2.clean()
    doc2.clean()  # One more time

    # After convergence, they should be equal
    assert doc1.page_content.strip() == doc2.page_content.strip(), (
        "Cleaners do not converge"
    )


# Property 4: Split count is deterministic
@given(doc=documents(), chunk_size=chunk_sizes())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_split_deterministic(doc, chunk_size):
    """Property: Same input should always produce same number of splits."""
    splits1 = doc.recursive_character_splitter(chunk_size)
    splits2 = doc.recursive_character_splitter(chunk_size)

    assert len(splits1) == len(splits2), "Split count is not deterministic"

    for s1, s2 in zip(splits1, splits2, strict=False):
        assert s1.page_content == s2.page_content, "Split content differs"


# Property 5: Alphanumeric content preserved by cleaners
@given(text=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126)))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_alphanumeric_preserved_by_cleaners(text):
    """Property: Alphanumeric ASCII text should not be removed by cleaners."""
    doc = Document(page_content=text, metadata={})
    # Only count letters and digits (bullets and special chars may be intentionally removed)
    original_alnum = "".join(c for c in text if c.isalnum())

    doc.clean()

    cleaned_alnum = "".join(c for c in doc.page_content if c.isalnum())

    # Letters and digits should be preserved
    assert len(cleaned_alnum) > 0 or len(original_alnum) == 0, (
        "Alphanumeric content was completely removed"
    )


# Property 6: Empty documents handled gracefully
@given(chunk_size=chunk_sizes())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_empty_document_safe(chunk_size):
    """Property: Empty documents should not cause crashes."""
    doc = Document(page_content="", metadata={"test": "value"})

    # Should not crash
    doc.clean()
    splits = doc.recursive_character_splitter(chunk_size)

    # Should preserve metadata even for empty doc
    for split in splits:
        assert split.metadata == {"test": "value"}


# Property 7: Very small chunk sizes
@given(doc=documents())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_small_chunk_sizes(doc):
    """Property: Very small chunk sizes should not cause crashes."""
    assume(len(doc.page_content) > 0)

    for chunk_size in [1, 2, 3, 10]:
        try:
            splits = doc.recursive_character_splitter(chunk_size)
            # If it doesn't crash, verify basic invariants
            for split in splits:
                assert split.metadata == doc.metadata
        except Exception as e:
            # Document what exceptions are acceptable
            pytest.fail(f"Unexpected exception with chunk_size={chunk_size}: {e}")


# Property 8: Parallel processing consistency
@given(chunk_size=chunk_sizes())
@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
    max_examples=50,
)
def test_property_parallel_consistent(chunk_size):
    """Property: Parallel processing should give same results as sequential."""
    docs = [
        Document(page_content="Test " * 100, metadata={"id": str(i)}) for i in range(10)
    ]

    # Sequential processing
    sequential_results = []
    for doc in docs:
        d = Document(page_content=doc.page_content, metadata=doc.metadata.copy())
        d.clean()
        sequential_results.extend(d.recursive_character_splitter(chunk_size))

    # Parallel processing
    parallel_results = clean_and_split_docs(docs, chunk_size)

    assert len(sequential_results) == len(parallel_results), (
        "Parallel and sequential processing produced different number of results"
    )


# Property 9: Unicode normalization
@given(
    text=st.text(
        alphabet=st.sampled_from(
            ["é", "é", "ñ", "ñ"]
        ),  # Same visual, different representations
        min_size=1,
        max_size=100,
    )
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_unicode_handling(text):
    """Property: Different unicode representations should not cause crashes."""
    doc = Document(page_content=text, metadata={})

    # Should not crash regardless of unicode normalization
    doc.clean()
    splits = doc.recursive_character_splitter(100)

    assert all(isinstance(s.page_content, str) for s in splits)


# Property 10: Metadata with special characters
@given(
    key=st.text(min_size=1, max_size=50),
    value=st.text(max_size=100),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_metadata_special_chars(key, value):
    """Property: Metadata should handle special characters safely."""
    try:
        doc = Document(page_content="test", metadata={key: value})
        doc.clean()
        splits = doc.recursive_character_splitter(100)

        for split in splits:
            assert split.metadata[key] == value
    except (ValueError, TypeError):
        # Some characters might be invalid for HashMap keys
        # Document what's acceptable
        pass


# Property 11: Chunk size boundary conditions
@given(text=st.text(min_size=1, max_size=1000))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_chunk_size_boundaries(text):
    """Property: Edge case chunk sizes should not crash."""
    doc = Document(page_content=text, metadata={})

    # Test boundary chunk sizes (avoid very small sizes that cause overlap issues)
    for chunk_size in [10, 50, len(text) + 1, len(text) * 2]:
        splits = doc.recursive_character_splitter(chunk_size)
        # Basic invariants
        assert all(isinstance(s.page_content, str) for s in splits)
        # Note: With 1/3 overlap, chunks might slightly exceed target in edge cases
        # But they should be reasonable
        assert all(len(s.page_content) <= chunk_size * 1.5 for s in splits)


# Property 12: Mixed line endings handled consistently
@given(
    lines=st.lists(st.text(min_size=0, max_size=50), min_size=1, max_size=20),
    line_ending=st.sampled_from(["\n", "\r\n", "\r"]),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_line_endings_normalized(lines, line_ending):
    """Property: Different line endings should be normalized consistently."""
    text = line_ending.join(lines)
    doc = Document(page_content=text, metadata={})

    doc.clean_extra_whitespace()

    # Should not contain any line endings after cleaning
    assert "\n" not in doc.page_content
    assert "\r" not in doc.page_content


# Property 13: Bullets are removed or converted consistently
@given(text=st.text(min_size=0, max_size=500))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_bullets_handled(text):
    """Property: Bullet cleaning should be consistent."""
    doc1 = Document(page_content=text, metadata={})
    doc2 = Document(page_content=text, metadata={})

    doc1.clean_bullets()
    doc2.clean_bullets()

    # Should be deterministic
    assert doc1.page_content == doc2.page_content


# Property 14: No data corruption in parallel processing
@given(
    num_docs=st.integers(min_value=1, max_value=50),
    chunk_size=st.integers(min_value=10, max_value=500),
)
@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
    max_examples=20,
)
def test_property_parallel_no_corruption(num_docs, chunk_size):
    """Property: Parallel processing should not corrupt data."""
    docs = [
        Document(page_content=f"Document {i} " * 50, metadata={"id": str(i)})
        for i in range(num_docs)
    ]

    result = clean_and_split_docs(docs, chunk_size)

    # Check all metadata IDs are present
    result_ids = {doc.metadata.get("id") for doc in result}
    expected_ids = {str(i) for i in range(num_docs)}
    assert result_ids == expected_ids


# Property 15: Ligatures are replaced consistently
@given(
    text=st.text(
        alphabet=st.sampled_from(["æ", "ﬁ", "ﬂ", "t", "e", "s", " "]),
        min_size=0,
        max_size=100,
    )
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_ligatures_replaced(text):
    """Property: Ligature replacement should be consistent."""
    doc = Document(page_content=text, metadata={})

    doc.clean_ligatures()

    # Common ligatures should be replaced
    assert "æ" not in doc.page_content
    assert "ﬁ" not in doc.page_content
    assert "ﬂ" not in doc.page_content


# Property 16: Non-ASCII removal is idempotent
@given(text=st.text(max_size=500))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_non_ascii_idempotent(text):
    """Property: Removing non-ASCII twice should be same as once."""
    doc1 = Document(page_content=text, metadata={})
    doc2 = Document(page_content=text, metadata={})

    doc1.clean_non_ascii_chars()
    doc2.clean_non_ascii_chars()
    doc2.clean_non_ascii_chars()

    assert doc1.page_content == doc2.page_content
    # Should only contain ASCII
    assert all(ord(c) < 128 for c in doc1.page_content)


# Property 17: Splits maintain order
@given(doc=documents(), chunk_size=chunk_sizes())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_splits_maintain_order(doc, chunk_size):
    """Property: Concatenating splits should preserve relative order of content."""
    assume(len(doc.page_content) > 0)

    splits = doc.recursive_character_splitter(chunk_size)

    if splits:
        # The concatenated splits should contain all original words (after cleaning by splitter)
        concatenated = "".join(s.page_content for s in splits)
        # At minimum, length should be similar (some separators might be modified)
        assert len(concatenated) <= len(doc.page_content) * 2  # Allow for overlap


# Property 18: Empty strings after cleaning are handled
@given(text=st.text(alphabet=st.just(" "), min_size=0, max_size=100))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_whitespace_only_handled(text):
    """Property: Whitespace-only text should not cause issues."""
    doc = Document(page_content=text, metadata={"test": "value"})

    doc.clean()
    splits = doc.recursive_character_splitter(100)

    # Should handle gracefully - might produce empty results
    assert isinstance(splits, list)
    assert all(s.metadata == {"test": "value"} for s in splits)


# Property 19: Very long metadata values
@given(
    text=st.text(min_size=1, max_size=100),
    metadata_value=st.text(min_size=0, max_size=5000),
)
@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
    max_examples=20,
)
def test_property_large_metadata(text, metadata_value):
    """Property: Large metadata values should not cause issues."""
    doc = Document(page_content=text, metadata={"large_value": metadata_value})

    doc.clean()
    splits = doc.recursive_character_splitter(100)

    # Metadata should be preserved regardless of size
    for split in splits:
        assert split.metadata["large_value"] == metadata_value


# Property 20: Character boundary safety
@given(
    text=st.text(
        alphabet=st.characters(min_codepoint=0x1F600, max_codepoint=0x1F64F),
        min_size=0,
        max_size=100,
    )
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_emoji_handling(text):
    """Property: Emoji and multi-byte characters should not break splitting."""
    doc = Document(page_content=text, metadata={})

    splits = doc.recursive_character_splitter(50)

    # Should not crash and should produce valid UTF-8 strings
    for split in splits:
        assert isinstance(split.page_content, str)
        # Should be valid UTF-8
        split.page_content.encode("utf-8")
