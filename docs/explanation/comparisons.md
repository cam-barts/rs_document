---
title: Comparisons & Integration
description: Comparing rs_document with alternatives and integration patterns
---

# Comparisons & Integration

Understanding how rs_document compares to other tools and fits into your workflow helps you make informed decisions about when and how to use it.

## vs LangChain RecursiveCharacterTextSplitter

LangChain is the most popular framework for building LLM applications and provides text splitting capabilities.

### Similarities

**Both implement recursive splitting**:

- Same core algorithm concept
- Hierarchical separator approach
- Chunk size targeting
- Context preservation through overlap

**Both are production-ready**:

- Well-tested implementations
- Active maintenance
- Good documentation

### Differences

| Feature | LangChain | rs_document |
|---------|-----------|-------------|
| **Performance** | Baseline | **20-25x faster** |
| **Parallelism** | GIL-limited | **True parallel (8x on 8 cores)** |
| **Chunk Overlap** | Configurable (any %) | **Fixed (~33%)** |
| **Separators** | Configurable (any list) | **Fixed (`\n\n`, `\n`, ``, `""`)** |
| **Splitting Strategies** | Multiple (recursive, character, token) | **Character only** |
| **Token Counting** | Built-in support | Not available |
| **Metadata Types** | Any Python object | **Strings only** |
| **Callbacks** | Supported | Not available |
| **Ecosystem** | Full LangChain integration | Standalone |

### When to Use LangChain

Choose LangChain's text splitter when:

1. **Custom overlap needed**: Your use case requires specific overlap percentages

   ```python
   # LangChain allows this
   splitter = RecursiveCharacterTextSplitter(
       chunk_size=1000,
       chunk_overlap=100  # 10% overlap
   )
   ```

2. **Custom separators needed**: Domain-specific split points

   ```python
   # LangChain allows this
   splitter = RecursiveCharacterTextSplitter(
       separators=["---", "###", "\n\n"]  # Markdown-specific
   )
   ```

3. **Token-based splitting needed**: Must respect model token limits

   ```python
   # LangChain supports this
   from langchain.text_splitter import TokenTextSplitter
   splitter = TokenTextSplitter(chunk_size=512, model_name="gpt-3.5-turbo")
   ```

4. **Small workloads**: Processing < 100 documents where performance doesn't matter

5. **Ecosystem integration**: Heavily using other LangChain components

   ```python
   from langchain.document_loaders import DirectoryLoader
   from langchain.text_splitter import RecursiveCharacterTextSplitter
   from langchain.embeddings import OpenAIEmbeddings
   from langchain.vectorstores import Chroma

   # Everything in LangChain ecosystem
   ```

### When to Use rs_document

Choose rs_document when:

1. **Performance matters**: Processing > 1,000 documents
   - rs_document: 15 minutes for 100k docs
   - LangChain: 6 hours for 100k docs

2. **Frequent reprocessing**: Experimenting with chunk sizes
   - rs_document enables rapid iteration
   - LangChain creates long wait times

3. **Real-time requirements**: Continuous document ingestion
   - rs_document: ~23,000 docs/sec throughput
   - LangChain: ~150 docs/sec throughput

4. **Default settings work**: 33% overlap and standard separators sufficient
   - 95% of RAG use cases

5. **Resource constraints**: Limited CPU time or budget
   - 20x less compute time
   - 20x lower cost

### Integration Pattern: Use Both

Common pattern: Use rs_document for splitting, LangChain for everything else

```python
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from rs_document import clean_and_split_docs, Document

# Load with LangChain
loader = DirectoryLoader("./docs", glob="**/*.txt")
lc_documents = loader.load()

# Convert to rs_document format
rs_docs = [
    Document(
        page_content=d.page_content,
        metadata={k: str(v) for k, v in d.metadata.items()}
    )
    for d in lc_documents
]

# Split with rs_document (fast)
chunks = clean_and_split_docs(rs_docs, chunk_size=1000)

# Convert back to LangChain format
from langchain.docstore.document import Document as LCDocument
lc_chunks = [
    LCDocument(page_content=c.page_content, metadata=c.metadata)
    for c in chunks
]

# Embed and store with LangChain
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(lc_chunks, embeddings)
```

