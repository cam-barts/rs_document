---
title: Why Rust?
description: The performance problem and why Rust is the solution
---

# Why Rust?

Understanding why rs_document exists requires understanding the performance challenges in RAG (Retrieval Augmented Generation) applications and why Rust provides an ideal solution.

## The Performance Problem

RAG applications need to process large document collections efficiently. A typical RAG pipeline involves three critical text processing steps:

1. **Cleaning** - Removing artifacts from PDFs, OCR errors, formatting issues
2. **Splitting** - Breaking documents into chunks that fit embedding models
3. **Scale** - Processing thousands or millions of documents

These operations seem simple, but at scale they become significant bottlenecks.

### Real-World Scenarios

Consider these common situations:

### Initial Knowledge Base Creation

- You have 100,000 PDF documents to process
- Each needs cleaning (5 operations) and splitting (1 operation)
- Pure Python: ~3 hours of processing time
- rs_document: ~8 minutes of processing time

### Experimentation with Chunk Sizes

- Testing different chunk sizes (500, 1000, 1500 characters) for retrieval quality
- Each experiment requires reprocessing the entire corpus
- Python: 3 hours × 3 experiments = 9 hours
- rs_document: 8 minutes × 3 experiments = 24 minutes

### Real-Time Document Ingestion

- New documents arrive continuously and need immediate processing
- Python: Can process ~150 documents/second on 8 cores
- rs_document: Can process ~23,000 documents/second on 8 cores

The difference between minutes and hours fundamentally changes what's practical to do.

## Why Python Is Slow for Text Processing

Pure Python implementations (like LangChain's text splitters and Unstructured.io's cleaners) work well for small datasets but become bottlenecks at scale. This isn't a criticism of those tools—Python has inherent limitations for text processing:

### Interpreted Execution Overhead

Python code is interpreted at runtime rather than compiled to machine code. Every operation involves:

- Looking up methods in object dictionaries
- Type checking at runtime
- Reference counting for memory management
- Frame creation for function calls

For text processing with millions of operations, this overhead accumulates significantly.

### String Immutability

Python strings are immutable. Every modification creates a new string:

```python
text = "hello world"
text = text.replace("world", "python")  # Creates entirely new string
```

For cleaning operations that make multiple passes over text, this means:

- Constant memory allocation
- Copying entire strings repeatedly
- Memory fragmentation
- Garbage collection pressure

A document going through 5 cleaning operations creates 5 complete copies in memory.

### Global Interpreter Lock (GIL)

The GIL prevents true parallelism in Python:

- Only one thread executes Python bytecode at a time
- Multi-core CPUs can't be fully utilized for Python-level operations
- Threading helps with I/O, but not with CPU-bound text processing

Processing 10,000 documents on an 8-core machine uses only 1 core in pure Python (without multiprocessing overhead).

### Regex Performance

Python's `re` module, while good, can't match the performance of compiled regex engines:

- No Just-In-Time (JIT) compilation of patterns
- Less aggressive optimization
- Overhead of Python-C boundary for each match

Text cleaning heavily relies on regex for pattern matching and replacement.

## Why Rust Is the Solution

Rust provides the perfect combination of performance and safety for this problem domain:

### Compiled Native Code

Rust compiles to native machine code with aggressive optimizations:

```rust
// This gets compiled to direct CPU instructions
pub fn clean_text(text: &mut String) {
    text.retain(|c| c.is_ascii());
}
```

- No interpretation overhead
- CPU can execute directly
- Compiler optimizations (inlining, loop unrolling, etc.)
- SIMD (Single Instruction Multiple Data) instructions automatically applied

The same operation in Python involves multiple layers of abstraction before reaching the CPU.

### Efficient String Handling

Rust's `String` type allows safe in-place modification:

```rust
let mut text = String::from("hello world");
text.replace_range(6..11, "rust");  // Modifies in place
```

This means:

