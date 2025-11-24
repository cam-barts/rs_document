#![allow(non_local_definitions)]

use pyo3::prelude::*;
use pyo3::types::PyList;
use rayon::prelude::*;
use regex::Regex;
use std::collections::HashMap;

/// This is a function that splits text by `separators` until they are smaller than `chunk_size`.
///
/// # Arguments
///
/// * `text` - The string that you want to split.
/// * `chunk_size` - The maximum size of the output splits.
/// * `separators` - The characters to split the text by, in order of which separator to use.
///
/// # Returns
///
/// A Vector of Strings, each with a size smaller than chunk_size. The chunks will only
/// be split until they are below the chunk_size threshold and then splitting not continue.
fn split_text(text: &str, chunk_size: usize, separators: &[&str]) -> Vec<String> {
    let mut intermediate_result = Vec::new();

    // Handle edge case: no separators left
    if separators.is_empty() {
        // Last resort: split by character if text is too large
        if text.len() <= chunk_size {
            return vec![text.to_string()];
        }
        // Split by character boundaries (UTF-8 safe)
        let mut result = Vec::new();
        let mut current = String::new();
        for ch in text.chars() {
            if current.len() + ch.len_utf8() > chunk_size && !current.is_empty() {
                result.push(current.clone());
                current.clear();
            }
            current.push(ch);
        }
        if !current.is_empty() {
            result.push(current);
        }
        return result;
    }

    let separator = separators[0];
    let chunks: Vec<&str> = text.split(separator).collect();
    let mut smallest_chunks = Vec::new();

    for chunk in chunks {
        if chunk.is_empty() {
            // Skip empty chunks
            continue;
        }
        if chunk.len() <= chunk_size {
            smallest_chunks.push(chunk.to_string());
        } else {
            let modified_separators = &separators[1..separators.len()];
            // Recurse with next modifiers.
            smallest_chunks.extend(split_text(chunk, chunk_size, modified_separators));
        }
    }
    // Handle empty smallest_chunks case
    if smallest_chunks.is_empty() {
        return Vec::new();
    }

    let mut current_chunk = smallest_chunks[0].clone();
    for chunk in &smallest_chunks[1..smallest_chunks.len()] {
        // Account for separator length when checking if we'd exceed chunk_size
        if current_chunk.len() + separator.len() + chunk.len() > chunk_size {
            intermediate_result.push(current_chunk.clone());
            current_chunk = chunk.to_owned();
        } else {
            current_chunk.push_str(separator);
            current_chunk.push_str(chunk);
        }
    }
    // Check if intermediate_result is empty or if current_chunk is different from last element
    if intermediate_result.is_empty()
        || intermediate_result[intermediate_result.len() - 1] != current_chunk
    {
        intermediate_result.push(current_chunk.clone());
    }
    intermediate_result
}

/// This function will split text into chunks 1/3 the size of `chunk_size`, and then
/// merge them back together such that there is a 1/3rd overlap in the returned chunks.
///
/// For example, if you get [A, B, C, D, E, F, G] back from `split_text` function, this function
/// will merge chunks and return [ABC, CDE, EFG]. This provides an overlap that is useful
/// for RAG projects. Individual chunks will never exceed `chunk_size` limit passed in.
///
/// # Arguments
///
/// * `text` - The string that you want to split.
/// * `chunk_size` - The maximum size of the output splits.
/// * `separators` - The characters to split the text by, in order of which separator to use.
///
/// # Returns
///
/// A Vector of Strings, each with a size smaller than chunk_size. The chunks will only
/// be split until they are below the chunk_size threshold and then splitting not continue.
/// Each chunk will overlap with it's neighbor chunks by about 1/3 of the `chunk_size`.
fn split_and_merge(text: &str, chunk_size: usize, separators: &[&str]) -> Vec<String> {
    let intermediate_size = chunk_size / 3;
    let splits = split_text(text, intermediate_size, separators);
    let mut result = Vec::new();

    // Handle edge cases
    if splits.is_empty() {
        // If text is empty, return single empty chunk
        if !text.is_empty() {
            result.push(text.to_string());
        }
        return result;
    }

    if splits.len() == 1 {
        // If only one split, return it as-is
        result.push(splits[0].clone());
        return result;
    }

    if splits.len() == 2 {
        // If two splits, merge them into one
        result.push(splits.concat());
        return result;
    }

    // Normal case: merge groups of 3 with step of 2 for overlap
    for i in (0..splits.len()).step_by(2) {
        if i + 3 <= splits.len() {
            let merged_chunk = splits[i..(i + 3)].concat();
            result.push(merged_chunk);
        } else {
            // Last group has fewer than 3 items
            let merged_chunk = splits[i..].concat();
            result.push(merged_chunk);
            break;
        }
    }

    result
}

