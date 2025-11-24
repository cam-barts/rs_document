---
title: Text Cleaning
description: Why clean documents, what each cleaner does, and the order of operations
---

# Text Cleaning

Text cleaning is the critical first step in document processing for RAG applications. Understanding why cleaning matters and what each operation does helps you use rs_document effectively.

## Why Clean Documents?

Documents from various sources contain artifacts that don't carry semantic meaning but hurt embedding quality and retrieval accuracy.

### The Problem: Noise in Embeddings

Embedding models encode text into vectors representing semantic meaning. Artifacts create noise:

```python
# Original text from PDF
text1 = "The ﬁrst step is to ﬁnd the optimal solution."

# After cleaning
text2 = "The first step is to find the optimal solution."

# Without cleaning
embedding1 = model.embed(text1)  # Encodes "ﬁ" ligature as unique token

# With cleaning
embedding2 = model.embed(text2)  # Encodes "fi" as standard token

# Query: "first step"
query_embedding = model.embed("first step")

# Similarity (higher is better)
similarity(query_embedding, embedding1) = 0.85  # Lower due to ligature
similarity(query_embedding, embedding2) = 0.95  # Higher, clean match
```

The cleaner text produces embeddings that better match queries.

### The Problem: Token Inefficiency

Artifacts waste token budget:

```python
# With extra whitespace and bullets
text = "●  Key point:   This is   important.  "
tokens = 12

# After cleaning
text = "Key point: This is important."
tokens = 6
```

Cleaning reduces token count by 50%, allowing more content in each chunk.

### Sources of Artifacts

Different document sources produce different artifacts:

#### PDF Extraction

PDFs are rendered for display, not text extraction. Common artifacts:

**Ligatures**: Typographic ligatures become special characters

- `fi` → `ﬁ` (single character)
- `fl` → `ﬂ`
- `ae` → `æ`
- `oe` → `œ`

**Bullets**: Rendered symbols become unicode characters

- List bullets: `●`, `■`, `•`, `◆`
- Checkboxes: `☐`, `☑`, `☒`

**Extra Whitespace**: Table formatting creates multiple spaces

```text
Name          Age         City
John          25          NYC
```

**Broken Paragraphs**: Multi-column layouts split paragraphs

```text
This is a sentence that was
incorrectly split across lines
because of column detection.
```

#### OCR Output

OCR (Optical Character Recognition) produces recognition errors:

**Non-ASCII Artifacts**: Characters misrecognized as symbols

- `l` (lowercase L) → `|` (pipe)
- `0` (zero) → `O` (letter O)
- Accent marks: `e` → `é`, `n` → `ñ`

**Whitespace Issues**: Inconsistent spacing from layout detection

```text
Word   spacing    is     irregular.
```

**Broken Words**: Characters split incorrectly

```text
rec-
ognition
```

#### Web Scraping

HTML conversion creates formatting artifacts:

**HTML Entities**: Special characters encoded

- `&nbsp;` → extra spaces
- `&mdash;` → `—`
- `&quot;` → `"`

**List Markers**: HTML lists become text bullets

```html
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

→ "• Item 1 • Item 2"
```

**Extra Whitespace**: CSS spacing becomes text spaces

## Available Cleaners

rs_document provides five cleaners, each targeting specific artifacts:

### `clean_ligatures()`

**What it does**: Converts typographic ligatures to component letters

**Transformations**:

```python
"ﬁ" → "fi"
"ﬂ" → "fl"
"ﬀ" → "ff"
"ﬃ" → "ffi"
"ﬄ" → "ffl"
"æ" → "ae"
"œ" → "oe"
"Æ" → "AE"
"Œ" → "OE"
```

**Why it matters**: Ligatures are common in professionally typeset PDFs (books, papers, reports). Without cleaning:

```python
# Query won't match because of ligature
query = "first"
text = "The ﬁrst step"  # Contains U+FB01 (ﬁ ligature)
# String match: False
# Similarity: Low
```

After cleaning:

```python
text = "The first step"
# String match: True
# Similarity: High
```

**Use case**: Essential for any PDF content, especially academic papers, books, and professional reports.

### `clean_bullets()`

**What it does**: Removes bullet point characters while preserving list structure

**Removes**:

```python
"●" → ""
"■" → ""
"•" → ""
"◆" → ""
"▪" → ""
"‣" → ""
```

**Example**:

```python
# Before
"● First item\n● Second item\n● Third item"

# After
"First item\nSecond item\nThird item"
```

**Why it matters**: Bullet characters don't carry semantic meaning and waste tokens. The list structure (line breaks) is preserved, which is what matters for understanding.

**Use case**: Documents with lists (presentations, reports, documentation).

