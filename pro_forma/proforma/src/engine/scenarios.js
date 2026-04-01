import { calculateProjection } from './financialModel.js';

function applyScenarioMultipliers(params, impactMult, costMult, launchOffset) {
  const adjusted = { ...params };
  adjusted.launchMonth = Math.max(1, (params.launchMonth || 4) + launchOffset);
  adjusted.fixedMonthlyCost = (params.fixedMonthlyCost || 10000) * costMult;
  adjusted.upfrontCost = (params.upfrontCost || 50000) * costMult;

  switch (params.revenueModel) {
    case 'new_revenue':
      adjusted.revenuePerCustomer = (params.revenuePerCustomer || 100) * impactMult;
      break;
    case 'churn_reduction': {
      const churnDelta = (params.oldChurn || 0.08) - (params.newChurn || 0.04);
      const adjustedDelta = churnDelta * impactMult;
      adjusted.newChurn = (params.oldChurn || 0.08) - adjustedDelta;
      break;
    }
    case 'cost_savings':
      adjusted.savingsPercentage = Math.min(1, (params.savingsPercentage || 0.2) * impactMult);
      break;
  }

  return adjusted;
}

export function generateScenarios(baseParams) {
  return {
    conservative: calculateProjection(applyScenarioMultipliers(baseParams, 0.7, 1.2, 2)),
    base: calculateProjection(baseParams),
    optimistic: calculateProjection(applyScenarioMultipliers(baseParams, 1.25, 0.9, -1)),
  };
}
