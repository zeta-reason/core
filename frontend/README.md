# Zeta Reason Frontend

React + TypeScript frontend for Zeta Reason v0.1 - Chain-of-thought reasoning benchmarking for LLMs.

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The app will be available at [http://localhost:5173](http://localhost:5173)

### 3. Ensure Backend is Running

The frontend expects the backend API to be running at `http://localhost:8000`.

Start the backend:

```bash
cd ../backend
source venv/bin/activate
uvicorn zeta_reason.main:app --reload
```

## Usage

1. **Upload Dataset**: Upload a JSONL file with tasks (each line: `{"id": "...", "input": "...", "target": "..."}`)

2. **Configure Models**: Select provider (OpenAI/Dummy), model ID, temperature, max tokens, and CoT settings

3. **Run Benchmark**: Click "Run Evaluation" (1 model) or "Compare N Models" (multiple models)

4. **View Results**:
   - Metrics table shows all metrics for each model
   - CoT Viewer lets you inspect individual task results and reasoning

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main application
│   ├── App.css               # Styles
│   ├── api/
│   │   └── client.ts         # Backend API client
│   ├── components/
│   │   ├── DatasetUpload.tsx # File upload component
│   │   ├── ModelSelector.tsx # Model configuration
│   │   ├── MetricsTable.tsx  # Results display
│   │   └── CotViewer.tsx     # CoT viewer
│   └── types/
│       └── api.ts            # TypeScript types
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Configuration

### Backend API URL

By default, the frontend connects to `http://localhost:8000`. To change this, set the `VITE_API_BASE_URL` environment variable:

```bash
# Create .env.local
echo "VITE_API_BASE_URL=http://your-backend-url:8000" > .env.local
```

## Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

## Development

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## Features

- **Dataset Upload**: Parse and validate JSONL files
- **Model Configuration**: Support for multiple models with individual settings
- **Real-time Evaluation**: Stream results from backend
- **Metrics Display**: Tabular view of all metrics
- **CoT Inspection**: Detailed view of reasoning for each task
- **Error Handling**: Clear error messages for API failures

## Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Native fetch** - HTTP client (no external dependencies)
