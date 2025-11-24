from rs_document import Document


def test_non_ascii_characters_cleanup() -> None:
    doc = Document(
        page_content="\x88This text contains non-ascii characters!\x88",
        metadata={},
    )
    assert "\x88" in doc.page_content
    doc.clean_non_ascii_chars()
    assert (
        str(doc)
        == 'Document(page_content="This text contains non-ascii characters!", metadata={})'
    )
    assert "\x88" not in doc.page_content


def test_bullet_characters_cleanup() -> None:
    doc = Document(page_content="●  This is an excellent point!", metadata={})
    assert "●" in doc.page_content
    doc.clean_bullets()
    assert (
        str(doc) == 'Document(page_content="This is an excellent point!", metadata={})'
    )
    assert "●" not in doc.page_content


def test_ligature_cleanup() -> None:
    doc = Document(page_content="æ This is an excellent point!", metadata={})
    assert "æ" in doc.page_content
    doc.clean_ligatures()
    assert (
        str(doc)
        == 'Document(page_content="ae This is an excellent point!", metadata={})'
    )
    assert "æ" not in doc.page_content


def test_extra_whitespace_cleanup() -> None:
    doc = Document(page_content="ITEM 1.     BUSINESS ", metadata={})
    doc.clean_extra_whitespace()
    assert str(doc) == 'Document(page_content="ITEM 1. BUSINESS", metadata={})'