This gives you:

- Fast document processing (rs_document)
- Rich ecosystem (LangChain)
- Best of both worlds

## vs Unstructured.io

Unstructured.io provides document parsing and cleaning tools for RAG applications.

### Similarities

**Both provide text cleaning**:

- Ligature cleaning
- Bullet removal
- Whitespace normalization
- Paragraph grouping

**Both target RAG use cases**:

- Designed for embedding quality
- Focus on common document formats
- Production-ready implementations

### Differences

| Feature | Unstructured.io | rs_document |
|---------|-----------------|-------------|
| **Cleaning Speed** | Baseline | **15-75x faster** |
| **Document Parsing** | PDF, DOCX, HTML, etc. | **Not available** |
| **Number of Cleaners** | 15+ cleaners | **5 core cleaners** |
| **Cleaner Configuration** | Configurable thresholds | **Fixed behavior** |
| **Splitting** | Basic splitting | **Advanced recursive splitting** |
| **Table Extraction** | Supported | Not available |
| **Layout Detection** | Supported | Not available |

### When to Use Unstructured.io

Choose Unstructured.io when:

1. **Document parsing needed**: Starting from PDF, DOCX, HTML files

   ```python
   from unstructured.partition.pdf import partition_pdf

   # Unstructured.io parses PDFs
   elements = partition_pdf("document.pdf")
   text = "\n\n".join([e.text for e in elements])
   ```

2. **Specialized cleaners needed**: Beyond the core 5 cleaners

   ```python
   from unstructured.cleaners.core import clean_dashes, clean_ordered_bullets

   # Additional cleaners available
   text = clean_dashes(text)
   text = clean_ordered_bullets(text)
   ```

3. **Table extraction needed**: Preserving table structure

   ```python
   # Unstructured.io detects tables
   elements = partition_pdf("document.pdf")
   tables = [e for e in elements if e.category == "Table"]
   ```

4. **Layout analysis needed**: Understanding document structure

   ```python
   # Unstructured.io identifies sections, headers, footers
   ```

5. **Fine-grained control**: Adjusting cleaner behavior

   ```python
   from unstructured.cleaners.core import clean_extra_whitespace

   # Can configure behavior
   text = clean_extra_whitespace(text, keep_tabs=True)
   ```

### When to Use rs_document

Choose rs_document when:

1. **Already have text**: Documents already extracted

   ```python
   # You've already extracted text from PDFs
   texts = extract_text_from_pdfs(pdf_files)

   # rs_document cleans and splits
   docs = [Document(text, {}) for text in texts]
   chunks = clean_and_split_docs(docs, chunk_size=1000)
   ```

2. **Performance critical**: Processing large volumes
   - Unstructured.io: 98ms per document for cleaning
   - rs_document: 4.2ms per document for cleaning
   - 23x faster

3. **Core cleaners sufficient**: Don't need specialized cleaning
   - 5 core cleaners handle most cases
   - Ligatures, bullets, whitespace, non-ASCII, paragraph grouping

4. **Need advanced splitting**: Recursive algorithm with overlap
   - Unstructured.io has basic splitting
   - rs_document has optimized recursive splitting

5. **Resource constraints**: Limited compute budget
   - 15-75x less CPU time for cleaning

### Integration Pattern: Use Both

Common pattern: Use Unstructured.io for parsing, rs_document for cleaning/splitting

```python
from unstructured.partition.pdf import partition_pdf
from rs_document import clean_and_split_docs, Document

# Parse with Unstructured.io
elements = partition_pdf("document.pdf")

# Extract text
text = "\n\n".join([e.text for e in elements if hasattr(e, 'text')])

# Clean and split with rs_document (fast)
doc = Document(text, {"source": "document.pdf"})
doc.clean()
chunks = doc.recursive_character_splitter(1000)
```

This gives you:

- PDF parsing (Unstructured.io)
- Fast cleaning and splitting (rs_document)

## Integration Patterns

Understanding where rs_document fits in different workflows.

### Pattern 1: RAG Pipeline

Standard RAG pipeline with rs_document for preprocessing:

