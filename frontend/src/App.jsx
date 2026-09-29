import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RiskMapPage from './pages/RiskMap';
import AlertsPage from './pages/Alerts';
import DashboardPage from './pages/Dashboard';
import CasesPage from './pages/Cases';
import CaseDetailsPage from './pages/CaseDetails';
import PredictionsPage from './pages/Predictions';
import InvestigationPage from './pages/Investigation';

const PlaceholderPage = ({ title }) => (
  <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-100">
    <h2 className="text-xl font-semibold text-slate-800 mb-4">{title}</h2>
    <p className="text-slate-600">This page is currently a placeholder and will be implemented in future steps.</p>
  </div>
);

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50 font-sans text-slate-900 flex flex-col">
        <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-cyan-600 tracking-tight">CASH TRAIL</h1>
              <p className="text-xs text-slate-500 hidden sm:block">Predictive Cybercrime Intelligence Platform</p>
            </div>
            <nav className="hidden md:flex space-x-8">
              <Link to="/" className="text-slate-600 hover:text-cyan-600 font-medium text-sm transition-colors">Dashboard</Link>
              <Link to="/cases" className="text-slate-600 hover:text-cyan-600 font-medium text-sm transition-colors">Cases</Link>
              <Link to="/predictions" className="text-slate-600 hover:text-cyan-600 font-medium text-sm transition-colors">Predictions</Link>
              <Link to="/risk-map" className="text-slate-600 hover:text-cyan-600 font-medium text-sm transition-colors">Risk Map</Link>
              <Link to="/alerts" className="text-slate-600 hover:text-cyan-600 font-medium text-sm transition-colors">Alerts</Link>
              <Link to="/investigation" className="text-slate-600 hover:text-cyan-600 font-medium text-sm transition-colors">Investigation</Link>
            </nav>
          </div>
        </header>

        <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/cases/:caseId" element={<CaseDetailsPage />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/risk-map" element={<RiskMapPage />} />
            <Route path="/alerts" element={<AlertsPage />} />
            <Route path="/investigation" element={<InvestigationPage />} />
          </Routes>
        </main>
        
        <footer className="bg-slate-800 text-slate-400 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm">
            <p>CashTrail - Predictive Cybercrime Intelligence Platform Prototype</p>
            <p className="mt-2 text-slate-500">For demonstration purposes only.</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
