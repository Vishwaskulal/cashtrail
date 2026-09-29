import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getCases } from '../services/api';

const Cases = () => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const data = await getCases();
        setCases(data.cases || []);
      } catch (err) {
        setError("Unable to load cases. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchCases();
  }, []);

  const filteredCases = cases.filter(c => {
    const matchesSearch = c.case_number.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          c.crime_category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    const matchesRisk = riskFilter === 'ALL' || c.risk_level === riskFilter;
    return matchesSearch && matchesStatus && matchesRisk;
  });

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100">{error}</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen">
      <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Cases</h1>
          <p className="text-slate-500 mt-1">Manage cybercrime investigations and intelligence</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 mb-6 flex gap-4 flex-wrap">
        <div className="flex-grow md:max-w-md">
          <label className="block text-xs font-medium text-slate-500 mb-1">Search</label>
          <input 
            type="text"
            placeholder="Search by ID or Category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full border-slate-300 rounded text-sm focus:ring-blue-500 p-2 border"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Status Filter</label>
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border-slate-300 rounded text-sm focus:ring-blue-500 p-2 border"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="UNDER_ANALYSIS">Under Analysis</option>
            <option value="CLOSED">Closed</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-500 mb-1">Risk Filter</label>
          <select 
            value={riskFilter} 
            onChange={(e) => setRiskFilter(e.target.value)}
            className="border-slate-300 rounded text-sm focus:ring-blue-500 p-2 border"
          >
            <option value="ALL">All Risks</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
            <option value="UNKNOWN">Unknown</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-10 text-center text-slate-500">Loading cases...</div>
        ) : filteredCases.length === 0 ? (
          <div className="p-10 text-center text-slate-500">No cases match your criteria.</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                <th className="p-4 font-semibold">Case ID</th>
                <th className="p-4 font-semibold">Date</th>
                <th className="p-4 font-semibold">Category</th>
                <th className="p-4 font-semibold">Amount</th>
                <th className="p-4 font-semibold">Status</th>
                <th className="p-4 font-semibold">Risk Level</th>
                <th className="p-4 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {filteredCases.map(c => (
                <tr key={c.case_number} className="hover:bg-slate-50">
                  <td className="p-4 font-medium text-slate-800">{c.case_number}</td>
                  <td className="p-4 text-slate-600">{new Date(c.complaint_date).toLocaleDateString()}</td>
                  <td className="p-4 text-slate-600">{c.crime_category}</td>
                  <td className="p-4 text-slate-600">${c.total_amount.toLocaleString()}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 rounded text-xs font-bold bg-slate-100 text-slate-700">{c.status}</span>
                  </td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      c.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                      c.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                      c.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      c.risk_level === 'LOW' ? 'bg-green-100 text-green-800' :
                      'bg-slate-100 text-slate-500'
                    }`}>
                      {c.risk_level}
                    </span>
                  </td>
                  <td className="p-4">
                    <Link to={`/cases/${c.case_number}`} className="text-blue-600 hover:underline font-medium">Details</Link>
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

export default Cases;
