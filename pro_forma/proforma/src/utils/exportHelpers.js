function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function exportSessionJSON(report) {
  const json = JSON.stringify(report, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  downloadBlob(blob, `proforma-session-${Date.now()}.json`);
}

export function exportExcel(projection, params) {
  const headers = ['Month', 'Impact', 'Fixed Costs', 'Variable Costs', 'Total Costs', 'Net', 'Cumulative'];
  const rows = projection.months.map((m, i) => [
    m,
    projection.impact[i].toFixed(2),
    projection.fixedCosts[i].toFixed(2),
    projection.variableCosts[i].toFixed(2),
    projection.totalCosts[i].toFixed(2),
    projection.net[i].toFixed(2),
    projection.cumulative[i].toFixed(2),
  ]);

  const csv = [
    `# ProForma Financial Projection`,
    `# Revenue Model: ${params.revenueModel || 'N/A'}`,
    `# Generated: ${new Date().toISOString()}`,
    '',
    headers.join(','),
    ...rows.map(r => r.join(',')),
    '',
    '# Summary',
    `Total Investment,${projection.totalInvestment.toFixed(2)}`,
    `Annual Impact,${projection.annualImpact.toFixed(2)}`,
    `Monthly Run Cost,${projection.monthlyRunCost.toFixed(2)}`,
    `Break-even Month,${projection.breakEvenMonth || 'N/A'}`,
  ].join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  downloadBlob(blob, `proforma-model-${Date.now()}.csv`);
}

export function exportPDF() {
  alert('PDF export coming in v2. For now, use your browser\'s Print function (Ctrl/Cmd+P) to save as PDF.');
}

export function exportSlide() {
  alert('Presentation export coming in v2.');
}
