import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getPredictions } from '../services/api';

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        const data = await getPredictions();
        setPredictions(data || []);
      } catch (err) {
        setError("Unable to load predictions. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchPredictions();
  }, []);

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100">{error}</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Predictions</h1>
        <p className="text-slate-500 mt-1">Review ML-generated potential withdrawal-risk intelligence</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-10 text-center text-slate-500">Loading predictions...</div>
        ) : predictions.length === 0 ? (
          <div className="p-10 text-center text-slate-500">No predictions available.</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                <th className="p-4 font-semibold">Case ID</th>
                <th className="p-4 font-semibold">Model Version</th>
                <th className="p-4 font-semibold">Top Potential Location</th>
                <th className="p-4 font-semibold">Overall Risk Level</th>
                <th className="p-4 font-semibold">Timestamp</th>
                <th className="p-4 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {predictions.map((p, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="p-4 font-medium text-slate-800">{p.case_id}</td>
                  <td className="p-4 text-slate-600">{p.model_version}</td>
                  <td className="p-4 text-slate-600">
                    {p.locations && p.locations.length > 0 ? (
                      <div>
                        <span className="font-semibold">{p.locations[0].location_name}</span>
                        <br />
                        <span className="text-xs text-slate-500">Score: {p.locations[0].risk_score.toFixed(4)}</span>
                      </div>
                    ) : 'N/A'}
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      p.overall_risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                      p.overall_risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      p.overall_risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {p.overall_risk_level}
                    </span>
                  </td>
                  <td className="p-4 text-slate-500">{new Date(p.prediction_timestamp).toLocaleString()}</td>
                  <td className="p-4">
                    <Link to={`/cases/${p.case_id}`} className="text-blue-600 hover:underline font-medium">View Case</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Predictions;