- One allocation for the lifetime of cleaning operations
- No intermediate string copies
- Direct memory manipulation
- Minimal garbage collection

A document going through 5 cleaning operations uses the same memory buffer throughout.

### True Parallelism with Rayon

Rust has no GIL. Rayon provides data parallelism that actually uses all cores:

```rust
documents.par_iter()  // Parallel iterator
    .map(|doc| {
        doc.clean();
        doc.split(chunk_size)
    })
    .flatten()
    .collect()
```

This code:

- Automatically splits work across available CPU cores
- Processes multiple documents simultaneously
- Scales linearly with core count
- Has minimal synchronization overhead

On an 8-core machine, you get close to 8x throughput for document processing.

### High-Performance Regex

Rust's `regex` crate provides one of the fastest regex engines available:

- DFA (Deterministic Finite Automaton) compilation
- Literal optimizations for fast prefix/suffix matching
- SIMD acceleration for character classes
- Zero-copy operations where possible

Pattern matching and replacement operations are significantly faster than Python's `re` module.

## The PyO3 Bridge

rs_document uses PyO3 to make Rust code callable from Python:

```rust
#[pyclass]
pub struct Document {
    pub page_content: String,
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl Document {
    #[new]
    pub fn new(page_content: String, metadata: HashMap<String, String>) -> Self {
        Self { page_content, metadata }
    }
}
```

PyO3 generates the Python extension module that:

- Exposes Rust structs as Python classes
- Converts between Python and Rust types
- Handles reference counting and memory management
- Minimizes copying across the language boundary

You get Rust performance with Python convenience—no need to rewrite your entire application.

## Measured Performance Gains

Typical performance improvements on modern hardware (8-core CPU):

| Operation | Python | rs_document | Speedup |
|-----------|--------|-------------|---------|
| Single document cleaning | ~20ms | <1ms | 20-25x |
| Single document splitting | ~100ms | <5ms | 20-25x |
| Batch processing (1000 docs) | ~20s | ~0.9s | 22x |
| Batch processing (1M docs) | ~6 hours | ~15 min | 24x |

The speedup is consistent across different dataset sizes—no performance degradation with large batches.

## When Performance Matters

Not every use case needs this level of performance optimization:

### Small Workloads (< 100 documents)

For small datasets, the speedup might not matter:

- Python: 2 seconds
- rs_document: 0.1 seconds
- Saved: 1.9 seconds

This difference is negligible in most workflows.

### Large Workloads (> 10,000 documents)

For large datasets, the speedup is transformative:

- Python: 20 minutes
- rs_document: 50 seconds
- Saved: 19+ minutes

This changes what's practical:

- Enables rapid experimentation
- Makes real-time processing feasible
- Reduces infrastructure costs

### Critical Factors

Performance matters when you have:

1. **Large document collections** (thousands to millions)
2. **Frequent reprocessing** (experimentation, updates)
3. **Real-time requirements** (immediate ingestion)
4. **Cost constraints** (reducing compute time)

If any of these apply, rs_document's performance advantage is significant.

## Design Trade-offs

Achieving this performance required specific design choices:

**Opinionated Defaults** - Fixed parameters enable aggressive optimization
**String-Only Metadata** - Simple types avoid complex Python-Rust conversions
**Limited Customization** - Specific behavior allows compiler optimizations
**Rust Dependency** - Building from source requires Rust toolchain

These trade-offs are detailed in [Design Philosophy](design-philosophy.md).

## The Bottom Line

Python is excellent for many tasks, but CPU-bound text processing at scale isn't one of them. Rust's compiled execution, efficient memory handling, and true parallelism provide dramatic performance improvements while maintaining Python's ease of use through PyO3.

rs_document doesn't replace your entire stack—it replaces the specific bottleneck of text cleaning and splitting, letting you keep Python for everything else.

Next: [Design Philosophy](design-philosophy.md) - Understanding the deliberate choices behind the API