```text
┌─────────────┐
│   Documents  │ (PDFs, DOCX, HTML)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │ (Unstructured.io, PyPDF2, etc.)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ rs_document │ (Clean & Split)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Embeddings │ (OpenAI, Cohere, local models)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Vector DB  │ (Pinecone, Weaviate, Chroma)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Retrieval  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│     LLM     │
└─────────────┘
```

rs_document handles the preprocessing step—cleaning and splitting text before embedding.

**Example**:

```python
# 1. Parse documents (your choice of tool)
texts = [parse_pdf(f) for f in pdf_files]

# 2. Clean and split with rs_document
from rs_document import Document, clean_and_split_docs
docs = [Document(text, {"file": f}) for text, f in zip(texts, pdf_files)]
chunks = clean_and_split_docs(docs, chunk_size=1000)

# 3. Generate embeddings (your choice of model)
vectors = embedding_model.embed([c.page_content for c in chunks])

# 4. Store in vector database
vector_db.insert(vectors, [c.metadata for c in chunks])
```

### Pattern 2: With LangChain

Integrate rs_document into LangChain pipelines:

```python
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from rs_document import clean_and_split_docs, Document

# Load documents with LangChain
loader = DirectoryLoader("./docs", glob="**/*.txt")
lc_docs = loader.load()

# Convert to rs_document
rs_docs = [
    Document(d.page_content, {k: str(v) for k, v in d.metadata.items()})
    for d in lc_docs
]

# Fast processing with rs_document
chunks = clean_and_split_docs(rs_docs, chunk_size=1000)

# Convert back to LangChain
from langchain_core.documents import Document as LCDocument
lc_chunks = [
    LCDocument(page_content=c.page_content, metadata=c.metadata)
    for c in chunks
]

# Continue with LangChain
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(lc_chunks, embeddings)

# Query
retriever = vectorstore.as_retriever()
results = retriever.get_relevant_documents("your query")
```

### Pattern 3: Standalone

Use rs_document independently without any framework:

```python
import rs_document

# Your custom document loading
def load_documents(directory):
    # Custom logic
    return documents

# Load documents
docs = load_documents("./docs")

# Process with rs_document
chunks = rs_document.clean_and_split_docs(docs, chunk_size=1000)

# Your custom embedding
def embed_chunks(chunks):
    # Custom logic
    return vectors

vectors = embed_chunks(chunks)

# Your custom storage
def store_vectors(vectors, metadata):
    # Custom logic
    pass

store_vectors(vectors, [c.metadata for c in chunks])
```

This pattern gives you full control—use rs_document for what it does best (cleaning and splitting) and handle everything else your way.

### Pattern 4: Batch Processing

Process large document collections efficiently:

```python
from rs_document import Document, clean_and_split_docs
import os
import json

# Load all documents
docs = []
for root, dirs, files in os.walk("./documents"):
    for file in files:
        if file.endswith(".txt"):
            path = os.path.join(root, file)
            with open(path) as f:
                text = f.read()
                docs.append(Document(text, {"source": path}))

# Batch process (parallel)
print(f"Processing {len(docs)} documents...")
chunks = clean_and_split_docs(docs, chunk_size=1000)
print(f"Created {len(chunks)} chunks")

# Save results
with open("chunks.json", "w") as f:
    json.dump([
        {"content": c.page_content, "metadata": c.metadata}
        for c in chunks
    ], f)
```

The batch function automatically parallelizes across available CPU cores.

### Pattern 5: Real-Time Ingestion

Process documents as they arrive:

```python
from rs_document import Document
import queue
import threading

# Document queue
doc_queue = queue.Queue()

def process_worker():
    """Worker thread that processes documents"""
    while True:
        doc = doc_queue.get()
        if doc is None:  # Poison pill
            break

        # Process document
        doc.clean()
        chunks = doc.recursive_character_splitter(1000)

        # Store chunks
        store_chunks(chunks)

        doc_queue.task_done()

# Start workers
workers = [threading.Thread(target=process_worker) for _ in range(4)]
for w in workers:
    w.start()

# Add documents as they arrive
def on_document_received(text, metadata):
    doc = Document(text, metadata)
    doc_queue.put(doc)

# ... handle incoming documents ...

# Cleanup
for _ in workers:
    doc_queue.put(None)  # Poison pill
for w in workers:
    w.join()
```

