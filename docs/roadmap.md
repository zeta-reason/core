# Zeta Reason Roadmap

This document outlines the planned features and enhancements for Zeta Reason across upcoming versions.

## Table of Contents

- [Version History](#version-history)
- [v1.0.0 (Current)](#v100-current)
- [v1.1.0 (Q1 2026)](#v110-q1-2026)
- [v1.2.0 (Q3 2026)](#v120-q3-2026)
- [v2.0.0 (Q1 2027)](#v200-q1-2027)
- [Future Considerations](#future-considerations)
- [Community Requests](#community-requests)

## Version History

| Version | Release Date | Status | Highlights |
|---------|--------------|--------|------------|
| v1.0.0 | Nov 2025 | **Current** | Core evaluation, experiment history, dark mode |
| v1.1.0 | Q1 2026 | Planned | Anthropic support, advanced filtering, LaTeX export |
| v1.2.0 | Q3 2026 | Planned | Database migration, Docker, performance optimizations |
| v2.0.0 | Q1 2027 | Future | Multi-turn eval, auto-tuning, collaboration features |

---

## v1.0.0 (Current)

**Release Date:** November 2025
**Status:** ✅ Released

### Features Delivered

#### Core Evaluation Pipeline
- ✅ Single model evaluation
- ✅ Multi-model comparison (up to 10 models)
- ✅ Async evaluation for performance
- ✅ Comprehensive error handling
- ✅ Progress tracking

#### Metrics Engine
- ✅ Accuracy (exact match)
- ✅ Brier Score (calibration)
- ✅ Expected Calibration Error (ECE)
- ✅ Self-Consistency Entropy (v0 - placeholder)
- ✅ Unsupported Step Rate (heuristic-based)
- ✅ CoT tokens, step count, latency

#### Model Providers
- ✅ OpenAI (GPT-4, GPT-3.5-turbo, etc.)
- ✅ DeepSeek (Chat, Reasoner)
- ✅ Qwen (Alibaba)
- ✅ GLM (ZhipuAI)
- ✅ Grok (xAI)
- ✅ Cohere
- ✅ Google Gemini
- ✅ Dummy provider (testing)

#### User Interface
- ✅ Dataset upload (JSONL)
- ✅ Model configuration interface
- ✅ Model presets (save/load)
- ✅ Flexible sampling (all tasks or random)
- ✅ Summary Mode (overview)
- ✅ Research Mode (per-task analysis)
- ✅ Metric cards with insights
- ✅ Interactive charts
- ✅ CoT viewer
- ✅ Export results (JSON)
- ✅ Dark mode theme
- ✅ Responsive design

#### Experiment History
- ✅ Auto-save experiments
- ✅ Experiment browsing sidebar
- ✅ Load past results
- ✅ Delete experiments
- ✅ Storage statistics

#### Developer Experience
- ✅ FastAPI backend with OpenAPI docs
- ✅ React 19 + TypeScript frontend
- ✅ Comprehensive type safety
- ✅ Error handling and validation
- ✅ Development tooling (Ruff, ESLint)

---

## v1.1.0 (Q1 2027)

**Target Release:** March 2027
**Theme:** Provider Expansion & Enhanced Analysis

### Planned Features

#### 1. Advanced Filtering in Research Mode
**Priority:** High
**Effort:** Small

Add powerful filtering capabilities:

**Filters:**
- ✅ Correctness (correct/incorrect)
- 🔄 Confidence range (e.g., only show confidence < 0.5)
- 🔄 Token count range
- 🔄 Step count range
- 🔄 Latency range
- 🔄 Text search in input/output
- 🔄 Model comparison (show only differences)

**UI:**
```typescript
interface FilterState {
  correctness: 'all' | 'correct' | 'incorrect';
  confidenceMin: number;
  confidenceMax: number;
  tokenCountMin: number;
  tokenCountMax: number;
  searchQuery: string;
  showOnlyDifferences: boolean;  // For multi-model
}
```

**Tasks:**
- [ ] Implement filter state management
- [ ] Add filter UI components
- [ ] Apply filters to task list
- [ ] Add filter presets ("High Confidence Errors", etc.)
- [ ] Persist filter state

#### 2. LaTeX Export
**Priority:** Medium
**Effort:** Small

Export results as LaTeX tables for papers:

```typescript
function exportToLatex(results: EvaluationResult[]): string {
  return `
\\begin{table}[h]
\\centering
\\begin{tabular}{lcccc}
\\toprule
Model & Accuracy & Brier & ECE & USR \\\\
\\midrule
${results.map(r => `
${r.model_configuration.model_id} &
${r.metrics.accuracy.toFixed(3)} &
${r.metrics.brier_score.toFixed(3)} &
${r.metrics.ece.toFixed(3)} &
${r.metrics.usr.toFixed(3)} \\\\
`).join('')}
\\bottomrule
\\end{tabular}
\\caption{Model Comparison Results}
\\label{tab:results}
\\end{table}
  `;
}
```

**Tasks:**
- [ ] Implement LaTeX export function
- [ ] Add export button to UI
- [ ] Support multiple table formats
- [ ] Add customization options (caption, label, etc.)

#### 3. CSV Export Enhancement
**Priority:** Low
**Effort:** Small

Improve CSV export with more options:

**Features:**
- Task-level CSV (one row per task)
- Aggregated CSV (one row per model)
- Custom column selection
- Include metadata

**Tasks:**
- [ ] Implement flexible CSV export
- [ ] Add export configuration modal
- [ ] Support both task-level and summary exports

#### 4. Custom Metric Plugins
**Priority:** Medium
**Effort:** Large

Allow users to define custom metrics:

```python
# User-defined metric
from zeta_reason.metrics import MetricPlugin

class CustomF1Score(MetricPlugin):
    """Custom F1 score implementation."""

    def compute(
        self,
        tasks: List[Task],
        outputs: List[ModelOutput]
    ) -> float:
        # Custom implementation
        precision = self._compute_precision(tasks, outputs)
        recall = self._compute_recall(tasks, outputs)
        return 2 * (precision * recall) / (precision + recall)

# Register plugin
register_metric("custom_f1", CustomF1Score())
```

**Tasks:**
- [ ] Design plugin API
- [ ] Implement plugin loading system
- [ ] Add plugin configuration UI
- [ ] Create plugin examples
- [ ] Document plugin development

---

## v1.2.0 (Q2 2027)

**Target Release:** June 2027
**Theme:** Performance & Deployment

### Planned Features

#### 1. Database Migration
**Priority:** High
**Effort:** Large

Migrate from file-based storage to PostgreSQL:

**Benefits:**
- Faster queries for large experiment sets
- ACID guarantees
- Advanced search capabilities
- Better concurrent access

**Tasks:**
- [ ] Design database schema
- [ ] Implement PostgreSQL backend
- [ ] Create migration scripts
- [ ] Add database configuration
- [ ] Maintain file-based option for small setups

#### 2. Docker Containerization
**Priority:** High
**Effort:** Medium

Provide Docker setup for easy deployment:

```dockerfile
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  database:
    image: postgres:15
    environment:
      - POSTGRES_DB=zeta_reason
```

**Tasks:**
- [ ] Create Dockerfiles
- [ ] Create docker-compose.yml
- [ ] Add deployment documentation
- [ ] Test on cloud platforms (AWS, GCP, Azure)

#### 3. Batch Processing
**Priority:** Medium
**Effort:** Medium

Process multiple datasets in batch:

**Features:**
- Queue multiple evaluations
- Background processing
- Email/webhook notifications on completion
- Pause/resume support

**Tasks:**
- [ ] Implement job queue (Celery or similar)
- [ ] Add batch API endpoints
- [ ] Create batch management UI
- [ ] Add notification system

#### 4. Cost Tracking
**Priority:** Medium
**Effort:** Small

Track API costs per evaluation:

```python
class CostTracker:
    """Track API costs."""

    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
    }

    def compute_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        pricing = self.PRICING[model]
        return (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )
```

**UI Features:**
- Cost per evaluation
- Budget alerts
- Cost breakdown by model
- Historical cost tracking

**Tasks:**
- [ ] Implement cost tracking
- [ ] Add cost display in UI
- [ ] Add budget warnings
- [ ] Track costs in experiment metadata

#### 5. Performance Optimizations
**Priority:** Medium
**Effort:** Medium

Improve performance for large evaluations:

**Optimizations:**
- Request batching (send multiple tasks in one API call)
- Result streaming (show results as they come in)
- Parallel evaluation (multiple concurrent requests)
- Caching (avoid re-evaluating identical inputs)

**Tasks:**
- [ ] Implement request batching
- [ ] Add WebSocket for real-time updates
- [ ] Optimize metrics computation
- [ ] Add result caching layer

---

## v2.0.0 (Q3 2027)

**Target Release:** September 2027
**Theme:** Advanced Features & Collaboration

### Planned Features

#### 1. Multi-Turn Dialogue Evaluation
**Priority:** High
**Effort:** Large

Support for conversational evaluation:

```json
{
  "id": "dialogue_001",
  "turns": [
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "I can't check weather."},
    {"role": "user", "content": "Then what can you do?"}
  ],
  "expected_response": "I can help with questions, math, etc."
}
```

**Features:**
- Multi-turn task format
- Context preservation
- Turn-level evaluation
- Dialogue coherence metrics

**Tasks:**
- [ ] Design multi-turn schema
- [ ] Implement dialogue evaluation
- [ ] Add turn-level metrics
- [ ] Create dialogue viewer UI

#### 2. Automated Hyperparameter Tuning
**Priority:** Medium
**Effort:** Large

Automatically find optimal model settings:

```python
class HyperparameterTuner:
    """Auto-tune model parameters."""

    def tune(
        self,
        model: str,
        dataset: List[Task],
        param_grid: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """
        Search parameter space for optimal config.

        Tries combinations of:
        - temperature: [0.0, 0.3, 0.7, 1.0]
        - max_tokens: [500, 1000, 2000]
        - use_cot: [True, False]
        """
        # Grid search or Bayesian optimization
        pass
```

**Tasks:**
- [ ] Implement grid search
- [ ] Add Bayesian optimization
- [ ] Create tuning UI
- [ ] Add tuning result visualization

#### 3. Collaborative Features
**Priority:** Medium
**Effort:** Large

Enable team collaboration:

**Features:**
- User accounts and authentication
- Shared experiments
- Comments and annotations
- Team workspaces
- Access control

**Tasks:**
- [ ] Add authentication system
- [ ] Implement user management
- [ ] Add experiment sharing
- [ ] Create collaboration UI

#### 4. Public Leaderboards
**Priority:** Medium
**Effort:** Large

Host public benchmarks with leaderboards:

**Features:**
- Submit results to public leaderboards
- Compare with community results
- Verified submissions
- Multiple benchmark categories

**Tasks:**
- [ ] Design leaderboard system
- [ ] Implement submission verification
- [ ] Create leaderboard UI
- [ ] Add ranking algorithms

#### 5. Advanced Reasoning Metrics
**Priority:** High
**Effort:** Large

Implement sophisticated reasoning evaluation:

**Metrics:**
- **Multi-Shot SCE**: True self-consistency with sampling
- **LLM-as-Judge USR**: Use GPT-4 to evaluate reasoning steps
- **Reasoning Graph Analysis**: Analyze step dependencies
- **Counterfactual Reasoning**: Test robustness to input changes

**Tasks:**
- [ ] Implement multi-shot sampling
- [ ] Add LLM-based step evaluation
- [ ] Create reasoning graph analyzer
- [ ] Design counterfactual tests

---

## Future Considerations

### Beyond v2.0

These features are under consideration but not yet scheduled:

#### 1. Active Learning Integration
Automatically identify informative examples for annotation.

#### 2. Model Distillation Support
Evaluate student models trained on teacher outputs.

#### 3. Adversarial Testing
Generate adversarial examples to test robustness.

#### 4. Multi-Language Support
Evaluate models in languages beyond English.

#### 5. Vision-Language Evaluation
Support for models like GPT-4V, Claude 3 with images.

#### 6. Real-Time Benchmarking
Continuous evaluation as models are updated.

#### 7. API Rate Limit Management
Intelligent request scheduling to avoid rate limits.

#### 8. Custom Prompt Templates
Save and reuse prompt templates across evaluations.

#### 9. Result Comparison Across Versions
Compare model performance across different versions.

#### 10. Integration with MLOps Tools
Connect with Weights & Biases, MLflow, etc.

---

## Community Requests

We track community feature requests in GitHub Issues. Vote on features you'd like to see!

### Top Requested Features (as of Nov 2026)

1.  **Anthropic Claude Support** - Scheduled for v1.1.0
2.  **Docker Setup** - Scheduled for v1.2.0
3.  **Cost Tracking** - Scheduled for v1.2.0
4.  **Multi-Turn Evaluation** - Scheduled for v2.0.0
5.  **Cohere Support** - Under consideration

### How to Request Features

1. Check existing GitHub Issues
2. If not found, create new issue with:
   - Clear description
   - Use case explanation
   - Priority level (nice-to-have vs. critical)
3. Community votes help us prioritize

---

## Development Principles

### Our Commitments

1. **Backward Compatibility**: We maintain API compatibility within major versions
2. **Data Safety**: Experiment data remains accessible across upgrades
3. **Documentation**: All features are documented before release
4. **Testing**: Comprehensive tests for all new features
5. **Community**: We listen to user feedback and adapt

### Release Cycle

- **Major versions** (v2.0, v3.0): Every 6-9 months
- **Minor versions** (v1.1, v1.2): Every 2-3 months
- **Patch versions** (v1.0.1): As needed for bug fixes

### Beta Testing

We offer beta access to upcoming features:
- Join our Discord for beta announcements
- Test features before general release
- Provide feedback to shape final design

---

## Contributing

Want to help build these features?

1. Check the roadmap for upcoming features
2. Look for "good first issue" tags
3. Discuss approach in GitHub Discussions
4. Submit a PR

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## Stay Updated

- **GitHub**: Star the repo for release notifications
- **Discord**: Join for community discussions
- **Blog**: Read release notes and feature deep-dives
- **Twitter**: Follow for announcements

---

**Last Updated:** November 2026
**Version:** 1.0.0

*This roadmap is a living document and may change based on user feedback and priorities.*
