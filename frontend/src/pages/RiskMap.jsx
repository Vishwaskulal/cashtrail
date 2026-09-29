import React, { useState, useEffect } from 'react';
import { getCasePrediction } from '../services/api';
import RiskMapComponent from '../components/RiskMap';

const RiskMap = () => {
  const [caseId, setCaseId] = useState('CASE_00001'); // default test case
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeFilter, setActiveFilter] = useState('ALL');

  const fetchPrediction = async (id) => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getCasePrediction(id);
      setPredictionData(data);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.status === 404) {
        setError('No prediction found for this Case ID.');
      } else {
        setError('Failed to fetch prediction data. Check if backend is running.');
      }
      setPredictionData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction(caseId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchPrediction(caseId);
  };

  const filteredLocations = predictionData?.locations?.filter(loc => 
    activeFilter === 'ALL' || loc.risk_level === activeFilter
  ) || [];

  return (
    <div className="p-6 max-w-7xl mx-auto font-sans">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Geographic Intelligence</h1>
          <p className="text-gray-500 mt-1">Predictive analysis of potential withdrawal locations</p>
        </div>
        
        <form onSubmit={handleSearch} className="mt-4 md:mt-0 flex gap-2">
          <input 
            type="text" 
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
            placeholder="Enter Case ID (e.g. CASE_00001)"
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none shadow-sm"
          />
          <button 
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            {loading ? 'Searching...' : 'Analyze'}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded shadow-sm">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {predictionData && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-3">
            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
              <div className="flex gap-2 mb-4">
                {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(level => (
                  <button 
                    key={level}
                    onClick={() => setActiveFilter(level)}
                    className={`px-3 py-1 text-xs font-medium rounded-full ${activeFilter === level ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
                  >
                    {level}
                  </button>
                ))}
              </div>
              
              <RiskMapComponent 
                locations={filteredLocations} 
                modelVersion={predictionData.model_version}
              />
              
              <div className="mt-4 flex flex-wrap gap-4 items-center justify-between text-sm">
                <div className="flex gap-4">
                  <div className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full bg-blue-500"></span> LOW
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full bg-amber-500"></span> MEDIUM
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full bg-red-500"></span> HIGH
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-3 h-3 rounded-full bg-red-900"></span> CRITICAL
                  </div>
                </div>
                <div className="text-gray-500 italic">
                  *Risk score represents model-estimated relative risk among candidate locations.
                </div>
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 h-full">
              <h2 className="text-lg font-bold text-gray-800 mb-4 border-b pb-2">Top Potential Risk Locations</h2>
              
              <div className="space-y-4">
                {filteredLocations.length > 0 ? (
                  filteredLocations.slice(0, 5).map((loc, index) => (
                    <div key={loc.location_id} className="p-3 bg-gray-50 rounded-lg border border-gray-100 relative">
                      <div className="absolute top-3 right-3 text-xs font-bold px-2 py-1 rounded bg-white shadow-sm"
                           style={{ color: loc.risk_level === 'CRITICAL' ? '#7f1d1d' : loc.risk_level === 'HIGH' ? '#ef4444' : loc.risk_level === 'MEDIUM' ? '#f59e0b' : '#3b82f6' }}>
                        {loc.risk_level}
                      </div>
                      <div className="font-semibold text-gray-800 pr-16">{index + 1}. {loc.location_name}</div>
                      <div className="text-xs text-gray-500 mt-1">{loc.city}, {loc.district}</div>
                      <div className="mt-2 text-sm text-gray-700">
                        Risk Score: <strong>{loc.risk_score.toFixed(4)}</strong>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500">No locations match the active filter.</p>
                )}
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-100">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Analysis Metadata</h3>
                <div className="text-xs text-gray-600 space-y-1">
                  <p><strong>Case:</strong> {predictionData.case_id}</p>
                  <p><strong>Overall Risk:</strong> {predictionData.overall_risk_level}</p>
                  <p><strong>Model Version:</strong> {predictionData.model_version}</p>
                  <p><strong>Analyzed At:</strong> {new Date(predictionData.prediction_timestamp).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskMap;
