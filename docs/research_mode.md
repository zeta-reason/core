# Research Mode Guide

Research Mode provides granular, per-task analysis for deep investigation of model behavior. This guide explains how to use Research Mode effectively for debugging, error analysis, and model comparison.

## Table of Contents

- [Overview](#overview)
- [When to Use Research Mode](#when-to-use-research-mode)
- [Interface Overview](#interface-overview)
- [Features](#features)
- [Workflows](#workflows)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

Research Mode complements Summary Mode by providing detailed, task-level insights. While Summary Mode shows aggregated metrics and high-level patterns, Research Mode lets you inspect individual model responses, reasoning chains, and errors.

**Key Differences:**

| Feature | Summary Mode | Research Mode |
|---------|--------------|---------------|
| **View Level** | Aggregated | Per-task |
| **Use Case** | Quick overview | Deep investigation |
| **Metrics** | Summary statistics | Individual values |
| **CoT Analysis** | Sample viewer | Full per-task reasoning |
| **Comparison** | Side-by-side charts | Task-by-task differences |
| **Filtering** | None | Advanced filters |
| **Export** | Overall results | Filtered subsets |

## When to Use Research Mode

### Use Research Mode When You Need To:

1. **Debug Specific Failures**
   - "Why did the model get task #42 wrong?"
   - "What pattern do failed tasks share?"

2. **Analyze Reasoning Quality**
   - "How does the model approach multi-step problems?"
   - "Are there systematic reasoning errors?"

3. **Compare Model Behaviors**
   - "How do GPT-4 and Claude differ on edge cases?"
   - "Which model provides clearer explanations?"

4. **Investigate Calibration Issues**
   - "Why is the model overconfident on wrong answers?"
   - "Which tasks have high confidence but low correctness?"

5. **Find Dataset Issues**
   - "Are there ambiguous questions?"
   - "Are the target answers always correct?"

6. **Extract Examples**
   - "Find good examples for few-shot prompts"
   - "Identify representative failures for error analysis"

## Interface Overview

### Switching to Research Mode

After running an evaluation, click the **"Research"** button in the mode toggle:

```
┌─────────────────────────────────────┐
│  [Summary] [Research] ← Click here  │
└─────────────────────────────────────┘
```

### Layout

```
┌──────────────────────────────────────────────────────────┐
│                      Research Mode                        │
├──────────────────────────────────────────────────────────┤
│  Filters: [All ▼] [Correctness ▼] [Search...]          │
├──────────────────────────────────────────────────────────┤
│  ┌────────────────────┐ ┌─────────────────────────────┐ │
│  │  Task List         │ │  Task Detail                │ │
│  │                    │ │                             │ │
│  │  ☑ Task 1          │ │  Input: "What is 2+2?"     │ │
│  │  ☑ Task 2          │ │                             │ │
│  │  ☒ Task 3  ← Error │ │  Chain of Thought:         │ │
│  │  ☑ Task 4          │ │  "Let me calculate..."     │ │
│  │  ...               │ │                             │ │
│  │                    │ │  Answer: "4"               │ │
│  │  Showing 42/100    │ │  Target: "4"               │ │
│  │                    │ │  Confidence: 0.95          │ │
│  └────────────────────┘ └─────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Features

### 1. Task List

**Description:** Scrollable list of all evaluated tasks.

**Elements:**
- ✅ **Checkmark** (green) - Correct answer
- ❌ **X mark** (red) - Incorrect answer
- **Task ID** - Unique identifier
- **Preview** - First few words of input

**Interactions:**
- Click to view task details
- Scroll to browse all tasks
- Filter to show subset

**Example:**
```
☑ Task 1: "What is 2+2?"
☑ Task 2: "If x+5=12..."
☒ Task 3: "Solve for y..." ← Incorrect
☑ Task 4: "What is..."
```

### 2. Task Detail View

**Description:** Full information for selected task.

**Sections:**

#### Input
The original question/prompt:
```
Input: "If a train travels 60 miles in 1 hour, how far does
it travel in 2.5 hours?"
```

#### Chain of Thought (if enabled)
The model's reasoning process:
```
Chain of Thought:
"Let me solve this step by step:
1. The train travels 60 miles in 1 hour
2. To find distance in 2.5 hours, multiply: 60 * 2.5
3. 60 * 2.5 = 150 miles
Therefore, the answer is 150 miles."
```

#### Model Answer
The model's extracted answer:
```
Answer: "150"
Confidence: 0.92
```

#### Target Answer
The expected correct answer:
```
Target: "150"
```

#### Correctness
Visual indicator:
```
✅ Correct
```
or
```
❌ Incorrect
```

#### Metadata
Additional information:
```
CoT Tokens: 45
Step Count: 3
Latency: 1,250 ms
```

### 3. Multi-Model Comparison

When comparing multiple models, Research Mode shows side-by-side results:

```
┌──────────────────────────────────────────────────────────┐
│  Task 3: "What is the capital of France?"               │
├──────────────────────────────────────────────────────────┤
│  Model 1: GPT-4                │  Model 2: GPT-3.5      │
│  ────────────────────           │  ────────────────────  │
│                                 │                        │
│  CoT: "The capital of France   │  CoT: "France capital  │
│  is Paris, which is also the   │  is Paris."            │
│  largest city..."               │                        │
│                                 │                        │
│  Answer: "Paris" ✅             │  Answer: "Paris" ✅    │
│  Confidence: 0.98               │  Confidence: 0.85      │
│  Tokens: 23                     │  Tokens: 8             │
└──────────────────────────────────────────────────────────┘
```

**Highlights:**
- Disagreements highlighted in **orange**
- Detailed reasoning comparison
- Efficiency differences (tokens, latency)

### 4. Filtering

**Available Filters:**

#### Correctness Filter
```
[All Tasks ▼]
├─ All Tasks
├─ Correct Only
└─ Incorrect Only
```

**Use Cases:**
- Focus on errors: "Incorrect Only"
- Find good examples: "Correct Only"

#### Text Search
```
[Search input/output...]
```

**Examples:**
- Search for "France" to find geography questions
- Search for specific numbers or keywords
- Find tasks mentioning certain concepts

#### Model-Specific (Multi-Model Comparison)
```
[Show Differences Only ☐]
```

**Use Case:**
- See only tasks where models disagree
- Focus on interesting edge cases

### 5. Export Filtered Results

Export the currently filtered subset:

```
[Export Filtered (JSON)] [Export Filtered (CSV)]
```

**Use Cases:**
- Create error analysis dataset
- Extract specific examples
- Share findings with team

## Workflows

### Workflow 1: Error Analysis

**Goal:** Understand why the model fails on certain tasks.

**Steps:**

1. **Filter to errors only**
   ```
   Correctness: [Incorrect Only ▼]
   ```

2. **Browse error list**
   - Look for patterns in task IDs
   - Check input previews for common themes

3. **Inspect individual errors**
   - Click on each error
   - Read the chain of thought
   - Identify reasoning failures:
     - Arithmetic mistakes
     - Misread input
     - Logical errors
     - Knowledge gaps

4. **Categorize errors**
   - Create a spreadsheet or notes
   - Group by error type:
     - Calculation errors
     - Misinterpretation
     - Incomplete reasoning
     - Hallucination

5. **Export for further analysis**
   ```
   [Export Filtered (JSON)]
   ```

**Example Findings:**
```
Error Categories (15 total errors):
- Arithmetic mistakes: 8 (53%)
- Misread input: 4 (27%)
- Logical errors: 2 (13%)
- Other: 1 (7%)
```

### Workflow 2: Model Comparison

**Goal:** Compare how different models handle the same tasks.

**Steps:**

1. **Run multi-model evaluation**
   - Configure 2-3 models
   - Run on same dataset

2. **Switch to Research Mode**
   - View side-by-side comparison

3. **Enable "Show Differences Only"**
   ```
   [Show Differences Only ☑]
   ```

4. **Analyze disagreements**
   - Why did GPT-4 get it right and GPT-3.5 wrong?
   - Which model's reasoning is clearer?
   - Are errors systematic or random?

5. **Compare reasoning quality**
   - Length and clarity of explanations
   - Step-by-step logic
   - Confidence calibration

6. **Document findings**
   - Note which model excels at what
   - Identify use-case specific recommendations

**Example Insights:**
```
GPT-4 vs GPT-3.5 Comparison:
- Agreement: 85/100 tasks
- GPT-4 unique correct: 12 tasks (complex reasoning)
- GPT-3.5 unique correct: 3 tasks (simple factual)
- Both wrong: 0 tasks
```

### Workflow 3: Calibration Investigation

**Goal:** Find tasks where confidence doesn't match correctness.

**Steps:**

1. **Filter to incorrect answers**
   ```
   Correctness: [Incorrect Only ▼]
   ```

2. **Browse tasks**
   - Look at confidence values
   - Identify high-confidence errors

3. **Analyze overconfident errors**
   - Read the chain of thought
   - Look for:
     - Assertive language ("clearly", "obviously")
     - Missing doubt markers
     - Simplified reasoning

4. **Compare to underconfident correct answers**
   - Switch to "Correct Only"
   - Find tasks with confidence < 0.5
   - Analyze hedging behavior

5. **Identify calibration patterns**
   - Which task types cause overconfidence?
   - Are certain domains poorly calibrated?

**Example Findings:**
```
Calibration Issues:
- High confidence errors (conf > 0.8, wrong): 5 tasks
  → Mostly arithmetic with multiple steps
- Low confidence correct (conf < 0.5, right): 3 tasks
  → Ambiguous phrasing in questions
```

### Workflow 4: Dataset Quality Check

**Goal:** Verify dataset quality and identify issues.

**Steps:**

1. **Review random sample**
   - Browse diverse tasks
   - Check for clarity and correctness

2. **Look for systematic errors**
   - If model consistently fails on certain tasks
   - Verify target answers are actually correct

3. **Check for ambiguity**
   - Tasks where both models disagree
   - Inspect if question is ambiguous

4. **Identify outliers**
   - Very high/low confidence
   - Very long/short reasoning
   - Check if task is malformed

5. **Document dataset issues**
   - Note problematic tasks
   - Suggest corrections or removals

**Example Issues Found:**
```
Dataset Issues:
- Task 23: Target answer incorrect (should be "4", not "5")
- Task 67: Ambiguous question (multiple valid answers)
- Task 91: Typo in input ("waht" instead of "what")
```

## Best Practices

### 1. Start with Summary Mode

**Rationale:** Get the big picture first.

**Workflow:**
1. Run evaluation
2. Check Summary Mode metrics
3. Identify concerning patterns
4. Switch to Research Mode for investigation

### 2. Use Filters Effectively

**Rationale:** Focus on relevant subset.

**Tips:**
- Start with "All Tasks" to get sense of data
- Apply filters one at a time
- Combine filters for precise targeting
- Document filter settings when sharing findings

### 3. Take Notes

**Rationale:** Capture insights for later reference.

**What to Note:**
- Task IDs of interesting examples
- Patterns in errors or reasoning
- Ideas for prompt improvements
- Dataset quality issues
- Model-specific behaviors

**Template:**
```markdown
## Research Session: [Date]
**Dataset:** GSM8K
**Models:** GPT-4, GPT-3.5-turbo

### Key Findings
- GPT-4 excels at multi-step arithmetic
- GPT-3.5 struggles with word problems >100 words

### Interesting Tasks
- Task 42: Both models correct but very different reasoning
- Task 67: GPT-4 wrong despite high confidence (0.95)

### Action Items
- Fix target answer for task 23
- Consider adding CoT examples for word problems
```

### 4. Export and Archive

**Rationale:** Preserve insights for future reference.

**What to Export:**
- Full results (JSON) for archival
- Filtered subsets (CSV) for analysis
- Screenshots of interesting cases
- Summary notes (Markdown)

### 5. Iterate and Improve

**Rationale:** Use insights to improve prompts and datasets.

**Feedback Loop:**
1. Analyze errors in Research Mode
2. Identify root causes
3. Update prompts or dataset
4. Re-evaluate
5. Compare improvements

## Examples

### Example 1: Finding Arithmetic Errors

**Scenario:** Model has 85% accuracy on math dataset, need to understand the 15% errors.

**Process:**

1. **Filter to errors**
   - Correctness: Incorrect Only
   - Result: 15 tasks shown

2. **Browse tasks**
   - Notice pattern: Most are multi-digit multiplication

3. **Inspect task 42**
   ```
   Input: "What is 237 * 45?"

   CoT: "Let me calculate:
   200 * 45 = 9000
   37 * 45 = 1665
   Total: 9000 + 1665 = 10665"

   Answer: "10665" ✅
   Target: "10665"
   ```
   Wait, this is marked correct. Check filter again.

4. **Inspect task 67**
   ```
   Input: "What is 123 * 67?"

   CoT: "Let me calculate:
   100 * 67 = 6700
   23 * 67 = 1641
   Total: 6700 + 1641 = 8341"

   Answer: "8341" ❌
   Target: "8241"
   ```
   Found it! Arithmetic error in second step.

5. **Pattern identified**
   - 12 of 15 errors are in the multiplication steps
   - Model splits correctly but makes calculation mistakes

**Action:** Consider adding worked examples or using calculator tool.

### Example 2: Model Disagreement Analysis

**Scenario:** GPT-4 and Claude disagree on 20/100 tasks. Investigate why.

**Process:**

1. **Enable "Show Differences Only"**

2. **Browse disagreements**
   - GPT-4 correct, Claude wrong: 15 tasks
   - Claude correct, GPT-4 wrong: 5 tasks

3. **Analyze GPT-4 advantages**
   - Tasks 12, 34, 56: Complex multi-step reasoning
   - GPT-4 breaks down steps more clearly
   - Claude sometimes skips intermediate steps

4. **Analyze Claude advantages**
   - Tasks 89, 92: Factual knowledge questions
   - Claude provides more detailed context
   - GPT-4 occasionally overcomplicates

5. **Insight**
   - Use GPT-4 for complex reasoning
   - Use Claude for knowledge-heavy tasks

### Example 3: High-Confidence Error Investigation

**Scenario:** Model has high Brier score. Find overconfident mistakes.

**Process:**

1. **Filter to incorrect answers**

2. **Sort by confidence** (mental note of high values)

3. **Inspect task 78**
   ```
   Input: "Is 17 a prime number?"

   CoT: "Let me check:
   17 is not divisible by 2, 3, 5, 7, 11, 13
   Clearly, 17 is prime."

   Answer: "Yes" ✅
   Target: "Yes"
   Confidence: 0.99
   ```
   This one is correct.

4. **Inspect task 91**
   ```
   Input: "How many days in a leap year?"

   CoT: "A leap year has an extra day in February.
   Normally 365 days, so leap year has 365 + 1 = 366."

   Answer: "366" ✅
   Target: "366"
   Confidence: 0.95
   ```
   Also correct.

5. **Find task 103**
   ```
   Input: "What is 0.1 + 0.2 in decimal?"

   CoT: "Simply add: 0.1 + 0.2 = 0.3"

   Answer: "0.3" ❌
   Target: "0.30000000000000004"  # Due to floating point
   Confidence: 0.98
   ```
   Found the issue! Model is overconfident on numeric edge cases.

**Action:** Review dataset targets for correctness, consider numerical tolerance.

---

## Keyboard Shortcuts

(Future feature)

```
j/k         Navigate tasks up/down
Space       Toggle task selection
f           Focus search box
c           Toggle correctness filter
Esc         Clear filters
```

---

## Troubleshooting

### Issue: "No tasks shown"

**Cause:** Filters too restrictive
**Solution:** Reset filters to "All Tasks"

### Issue: "Slow scrolling with large datasets"

**Cause:** Rendering 1000+ tasks
**Solution:** Use filtering to reduce visible set
**Future:** Virtual scrolling for performance

### Issue: "Can't find specific task"

**Cause:** Not using search
**Solution:** Use text search for task ID or keywords

---

## Tips and Tricks

1. **Use search for task IDs**
   - Search "task_042" to jump directly

2. **Export before filtering**
   - Keep full results, filter later in spreadsheet

3. **Screenshot interesting cases**
   - Visual reference for presentations

4. **Compare against baseline**
   - Load previous experiment, switch to new one
   - Manual comparison of specific tasks

5. **Iterate quickly**
   - Fix one issue, re-run, check in Research Mode
   - Rapid feedback loop

---

**Last Updated:** January 2025
**Version:** 1.0.0-beta
