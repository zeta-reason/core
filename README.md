# Zeta Reason

> Chain-of-Thought Reasoning Benchmarking for Large Language Models

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/zeta-reason/core)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Zeta Reason is an experimental LLM evaluation application with a FastAPI backend and React/TypeScript frontend. It supports dataset-driven model comparison, experiment history, and inspection of model outputs and model-generated explanation text.

![Zeta Reason Interface](docs/screenshots/main-interface.png)

## Metric boundaries

This is evaluation infrastructure under development. Interpret the current metrics carefully:

- **Accuracy:** normalized exact answer matching.
- **USR v0:** an answer-correctness proxy, not validation of unsupported reasoning steps.
- **SCE v0:** entropy of answers across dataset questions, not repeated-prompt self-consistency.
- **Brier / ECE:** require confidence values; unavailable when providers return no confidence.
- **Reasoning length, steps, self-correction:** whitespace counts and text-pattern heuristics, not validated reasoning-quality measures.

Model-generated explanation text does not establish internal reasoning or faithfulness. Provider integration code is not a guarantee of live API compatibility. The dummy provider supports local evaluation without paid API calls.

## ✨ Features

### Core Capabilities
- **Multi-Model Comparison** - Evaluate and compare multiple LLMs side-by-side
- **Output Inspection** - Inspect model-generated explanation text
- **Experimental Metrics** - Accuracy, optional calibration, and explicitly limited text heuristics
- **Flexible Sampling** - Full dataset or random sampling for faster iteration
- **Experiment History** - Auto-save and revisit past evaluations
- **Dark Mode** - Comfortable viewing in any environment

### Evaluation Modes
- **Summary Mode** - High-level overview with metric cards and comparison charts
- **Research Mode** - Detailed per-task analysis for deep investigation

### Model Support
- **OpenAI** - GPT-4, GPT-3.5-turbo, and other models ✅
- **DeepSeek** - Chat, Reasoner ✅
- **Qwen** - Plus, Max, Turbo ✅
- **GLM** - GLM-4, GLM-4-Plus ✅
- **Grok (xAI)** - Integration code exists; live compatibility is unverified
- **Dummy Provider** - Fast testing with synthetic responses ✅
- **Not yet implemented (will return errors until shipped)**: Anthropic (Claude), Google (Gemini), Cohere (Command)
- **Extensible** - Easy to add new providers

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js compatible with Vite 7 (20.19+ or 22.12+)
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/zeta-reason/core.git
cd core
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

3. **Configure API Keys**
```bash
# Create .env file in backend/
# Create backend/.env manually; no template is currently included.
# Add your API keys:
# OPENAI_API_KEY=your_key_here
```

4. **Frontend Setup**
```bash
cd ../frontend
npm install
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m zeta_reason.main
# Server starts at http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# App starts at http://localhost:5173
```

Visit `http://localhost:5173` in your browser.

## 📖 Usage

### Basic Workflow

1. **Upload Dataset**
   - Prepare a JSONL file with your tasks
   - Each line: `{"id": "1", "input": "Question?", "target": "Answer"}`
   - Upload via the web interface

2. **Configure Models**
   - Select provider (OpenAI, Dummy)
   - Choose model (gpt-4, gpt-3.5-turbo, etc.)
   - Set temperature, max tokens, CoT mode
   - Add multiple models for comparison

3. **Run Evaluation**
   - Click "Run Evaluation" or "Compare N Models"
   - Wait for completion (progress shown)
   - Results appear automatically

4. **Analyze Results**
   - **Summary Mode**: Overview metrics, charts, CoT viewer
   - **Research Mode**: Per-task deep dive, error analysis
   - Download results as JSON or CSV

5. **Review History**
   - Click "History ►" to open saved experiments
   - Load previous results
   - Compare across time

### Example Dataset

```jsonl
{"id": "1", "input": "What is 15 * 23?", "target": "345"}
{"id": "2", "input": "If x + 5 = 12, what is x?", "target": "7"}
{"id": "3", "input": "What is the capital of France?", "target": "Paris"}
```

See [Dataset Format Guide](docs/dataset_format.md) for complete specification.

## 📊 Metrics

The following labels appear in the application; the descriptions below reflect current implementation limits:

| Metric | Description | Range |
|--------|-------------|-------|
| **Accuracy (ACC)** | Exact match rate | 0-100% |
| **Brier Score** | Calibration quality (lower is better) | 0-1 |
| **ECE** | Expected Calibration Error | 0-1 |
| **SCE** | Answer entropy across dataset questions (v0) | 0-∞ |
| **USR** | Incorrect-answer proxy, not step verification | 0-100% |
| **CoT Tokens** | Whitespace-based reasoning length estimate | 0-∞ |
| **Step Count** | Numbered/bulleted-line heuristic | 0-∞ |
| **Latency** | Average response time | 0-∞ ms |

See [Metrics Specification](docs/metrics_spec.md) for detailed formulas and interpretations.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Summary Mode │  │ Research Mode│  │  Exp History │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Evaluator   │  │ Metrics Eng. │  │   Storage    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              Model Runners (OpenAI, Dummy, ...)             │
└─────────────────────────────────────────────────────────────┘
```

See [Architecture Documentation](docs/architecture.md) for details.

## 🔬 Research Mode

Research Mode provides granular, per-task analysis for deep investigation:

- **Task-by-Task Breakdown** - Individual inputs, outputs, and reasoning
- **Error Analysis** - Filter by correctness, examine failure patterns
- **Chain-of-Thought Inspection** - Full reasoning traces
- **Confidence Visualization** - Per-task confidence levels
- **Comparative View** - Side-by-side model comparison

See [Research Mode Guide](docs/research_mode.md) for usage.

## 🗺️ Roadmap

### Current experimental implementation
- ✅ Core evaluation pipeline
- ✅ OpenAI provider
- ✅ Multi-model comparison
- ✅ Summary & Research modes
- ✅ Experiment history
- ✅ Dark mode

### v1.1 (Planned)
- 🔄 Anthropic (Claude) support
- 🔄 Advanced filtering in Research Mode
- 🔄 Export to LaTeX tables
- 🔄 Custom metric plugins

### v2.0 (Future)
- 📋 Multi-turn dialogue evaluation
- 📋 Automated hyperparameter tuning
- 📋 Collaborative features
- 📋 Public benchmark leaderboards

See [Full Roadmap](docs/roadmap.md) for details.

## 🛠️ Development

### Project Structure

```
zeta-reason/
├── backend/
│   ├── zeta_reason/
│   │   ├── main.py              # FastAPI app
│   │   ├── evaluator.py         # Evaluation engine
│   │   ├── metrics.py           # Metrics computation
│   │   ├── models/              # Model runners
│   │   ├── storage/             # Experiment storage
│   │   └── schemas.py           # Pydantic models
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── api/                 # API clients
│   │   ├── types/               # TypeScript types
│   │   └── contexts/            # React contexts
│   ├── package.json
│   └── vite.config.ts
└── docs/
```

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend build check (there is no frontend test script):**
```bash
cd frontend
npm run build
```

### Code Quality

**Backend:**
```bash
ruff check .
mypy zeta_reason/
```

**Frontend:**
```bash
npm run lint
npm run type-check
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by research in chain-of-thought reasoning and LLM evaluation
- Built with FastAPI, React, and modern web technologies
- Community feedback and contributions

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/zeta-reason/core/issues)
- **Discussions**: [GitHub Discussions](https://github.com/zeta-reason/core/discussions)
- **Email**: a4santho@uwaterloo.ca

---

**Built with ❤️ in Waterloo/Toronto for LLM researchers and developers**
