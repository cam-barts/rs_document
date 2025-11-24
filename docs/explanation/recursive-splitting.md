---
title: Recursive Splitting
description: How the recursive character splitting algorithm works and why it's effective
---

# Recursive Splitting

The recursive character splitter is the core splitting algorithm in rs_document. Understanding how it works helps you use it effectively and reason about the chunks it produces.

## What Problem Does It Solve?

Naive text splitting approaches have significant drawbacks:

### Simple Fixed-Size Splitting

```python
# Split every N characters
chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
```

Problems:

- Splits mid-word or mid-sentence
- No semantic boundaries respected
- No overlap between chunks
- Poor retrieval quality

### Simple Separator Splitting

```python
# Split on paragraphs
chunks = text.split("\n\n")
```

Problems:

- Variable chunk sizes (some very large, some tiny)
- Won't fit embedding model context windows
- Inefficient storage of tiny chunks

Recursive character splitting solves both problems: it respects semantic boundaries while maintaining target chunk sizes and creating overlap.

## The Algorithm

The algorithm works in three main stages:

### Stage 1: Initial Split

Split the document into small chunks at 1/3 of the target size.

**Why 1/3?** This allows grouping 3 chunks to reach the target size while creating ~33% overlap between groups.

For a target of 1000 characters:

- Small chunk size: 333 characters
- Three small chunks: ~999 characters

### Stage 2: Respect Semantic Boundaries

Use separators in hierarchical order to find good split points:

```text
1. "\n\n" - Paragraph boundaries (strongest semantic boundary)
2. "\n"   - Line breaks (sentences, list items)
3. " "    - Word boundaries (preserves whole words)
4. ""     - Character boundaries (last resort)
```

Try each separator recursively until chunks fit the size constraint.

### Stage 3: Merge with Overlap

Group every 3 consecutive small chunks together. This creates:

- Chunks near the target size
- Natural overlap where groups share chunks

## Detailed Example

Let's trace through a concrete example to see exactly how this works.

### Input

```text
Document: "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (26 chars)
Target chunk size: 9 characters
```

### Step 1: Calculate Small Chunk Size

```text
small_chunk_size = target_size / 3 = 9 / 3 = 3 characters
```

### Step 2: Split into Small Chunks

Split document every 3 characters:

```text
[ABC] [DEF] [GHI] [JKL] [MNO] [PQR] [STU] [VWX] [YZ]
  0     1     2     3     4     5     6     7    8
```

We have 9 small chunks.

### Step 3: Group by 3 with Sliding Window

Group consecutive chunks with a sliding window:

```text
Chunk 0: [ABC DEF GHI] = "ABCDEFGHI" (chars 0-9)
Chunk 1: [DEF GHI JKL] = "DEFGHIJKL" (chars 3-12)
Chunk 2: [GHI JKL MNO] = "GHIJKLMNO" (chars 6-15)
Chunk 3: [JKL MNO PQR] = "JKLMNOPQR" (chars 9-18)
Chunk 4: [MNO PQR STU] = "MNOPQRSTU" (chars 12-21)
Chunk 5: [PQR STU VWX] = "PQRSTUVWX" (chars 15-24)
Chunk 6: [STU VWX YZ]  = "STUVWXYZ"  (chars 18-26)
```

### Analyzing the Overlap

Each chunk shares content with its neighbors:

```text
Chunk 0: ABC DEF GHI
Chunk 1:     DEF GHI JKL    (overlaps DEF GHI with chunk 0)
Chunk 2:         GHI JKL MNO (overlaps GHI JKL with chunk 1)
```

Overlap percentage: 6 chars overlap / 9 chars total = 66% overlap between adjacent chunks.

Overall, each chunk shares ~33% with the previous and ~33% with the next chunk.

## Real Text Example

Let's see how this works with actual text:

### Input

```text
Introduction to Machine Learning

Machine learning is a field of artificial intelligence. It enables
systems to learn from data without explicit programming.

Deep learning is a subset of machine learning. It uses neural networks
with many layers to model complex patterns.

Applications include image recognition, natural language processing,
and autonomous vehicles.
```

Target: 150 characters per chunk

### Step 1: Try `\n\n` Separator

Split on paragraph breaks:

```text
Chunk A: "Introduction to Machine Learning" (33 chars)
Chunk B: "Machine learning is a field..." (118 chars)
Chunk C: "Deep learning is a subset..." (124 chars)
Chunk D: "Applications include..." (89 chars)
```

