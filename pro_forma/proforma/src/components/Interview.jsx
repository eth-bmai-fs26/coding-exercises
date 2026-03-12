import { useState, useEffect, useCallback } from 'react';
import { askClaude } from '../api/claude.js';
import { getNextFallbackQuestion } from '../api/fallback.js';
import { sessionTracker } from '../utils/sessionTracker.js';

export default function Interview({ state, dispatch }) {
  const [inputValue, setInputValue] = useState('');
  const [description, setDescription] = useState('');

  const fetchNextQuestion = useCallback(async (desc, answers, useFallback) => {
    dispatch({ type: 'SET_LOADING', payload: true });

    if (useFallback) {
      const q = getNextFallbackQuestion(desc, answers);
      if (q.complete) {
        dispatch({ type: 'SET_PARAMETERS', payload: q.final_parameters });
        dispatch({ type: 'COMPLETE_INTERVIEW' });
      } else {
        sessionTracker.startQuestion(q.question_id);
        dispatch({ type: 'SET_QUESTION', payload: q });
      }
      return;
    }

    const result = await askClaude(desc, answers);
    if (result.fallback) {
      dispatch({ type: 'SET_FALLBACK' });
      const q = getNextFallbackQuestion(desc, answers);
      if (q.complete) {
        dispatch({ type: 'SET_PARAMETERS', payload: q.final_parameters });
        dispatch({ type: 'COMPLETE_INTERVIEW' });
      } else {
        sessionTracker.startQuestion(q.question_id);
        dispatch({ type: 'SET_QUESTION', payload: q });
      }
      return;
    }

    if (result.complete) {
      dispatch({ type: 'SET_PARAMETERS', payload: result.final_parameters });
      dispatch({ type: 'COMPLETE_INTERVIEW' });
    } else {
      sessionTracker.startQuestion(result.question_id);
      dispatch({ type: 'SET_QUESTION', payload: result });
    }
  }, [dispatch]);

  const handleSubmitDescription = (e) => {
    e.preventDefault();
    if (!description.trim()) return;
    dispatch({ type: 'SET_DESCRIPTION', payload: description.trim() });
    sessionTracker.logEvent('description_submitted', { description: description.trim() });
    fetchNextQuestion(description.trim(), [], state.useFallback);
  };

  const handleAnswer = (value) => {
    const q = state.currentQuestion;
    const mappedValue = q.mapValue ? q.mapValue(value) : value;

    sessionTracker.answerQuestion(q.question_id, value, q.default_value);

    const answer = {
      questionId: q.question_id,
      questionText: q.question_text,
      value,
      mappedValue,
      parameterKey: q.parameter_key,
      unit: q.unit,
    };

    dispatch({ type: 'ANSWER_QUESTION', payload: answer });

    // Set the parameter immediately for live dashboard update
    if (q.parameter_key) {
      dispatch({ type: 'SET_PARAMETER', key: q.parameter_key, value: mappedValue });
    }

    // Set any inferred parameters
    if (q.inferred_parameters) {
      dispatch({ type: 'SET_PARAMETERS', payload: q.inferred_parameters });
    }

    const newAnswers = [...state.answers, answer];
    fetchNextQuestion(state.description, newAnswers, state.useFallback);
  };

  if (state.interviewComplete) {
    return (
      <div className="fade-in">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
            <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-white">Interview Complete</h2>
        </div>
        <p className="text-gray-400 text-sm mb-4">
          Your business case for <span className="text-accent">&ldquo;{state.description}&rdquo;</span> is ready.
          Edit any assumption below to update the projections in real time.
        </p>
        <div className="border-t border-dark-700 pt-4">
          <h3 className="text-sm font-medium text-gray-300 uppercase tracking-wider mb-3">
            Assumptions
          </h3>
        </div>
      </div>
    );
  }

  if (!state.interviewStarted) {
    return (
      <div className="fade-in">
        <h2 className="font-display text-xl font-bold text-white mb-2">
          What&rsquo;s your initiative?
        </h2>
        <p className="text-gray-400 text-sm mb-6">
          Describe the business initiative you want to model. Be specific &mdash; mention the industry, target market, and what problem it solves.
        </p>
        <form onSubmit={handleSubmitDescription}>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="e.g., AI-powered client risk assessment tool for a Swiss private bank to automate KYC compliance checks..."
            className="w-full h-32 bg-dark-800 border border-dark-600 rounded-lg p-4 text-gray-100 placeholder-gray-600 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent resize-none text-sm"
          />
          <button
            type="submit"
            disabled={!description.trim()}
            className="mt-3 w-full bg-accent hover:bg-accent-light disabled:bg-dark-600 disabled:text-gray-600 text-dark-900 font-semibold py-2.5 px-4 rounded-lg transition-colors text-sm"
          >
            Build My Business Case
          </button>
        </form>
      </div>
    );
  }

  // Show current question
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
          Question {state.answers.length + 1}
        </h2>
        <div className="flex gap-1">
          {Array.from({ length: 8 }, (_, i) => (
            <div
              key={i}
              className={`w-6 h-1 rounded-full transition-colors ${
                i < state.answers.length ? 'bg-accent' : i === state.answers.length ? 'bg-accent/50' : 'bg-dark-600'
              }`}
            />
          ))}
        </div>
      </div>

      {state.loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
            <span className="text-gray-400 text-sm ml-2">Analyzing...</span>
          </div>
        </div>
      ) : state.currentQuestion ? (
        <QuestionCard
          question={state.currentQuestion}
          onAnswer={handleAnswer}
          inputValue={inputValue}
          setInputValue={setInputValue}
        />
      ) : null}

      {/* Previous answers */}
      {state.answers.length > 0 && (
        <div className="mt-6 border-t border-dark-700 pt-4">
          <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Previous Answers</h3>
          <div className="space-y-2">
            {state.answers.map((a, i) => (
              <div key={i} className="text-xs text-gray-400 flex justify-between">
                <span className="truncate mr-2">{a.questionText}</span>
                <span className="text-accent font-medium whitespace-nowrap">
                  {a.value} {a.unit || ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function QuestionCard({ question, onAnswer, inputValue, setInputValue }) {
  const q = question;
  const [localValue, setLocalValue] = useState(
    q.default_value !== undefined ? q.default_value : ''
  );

  useEffect(() => {
    setLocalValue(q.default_value !== undefined ? q.default_value : '');
    setInputValue('');
  }, [q.question_id, q.default_value, setInputValue]);

  const submit = (val) => {
    onAnswer(val !== undefined ? val : localValue);
  };

  return (
    <div className="slide-up">
      <h3 className="text-lg font-semibold text-white mb-2">{q.question_text}</h3>
      {q.help_text && (
        <p className="text-sm text-gray-400 mb-4 bg-dark-800 rounded-lg p-3 border border-dark-700">
          {q.help_text}
        </p>
      )}

      {q.input_type === 'select' && (
        <div className="space-y-2">
          {(q.options || []).map((opt) => (
            <button
              key={opt}
              onClick={() => submit(opt)}
              className={`w-full text-left px-4 py-3 rounded-lg border transition-colors text-sm ${
                opt === q.default_value
                  ? 'border-accent/50 bg-accent/10 text-white'
                  : 'border-dark-600 bg-dark-800 text-gray-300 hover:border-accent/30 hover:bg-dark-700'
              }`}
            >
              {opt}
              {opt === q.default_value && (
                <span className="text-accent text-xs ml-2">(suggested)</span>
              )}
            </button>
          ))}
        </div>
      )}

      {q.input_type === 'number' && (
        <div>
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={localValue}
              onChange={(e) => setLocalValue(Number(e.target.value))}
              min={q.min}
              max={q.max}
              step={q.step}
              className="flex-1 bg-dark-800 border border-dark-600 rounded-lg px-4 py-3 text-white focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent text-sm"
            />
            {q.unit && (
              <span className="text-gray-400 text-sm font-medium min-w-[60px]">{q.unit}</span>
            )}
          </div>
          <button
            onClick={() => submit()}
            className="mt-3 w-full bg-accent hover:bg-accent-light text-dark-900 font-semibold py-2.5 px-4 rounded-lg transition-colors text-sm"
          >
            Continue
          </button>
        </div>
      )}

      {q.input_type === 'slider' && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">{q.min}{q.unit ? ` ${q.unit}` : ''}</span>
            <span className="text-accent font-bold text-lg">{localValue}{q.unit ? ` ${q.unit}` : ''}</span>
            <span className="text-gray-400 text-sm">{q.max}{q.unit ? ` ${q.unit}` : ''}</span>
          </div>
          <input
            type="range"
            value={localValue}
            onChange={(e) => setLocalValue(Number(e.target.value))}
            min={q.min}
            max={q.max}
            step={q.step}
            className="w-full"
          />
          <button
            onClick={() => submit()}
            className="mt-3 w-full bg-accent hover:bg-accent-light text-dark-900 font-semibold py-2.5 px-4 rounded-lg transition-colors text-sm"
          >
            Continue
          </button>
        </div>
      )}

      {q.input_type === 'text' && (
        <div>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your answer..."
            className="w-full bg-dark-800 border border-dark-600 rounded-lg px-4 py-3 text-white focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent text-sm"
          />
          <button
            onClick={() => submit(inputValue)}
            className="mt-3 w-full bg-accent hover:bg-accent-light text-dark-900 font-semibold py-2.5 px-4 rounded-lg transition-colors text-sm"
          >
            Continue
          </button>
        </div>
      )}
    </div>
  );
}
