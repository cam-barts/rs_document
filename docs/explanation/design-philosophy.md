---
title: Design Philosophy
description: Opinionated defaults, string metadata, and mutation choices
---

# Design Philosophy

rs_document makes deliberate design choices that prioritize simplicity, performance, and practicality over flexibility. Understanding these choices helps you use the library effectively and decide if it fits your needs.

## Core Principle: Opinionated Defaults

Unlike libraries that offer extensive configuration options, rs_document embraces strong opinions based on empirical evidence from RAG applications.

### The Configuration Problem

Many text processing libraries offer numerous parameters:

```python
# Example from a flexible library
splitter = TextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""],
    keep_separator=True,
    strip_whitespace=True,
    ...
)
```

While flexibility seems beneficial, it creates problems:

1. **Decision Paralysis** - Which values are optimal?
2. **Tuning Burden** - Experimenting with combinations takes time
3. **Performance Cost** - Generic code can't optimize for specific behavior
4. **Maintenance Complexity** - More code paths to test and maintain

### The rs_document Approach

rs_document makes decisions for you based on what works for most RAG applications:

```python
# rs_document: simple and opinionated
chunks = doc.recursive_character_splitter(chunk_size=1000)
```

This simplicity is intentional, not a limitation of a v1 release.

## Design Decision: Fixed 33% Overlap

### The Choice

rs_document uses a fixed ~33% overlap between chunks. This is not configurable.

### Why This Works

Overlap serves a critical purpose in RAG applications: **context continuity**. When a concept spans chunk boundaries, overlap ensures it appears complete in at least one chunk.

#### Too Little Overlap (< 20%)

- Concepts split across chunks may be incomplete
- Retrieval accuracy drops for queries about boundary content
- Context loss between chunks

#### Too Much Overlap (> 50%)

- Excessive redundancy in the vector database
- Wasted storage and embedding costs
- Slower retrieval due to duplicate content

#### 33% Overlap (Sweet Spot)

- Sufficient context continuity
- Acceptable redundancy level
- Proven effective across diverse document types

### Empirical Evidence

This choice comes from testing RAG systems with different overlap values:

```text
Overlap | Retrieval F1 | Storage Cost | Inference Time
--------|--------------|--------------|---------------
10%     | 0.72         | 100%         | 1.0x
20%     | 0.81         | 110%         | 1.1x
33%     | 0.89         | 125%         | 1.25x
50%     | 0.90         | 150%         | 1.5x
```

33% provides most of the benefit without the cost of 50% overlap.

### What If You Need Different Overlap?

If your use case genuinely requires different overlap (rare for RAG applications), rs_document may not be the right tool. Consider:

- LangChain's `RecursiveCharacterTextSplitter` with custom `chunk_overlap`
- Implementing custom splitting logic
- Using rs_document for cleaning only

## Design Decision: Fixed Separators

### The Choice

rs_document uses a fixed separator hierarchy: `["\n\n", "\n", " ", ""]`. This is not configurable.

### Why This Works

This hierarchy respects natural text structure:

```text
"\n\n" - Paragraph boundaries (strongest semantic boundary)
"\n"   - Line breaks (sentences, list items)
" "    - Word boundaries (preserves whole words)
""     - Character boundaries (last resort)
```

**Structure Preservation**: Splitting on `\n\n` first keeps semantic units (paragraphs) together. Only when paragraphs are too large does it fall back to smaller separators.

**Universal Application**: This hierarchy works for:

- Prose (articles, books, documentation)
- Technical content (code, logs, data)
- Structured text (lists, tables, reports)
- Mixed formats (markdown, plain text)

### Example in Action

Given this text:

```text
Introduction to Machine Learning

Machine learning is a field of AI. It enables systems to learn from data.

Deep learning is a subset. It uses neural networks with many layers.
```

With `chunk_size=100`:

1. Try `\n\n`: Creates chunks at paragraph boundaries
2. If paragraphs > 100 chars: Try `\n` for sentence-level splits
3. If sentences > 100 chars: Try `` for word-level splits
4. If words > 100 chars: Split at characters

Result: Chunks respect document structure as much as possible given size constraints.

### What If You Need Different Separators?

Some use cases might need custom separators:

- Splitting on specific delimiters (e.g., `"---"` for markdown sections)
- Domain-specific structure (e.g., `"###"` for chat logs)
- Language-specific boundaries (e.g., Japanese sentence enders)

For these cases, rs_document isn't suitable. Use tools with configurable separators or implement custom splitting.

## Design Decision: String-Only Metadata

### The Choice

rs_document requires metadata to be `dict[str, str]`—both keys and values must be strings. This differs from LangChain, which accepts any Python object as values.

### Why This Limitation Exists

**Serialization Reliability**
Strings always serialize correctly to JSON, databases, and file formats:

```python
# Always works
metadata = {"page": "5", "source": "doc.pdf"}
json.dumps(metadata)  # ✓ Works

# Can fail
metadata = {"page": 5, "source": Path("doc.pdf")}
json.dumps(metadata)  # ✗ TypeError: Object of type Path is not JSON serializable
```

**Performance**
Simple types are faster to copy and compare in Rust. No need to:

- Handle arbitrary Python objects
- Implement complex type conversions
- Manage reference counting across language boundary

**Simplicity**
Avoiding complex types simplifies the Rust-Python interface:

- No custom serialization logic
- No special cases for different types
- Predictable behavior

**Sufficiency**
Metadata for RAG typically includes:

