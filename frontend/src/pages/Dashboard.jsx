import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardStats, getCases, getAlerts, getPredictions } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentCases, setRecentCases] = useState([]);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsData, casesData, alertsData, predictionsData] = await Promise.all([
          getDashboardStats(),
          getCases(),
          getAlerts({ status: 'ACTIVE' }),
          getPredictions()
        ]);
        
        setStats(statsData);
        setRecentCases(casesData.cases ? casesData.cases.slice(0, 5) : []);
        setActiveAlerts(alertsData.alerts ? alertsData.alerts.slice(0, 5) : []);
        setRecentPredictions(predictionsData.slice(0, 5));
      } catch (err) {
        console.error(err);
        setError("Unable to load dashboard data. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto flex justify-center items-center h-64">
        <p className="text-gray-500 text-lg">Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100">{error}</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Intelligence Dashboard</h1>
        <p className="text-slate-500 mt-1">Overview of predictive insights and investigations</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Total Cases</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">{stats?.total_cases || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">High-Risk Cases</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{stats?.high_risk_cases || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Total Predictions</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">{stats?.total_predictions || 0}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <p className="text-sm text-slate-500 font-medium">Active Alerts</p>
          <p className="text-3xl font-bold text-amber-600 mt-2">{stats?.active_alerts || 0}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Recent Cases */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h2 className="text-lg font-bold text-slate-800">Recent Cases</h2>
              <Link to="/cases" className="text-sm text-blue-600 hover:text-blue-800 font-medium">View All</Link>
            </div>
            <div className="p-0">
              {recentCases.length === 0 ? (
                <div className="p-6 text-center text-slate-500">No cases available.</div>
              ) : (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                      <th className="p-4 font-semibold">Case ID</th>
                      <th className="p-4 font-semibold">Date</th>
                      <th className="p-4 font-semibold">Category</th>
                      <th className="p-4 font-semibold">Risk Level</th>
                      <th className="p-4 font-semibold">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    {recentCases.map(c => (
                      <tr key={c.case_number} className="hover:bg-slate-50">
                        <td className="p-4 font-medium text-slate-800">{c.case_number}</td>
                        <td className="p-4 text-slate-600">{new Date(c.complaint_date).toLocaleDateString()}</td>
                        <td className="p-4 text-slate-600">{c.crime_category}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            c.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                            c.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                            'bg-slate-100 text-slate-800'
                          }`}>
                            {c.risk_level}
                          </span>
                        </td>
                        <td className="p-4">
                          <Link to={`/cases/${c.case_number}`} className="text-blue-600 hover:underline">Details</Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Recent Predictions */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h2 className="text-lg font-bold text-slate-800">Recent Predictions</h2>
              <Link to="/predictions" className="text-sm text-blue-600 hover:text-blue-800 font-medium">View All</Link>
            </div>
            <div className="p-0">
              {recentPredictions.length === 0 ? (
                <div className="p-6 text-center text-slate-500">No predictions available.</div>
              ) : (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                      <th className="p-4 font-semibold">Case</th>
                      <th className="p-4 font-semibold">Top Potential Location</th>
                      <th className="p-4 font-semibold">Risk Score</th>
                      <th className="p-4 font-semibold">Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    {recentPredictions.map((p, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="p-4 font-medium text-slate-800">{p.case_id}</td>
                        <td className="p-4 text-slate-600">
                          {p.locations && p.locations.length > 0 ? p.locations[0].location_name : 'N/A'}
                        </td>
                        <td className="p-4 font-semibold text-slate-700">
                          {p.locations && p.locations.length > 0 ? p.locations[0].risk_score.toFixed(4) : '-'}
                        </td>
                        <td className="p-4 text-slate-500 whitespace-nowrap">
                          {new Date(p.prediction_timestamp).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-8">
          
          {/* Active Alerts */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200">
            <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-red-50/30">
              <h2 className="text-lg font-bold text-slate-800">Active Alerts</h2>
              <Link to="/alerts" className="text-sm text-red-600 hover:text-red-800 font-medium">View All</Link>
            </div>
            <div className="p-5 space-y-4">
              {activeAlerts.length === 0 ? (
                <div className="text-center text-slate-500 py-4">No active alerts.</div>
              ) : (
                activeAlerts.map(alert => (
                  <div key={alert.id} className="p-4 rounded border border-red-100 bg-red-50">
                    <div className="flex justify-between items-start mb-2">
                      <p className="font-bold text-red-900">{alert.case_number}</p>
                      <span className="text-xs font-bold bg-red-200 text-red-900 px-2 py-1 rounded">
                        {alert.risk_level}
                      </span>
                    </div>
                    <p className="text-sm text-red-800 mb-3">{alert.title}</p>
                    <Link to="/alerts" className="text-sm text-red-700 hover:underline font-medium">
                      Review Alert →
                    </Link>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* GIS Preview */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200">
            <div className="p-5 border-b border-slate-100 flex justify-between items-center">
              <h2 className="text-lg font-bold text-slate-800">Risk Map Preview</h2>
            </div>
            <div className="p-5 flex flex-col items-center justify-center bg-slate-50 h-48 rounded-b-xl border-t-0 border border-slate-100">
              <p className="text-slate-500 mb-4 text-center">GIS visualization of potential withdrawal-risk locations</p>
              <Link to="/risk-map" className="px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 transition font-medium">
                Open Full Risk Map
              </Link>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;