/// A Document struct that adheres to LangChain's [Document Class](https://api.python.langchain.com/en/latest/documents/langchain_core.documents.base.Document.html).
#[pyclass]
#[derive(Clone)]
struct Document {
    /// The text of the document.
    #[pyo3(get, set)]
    page_content: String,
    /// Metadata for the document. Currently only supports strings as keys *and* values.
    #[pyo3(get, set)]
    metadata: HashMap<String, String>,
}

#[pymethods]
impl Document {
    /// Returns a new document with page content and metadata.
    ///
    /// # Arguments
    ///
    /// * `page_content` - A string that holds the content of the document.
    /// * `metadata` - A python dictionary of metadata for the document.
    #[new]
    fn new(page_content: String, metadata: HashMap<String, String>) -> Self {
        Document {
            page_content,
            metadata,
        }
    }
    /// Create a human readable repr(Document) and str(Document).
    fn __repr__(&self) -> String {
        format!(
            "Document(page_content=\"{}\", metadata={:?})",
            self.page_content, self.metadata
        )
    }

    /// Create a human readable repr(Document) and str(Document).
    fn __str__(&self) -> String {
        self.__repr__()
    }

    /// Remove Non Ascii characters from document's page_content.
    ///
    ///For Example:
    ///
    /// \x88This text contains non-ascii characters!\x88
    ///     -> This text contains non-ascii characters!
    /// """
    fn clean_non_ascii_chars(&mut self) {
        let cleaned_page_content = self.page_content.chars().filter(|c| c.is_ascii()).collect();
        self.page_content = cleaned_page_content;
    }
    #[staticmethod]
    fn _unicode_bullets_pattern() -> String {
        let bullets_pattern: String = vec![
            "\u{0095}", "\u{2022}", "\u{2023}", "\u{2043}", "\u{3164}", "\u{204C}", "\u{204D}",
            "\u{2219}", "\u{25CB}", "\u{25CF}", "\u{25D8}", "\u{25E6}", "\u{2619}", "\u{2765}",
            "\u{2767}", "\u{29BE}", "\u{29BF}", "\u{002D}", "\u{2013}", "\u{25AA}", "\u{25AB}",
            "\\*", "\\x95", "·",
        ]
        .join("|");
        bullets_pattern
    }

    /// Remove bullets from page_content using a regular expression pattern.
    ///
    /// For Example:
    ///
    /// ●  This is an excellent point! -> This is an excellent point!
    fn clean_bullets(&mut self) {
        let text = &self.page_content;
        let unicode_bullets_pattern = Document::_unicode_bullets_pattern();
        let unicode_bullets_re: Regex =
            Regex::new(&format!(r"(?:{})", unicode_bullets_pattern)).unwrap();

        if unicode_bullets_re.find(text).is_some() {
            let cleaned_text = unicode_bullets_re.replace(text, "").to_string();
            self.page_content = cleaned_text.trim().to_string();
        }
    }

    /// Replace common ligatures like æ in page_content.
    ///
    /// For Example:
    ///
    /// The beneﬁts -> The benefits
    /// High quality ﬁnancial -> High quality financial
    fn clean_ligatures(&mut self) {
        let text = &self.page_content;
        let ligatures_map: HashMap<char, &str> = [
            ('æ', "ae"),
            ('Æ', "AE"),
            ('ﬀ', "ff"),
            ('ﬁ', "fi"),
            ('ﬂ', "fl"),
            ('ﬃ', "ffi"),
            ('ﬄ', "ffl"),
            ('ﬅ', "ft"),
            ('ʪ', "ls"),
            ('œ', "oe"),
            ('Œ', "OE"),
            ('ȹ', "qp"),
            ('ﬆ', "st"),
            ('ʦ', "ts"),
        ]
        .iter()
        .cloned()
        .collect();

        let mut cleaned_text = String::from(text);

        for (k, v) in ligatures_map.iter() {
            cleaned_text = cleaned_text.replace(*k, v);
        }

        self.page_content = cleaned_text;
    }

    /// Remove extraneous whitespace from page_content
    ///
    /// For Example:
    ///
    /// ITEM 1.     BUSINESS -> ITEM 1. BUSINESS
    fn clean_extra_whitespace(&mut self) {
        let text = &self.page_content;
        // Handle all line ending types: \r\n, \r, \n
        let cleaned_text = text
            .replace(0xa0 as char, " ") // Non-breaking space
            .replace("\r\n", " ") // Windows line ending
            .replace("\r", " ") // Old Mac line ending
            .replace("\n", " "); // Unix line ending
        let cleaned_text = Regex::new(r"([ ]{2,})")
            .unwrap()
            .replace_all(&cleaned_text, " ");
        self.page_content = cleaned_text.trim().to_string();
    }

