import { useReducer, useEffect, useCallback } from 'react';
import { calculateProjection } from './engine/financialModel.js';
import { generateScenarios } from './engine/scenarios.js';
import { sessionTracker } from './utils/sessionTracker.js';
import Interview from './components/Interview.jsx';
import Dashboard from './components/Dashboard.jsx';
import Assumptions from './components/Assumptions.jsx';
import ScenarioTabs from './components/ScenarioTabs.jsx';
import ExportBar from './components/ExportBar.jsx';
import SessionInsights from './components/SessionInsights.jsx';

const DEMO_PARAMS = {
  revenueModel: 'cost_savings',
  currentMonthlyCost: 200000,
  savingsPercentage: 0.25,
  fixedMonthlyCost: 45000,
  variableRate: 0.05,
  upfrontCost: 150000,
  launchMonth: 4,
  startingBudget: 500000,
  additionalCosts: [],
};

const INITIAL_STATE = {
  description: '',
  parameters: {},
  answers: [],
  currentQuestion: null,
  scenarios: null,
  activeScenario: 'base',
  interviewComplete: false,
  interviewStarted: false,
  loading: false,
  useFallback: false,
};

function reducer(state, action) {
  switch (action.type) {
    case 'SET_DESCRIPTION':
      return { ...state, description: action.payload, interviewStarted: true };
    case 'SET_QUESTION':
      return { ...state, currentQuestion: action.payload, loading: false };
    case 'ANSWER_QUESTION':
      return {
        ...state,
        answers: [...state.answers, action.payload],
        loading: true,
      };
    case 'SET_PARAMETER': {
      const newParams = { ...state.parameters, [action.key]: action.value };
      return { ...state, parameters: newParams };
    }
    case 'SET_PARAMETERS':
      return { ...state, parameters: { ...state.parameters, ...action.payload } };
    case 'COMPLETE_INTERVIEW':
      return { ...state, interviewComplete: true, loading: false, currentQuestion: null };
    case 'SET_SCENARIOS':
      return { ...state, scenarios: action.payload };
    case 'SET_SCENARIO':
      return { ...state, activeScenario: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_FALLBACK':
      return { ...state, useFallback: true };
    case 'LOAD_DEMO':
      return {
        ...state,
        description: 'AI-powered client risk assessment tool for a Swiss private bank',
        parameters: { ...DEMO_PARAMS },
        interviewComplete: true,
        interviewStarted: true,
      };
    case 'RESET':
      sessionTracker.reset();
      return { ...INITIAL_STATE };
    default:
      return state;
  }
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, INITIAL_STATE);

  // Recalculate projections whenever parameters change
  useEffect(() => {
    if (Object.keys(state.parameters).length > 0) {
      try {
        const scenarios = generateScenarios(state.parameters);
        dispatch({ type: 'SET_SCENARIOS', payload: scenarios });
      } catch (e) {
        console.error('Projection calculation error:', e);
      }
    }
  }, [state.parameters]);

  const handleParameterChange = useCallback((key, value) => {
    const oldValue = state.parameters[key];
    sessionTracker.logParameterEdit(key, oldValue, value);
    dispatch({ type: 'SET_PARAMETER', key, value });
  }, [state.parameters]);

  const handleScenarioChange = useCallback((scenario) => {
    sessionTracker.logScenarioView(scenario);
    dispatch({ type: 'SET_SCENARIO', payload: scenario });
  }, []);

  const currentProjection = state.scenarios?.[state.activeScenario] || null;

  return (
    <div className="min-h-screen bg-dark-900 flex flex-col">
      {/* Header */}
      <header className="border-b border-dark-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="font-display text-2xl font-bold text-white tracking-tight">
            ProForma
          </h1>
          <span className="text-xs text-gray-500 border border-dark-500 rounded px-2 py-0.5 uppercase tracking-wider">
            Beta
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              dispatch({
                type: 'LOAD_DEMO',
              });
            }}
            className="text-sm text-accent hover:text-accent-light transition-colors px-3 py-1.5 border border-dark-500 rounded hover:border-accent/50"
          >
            Try Demo
          </button>
          <button
            onClick={() => dispatch({ type: 'RESET' })}
            className="text-sm text-gray-400 hover:text-white transition-colors px-3 py-1.5 border border-dark-500 rounded hover:border-gray-400"
          >
            Reset
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Interview */}
        <div className="w-[40%] border-r border-dark-700 overflow-y-auto p-6">
          <Interview
            state={state}
            dispatch={dispatch}
          />
          {state.interviewComplete && (
            <div className="mt-6">
              <Assumptions
                parameters={state.parameters}
                onChange={handleParameterChange}
              />
            </div>
          )}
        </div>

        {/* Right Panel - Dashboard */}
        <div className="w-[60%] overflow-y-auto p-6">
          {state.scenarios ? (
            <>
              <ScenarioTabs
                active={state.activeScenario}
                onChange={handleScenarioChange}
              />
              <Dashboard
                projection={currentProjection}
                parameters={state.parameters}
              />
            </>
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4 opacity-20">📊</div>
                <p className="text-gray-500 text-lg">
                  Describe your initiative to begin
                </p>
                <p className="text-gray-600 text-sm mt-2">
                  Your financial dashboard will build itself as you answer questions
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Export Bar */}
      {state.scenarios && (
        <ExportBar
          projection={currentProjection}
          parameters={state.parameters}
        />
      )}

      {/* Session Insights */}
      <SessionInsights />
    </div>
  );
}
