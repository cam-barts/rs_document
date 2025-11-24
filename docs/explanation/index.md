---
title: Understanding RS Document
description: Overview of concepts and design decisions behind rs_document
---

# Understanding RS Document

This section explains the concepts, design decisions, and architecture behind rs_document. Whether you're evaluating the library for your project or seeking to understand how it works, these pages will help you grasp the "why" behind the implementation.

## What You'll Learn

### Core Concepts

**[Why Rust?](why-rust.md)** - Understand the performance problem that rs_document solves and why Rust was chosen as the solution. Learn about the bottlenecks in pure Python implementations and how compiled code with efficient string handling delivers 20-25x speedups.

**[Design Philosophy](design-philosophy.md)** - Explore the deliberate design choices that make rs_document simple yet powerful: opinionated defaults that work for 95% of use cases, string-only metadata for reliability, and the mutation vs immutability trade-offs.

**[Recursive Splitting](recursive-splitting.md)** - Deep dive into how the recursive character splitter works, why it creates overlapping chunks, and what makes it effective for RAG applications. Includes concrete examples and algorithm walkthroughs.

### Practical Understanding

**[Text Cleaning](text-cleaning.md)** - Learn why document cleaning matters for embeddings, what each cleaner does, and why they run in a specific order. Understand the artifacts from PDFs, OCR, and web scraping that hurt retrieval quality.

**[Performance](performance.md)** - Discover what makes rs_document fast: compiled code, efficient string handling, SIMD optimizations, and parallel processing. See benchmarks and understand when performance matters for your use case.

**[Comparisons](comparisons.md)** - Compare rs_document with LangChain and Unstructured.io to understand when to use each tool. Learn integration patterns for RAG pipelines, LangChain workflows, and standalone usage.

## Philosophy in Brief

rs_document is designed around a few key principles:

1. **Performance First** - Text processing shouldn't be your bottleneck
2. **Opinionated Defaults** - Proven settings that work for most RAG applications
3. **Simple API** - Fewer parameters means less cognitive load
4. **Do One Thing Well** - Fast cleaning and splitting, not an all-in-one solution

## Who Should Read This

- **Evaluators** - Deciding if rs_document fits your RAG pipeline
- **New Users** - Understanding how to use the library effectively
- **Contributors** - Learning the design principles behind implementation decisions
- **Curious Developers** - Interested in performance optimization and Rust-Python integration

## How to Navigate

Each page is self-contained and can be read independently. However, reading them in order will build your understanding progressively from problem to solution to practical application.

Start with [Why Rust?](why-rust.md) to understand the motivation, then explore the topics most relevant to your needs.

## Beyond This Guide

This explanation section focuses on concepts and understanding. For practical usage:

- See the [Getting Started](../index.md) guide for installation and basic usage
- Check the [API Reference](../reference/) for detailed method documentation

The goal is to help you not just use rs_document, but understand *why* it works the way it does. This understanding will help you make better decisions about when and how to use it in your projects.
