import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getCases } from '../services/api';

const Investigation = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const data = await getCases();
        // Filter for cases that likely need investigation (HIGH/CRITICAL risk or NEW status)
        const relevantCases = (data.cases || []).filter(c => 
          c.risk_level === 'HIGH' || c.risk_level === 'CRITICAL' || c.status === 'NEW'
        );
        setCases(relevantCases);
      } catch (err) {
        setError("Unable to load investigation cases.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchCases();
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
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Investigation Workflow</h1>
        <p className="text-slate-500 mt-1">Review prioritized cases and manage notes</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800 mb-4 border-b pb-2">Prioritized Cases for Review</h2>
        
        {loading ? (
          <p className="text-slate-500">Loading cases...</p>
        ) : cases.length === 0 ? (
          <p className="text-slate-500 text-center py-8">No high-priority cases require investigation at this time.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cases.map(c => (
              <div key={c.case_number} className="bg-slate-50 rounded-xl border border-slate-200 p-5 hover:shadow-md transition">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-bold text-lg text-slate-800">{c.case_number}</h3>
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                      c.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                      c.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {c.risk_level === 'UNKNOWN' ? 'NEW' : c.risk_level}
                  </span>
                </div>
                <p className="text-sm text-slate-600 mb-2"><strong>Category:</strong> {c.crime_category}</p>
                <p className="text-sm text-slate-600 mb-4"><strong>Date:</strong> {new Date(c.complaint_date).toLocaleDateString()}</p>
                <div className="flex gap-2">
                  <Link to={`/cases/${c.case_number}`} className="flex-1 text-center py-2 bg-slate-800 text-white text-sm font-medium rounded hover:bg-slate-700 transition">
                    Investigate & Add Note
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Investigation;
