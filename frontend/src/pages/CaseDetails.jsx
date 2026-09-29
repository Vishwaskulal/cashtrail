import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getCase, getPrediction, getInvestigationNotes, createInvestigationNote } from '../services/api';

const CaseDetails = () => {
  const { caseId } = useParams();
  const [caseData, setCaseData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [noteSubmitting, setNoteSubmitting] = useState(false);

  useEffect(() => {
    const fetchCaseData = async () => {
      try {
        const [cData, pData, nData] = await Promise.all([
          getCase(caseId),
          getPrediction(caseId).catch(() => null),
          getInvestigationNotes(caseId).catch(() => [])
        ]);
        
        setCaseData(cData);
        setPrediction(pData);
        setNotes(nData);
      } catch (err) {
        console.error(err);
        setError("Unable to load case details. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchCaseData();
  }, [caseId]);

  const handleNoteSubmit = async (e) => {
    e.preventDefault();
    if (!newNote.trim()) return;
    
    setNoteSubmitting(true);
    try {
      await createInvestigationNote(caseId, { note_content: newNote, author_id: 1 });
      const updatedNotes = await getInvestigationNotes(caseId);
      setNotes(updatedNotes);
      setNewNote('');
    } catch (err) {
      alert("Failed to add note.");
    } finally {
      setNoteSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto flex justify-center items-center h-64">
        <p className="text-slate-500 text-lg">Loading case details...</p>
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100">{error || "Case not found."}</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto font-sans bg-slate-50 min-h-screen">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <Link to="/cases" className="text-blue-600 hover:underline text-sm mb-2 inline-block">← Back to Cases</Link>
          <h1 className="text-3xl font-bold text-slate-800 tracking-tight">Case {caseData.case_number}</h1>
          <p className="text-slate-500 mt-1">Status: {caseData.status}</p>
        </div>
        <Link to="/risk-map" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium">
          View on Risk Map
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Details & Predictions */}
        <div className="lg:col-span-2 space-y-6">
          
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-xl font-bold text-slate-800 mb-4 border-b pb-2">Case Information</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-slate-500">Complaint Date</p>
                <p className="font-semibold">{new Date(caseData.complaint_date).toLocaleDateString()}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500">Crime Category</p>
                <p className="font-semibold">{caseData.crime_category}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500">Total Amount</p>
                <p className="font-semibold">${caseData.total_amount.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500">Overall Risk Level</p>
                <p className={`font-bold ${caseData.risk_level === 'CRITICAL' ? 'text-red-700' : caseData.risk_level === 'HIGH' ? 'text-orange-600' : 'text-slate-700'}`}>
                  {caseData.risk_level}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h2 className="text-xl font-bold text-slate-800 mb-4 border-b pb-2 flex justify-between">
              <span>Potential Withdrawal-Risk Locations</span>
              {prediction && <span className="text-xs text-slate-500 font-normal self-end mb-1">Generated: {new Date(prediction.prediction_timestamp).toLocaleString()}</span>}
            </h2>
            
            {!prediction || prediction.locations.length === 0 ? (
              <p className="text-slate-500 italic">No ML prediction data available for this case.</p>
            ) : (
              <div className="space-y-4">
                {prediction.locations.slice(0, 5).map((loc, idx) => (
                  <div key={idx} className="flex justify-between items-center p-4 border border-slate-100 rounded bg-slate-50">
                    <div>
                      <p className="font-bold text-slate-800">{loc.location_name} <span className="text-xs text-slate-500 font-normal ml-2">({loc.location_id})</span></p>
                      <p className="text-sm text-slate-600">{loc.city}, {loc.district}, {loc.state}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-slate-500 uppercase tracking-wider">Risk Score</p>
                      <p className={`font-bold text-lg ${loc.risk_score >= 0.8 ? 'text-red-600' : 'text-orange-500'}`}>
                        {loc.risk_score.toFixed(4)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Investigation Notes */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col h-full">
            <h2 className="text-xl font-bold text-slate-800 mb-4 border-b pb-2">Investigation Notes</h2>
            
            <div className="flex-grow overflow-y-auto max-h-96 space-y-4 mb-4">
              {notes.length === 0 ? (
                <p className="text-slate-500 text-sm italic">No investigation notes yet.</p>
              ) : (
                notes.map(note => (
                  <div key={note.id} className="bg-slate-50 p-3 rounded border border-slate-100">
                    <p className="text-xs text-slate-400 mb-1 flex justify-between">
                      <span>Investigator #{note.author_id}</span>
                      <span>{new Date(note.created_at).toLocaleString()}</span>
                    </p>
                    <p className="text-sm text-slate-700 whitespace-pre-wrap">{note.note_content}</p>
                  </div>
                ))
              )}
            </div>

            <div className="mt-auto border-t pt-4">
              <form onSubmit={handleNoteSubmit}>
                <textarea
                  className="w-full border border-slate-300 rounded p-2 text-sm mb-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  rows="3"
                  placeholder="Add an investigation note..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  required
                ></textarea>
                <button 
                  type="submit" 
                  disabled={noteSubmitting}
                  className="w-full bg-slate-800 text-white rounded py-2 text-sm font-medium hover:bg-slate-700 disabled:opacity-50"
                >
                  {noteSubmitting ? 'Saving...' : 'Add Note'}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseDetails;