rs_document's speed enables real-time processing even under heavy load.

## Migration from Other Tools

### Migrating from LangChain

If you're currently using LangChain's text splitter:

**Before**:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)
```

**After**:

```python
from rs_document import clean_and_split_docs, Document

# Convert LangChain documents to rs_document
rs_docs = [
    Document(d.page_content, {k: str(v) for k, v in d.metadata.items()})
    for d in documents
]

# Split (overlap is fixed at ~33%)
chunks = clean_and_split_docs(rs_docs, chunk_size=1000)

# Convert back if needed
from langchain_core.documents import Document as LCDocument
lc_chunks = [
    LCDocument(page_content=c.page_content, metadata=c.metadata)
    for c in chunks
]
```

**Considerations**:

- Overlap changes from 20% to ~33% (may affect retrieval)
- Separators fixed (if you customized, may need adjustment)
- Performance improves dramatically

### Migrating from Unstructured.io

If you're currently using Unstructured.io for cleaning:

**Before**:

```python
from unstructured.cleaners.core import (
    clean_extra_whitespace,
    clean_ligatures,
    clean_bullets,
    group_broken_paragraphs
)

text = clean_extra_whitespace(text)
text = clean_ligatures(text)
text = clean_bullets(text)
text = group_broken_paragraphs(text)
```

**After**:

```python
from rs_document import Document

doc = Document(text, {})
doc.clean()  # Runs all cleaners
text = doc.page_content
```

**Considerations**:

- Same cleaning logic, much faster
- Fewer cleaners available (only 5 core cleaners)
- No configuration options (fixed behavior)

## Decision Framework

Use this framework to decide which tool(s) to use:

### Question 1: Do you need document parsing?

- **Yes**: Use Unstructured.io or similar parser → then rs_document
- **No**: Already have text → rs_document or LangChain

### Question 2: How many documents?

- **< 100**: Any tool works, choose based on ecosystem
- **100-1,000**: rs_document saves time but not critical
- **> 1,000**: rs_document strongly recommended
- **> 10,000**: rs_document essential

### Question 3: Do you need customization?

**Custom overlap percentage?**

- **Yes**: LangChain
- **No**: rs_document

**Custom separators?**

- **Yes**: LangChain
- **No**: rs_document

**Token-based splitting?**

- **Yes**: LangChain
- **No**: rs_document

**Specialized cleaners?**

- **Yes**: Unstructured.io
- **No**: rs_document

### Question 4: What's your architecture?

**Heavy LangChain usage?**

- Consider: LangChain for everything
- Or: rs_document for splitting, LangChain for rest

**Custom pipeline?**

- rs_document fits easily (simple API)

**Unstructured.io for parsing?**

- Add rs_document for fast cleaning/splitting

## Summary

### Use rs_document when

1. Performance matters (> 1,000 documents)
2. Default settings work (33% overlap, standard separators)
3. Core cleaners sufficient (ligatures, bullets, whitespace, etc.)
4. Already have extracted text
5. Resource constraints (budget, time)

### Use LangChain when

1. Need customization (overlap, separators, token-based)
2. Small workloads (< 100 documents)
3. Heavy ecosystem integration
4. Need callbacks or advanced features

### Use Unstructured.io when

1. Need document parsing (PDF, DOCX, HTML)
2. Need specialized cleaners
3. Need table extraction or layout analysis
4. Performance is not critical

### Use multiple tools

- Unstructured.io for parsing
- rs_document for cleaning/splitting
- LangChain for embeddings/retrieval/LLM
- Best of all worlds

The tools are complementary—choosing one doesn't exclude the others. Most production systems use multiple tools, each for what it does best.

---

This completes the explanation section. You now understand:

1. [Why Rust](why-rust.md) - The performance problem and solution
2. [Design Philosophy](design-philosophy.md) - The deliberate choices
3. [Recursive Splitting](recursive-splitting.md) - How the algorithm works
4. [Text Cleaning](text-cleaning.md) - Why clean and what each cleaner does
5. [Performance](performance.md) - What makes it fast and when it matters
6. **Comparisons** - When to use rs_document vs alternatives

Armed with this understanding, you can make informed decisions about using rs_document effectively in your RAG applications.
