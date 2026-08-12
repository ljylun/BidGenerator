# Tasks

- [x] Task 1: Run book-to-skill extraction on the PDF
  - [x] SubTask 1.1: Locate the book-to-skill extract.py script in the skills directory
  - [x] SubTask 1.2: Run extraction with `BOOK_TYPE=technical` to preserve code blocks and structure
  - [x] SubTask 1.3: Verify `full_text.txt` and `metadata.json` are created in the temp work directory

- [x] Task 2: Analyze extracted content and determine skill structure
  - [x] SubTask 2.1: Read first 8,000 characters of `full_text.txt` to identify title, authors, and chapter structure
  - [x] SubTask 2.2: Map all chapter headings and section boundaries
  - [x] SubTask 2.3: Identify core frameworks, principles, techniques, and anti-patterns per chapter
  - [x] SubTask 2.4: Determine skill slug name (e.g., `tunstall-transformers` or `nlp-transformers-huggingface`)

- [x] Task 3: Generate chapter summary files
  - [x] SubTask 3.1: Create `chapters/ch03-transformer-anatomy.md` with core idea, frameworks, key concepts, mental models, anti-patterns, code examples, and key takeaways
  - [x] SubTask 3.2: Create `chapters/ch07-question-answering.md` with QA-specific frameworks (ExtractiveQA, RAG, DPR), evaluation metrics, and Haystack pipeline patterns
  - [x] SubTask 3.3: Create `chapters/ch11-future-directions.md` with scaling strategies, efficient attention, multimodal transformers, and research directions

- [x] Task 4: Generate supporting reference files
  - [x] SubTask 4.1: Create `glossary.md` with alphabetically sorted key terms and definitions
  - [x] SubTask 4.2: Create `patterns.md` with concrete techniques (scaled dot-product attention, multi-head attention, RAG, DPR, etc.)
  - [x] SubTask 4.3: Create `cheatsheet.md` with decision rules, trade-off matrices, and thresholds for transformer selection and QA system design

- [x] Task 5: Generate master SKILL.md
  - [x] SubTask 5.1: Create `SKILL.md` with metadata, usage instructions, core frameworks, chapter index, topic index, and supporting files reference
  - [x] SubTask 5.2: Ensure SKILL.md body stays under 4,000 tokens with most important content front-loaded

- [x] Task 6: Finalize and report
  - [x] SubTask 6.1: Clean up temporary extraction files
  - [x] SubTask 6.2: Verify all generated files exist and are properly formatted
  - [x] SubTask 6.3: Report skill location, file sizes, and usage instructions to the user

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 2
- Task 5 depends on Tasks 3 and 4
- Task 6 depends on Task 5
