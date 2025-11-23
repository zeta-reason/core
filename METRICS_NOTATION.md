# Metric Notation Guide

## Understanding Metric Values in Zeta Reason

Zeta Reason uses a consistent notation system to distinguish between measured zeros and missing data across all metric displays.

### Notation System

| Display | Meaning | Example Context |
|---------|---------|-----------------|
| **`0.000`** | Real measured zero | Model has 0% accuracy, or metric computed to exactly zero |
| **`—`** | No data available | Metric not yet implemented, or insufficient data to compute |

### Why This Matters

This distinction is critical for research interpretation:

- **`0.000` (Real Zero)**: The metric was successfully computed and the actual value is zero
  - Example: Accuracy = 0.000 means the model got 0% of answers correct
  - Example: USR = 0.000 means no unsupported reasoning steps detected

- **`—` (Em Dash)**: The metric could not be computed or is not available
  - Example: Brier Score = — means no confidence scores were provided by the model
  - Example: CoT Tokens = — means chain-of-thought was not enabled

### Common Scenarios

#### Calibration Metrics (Brier, ECE)
- Show **`—`** when model doesn't provide confidence scores
- Show numeric values (including 0.000) when confidence is available

#### CoT Metrics (CoT Tokens, Step Count, Self-Correction Rate)
- Show **`—`** when use_cot=false or no CoT text generated
- Show numeric values (including 0) when CoT is enabled

#### Efficiency Metrics (Total Tokens, Latency)
- Show **`—`** when backend doesn't track token usage
- Show numeric values (including 0) when tracking is enabled

### Implementation Details

**Backend (Python):**
```python
# Returns None (null in JSON) when no data
def mean_or_none(values: List[Optional[float]]) -> Optional[float]:
    valid_values = [v for v in values if v is not None]
    if not valid_values:
        return None  # ← This becomes null in JSON
    return sum(valid_values) / len(valid_values)
```

**Frontend (TypeScript):**
```typescript
// Converts null/undefined to em dash
export function formatMetric(value: number | null | undefined, digits: number = 3): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '—';  // Em dash (U+2014)
  }
  return value.toFixed(digits);
}
```

### Visual Legend

The Zeta Reason UI displays a compact legend in Summary Mode:

```
0.000 = measured zero  •  — = no data
```

This appears between the metric cards and the metrics table for easy reference.

### For Screenshots and Papers

When including Zeta Reason results in papers or presentations:

1. **Caption should note the notation:**
   > "Note: `—` indicates metric not computed (e.g., no confidence scores); `0.000` indicates measured zero."

2. **Table footnotes:**
   > † Em dash (—) indicates insufficient data to compute metric.

3. **Figure labels:**
   > "Metrics showing `—` were not available for this model configuration."

### Examples from Real Usage

**Example 1: GPT-4 with CoT enabled**
```
Accuracy:     0.850
Brier Score:  —        (model doesn't provide confidence)
CoT Tokens:   1,234    (average across dataset)
```

**Example 2: Dummy model without CoT**
```
Accuracy:     0.000    (got 0% correct)
USR:          1.000    (all answers wrong)
CoT Tokens:   —        (CoT not enabled)
```

**Example 3: Perfect model**
```
Accuracy:     1.000    (100% correct)
USR:          0.000    (no unsupported steps)
Brier:        0.012    (well-calibrated)
```

---

## Technical Contract

The entire Zeta Reason system maintains this contract:

### Backend
- ✅ Uses `mean_or_none()` / `safe_mean()` for all aggregations
- ✅ Returns `None` (Python) when no data available
- ✅ Returns actual numeric values (including 0.0) when computed
- ✅ Proper `Optional[float]` types in Pydantic schemas

### Frontend
- ✅ Uses `formatMetric()` / `formatMetricInt()` for all displays
- ✅ Shows `—` (em dash) for null/undefined/NaN values
- ✅ Shows formatted numbers (including 0.000) for real values
- ✅ Consistent across metric cards, tables, and research mode

### JSON API
```json
{
  "metrics": {
    "accuracy": 0.85,
    "brier": null,
    "ece": null,
    "sce": 0.34,
    "usr": 0.12,
    "cot_tokens_mean": 1234.5,
    "total_tokens_mean": null,
    "latency_mean_ms": 2500.0
  }
}
```

---

## FAQ

**Q: Why use em dash (—) instead of "N/A"?**
A: The em dash is more concise and visually distinctive in tables. It's a standard notation in data visualization for missing values.

**Q: Could a real zero be mistaken for missing data?**
A: No. Real zeros always display with decimal places (e.g., `0.000` or `0`) while missing data shows the em dash symbol `—`.

**Q: What about integer metrics like token counts?**
A: Integer metrics show `0` (no decimal) when zero, or `—` when missing. Example: CoT Tokens = `0` vs `—`.

**Q: How do I export results with this notation?**
A: The "Download Results (JSON)" button exports raw JSON with `null` values preserved. Use your preferred tool to interpret nulls vs zeros.

---

*Last updated: 2025-01-20*
