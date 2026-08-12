# NLP with Transformers Book Skill Spec

## Why
Convert the O'Reilly book excerpt "Natural Language Processing with Transformers" into a structured agent skill that captures the author's frameworks, techniques, and mental models for building language applications with Hugging Face.

## What Changes
- Extract text from the PDF containing Chapters 3, 7, and 11
- Analyze the book structure to identify frameworks, principles, and techniques
- Generate a complete skill with SKILL.md, chapter summaries, glossary, patterns, and cheatsheet
- **BREAKING**: None — this creates a new skill without modifying existing systems

## Impact
- Affected specs: None — new capability
- Affected code: Creates new skill files under `.trae/skills/` or equivalent skills directory

## ADDED Requirements
### Requirement: Book-to-Skill Conversion
The system SHALL convert the PDF `g:\Projects\BidGenerator\ebooks\oreilly_chapter_excerpt_nlpt.pdf` into a structured agent skill.

#### Scenario: Successful extraction and skill generation
- **WHEN** the extraction script processes the PDF
- **THEN** the system produces `full_text.txt` and `metadata.json` in a temporary work directory

#### Scenario: Skill file generation
- **WHEN** the book structure is analyzed
- **THEN** the system generates:
  - `SKILL.md` with core frameworks and chapter index
  - `chapters/ch03-transformer-anatomy.md`
  - `chapters/ch07-question-answering.md`
  - `chapters/ch11-future-directions.md`
  - `glossary.md` with key terms
  - `patterns.md` with techniques and design patterns
  - `cheatsheet.md` with decision rules and quick reference

#### Scenario: Skill usability
- **WHEN** an agent loads the generated skill
- **THEN** the agent can answer questions about transformer anatomy, question answering systems, and future directions in NLP using the book's frameworks

## MODIFIED Requirements
None.

## REMOVED Requirements
None.