Small chunk size = 150 / 3 = 50 chars

All chunks fit the 50 char target, so we use this split.

### Step 2: Group by 3

```text
Final Chunk 0: [A + B + C]
"Introduction to Machine Learning

Machine learning is a field of artificial intelligence. It enables
systems to learn from data without explicit programming.

Deep learning is a subset of machine learning."
(~275 chars, includes 3 paragraphs)

Final Chunk 1: [B + C + D]
"Machine learning is a field of artificial intelligence. It enables
systems to learn from data without explicit programming.

Deep learning is a subset of machine learning. It uses neural networks
with many layers to model complex patterns.

Applications include image recognition..."
(~331 chars, overlaps with Chunk 0)
```

Notice how paragraph B and C appear in both chunks, creating context overlap.

## The Recursive Part

What makes this "recursive"? The algorithm recursively tries separators until it finds one that produces small enough chunks.

### Pseudocode

```python
def recursive_split(text, target_size, separators):
    if len(text) <= target_size:
        return [text]  # Text already small enough

    if not separators:
        # No more separators, split by character
        return [text[i:i+target_size] for i in range(0, len(text), target_size)]

    # Try current separator
    sep = separators[0]
    parts = text.split(sep)

    # Check if all parts are small enough
    if all(len(part) <= target_size for part in parts):
        return parts

    # Some parts too big, recurse with next separator
    return recursive_split(text, target_size, separators[1:])
```

### Example of Recursion in Action

Consider a long paragraph with no `\n\n` breaks:

```text
"This is a very long paragraph with no paragraph breaks. It contains many
sentences that need to be split somehow to fit the target size. The recursive
algorithm will try each separator in turn."
```

1. Try `\n\n`: No splits (paragraph has no `\n\n`)
2. Try `\n`: One split (at the line break)
3. Check: Are both parts < target? If no...
4. Try ``: Multiple splits at spaces
5. Check: Are all parts < target? If yes, use these splits

The algorithm automatically falls back to finer-grained separators as needed.

## Why This Algorithm Is Effective

### Semantic Boundary Respect

By trying `\n\n` first, the algorithm keeps paragraphs together when possible. This preserves:

- Complete thoughts
- Thematic coherence
- Logical flow

Only when paragraphs are too large does it split at finer boundaries.

### Consistent Chunk Sizes

Unlike pure semantic splitting (e.g., split on paragraphs), this algorithm ensures:

- Chunks fit embedding model context windows
- Relatively uniform chunk sizes for efficient storage
- No tiny chunks that waste database entries

### Overlap for Context

The sliding window grouping creates natural overlap:

```text
Chunk 0: ====AAAA====BBBB====CCCC====
Chunk 1:          ====BBBB====CCCC====DDDD====
Chunk 2:                   ====CCCC====DDDD====EEEE====
```

This overlap is critical for retrieval:

**Without Overlap**
Query: "How does CCCC relate to BBBB?"

- Might miss the connection if they're in different chunks

**With Overlap**
Query: "How does CCCC relate to BBBB?"

- Chunk 0 contains both BBBB and CCCC
- Chunk 1 also contains both
- Higher chance of retrieval

### Computational Efficiency

The algorithm is efficient:

- Single pass to create small chunks
- Simple grouping operation to create final chunks
- No need to compute embeddings or semantic similarity
- Scales linearly with text length

## Configuration Trade-offs

The algorithm has fixed parameters in rs_document. Let's understand why these choices were made:

### Why 33% Overlap?

```text
10% overlap: =====AAAAA====B=====
             =====B====CCCCC=====
             (Minimal context sharing)

33% overlap: =====AAAA====BBBB====CCCC=====
             ========BBBB====CCCC====DDDD====
             (Good context continuity)

50% overlap: =====AAA====BBB====CCC=====
             ====AAA====BBB====CCC====DDD====
             (Excessive redundancy)
```

33% provides strong context continuity without excessive storage cost.

### Why Fixed Separators?

The hierarchy `["\n\n", "\n", " ", ""]` works universally:

- **Prose**: Respects paragraphs, sentences, words
- **Code**: Respects blank lines, line breaks, tokens
- **Lists**: Respects items, lines, words
- **Tables**: Respects rows, cells, words

Custom separators would be needed for:

- Domain-specific formats (e.g., `"---"` for YAML)
- Non-English text (different sentence endings)
- Structured data with special delimiters

For 95% of RAG use cases, the default hierarchy is optimal.

## Common Questions

### Why Not Semantic Splitting?

