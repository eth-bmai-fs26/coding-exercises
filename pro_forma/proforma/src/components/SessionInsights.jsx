import { useState } from 'react';
import { sessionTracker } from '../utils/sessionTracker.js';
import { exportSessionJSON } from '../utils/exportHelpers.js';

export default function SessionInsights() {
  const [open, setOpen] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleExportReport = () => {
    const report = sessionTracker.getReport(feedback);
    exportSessionJSON(report);
    sessionTracker.logExport('session_json');
  };

  const events = sessionTracker.events || [];
  const painPoints = sessionTracker.getPainPoints();

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-4 right-4 w-10 h-10 bg-dark-800 border border-dark-600 rounded-full flex items-center justify-center hover:border-accent/50 transition-colors z-50 shadow-lg"
        title="Session Insights"
      >
        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </button>

      {/* Panel */}
      {open && (
        <div className="fixed bottom-16 right-4 w-96 max-h-[70vh] bg-dark-800 border border-dark-700 rounded-xl shadow-2xl z-50 flex flex-col overflow-hidden fade-in">
          <div className="flex items-center justify-between px-4 py-3 border-b border-dark-700">
            <h3 className="text-sm font-semibold text-white">Session Insights</h3>
            <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-white">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Pain Points */}
            {painPoints.length > 0 && (
              <div>
                <h4 className="text-xs font-medium text-orange-400 uppercase tracking-wider mb-2">
                  Pain Points Detected ({painPoints.length})
                </h4>
                <div className="space-y-1">
                  {painPoints.map((pp, i) => (
                    <div key={i} className="text-xs text-orange-300/70 bg-orange-900/20 rounded px-2 py-1">
                      {pp.type === 'hesitation' && `Hesitated on ${pp.questionId} (${(pp.timeSpentMs / 1000).toFixed(0)}s)`}
                      {pp.type === 'multiple_edits' && `Edited "${pp.parameter}" ${pp.editCount} times`}
                      {pp.type === 'default_overridden' && `Overrode default on ${pp.questionId}`}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Event Log */}
            <div>
              <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Interaction Log ({events.length} events)
              </h4>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {events.map((event, i) => (
                  <div key={i} className="text-xs text-gray-500 flex gap-2">
                    <span className="text-gray-600 whitespace-nowrap">
                      {(event.elapsed / 1000).toFixed(0)}s
                    </span>
                    <span className="text-gray-400">{event.type}</span>
                    {event.questionId && <span className="text-gray-500">({event.questionId})</span>}
                  </div>
                ))}
                {events.length === 0 && (
                  <p className="text-xs text-gray-600">No events recorded yet.</p>
                )}
              </div>
            </div>

            {/* Feedback */}
            <div>
              <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
                Your Feedback
              </h4>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="What was confusing? What's missing?"
                className="w-full h-20 bg-dark-700 border border-dark-600 rounded-lg p-2 text-xs text-gray-300 placeholder-gray-600 focus:border-accent focus:outline-none resize-none"
              />
            </div>
          </div>

          <div className="px-4 py-3 border-t border-dark-700">
            <button
              onClick={handleExportReport}
              className="w-full bg-accent hover:bg-accent-light text-dark-900 font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
            >
              Export Session Report (JSON)
            </button>
          </div>
        </div>
      )}
    </>
  );
}
