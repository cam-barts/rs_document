# RS Document

A opinionated Rust implementation of various common functions of LangChain's [Document model](https://github.com/langchain-ai/langchain/blob/master/libs/core/langchain_core/documents/base.py) as well as 
[Unstructured.io's post processors](https://github.com/Unstructured-IO/unstructured/blob/main/unstructured/cleaners/core.py). 

## Why?

I've been tinkering with different RAG projects and have landed on a set of processes that are pretty common between them. I was looking for a reason to try out the excellent [maturin](https://github.com/PyO3/maturin) build system that allows for rust to be brought in as a python package. Since my common processes involve alot of text processing over ususally a large number of documents, this seemed like a great project to get going with it.

# Installation

```sh
pip install rs-document
```

# Usage

The main function of this package is to quickly clean and split many documents.

```python
from rs_document import Document, clean_and_split_docs


# Create a document with known attributes
content = "A" * 4000
data = {"Hello": "World"}
doc = Document(page_content=content, metadata=data)


# Run all cleaners on the document
doc.clean()

# Recursively split document
doc.recursive_character_splitter(1000) # -> Produces list of documents

```

## Cleaners

The cleaners that are reimplemented from [Unstructured.io](https://github.com/Unstructured-IO/unstructured/blob/main/unstructured/cleaners/core.py) are:
 - clean_non_ascii_chars
 - clean_bullets
 - clean_ligatures
 - clean_extra_whitespace
 - group_broken_paragraphs
 - new_line_grouper
 - auto_paragraph_grouper

Instead of being standalone functions, I implemented them as methods on the Document class.

There is also a `.clean()` method, which will run all of the cleaners. 

The `test_cleaners.py` module shows how they can be used.

```python
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

```

## Splitters

There are two splitters:
 - split_on_num_characters
 - recursive_character_splitter

Similarly, they are implemented as methods on the doc class.

```python

def test_splitting(document_fixture: Document) -> None:
    split = document_fixture.split_on_num_characters(5)
    assert len(split) == len(document_fixture.page_content) / 5
    assert split[0].metadata == {"Hello": "World"}
    assert split[0].page_content == "AAAAA"

```

### A Note about `recursive_character_splitter`

The recursive character splitter is modeled after LangChain's recursive character splitter, 
but is absolutely not a 1:1 implementation. You will note that it doesn't take in a chunk overlap.
This is because I've implemented it to have an effective overlap of about 1/3 the chunk size, 
as this is the number I've landed on being the most useful in my tinkering. Also, it 
doesn't allow passing in seperators, because the default seperators seem to be the best 
in every situation I've encountered. This makes the interface as simple as passing in a 
`chunk_size`. 


## clean_and_split_docs function

To keep interfacing with this module as quick and easy in most of my projects as possible,
I've also implemented a wrapper function `clean_and_split_docs`, which takes in a list of 
documents (like what you'd get from a document loader) and a `chunk_size`, and it give back
a list of clean and split documents.


# Performance

I knew that rust has a leg up on text processing performance over python, but I wanted to 
be sure that the performance improvements would be worth taking on another dependancy.

I did some very scientific and rigorous testing on my personal machine, and cleaning and splitting
1,000 to 1,000,000 documents is somewhere between 40 and 75x faster with the rust implementation.

I added some tests to ensure as this package improves that those performace gains won't be lost.

The tests expect 25,000 documents to be processed per second, and for the rust version to be 
minimum 25 times faster than the python version. 
