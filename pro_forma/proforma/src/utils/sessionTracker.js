class SessionTracker {
  constructor() {
    this.reset();
  }

  reset() {
    this.startTime = Date.now();
    this.events = [];
    this.questionTimestamps = {};
    this.parameterHistory = {};
    this.defaults = {};
  }

  logEvent(type, data = {}) {
    this.events.push({
      type,
      timestamp: Date.now(),
      elapsed: Date.now() - this.startTime,
      ...data,
    });
  }

  startQuestion(questionId) {
    this.questionTimestamps[questionId] = Date.now();
  }

  answerQuestion(questionId, value, defaultValue) {
    const timeSpent = this.questionTimestamps[questionId]
      ? Date.now() - this.questionTimestamps[questionId]
      : 0;

    this.defaults[questionId] = defaultValue;

    this.logEvent('question_answered', {
      questionId,
      value,
      defaultValue,
      defaultAccepted: value === defaultValue,
      timeSpentMs: timeSpent,
      hesitated: timeSpent > 30000,
    });
  }

  logParameterEdit(key, oldValue, newValue) {
    if (!this.parameterHistory[key]) {
      this.parameterHistory[key] = [];
    }
    this.parameterHistory[key].push({ oldValue, newValue, timestamp: Date.now() });

    this.logEvent('assumption_edited', { key, oldValue, newValue });
  }

  logScenarioView(scenario) {
    this.logEvent('scenario_viewed', { scenario });
  }

  logExport(type) {
    this.logEvent('export_clicked', { exportType: type });
  }

  getPainPoints() {
    const painPoints = [];

    // Questions with hesitation (>30s)
    this.events
      .filter(e => e.type === 'question_answered' && e.hesitated)
      .forEach(e => painPoints.push({
        type: 'hesitation',
        questionId: e.questionId,
        timeSpentMs: e.timeSpentMs,
      }));

    // Parameters edited multiple times
    Object.entries(this.parameterHistory)
      .filter(([, edits]) => edits.length > 1)
      .forEach(([key, edits]) => painPoints.push({
        type: 'multiple_edits',
        parameter: key,
        editCount: edits.length,
      }));

    // Defaults that were overridden
    this.events
      .filter(e => e.type === 'question_answered' && !e.defaultAccepted)
      .forEach(e => painPoints.push({
        type: 'default_overridden',
        questionId: e.questionId,
        defaultValue: e.defaultValue,
        chosenValue: e.value,
      }));

    return painPoints;
  }

  getReport(feedback = '') {
    return {
      sessionId: `session_${this.startTime}`,
      startTime: new Date(this.startTime).toISOString(),
      endTime: new Date().toISOString(),
      durationMs: Date.now() - this.startTime,
      events: this.events,
      parameterHistory: this.parameterHistory,
      painPoints: this.getPainPoints(),
      feedback,
    };
  }
}

export const sessionTracker = new SessionTracker();