### `clean_extra_whitespace()`

**What it does**: Normalizes all whitespace

**Operations**:

1. Replace multiple spaces with single space: `"a    b"` → `"a b"`
2. Remove leading whitespace: `"  text"` → `"text"`
3. Remove trailing whitespace: `"text  "` → `"text"`
4. Normalize line endings: `"\r\n"` → `"\n"`

**Example**:

```python
# Before
"  This   has    extra     spaces.  \n   And   leading   spaces. "

# After
"This has extra spaces.\nAnd leading spaces."
```

**Why it matters**:

- Reduces token count (multiple spaces are multiple tokens)
- Improves embedding consistency
- Removes visual formatting that doesn't carry meaning

**Use case**: All documents, but especially PDFs with table formatting and OCR output.

### `clean_non_ascii_chars()`

**What it does**: Removes all characters outside the ASCII range (0-127)

**Removes**:

- Accented characters: `é`, `ñ`, `ü`
- Symbols: `™`, `©`, `°`
- Emoji: 😀, 👍, ❤️
- Special punctuation: `—`, `…`, `'`

**Example**:

```python
# Before
"Café résumé — très bien! 😀"

# After
"Caf rsum  trs bien! "
```

**⚠️ Warning**: This cleaner is aggressive and removes useful information in many cases.

**Use cases**:

- Legacy systems requiring ASCII-only text
- Specific embedding models trained only on ASCII
- English-only content where non-ASCII is truly noise

**Avoid for**:

- Multilingual content (removes non-English characters)
- Modern systems (most support Unicode)
- Content with intentional symbols or emoji

**Alternative**: Only use if you have a specific requirement for ASCII-only text. Otherwise, skip this cleaner.

### `group_broken_paragraphs()`

**What it does**: Rejoins paragraphs incorrectly split by PDF extraction

**Algorithm**:

1. Find lines that end without punctuation
2. If next line doesn't start with capital letter
3. Merge lines into single paragraph

**Example**:

```python
# Before (broken paragraph from 2-column PDF)
"This is a sentence that was\nsplit across lines because\nof the column layout."

# After
"This is a sentence that was split across lines because of the column layout."
```

**Why it matters**: Broken paragraphs create artificial semantic boundaries. Retrieval systems might treat them as separate thoughts.

**Use case**: PDFs with multi-column layouts, scanned documents with OCR.

**Note**: This cleaner is conservative—it only merges when confident the split was erroneous. It won't merge legitimate line breaks.

## The `.clean()` Method

The `.clean()` method runs all cleaners in a specific order:

```python
doc = Document(text, metadata)
doc.clean()
# Equivalent to:
# doc.clean_extra_whitespace()
# doc.clean_ligatures()
# doc.clean_bullets()
# doc.clean_non_ascii_chars()
# doc.group_broken_paragraphs()
```

### Why This Order?

The sequence matters for best results:

**1. `clean_extra_whitespace()` first**

- Normalizes input for other cleaners
- Ensures consistent spacing for pattern matching
- Reduces noise before other operations

**2. `clean_ligatures()` second**

- Converts to standard ASCII letters
- Ensures subsequent cleaners work with normalized text

**3. `clean_bullets()` third**

- Removes symbols after ligatures are normalized
- Operates on clean whitespace

**4. `clean_non_ascii_chars()` fourth**

- Removes remaining non-ASCII after ligatures converted
- Operates on text with normalized spacing and bullets removed

**5. `group_broken_paragraphs()` last**

- Works with fully cleaned text
- Merges paragraphs after all character-level cleaning
- Benefits from normalized whitespace

Running in different order could miss artifacts or make incorrect decisions.

## Selective Cleaning

You can run cleaners individually if you don't need all of them:

```python
from rs_document import Document

doc = Document(text, metadata)

# Only clean whitespace and ligatures
doc.clean_extra_whitespace()
doc.clean_ligatures()

# Skip bullets, non-ASCII, and paragraph grouping
```

**Common combinations**:

**Minimal cleaning** (fastest, least aggressive):

```python
doc.clean_extra_whitespace()
doc.clean_ligatures()
```

**Standard cleaning** (good for most PDFs):

```python
doc.clean_extra_whitespace()
doc.clean_ligatures()
doc.clean_bullets()
doc.group_broken_paragraphs()
# Skip clean_non_ascii_chars()
```

**Aggressive cleaning** (ASCII-only systems):

```python
doc.clean()  # All cleaners
```

## Performance Characteristics

Cleaning operations are fast in rs_document:

