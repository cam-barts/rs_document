import time
from pathlib import Path

import pytest
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rs_document import Document, clean_and_split_docs
from rs_document.post_processors import UNSTRUCTURED_POST_PROCESSORS

# Path to test files relative to this test file
TEST_DIR = Path(__file__).parent


@pytest.fixture()
def document_fixture() -> Document:
    """Create a document with known attributes."""
    content = "A" * 20
    data = {"Hello": "World"}
    return Document(page_content=content, metadata=data)


def test_attributes(document_fixture: Document) -> None:
    assert document_fixture.page_content == "A" * 20
    assert document_fixture.metadata == {"Hello": "World"}


def test_splitting(document_fixture: Document) -> None:
    split = document_fixture.split_on_num_characters(5)
    assert len(split) == len(document_fixture.page_content) / 5
    assert split[0].metadata == {"Hello": "World"}
    assert split[0].page_content == "AAAAA"


def test_repr(document_fixture: Document) -> None:
    assert (
        repr(document_fixture)
        == 'Document(page_content="AAAAAAAAAAAAAAAAAAAA", metadata={"Hello": "World"})'
    )


def test_str(document_fixture: Document) -> None:
    assert (
        str(document_fixture)
        == 'Document(page_content="AAAAAAAAAAAAAAAAAAAA", metadata={"Hello": "World"})'
    )


@pytest.mark.slow()
@pytest.mark.parametrize("number_files", [10_000, 25_000, 1_000_000])
def test_less_than_5_second_speed(number_files) -> None:
    # Expected performance is about 15,000 docs per second.
    MAX_TIME_SECONDS = number_files / 15_000
    metadata = {"Hello": "World"}

    with open(TEST_DIR / "lorem.txt") as textfile:
        content = textfile.read()

    docs: list[Document] = []
    for _ in range(number_files):
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)

    rust_now = time.time()
    clean_and_split_docs(docs, 2000)
    rust_later = time.time()

    rust_time = rust_later - rust_now

    assert rust_time <= MAX_TIME_SECONDS


@pytest.mark.slow()
@pytest.mark.parametrize("number_files", [1_000, 10_000, 25_000])
def test_performance_improvement_over_python(number_files) -> None:
    # Want at least 15 times performance improvement for this to be viable at various
    # size inputs
    EXPECTED_PERFORMANCE_IMPROVEMENT = 15
    metadata = {"Hello": "World"}

    with open(TEST_DIR / "lorem.txt") as textfile:
        content = textfile.read()

    docs: list[Document] = []
    for _ in range(number_files):
        doc = Document(page_content=content, metadata=metadata)
        docs.append(doc)

    rust_now = time.time()
    clean_and_split_docs(docs, 2000)
    rust_later = time.time()

    rust_time = rust_later - rust_now

    python_docs: list[Document] = []
    for _ in range(number_files):
        doc = Document(page_content=content, metadata=metadata)
        python_docs.append(doc)

    python_now = time.time()
    for document in python_docs:
        for processor in UNSTRUCTURED_POST_PROCESSORS:
            document.page_content = processor(document.page_content)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=2000 / 3,
        length_function=len,
        is_separator_regex=False,
    )

    python_docs = text_splitter.split_documents(python_docs)

    python_later = time.time()

    python_time = python_later - python_now

    assert (python_time / rust_time) >= EXPECTED_PERFORMANCE_IMPROVEMENT
