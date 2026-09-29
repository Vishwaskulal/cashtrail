import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      let url = '/api/alerts?';
      if (statusFilter !== 'ALL') url += `status=${statusFilter}&`;
      if (riskFilter !== 'ALL') url += `risk_level=${riskFilter}`;
      
      const response = await api.get(url);
      setAlerts(response.data.alerts || []);
    } catch (err) {
      console.error(err);
      setError('Failed to load alerts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, riskFilter]);

  const handleStatusUpdate = async (alertId, action) => {
    try {
      await api.patch(`/api/alerts/${alertId}/${action}`, { user_id: 1 });
      fetchAlerts(); // Refresh the list
    } catch (err) {
      alert('Failed to update alert status. It may no longer be in the required state.');
    }
  };

  // Stats
  const activeCount = alerts.filter(a => a.status === 'ACTIVE').length;
  const acknowledgedCount = alerts.filter(a => a.status === 'ACKNOWLEDGED').length;
  const resolvedCount = alerts.filter(a => a.status === 'RESOLVED').length;

  return (
    <div className="p-6 max-w-7xl mx-auto font-sans">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Intelligence Alerts</h1>
          <p className="text-gray-500 mt-1">Review model-generated potential risk locations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-red-50 p-4 rounded-xl border border-red-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-red-600 font-medium">Active Alerts</p>
            <p className="text-2xl font-bold text-red-800">{activeCount}</p>
          </div>
        </div>
        <div className="bg-amber-50 p-4 rounded-xl border border-amber-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-amber-600 font-medium">Acknowledged</p>
            <p className="text-2xl font-bold text-amber-800">{acknowledgedCount}</p>
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded-xl border border-green-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-green-600 font-medium">Resolved</p>
            <p className="text-2xl font-bold text-green-800">{resolvedCount}</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-6 flex gap-4 flex-wrap">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Status Filter</label>
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="border-gray-300 rounded text-sm focus:ring-blue-500 p-2 border"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="RESOLVED">Resolved</option>
            <option value="DISMISSED">Dismissed</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">Risk Filter</label>
          <select 
            value={riskFilter} 
            onChange={(e) => setRiskFilter(e.target.value)}
            className="border-gray-300 rounded text-sm focus:ring-blue-500 p-2 border"
          >
            <option value="ALL">All Risks</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {error && <div className="text-red-500 mb-4">{error}</div>}

      <div className="space-y-4">
        {loading ? (
          <p className="text-gray-500">Loading alerts...</p>
        ) : alerts.length > 0 ? (
          alerts.map(alert => (
            <div key={alert.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 relative">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                    🚨 Potential Withdrawal-Risk Alert
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">Created: {new Date(alert.created_at).toLocaleString()}</p>
                </div>
                <div className={`px-3 py-1 rounded text-xs font-bold ${
                  alert.status === 'ACTIVE' ? 'bg-red-100 text-red-800' : 
                  alert.status === 'ACKNOWLEDGED' ? 'bg-amber-100 text-amber-800' :
                  alert.status === 'RESOLVED' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {alert.status}
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-50 p-3 rounded border border-gray-100">
                  <p className="text-xs text-gray-500 uppercase">Case</p>
                  <p className="font-semibold text-gray-800">{alert.case_number}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded border border-gray-100">
                  <p className="text-xs text-gray-500 uppercase">Location Code</p>
                  <p className="font-semibold text-gray-800">{alert.location_code}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded border border-gray-100">
                  <p className="text-xs text-gray-500 uppercase">Risk Level</p>
                  <p className={`font-bold ${alert.risk_level === 'CRITICAL' ? 'text-red-900' : 'text-red-600'}`}>{alert.risk_level}</p>
                </div>
                <div className="bg-gray-50 p-3 rounded border border-gray-100">
                  <p className="text-xs text-gray-500 uppercase">Risk Score</p>
                  <p className="font-semibold text-gray-800">{alert.risk_score.toFixed(4)}</p>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded text-sm text-blue-900 border border-blue-100 mb-4">
                {alert.message}
              </div>

              <div className="flex gap-2 border-t pt-4">
                {alert.status === 'ACTIVE' && (
                  <button onClick={() => handleStatusUpdate(alert.id, 'acknowledge')} className="px-4 py-2 bg-amber-500 text-white rounded hover:bg-amber-600 font-medium text-sm">
                    Acknowledge
                  </button>
                )}
                {(alert.status === 'ACTIVE' || alert.status === 'ACKNOWLEDGED') && (
                  <button onClick={() => handleStatusUpdate(alert.id, 'resolve')} className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 font-medium text-sm">
                    Resolve
                  </button>
                )}
                {alert.status === 'ACTIVE' && (
                  <button onClick={() => handleStatusUpdate(alert.id, 'dismiss')} className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 font-medium text-sm">
                    Dismiss
                  </button>
                )}
                <a href={`/risk-map`} className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50 font-medium text-sm">
                  View Case Map
                </a>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
            <p className="text-gray-500">No alerts found matching the criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;
