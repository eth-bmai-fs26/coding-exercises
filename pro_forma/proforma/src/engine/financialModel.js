export function calculateProjection(params) {
  const {
    revenueModel = 'new_revenue',
    launchMonth = 4,
    // new_revenue params
    baseCustomers = 0,
    growthRate = 0.05,
    revenuePerCustomer = 100,
    // churn_reduction params
    subscriberBase = 0,
    oldChurn = 0.08,
    newChurn = 0.04,
    avgRevenuePerUser = 50,
    // cost_savings params
    currentMonthlyCost = 0,
    savingsPercentage = 0.2,
    // cost params
    fixedMonthlyCost = 10000,
    variableRate = 0.1,
    upfrontCost = 50000,
    startingBudget = 200000,
    // additional cost lines
    additionalCosts = [],
  } = params;

  const months = Array.from({ length: 24 }, (_, i) => i + 1);
  const impact = [];
  const fixedCosts = [];
  const variableCosts = [];
  const totalCosts = [];
  const net = [];
  const cumulative = [];

  const effectiveLaunch = Math.max(1, Math.min(24, Math.round(launchMonth)));

  for (let i = 0; i < 24; i++) {
    const t = i + 1;

    // Calculate impact based on revenue model
    let monthImpact = 0;
    if (t >= effectiveLaunch) {
      const monthsSinceLaunch = t - effectiveLaunch;
      switch (revenueModel) {
        case 'new_revenue':
          monthImpact = baseCustomers * Math.pow(1 + Math.max(growthRate, -0.99), monthsSinceLaunch) * revenuePerCustomer;
          break;
        case 'churn_reduction':
          monthImpact = subscriberBase * Math.max(0, oldChurn - newChurn) * avgRevenuePerUser;
          break;
        case 'cost_savings':
          monthImpact = currentMonthlyCost * Math.min(1, Math.max(0, savingsPercentage));
          break;
        default:
          monthImpact = 0;
      }
    }
    impact.push(Math.max(0, monthImpact));

    // Calculate costs
    const additionalFixed = additionalCosts.reduce((sum, c) => sum + (c.monthly || 0), 0);
    const monthFixed = fixedMonthlyCost + additionalFixed;
    fixedCosts.push(monthFixed);

    const monthVariable = variableRate * impact[i];
    variableCosts.push(monthVariable);

    const monthUpfront = t === 1 ? upfrontCost : 0;
    totalCosts.push(monthFixed + monthVariable + monthUpfront);

    // Net and cumulative
    net.push(impact[i] - totalCosts[i]);
    cumulative.push((i === 0 ? 0 : cumulative[i - 1]) + net[i]);
  }

  // Find break-even month (when cumulative crosses zero from negative)
  let breakEvenMonth = null;
  for (let i = 1; i < 24; i++) {
    if (cumulative[i - 1] < 0 && cumulative[i] >= 0) {
      // Linear interpolation for more precise break-even
      const fraction = -cumulative[i - 1] / (cumulative[i] - cumulative[i - 1]);
      breakEvenMonth = Math.round((i + fraction) * 10) / 10 + 1;
      break;
    }
  }
  // If cumulative starts positive and stays positive
  if (breakEvenMonth === null && cumulative[0] >= 0) {
    breakEvenMonth = 1;
  }

  // Calculate runway (when starting budget + cumulative hits zero)
  let runwayMonth = null;
  const budgetCurve = cumulative.map(c => startingBudget + c);
  for (let i = 0; i < 24; i++) {
    if (budgetCurve[i] <= 0) {
      runwayMonth = i + 1;
      break;
    }
  }

  // Summary stats
  const totalInvestment = upfrontCost + totalCosts.reduce((s, c) => s + c, 0) - totalCosts.reduce((s, _, i) => s + impact[i], 0) < 0
    ? upfrontCost + fixedCosts.slice(0, effectiveLaunch - 1).reduce((s, c) => s + c, 0)
    : upfrontCost + fixedCosts.reduce((s, c) => s + c, 0);
  const annualImpact = impact.slice(0, 12).reduce((s, v) => s + v, 0);
  const monthlyRunCost = fixedMonthlyCost + additionalCosts.reduce((sum, c) => sum + (c.monthly || 0), 0);

  return {
    months,
    impact,
    fixedCosts,
    variableCosts,
    totalCosts,
    net,
    cumulative,
    budgetCurve,
    breakEvenMonth,
    runwayMonth,
    totalInvestment: upfrontCost + totalCosts.slice(0, Math.max(0, effectiveLaunch - 1)).reduce((s, c) => s + c, 0),
    annualImpact,
    monthlyRunCost,
    startingBudget,
  };
}