| Operation | Time (single doc) | Speedup vs Python |
|-----------|------------------|-------------------|
| `clean_extra_whitespace()` | < 0.1ms | 15-20x |
| `clean_ligatures()` | < 0.1ms | 25-30x |
| `clean_bullets()` | < 0.1ms | 20-25x |
| `clean_non_ascii_chars()` | < 0.1ms | 30-40x |
| `group_broken_paragraphs()` | < 0.5ms | 50-75x |
| `clean()` (all) | < 1ms | 20-25x |

For batch processing:

```python
# 10,000 documents
docs = [Document(text, {}) for text in texts]

# Clean all
for doc in docs:
    doc.clean()

# Total time: ~10 seconds
# Python equivalent: ~4 minutes
```

## Best Practices

### Always Clean Before Splitting

Clean first, then split:

```python
# Correct
doc.clean()
chunks = doc.recursive_character_splitter(1000)

# Wrong (splits uncleaned text)
chunks = doc.recursive_character_splitter(1000)
for chunk in chunks:
    chunk.clean()  # Cleaning each chunk separately
```

Cleaning before splitting:

- More efficient (clean once vs clean N chunks)
- Better chunk boundaries (splitting operates on clean text)
- More consistent results

### Use `clean_and_split_docs()` for Batches

For multiple documents, use the batch function:

```python
from rs_document import clean_and_split_docs

chunks = clean_and_split_docs(docs, chunk_size=1000)
```

This:

- Cleans and splits in one pass
- Processes documents in parallel
- Returns all chunks from all documents

### Consider Your Content Type

Adjust cleaning based on source:

**PDFs from books/papers**:

```python
doc.clean_extra_whitespace()
doc.clean_ligatures()
doc.group_broken_paragraphs()
```

**OCR output**:

```python
doc.clean()  # All cleaners, OCR is noisy
```

**Web content**:

```python
doc.clean_extra_whitespace()
doc.clean_bullets()
# Skip ligatures (rare in HTML) and non-ASCII (preserve content)
```

**Clean text** (already processed):

```python
# Maybe just whitespace normalization
doc.clean_extra_whitespace()
```

### Testing Cleaning Impact

Evaluate cleaning on sample documents:

```python
from rs_document import Document

# Before cleaning
doc1 = Document(original_text, {})
embedding1 = embed_model.embed(doc1.page_content)

# After cleaning
doc2 = Document(original_text, {})
doc2.clean()
embedding2 = embed_model.embed(doc2.page_content)

# Compare
print(f"Original: {len(doc1.page_content)} chars")
print(f"Cleaned: {len(doc2.page_content)} chars")
print(f"Reduction: {len(doc1.page_content) - len(doc2.page_content)} chars")

# Test retrieval
query = "your test query"
sim1 = similarity(embed_model.embed(query), embedding1)
sim2 = similarity(embed_model.embed(query), embedding2)
print(f"Similarity improvement: {sim2 - sim1:.3f}")
```

## Limitations

Understanding what cleaners don't do:

**No Spelling Correction**: OCR errors like "recieve" → "receive" aren't fixed

**No Grammar Fix**: Broken sentences aren't reconstructed

**No Language Translation**: Non-English text isn't translated

**No Semantic Cleaning**: Meaningless content (lorem ipsum) isn't detected

**No HTML Removal**: HTML tags aren't removed (use an HTML parser first)

Cleaners focus on formatting artifacts, not content quality.

## Comparison with Alternatives

### vs Unstructured.io

**Similarities**:

- rs_document implements same core cleaners
- Logic matches Unstructured.io's behavior

**Differences**:

- rs_document: Faster (15-75x per cleaner)
- Unstructured.io: More cleaners available (dashes, ordered bullets, etc.)
- Unstructured.io: More configuration options

**When to use each**:

- rs_document: Speed matters, core cleaners sufficient
- Unstructured.io: Need specialized cleaners or fine-grained control

### vs LangChain

LangChain doesn't provide comprehensive text cleaners. Use rs_document for cleaning, LangChain for other pipeline steps.

### vs Custom Regex

Writing custom regex cleaners:

**Advantages of custom**:

- Tailored to your specific artifacts
- Full control over behavior

**Advantages of rs_document**:

- Pre-tested, reliable implementations
- Significantly faster
- Less code to maintain

Use rs_document cleaners as a baseline, add custom cleaning only for domain-specific artifacts.

## Summary

Text cleaning is essential for high-quality RAG:

1. **Why**: Removes artifacts that hurt embedding quality and waste tokens
2. **What**: Five cleaners target different artifact types
3. **How**: Run `.clean()` or selective cleaners based on content type
4. **When**: Always clean before splitting for best results

Proper cleaning improves retrieval accuracy and reduces token costs—making it a high-impact, low-effort optimization.

Next: [Performance](performance.md) - Understanding what makes rs_document fast
