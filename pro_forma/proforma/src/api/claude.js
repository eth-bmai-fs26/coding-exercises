const SYSTEM_PROMPT = `You are a financial modeling assistant helping executives build business cases for corporate initiatives.

Given the user's initiative description and their answers so far, generate the next question to ask.

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, no code fences — just the JSON object.

Response structure for each question:
{
  "question_id": "q1",
  "question_text": "The question to display",
  "help_text": "Helpful context or industry benchmarks",
  "input_type": "select" | "number" | "slider" | "text",
  "options": ["Option A", "Option B", "Option C"],
  "default_value": 50,
  "min": 0, "max": 100, "step": 1,
  "unit": "CHF" | "%" | "months" | "people",
  "parameter_key": "subscriber_base",
  "inferred_parameters": {
    "revenue_model": "churn_reduction",
    "industry": "media"
  }
}

When you have enough information (6-8 questions answered), respond with:
{
  "complete": true,
  "summary": "Brief summary of the business case",
  "final_parameters": { ... all model parameters using camelCase keys: revenueModel, baseCustomers, growthRate, revenuePerCustomer, subscriberBase, oldChurn, newChurn, avgRevenuePerUser, currentMonthlyCost, savingsPercentage, fixedMonthlyCost, variableRate, upfrontCost, launchMonth, startingBudget ... }
}

Use Swiss Francs (CHF) as the default currency. Provide Swiss/European industry benchmarks where relevant. Be specific to the user's described initiative — do not ask generic questions.`;

function buildConversationContext(description, answers) {
  let context = `Initiative: ${description}\n\n`;
  if (answers.length > 0) {
    context += 'Answers so far:\n';
    answers.forEach(a => {
      context += `- ${a.questionText}: ${a.value}${a.unit ? ' ' + a.unit : ''}\n`;
    });
    context += `\nPlease generate question #${answers.length + 1}.`;
  } else {
    context += 'This is the first question. Start by asking about the revenue model type.';
  }
  return context;
}

function parseResponse(text) {
  // Strip markdown code fences if present
  let cleaned = text.trim();
  if (cleaned.startsWith('```')) {
    cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
  }
  return JSON.parse(cleaned);
}

export async function askClaude(description, answers) {
  try {
    const response = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: SYSTEM_PROMPT,
        messages: [
          { role: 'user', content: buildConversationContext(description, answers) },
        ],
      }),
    });

    const data = await response.json();

    if (data.error) {
      return { fallback: true, error: data.error };
    }

    const text = data.content?.[0]?.text;
    if (!text) {
      return { fallback: true, error: 'empty_response' };
    }

    return parseResponse(text);
  } catch (err) {
    return { fallback: true, error: err.message };
  }
}
