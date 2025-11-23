/**
 * Main application component for Zeta Reason frontend
 * React Router-based architecture with sidebar navigation
 */

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { RunDetails } from './pages/RunDetails';
import { NewRun } from './pages/NewRun';
import { APIKeys } from './pages/APIKeys';
import { Compare } from './pages/Compare';

import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/run/:runId" element={<RunDetails />} />
            <Route path="/new" element={<NewRun />} />
            <Route path="/api-keys" element={<APIKeys />} />
            <Route path="/compare" element={<Compare />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
