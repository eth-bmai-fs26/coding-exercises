import { exportPDF, exportExcel, exportSlide } from '../utils/exportHelpers.js';
import { sessionTracker } from '../utils/sessionTracker.js';

export default function ExportBar({ projection, parameters }) {
  const handleExport = (type, fn) => {
    sessionTracker.logExport(type);
    fn(projection, parameters);
  };

  return (
    <div className="border-t border-dark-700 bg-dark-800 px-6 py-3 flex items-center justify-between">
      <span className="text-xs text-gray-500">Export your business case</span>
      <div className="flex gap-3">
        <button
          onClick={() => handleExport('pdf', exportPDF)}
          className="text-sm text-gray-300 hover:text-white border border-dark-600 hover:border-accent/50 px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          Executive Summary PDF
        </button>
        <button
          onClick={() => handleExport('excel', exportExcel)}
          className="text-sm text-gray-300 hover:text-white border border-dark-600 hover:border-accent/50 px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          Detailed Excel Model
        </button>
        <button
          onClick={() => handleExport('slide', exportSlide)}
          className="text-sm text-gray-300 hover:text-white border border-dark-600 hover:border-accent/50 px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 13v-1m4 1v-3m4 3V8M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
          Presentation Slide
        </button>
      </div>
    </div>
  );
}
