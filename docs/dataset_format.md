# Dataset Format Specification

This document describes the dataset format expected by Zeta Reason for evaluating language models.

## Table of Contents

- [Overview](#overview)
- [JSONL Format](#jsonl-format)
- [Task Schema](#task-schema)
- [Field Specifications](#field-specifications)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Validation](#validation)
- [Common Benchmarks](#common-benchmarks)

## Overview

Zeta Reason uses **JSONL** (JSON Lines) format for datasets. Each line in the file represents a single evaluation task as a JSON object.

**Key Benefits:**
- **Streaming**: Process tasks one at a time
- **Human-readable**: Easy to inspect and edit
- **Append-only**: Add tasks without rewriting file
- **Tool-friendly**: Compatible with `jq`, grep, etc.

## JSONL Format

### Basic Structure

```jsonl
{"id": "1", "input": "Question 1", "target": "Answer 1"}
{"id": "2", "input": "Question 2", "target": "Answer 2"}
{"id": "3", "input": "Question 3", "target": "Answer 3"}
```

**Requirements:**
- One JSON object per line
- No commas between lines
- Valid JSON on each line
- UTF-8 encoding

## Task Schema

### Required Fields

```typescript
interface Task {
  id: string;        // Unique identifier for the task
  input: string;     // The question/prompt for the model
  target: string;    // The expected correct answer
}
```

### TypeScript Definition

```typescript
export interface Task {
  /**
   * Unique identifier for this task.
   * Must be unique within the dataset.
   * Examples: "1", "task_001", "gsm8k_42"
   */
  id: string;

  /**
   * The input prompt/question for the model.
   * Can be a question, problem, or instruction.
   * Example: "What is the capital of France?"
   */
  input: string;

  /**
   * The target/expected correct answer.
   * Used for exact match comparison.
   * Example: "Paris"
   */
  target: string;
}
```

### Python Definition

```python
from pydantic import BaseModel, Field

class Task(BaseModel):
    """A single evaluation task."""

    id: str = Field(
        ...,
        description="Unique identifier for this task"
    )

    input: str = Field(
        ...,
        description="The input prompt/question for the model"
    )

    target: str = Field(
        ...,
        description="The expected correct answer"
    )
```

## Field Specifications

### `id` Field

**Purpose:** Uniquely identifies each task within the dataset.

**Requirements:**
- **Type**: String
- **Uniqueness**: Must be unique across all tasks
- **Length**: No strict limit, but keep under 256 chars
- **Format**: Alphanumeric + underscores/hyphens recommended

**Examples:**
```json
"id": "1"
"id": "task_001"
"id": "gsm8k_0042"
"id": "math-algebra-quadratic-001"
```

**Best Practices:**
- Use sequential numbers for simple datasets
- Include dataset prefix for mixed datasets
- Use descriptive IDs for debugging

### `input` Field

**Purpose:** The question, problem, or prompt to present to the model.

**Requirements:**
- **Type**: String
- **Encoding**: UTF-8
- **Length**: No strict limit (but be mindful of model context limits)
- **Content**: Clear, unambiguous task description

**Examples:**

**Simple Question:**
```json
"input": "What is the capital of France?"
```

**Math Problem:**
```json
"input": "If x + 5 = 12, what is the value of x?"
```

**Multi-Step Problem:**
```json
"input": "A store sells apples for $2 each and oranges for $3 each. If John buys 5 apples and 3 oranges, how much does he spend in total?"
```

**With Instructions:**
```json
"input": "Solve the following equation step by step: 3x - 7 = 14"
```

**Best Practices:**
- Be specific and unambiguous
- Include all necessary context
- For CoT evaluation, explicitly request step-by-step reasoning
- Avoid typos and grammatical errors

### `target` Field

**Purpose:** The expected correct answer for exact match comparison.

**Requirements:**
- **Type**: String
- **Format**: Matches expected answer format
- **Normalization**: Answer will be normalized (lowercase, stripped)

**Examples:**

**Single Word:**
```json
"target": "Paris"
```

**Number:**
```json
"target": "42"
```

**Short Phrase:**
```json
"target": "the quick brown fox"
```

**Formula/Expression:**
```json
"target": "x = 7"
```

**Best Practices:**
- Use canonical form (e.g., "7" not "seven")
- Be consistent with formatting
- Avoid extra punctuation
- For numerical answers, use standard notation
- For multiple valid answers, choose the most common form

## Examples

### Example 1: Math Dataset

```jsonl
{"id": "1", "input": "What is 15 * 23?", "target": "345"}
{"id": "2", "input": "If x + 5 = 12, what is x?", "target": "7"}
{"id": "3", "input": "What is the square root of 144?", "target": "12"}
{"id": "4", "input": "Solve for y: 2y - 8 = 16", "target": "12"}
{"id": "5", "input": "What is 7! (7 factorial)?", "target": "5040"}
```

### Example 2: General Knowledge

```jsonl
{"id": "geo_001", "input": "What is the capital of France?", "target": "Paris"}
{"id": "geo_002", "input": "What is the largest ocean on Earth?", "target": "Pacific Ocean"}
{"id": "sci_001", "input": "What is the chemical symbol for gold?", "target": "Au"}
{"id": "sci_002", "input": "How many planets are in our solar system?", "target": "8"}
{"id": "hist_001", "input": "In what year did World War II end?", "target": "1945"}
```

### Example 3: Chain-of-Thought Prompting

```jsonl
{"id": "cot_001", "input": "Think step by step: If a train travels 60 miles in 1 hour, how far does it travel in 2.5 hours?", "target": "150"}
{"id": "cot_002", "input": "Let's solve this step by step: A rectangle has length 8 and width 5. What is its area?", "target": "40"}
{"id": "cot_003", "input": "Work through this problem: If 3 apples cost $6, how much do 7 apples cost?", "target": "14"}
```

### Example 4: Complex Multi-Step Problems

```jsonl
{"id": "gsm8k_042", "input": "Janet's ducks lay 16 eggs per day. She eats three for breakfast every morning and bakes muffins for her friends every day with four. She sells the remainder at the farmers' market daily for $2 per fresh duck egg. How much in dollars does she make every day at the farmers' market?", "target": "18"}
```

## Best Practices

### 1. Task Design

**Do:**
- ✅ Make questions clear and unambiguous
- ✅ Provide all necessary context
- ✅ Use consistent formatting
- ✅ Test a few examples manually first

**Don't:**
- ❌ Include ambiguous questions
- ❌ Assume unstated knowledge
- ❌ Use inconsistent formats
- ❌ Include typos or errors

### 2. Answer Format

**Do:**
- ✅ Use canonical forms
- ✅ Be consistent across similar questions
- ✅ Use standard notation
- ✅ Verify answers are correct

**Don't:**
- ❌ Use multiple formats for same answer type
- ❌ Include extraneous punctuation
- ❌ Use ambiguous abbreviations
- ❌ Forget to verify correctness

### 3. Dataset Size

**Recommendations:**
- **Small test set**: 10-50 tasks (quick iteration)
- **Development set**: 100-500 tasks (model tuning)
- **Evaluation set**: 500-5000 tasks (robust benchmarking)
- **Large benchmark**: 5000+ tasks (public leaderboard)

**Sampling:**
- Use Zeta Reason's random sampling for faster iteration
- Always evaluate on full set for final results

### 4. File Organization

**Recommended Structure:**
```
datasets/
├── math/
│   ├── arithmetic.jsonl
│   ├── algebra.jsonl
│   └── geometry.jsonl
├── knowledge/
│   ├── science.jsonl
│   └── history.jsonl
└── reasoning/
    ├── logic.jsonl
    └── common_sense.jsonl
```

### 5. Version Control

- Track datasets in git
- Use descriptive commit messages
- Tag versions (v1.0, v2.0)
- Document changes in CHANGELOG

## Validation

### Manual Validation

Before uploading to Zeta Reason:

1. **Check JSONL format:**
   ```bash
   # Each line should be valid JSON
   cat dataset.jsonl | jq '.'
   ```

2. **Verify required fields:**
   ```bash
   # Check for missing fields
   cat dataset.jsonl | jq 'select(.id == null or .input == null or .target == null)'
   ```

3. **Check for duplicates:**
   ```bash
   # Find duplicate IDs
   cat dataset.jsonl | jq -r '.id' | sort | uniq -d
   ```

4. **Inspect sample:**
   ```bash
   # View first 5 tasks
   head -n 5 dataset.jsonl | jq '.'
   ```

### Programmatic Validation

```python
import json
from pathlib import Path
from typing import List, Set

def validate_dataset(file_path: Path) -> List[str]:
    """Validate a JSONL dataset file."""
    errors = []
    seen_ids: Set[str] = set()
    line_num = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_num += 1

            # Check valid JSON
            try:
                task = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_num}: Invalid JSON - {e}")
                continue

            # Check required fields
            for field in ['id', 'input', 'target']:
                if field not in task:
                    errors.append(f"Line {line_num}: Missing field '{field}'")

            # Check types
            if not isinstance(task.get('id'), str):
                errors.append(f"Line {line_num}: 'id' must be string")
            if not isinstance(task.get('input'), str):
                errors.append(f"Line {line_num}: 'input' must be string")
            if not isinstance(task.get('target'), str):
                errors.append(f"Line {line_num}: 'target' must be string")

            # Check for duplicates
            task_id = task.get('id')
            if task_id in seen_ids:
                errors.append(f"Line {line_num}: Duplicate ID '{task_id}'")
            seen_ids.add(task_id)

    return errors

# Usage
errors = validate_dataset(Path("dataset.jsonl"))
if errors:
    for error in errors:
        print(f"ERROR: {error}")
else:
    print("✓ Dataset is valid!")
```

### Frontend Validation

Zeta Reason automatically validates on upload:

- ✅ JSONL format
- ✅ Required fields
- ✅ Field types
- ❌ Provides clear error messages

## Common Benchmarks

### GSM8K Format

Grade School Math 8K dataset:

```jsonl
{"id": "gsm8k_0", "input": "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?", "target": "72"}
```

**Converting from original:**
```python
# Original GSM8K format
{
  "question": "...",
  "answer": "####72"
}

# Convert to Zeta Reason format
{
  "id": f"gsm8k_{idx}",
  "input": data["question"],
  "target": data["answer"].split("####")[1].strip()
}
```

### MMLU Format

Multiple choice questions (convert to text):

```jsonl
{"id": "mmlu_001", "input": "What is the capital of France? A) London B) Paris C) Berlin D) Madrid", "target": "B"}
```

### Custom Reasoning Tasks

```jsonl
{"id": "logic_001", "input": "If all cats are mammals, and all mammals are animals, then all cats are: A) Plants B) Animals C) Minerals", "target": "B"}
```

## Advanced Features (Future)

### Metadata Fields (Planned)

```json
{
  "id": "task_001",
  "input": "What is 2+2?",
  "target": "4",
  "metadata": {
    "difficulty": "easy",
    "category": "arithmetic",
    "source": "custom",
    "tags": ["math", "addition"]
  }
}
```

### Multi-Answer Support (Planned)

```json
{
  "id": "task_001",
  "input": "Name a primary color",
  "target": ["red", "blue", "yellow"]
}
```

### Partial Credit (Planned)

```json
{
  "id": "task_001",
  "input": "List three planets",
  "target": "Earth, Mars, Venus",
  "scoring": "partial_credit"
}
```

## Troubleshooting

### Common Issues

**Issue**: "Failed to parse line X"
- **Cause**: Invalid JSON syntax
- **Fix**: Validate JSON with `jq` or JSON linter

**Issue**: "Missing required field"
- **Cause**: Task missing `id`, `input`, or `target`
- **Fix**: Add missing fields

**Issue**: "Duplicate task ID"
- **Cause**: Same ID used multiple times
- **Fix**: Ensure all IDs are unique

**Issue**: "Empty dataset"
- **Cause**: File is empty or all lines are invalid
- **Fix**: Check file content and format

### Getting Help

- Check validation errors in Zeta Reason UI
- Use `jq` for JSON debugging
- Review example datasets in repo
- Ask in GitHub Discussions

---

## Tools

### Dataset Converter

Convert CSV to JSONL:

```python
import csv
import json

def csv_to_jsonl(csv_file: str, jsonl_file: str):
    """Convert CSV to JSONL format."""
    with open(csv_file, 'r') as cf, open(jsonl_file, 'w') as jf:
        reader = csv.DictReader(cf)
        for row in reader:
            task = {
                "id": row["id"],
                "input": row["question"],
                "target": row["answer"]
            }
            jf.write(json.dumps(task) + '\n')
```

### Dataset Splitter

Split into train/test:

```python
import random

def split_dataset(
    input_file: str,
    train_file: str,
    test_file: str,
    test_ratio: float = 0.2
):
    """Split dataset into train and test sets."""
    with open(input_file, 'r') as f:
        tasks = [json.loads(line) for line in f]

    random.shuffle(tasks)
    split_idx = int(len(tasks) * (1 - test_ratio))

    train_tasks = tasks[:split_idx]
    test_tasks = tasks[split_idx:]

    for tasks, file in [(train_tasks, train_file), (test_tasks, test_file)]:
        with open(file, 'w') as f:
            for task in tasks:
                f.write(json.dumps(task) + '\n')
```

---

**Last Updated:** January 2025
**Version:** 1.0.0-beta