Semantic splitting uses embeddings to find natural break points. Why doesn't rs_document do this?

**Reasons**:

1. **Performance**: Computing embeddings is expensive
2. **Simplicity**: No need for embedding models as dependencies
3. **Consistency**: Deterministic results, not model-dependent
4. **Sufficiency**: Character-based splitting works well for most RAG

Semantic splitting is a valid approach but addresses a different point in the performance-accuracy trade-off curve.

### Why Not Token-Based Splitting?

Token-based splitting respects model tokenization. Why doesn't rs_document do this?

**Reasons**:

1. **Model Agnostic**: Works with any embedding model
2. **Performance**: Tokenization is slower than character counting
3. **Simplicity**: No need for tokenizer dependencies
4. **Sufficiency**: Character approximation works well

If you need exact token limits, post-process with a tokenizer:

```python
from rs_document import Document
from tiktoken import get_encoding

doc = Document(long_text, {})
chunks = doc.recursive_character_splitter(3000)  # Approximate

# Verify token counts
enc = get_encoding("cl100k_base")
for chunk in chunks:
    tokens = enc.encode(chunk.page_content)
    assert len(tokens) <= 1024  # Actual limit
```

### What About Edge Cases?

**Very Long Words/URLs**: If a word is longer than the chunk size:

```python
text = "A" * 10000  # 10000 char word
chunks = doc.recursive_character_splitter(1000)
# Will split at character boundary: "AAA...AAA" (1000 chars each)
```

**No Natural Boundaries**: For text with no separators:

```python
text = "A" * 10000  # No spaces or newlines
# Falls back to character splitting automatically
```

The algorithm gracefully handles these cases by falling back to character splitting.

## Implementation Notes

The Rust implementation includes optimizations:

### Memory Efficiency

Small chunks are stored as string slices (references) into the original text, avoiding copies:

```rust
// Conceptually
let original = String::from("long document");
let small_chunks = vec![
    &original[0..100],    // Slice, not copy
    &original[100..200],  // Slice, not copy
    // ...
];
```

### Parallel Processing

When processing multiple documents with `clean_and_split_docs()`, the splitting happens in parallel:

```rust
documents.par_iter()
    .map(|doc| doc.recursive_character_splitter(size))
    .flatten()
    .collect()
```

Each document is split independently, utilizing all CPU cores.

## Comparison with Alternatives

### LangChain RecursiveCharacterTextSplitter

**Same**:

- Recursive separator hierarchy
- Similar algorithm concept

**Different**:

- LangChain: Configurable overlap (any percentage)
- rs_document: Fixed 33% overlap
- LangChain: Configurable separators
- rs_document: Fixed separators
- Performance: rs_document ~20x faster

### Simple Fixed-Size Splitting

**Advantage of recursive splitting**:

- Respects semantic boundaries
- Creates overlap
- More intelligent split points

**Disadvantage**:

- More complex implementation
- Slightly slower than naive splitting

The quality improvement far outweighs the complexity cost.

## Best Practices

### Choosing Chunk Size

Target chunk size depends on your embedding model:

```python
# Common embedding model context windows
OpenAI text-embedding-ada-002: 8191 tokens (~32k chars)
Cohere embed-english-v3.0: 512 tokens (~2k chars)
Sentence Transformers: 512 tokens (~2k chars)
```

Rule of thumb: `chunk_size = 0.75 * context_window * 4` (chars per token)

Example: For 512 token model: `chunk_size = 0.75 * 512 * 4 = 1536 chars`

### Testing Different Sizes

Experiment with different chunk sizes:

```python
for size in [500, 1000, 1500, 2000]:
    chunks = doc.recursive_character_splitter(size)
    # Evaluate retrieval quality with each size
```

Larger chunks: More context, fewer chunks
Smaller chunks: More precise, more chunks

### Handling Already-Split Text

If your text is already structured (e.g., JSON with sections):

```python
# Split sections separately, not the whole document
for section in document_sections:
    doc = Document(section.text, section.metadata)
    chunks = doc.recursive_character_splitter(1000)
```

This prevents mixing content from different sections.

## Summary

The recursive character splitter is elegant in its simplicity:

1. Split small, group with overlap
2. Try semantic boundaries first, fall back as needed
3. Produce chunks at target size with ~33% overlap

This algorithm balances semantic coherence, practical chunk sizes, and overlap for retrieval quality—all while being fast and deterministic.

Next: [Text Cleaning](text-cleaning.md) - Understanding why and how documents are cleaned