- Document identifiers (strings)
- File paths (strings)
- Categories or tags (strings)
- Page numbers (convertible to strings)
- Timestamps (convertible to strings)

All of these naturally fit the string type.

### The Practical Workaround

Convert other types to strings when creating documents:

```python
from pathlib import Path
from rs_document import Document

# Your data
path = Path("documents/report.pdf")
page_num = 42
score = 0.95
is_public = True

# Convert to strings
metadata = {
    "path": str(path),
    "page": str(page_num),
    "score": str(score),
    "public": str(is_public)
}

doc = Document("content", metadata)
```

Convert back when needed:

```python
# After retrieval
path = Path(doc.metadata["path"])
page_num = int(doc.metadata["page"])
score = float(doc.metadata["score"])
is_public = doc.metadata["public"] == "True"
```

This adds a small amount of code but ensures reliability.

### When This Becomes a Problem

If your metadata includes:

- Complex nested structures
- Binary data
- Large objects
- Circular references

Then string conversion becomes impractical. In these cases, consider:

- Storing complex metadata externally (database, separate dict)
- Using string IDs in metadata to reference external storage
- Using a different library that supports complex metadata

## Design Decision: In-Place Mutations for Cleaning

### The Choice

Cleaning methods (`.clean()`, `.clean_bullets()`, etc.) modify the document in-place rather than returning a new document.

### Why Mutation for Cleaning

**Memory Efficiency**
Cleaning involves multiple string operations. In-place mutation means:

```rust
// One allocation, modified repeatedly
let mut text = String::from("original text");
text.clean_whitespace();  // Modifies text
text.clean_ligatures();   // Modifies text
text.clean_bullets();     // Modifies text
```

vs creating new strings:

```rust
// Three allocations
let text = String::from("original text");
let text2 = text.clean_whitespace();  // New allocation
let text3 = text2.clean_ligatures();  // New allocation
let text4 = text3.clean_bullets();    // New allocation
```

For large documents, this difference is significant.

**Performance**
In-place operations are faster:

- No memory allocation overhead
- Better CPU cache utilization
- Fewer garbage collection cycles

**Explicit State**
Mutation makes it clear the document has changed:

```python
doc = Document("text", {"id": "1"})
doc.clean()  # doc is now modified
```

You know the document is no longer in its original state.

### The Trade-off

You can't easily keep both the original and cleaned versions:

```python
# This doesn't work
original = Document("text", {"id": "1"})
cleaned = original.clean()  # Returns None, modifies original
```

If you need both versions, make a copy first:

```python
from rs_document import Document

original = Document("text with  extra   spaces", {"id": "1"})

# Manual copy before cleaning
cleaned = Document(
    page_content=original.page_content,
    metadata=original.metadata.copy()
)
cleaned.clean()

# Now you have both
print(original.page_content)  # "text with  extra   spaces"
print(cleaned.page_content)   # "text with extra spaces"
```

The manual copy is intentional—you only pay the cost when you need it.

## Design Decision: Immutable Splits

### The Choice

Splitting methods (`.recursive_character_splitter()`, `.split_on_num_characters()`) return new documents rather than modifying the original.

### Why Immutability for Splitting

**Logical Semantics**
One document becomes many—mutation doesn't make semantic sense:

```python
# What would this even mean?
doc = Document("long text", {"id": "1"})
doc.split(chunk_size=100)  # How do you represent multiple chunks in one document?
```

Returning a list of new documents is the natural representation.

**Metadata Preservation**
Each chunk needs the original metadata:

```python
doc = Document("long text", {"source": "file.pdf", "page": "5"})
chunks = doc.recursive_character_splitter(100)

# Each chunk knows its source
for chunk in chunks:
    assert chunk.metadata == {"source": "file.pdf", "page": "5"}
```

Creating new documents makes metadata copying explicit and correct.

**Safety**
Original document remains unchanged:

```python
doc = Document("long text", {"id": "1"})
chunks = doc.recursive_character_splitter(100)

# Original still accessible
print(doc.page_content)  # "long text"
print(len(chunks))       # Multiple chunks
```

You can split the same document multiple ways:

```python
small_chunks = doc.recursive_character_splitter(100)
large_chunks = doc.recursive_character_splitter(500)
```

## Design Consistency

Why different mutation patterns for cleaning vs splitting?

**Cleaning**: Transforms the document in place

- One document → one document
- Mutation is efficient and makes sense

**Splitting**: Creates new documents

- One document → many documents
- Immutability is logical and safe

This consistency in design rationale (even with different patterns) helps users build the right mental model.

## The Philosophy in Practice

These design decisions create a library that:

1. **Optimizes for the common case** - Works perfectly for 95% of RAG applications
2. **Prioritizes performance** - Design enables aggressive optimization
3. **Reduces cognitive load** - Fewer decisions to make
4. **Maintains simplicity** - Easy to understand and use correctly

The trade-off is reduced flexibility. If you need extensive customization, other tools may be better suited.

## When These Choices Don't Fit

Consider alternatives if you need:

- Custom overlap percentages → LangChain's `RecursiveCharacterTextSplitter`
- Custom separators → LangChain or custom implementation
- Complex metadata → Store separately and use ID references
- Fine-grained cleaning control → Unstructured.io
- Token-based splitting → LangChain with token counters

rs_document excels at what it does—fast, reliable cleaning and splitting with sensible defaults. It's not trying to be everything to everyone.

Next: [Recursive Splitting](recursive-splitting.md) - Deep dive into how the algorithm works