    /// Groups paragraphs that have bullets and line breaks
    ///
    /// For example:
    ///
    /// '''○ The big red fox
    /// is walking down the lane.
    ///
    /// ○ At the end of the lane
    /// the fox met a friendly bear.'''
    ///
    /// Gets converted to
    ///
    /// '''○ The big red fox is walking down the lane.
    /// ○ At the end of the land the fox met a bear.'''
    #[staticmethod]
    fn _group_bullet_paragraph(paragraph: &str) -> Vec<String> {
        // Replace "e " at start with bullet - without lookahead
        let cleaned_paragraph = if paragraph.starts_with("e ") {
            format!("·{}", &paragraph[1..])
        } else {
            paragraph.to_string()
        };

        let bullets_pattern = Document::_unicode_bullets_pattern();
        let unicode_bullets_re: Regex = Regex::new(&format!(r"({})", bullets_pattern)).unwrap();

        // Pattern to replace newlines with spaces (not bullets!)
        let newline_pattern_re: Regex = Regex::new(r"\s*\n\s*").unwrap();

        let mut clean_paragraphs = Vec::new();

        // Manually split on bullets by finding all matches and splitting between them
        let mut bullet_positions = Vec::new();

        for mat in unicode_bullets_re.find_iter(&cleaned_paragraph) {
            bullet_positions.push(mat.start());
        }

        // Split text at bullet positions
        if bullet_positions.is_empty() {
            // No bullets found, process entire paragraph
            let cleaned = newline_pattern_re
                .replace_all(&cleaned_paragraph, " ")
                .to_string();
            if !cleaned.trim().is_empty() {
                clean_paragraphs.push(cleaned);
            }
        } else {
            for (i, &pos) in bullet_positions.iter().enumerate() {
                if i == 0 && pos > 0 {
                    // Text before first bullet
                    let segment = &cleaned_paragraph[0..pos];
                    let cleaned = newline_pattern_re.replace_all(segment, " ").to_string();
                    if !cleaned.trim().is_empty() {
                        clean_paragraphs.push(cleaned);
                    }
                }

                // Get text from this bullet to next bullet (or end)
                let start = pos;
                let end = if i + 1 < bullet_positions.len() {
                    bullet_positions[i + 1]
                } else {
                    cleaned_paragraph.len()
                };

                let segment = &cleaned_paragraph[start..end];
                let cleaned = newline_pattern_re.replace_all(segment, " ").to_string();
                if !cleaned.trim().is_empty() {
                    clean_paragraphs.push(cleaned);
                }
            }
        }

        clean_paragraphs
    }

    /// Groups paragraphs in page_content that have line breaks.
    ///
    /// For example:
    ///
    /// '''The big red fox
    /// is walking down the lane.
    ///
    /// At the end of the lane
    /// the fox met a bear.'''
    ///
    /// Gets converted to
    ///
    /// '''The big red fox is walking down the lane.
    /// At the end of the land the fox met a bear.'''
    fn group_broken_paragraphs(&mut self) {
        let text = &self.page_content;

        let bullets_pattern = Document::_unicode_bullets_pattern();

        // Pattern to match single newline with optional whitespace
        let paragraph_pattern = r"\s*\n\s*";
        // Pattern to match double newlines (blank line) - TWO consecutive paragraph patterns
        let double_paragraph_pattern = format!(r"({})", paragraph_pattern) + "{2}";
        let double_paragraph_pattern_re: Regex = Regex::new(&double_paragraph_pattern).unwrap();

        // Simple pattern to replace single newlines
        let single_newline_re: Regex = Regex::new(paragraph_pattern).unwrap();

        let unicode_bullets_re: Regex = Regex::new(&format!(r"(?:{})", bullets_pattern)).unwrap();

        // Split on double newlines (blank lines) to get separate paragraphs
        let paragraphs: Vec<&str> = double_paragraph_pattern_re.split(text).collect();
        let mut clean_paragraphs = Vec::new();

        for paragraph in paragraphs {
            if !paragraph.trim().is_empty() {
                let para_split: Vec<&str> = paragraph.split("\n").collect();
                let all_lines_short = para_split
                    .iter()
                    .all(|line| line.split_whitespace().count() < 5);

                // Check if paragraph starts with "e " or contains bullet patterns
                let has_e_bullet = paragraph.trim().starts_with("e ");
                if unicode_bullets_re.is_match(paragraph.trim()) || has_e_bullet {
                    clean_paragraphs.extend(Document::_group_bullet_paragraph(paragraph));
                } else if all_lines_short {
                    clean_paragraphs.extend(
                        para_split
                            .iter()
                            .filter(|line| !line.trim().is_empty())
                            .map(|line| line.to_string()),
                    );
                } else {
                    // Replace single newlines with spaces to join broken lines
                    clean_paragraphs
                        .push(single_newline_re.replace_all(paragraph, " ").to_string());
                }
            }
        }

        self.page_content = clean_paragraphs.join("\n\n");
    }

    /// Concatenates page_content that has one-line paragraph break pattern.
    ///
    /// For example,
    ///
    /// Iwan Roberts
    /// Roberts celebrating after scoring a goal for Norwich City
    /// in 2004
    ///
    /// Will be returned as:
    ///
    /// Iwan Roberts\n\nRoberts celebrating after scoring a goal for Norwich City\n\nin 2004
    fn new_line_grouper(&mut self) {
        let text = &self.page_content;
        let paragraphs: Vec<&str> = text.split("\n").collect();
        let clean_paragraphs: Vec<&str> = paragraphs
            .iter()
            .filter(|paragraph| !paragraph.trim().is_empty())
            .cloned()
            .collect();
        self.page_content = clean_paragraphs.join("\n\n")
    }

    /// Checks the ratio of new line (\n) over the total max_line_count
    ///
    /// If the ratio of new line is less than the threshold,
    /// the document is considered a new-line grouping type
    /// and return the original text
    ///
    /// If the ratio of new line is greater than or equal to the threshold,
    /// the document is considered a blank-line grouping type
    /// and passed on to group_broken_paragraphs function
    fn auto_paragraph_grouper(&mut self) {
        let text = &self.page_content;
        let max_line_count: usize = 2000;
        let threshold: f64 = 0.1;
        let lines: Vec<&str> = text.split("\n").collect();
        let max_line_count = std::cmp::min(lines.len(), max_line_count);
        let (mut line_count, mut empty_line_count) = (0, 0);

        for line in &lines[..max_line_count] {
            line_count += 1;
            if line.trim().is_empty() {
                empty_line_count += 1;
            }
        }

        let ratio = empty_line_count as f64 / line_count as f64;

        if ratio < threshold {
            self.new_line_grouper()
        } else {
            self.group_broken_paragraphs()
        }
    }

    /// A helper function that calls all of the cleaning functions at once
    pub fn clean(&mut self) {
        self.clean_extra_whitespace();
        self.clean_ligatures();
        self.clean_bullets();
        self.clean_non_ascii_chars();
        self.auto_paragraph_grouper();
    }

    /// An opinionated splitter based on LangChain's [RecursiveCharacterTextSplitter](https://api.python.langchain.com/en/latest/text_splitter/langchain.text_splitter.RecursiveCharacterTextSplitter.html).
    ///
    /// This splitter will always default to 1/3 of the chunk_size as the chunk_overlap.
    pub fn recursive_character_splitter(&self, chunk_size: usize) -> Vec<Document> {
        let separators = &["\n\n", "\n", " ", ""];
        let split_docs = split_and_merge(&self.page_content, chunk_size, separators);
        let mut result = Vec::new();
        for text in split_docs {
            let doc = Document {
                page_content: text,
                metadata: self.metadata.clone(),
            };
            result.push(doc);
        }
        result
    }
    /// A basic splitter to split on a number of characters.
    pub fn split_on_num_characters(&self, num_characters: u32) -> Vec<Document> {
        let mut result = Vec::new();
        let mut current_chunk = String::new();
        for (index, character) in self.page_content.chars().enumerate() {
            current_chunk.push(character);
            if (index + 1) % num_characters as usize == 0 {
                let doc = Document {
                    page_content: current_chunk.clone(),
                    metadata: self.metadata.clone(),
                };
                result.push(doc);
                current_chunk.clear();
            }
        }
        if !current_chunk.is_empty() {
            let doc = Document {
                page_content: current_chunk.clone(),
                metadata: self.metadata.clone(),
            };
            result.push(doc);
        }
        result
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn rs_document(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Document>()?;
    m.add_function(wrap_pyfunction!(clean_and_split_docs, m)?)?;
    Ok(())
}

#[pyfunction]
fn clean_and_split_docs(docs: &PyList, chunk_size: usize) -> PyResult<Vec<Document>> {
    let doc_vec: Vec<Document> = docs.extract::<Vec<Document>>().unwrap();

    let result: Vec<Document> = doc_vec
        .par_iter()
        .map(|document| {
            let mut document = document.clone();
            document.clean();
            document.recursive_character_splitter(chunk_size)
        })
        .flatten()
        .collect();

    Ok(result)
}
