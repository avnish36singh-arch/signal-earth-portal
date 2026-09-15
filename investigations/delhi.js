/* ==========================================================================
   SIGNAL EARTH — DELHI INVESTIGATION CONTROLLER
   Gap-Fixed CPCB Daily Telemetry (asfreq('D') with explicit nulls across 2019-2020)
   ========================================================================== */

const OBSIDIAN_LAYOUT = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Inter, system-ui, sans-serif', color: '#9BA3AF', size: 12 },
  margin: { t: 30, r: 24, b: 45, l: 55 },
  xaxis: { 
    gridcolor: 'rgba(255, 255, 255, 0.05)', 
    zerolinecolor: 'rgba(255, 255, 255, 0.08)',
    tickfont: { size: 11, color: '#6B7280' }
  },
  yaxis: { 
    gridcolor: 'rgba(255, 255, 255, 0.05)', 
    zerolinecolor: 'rgba(255, 255, 255, 0.08)',
    tickfont: { size: 11, color: '#6B7280' }
  }
};

const CONFIG = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: ['lasso2d', 'select2d']
};

fetch('../data/delhi_daily_gapfixed.json')
  .then(r => r.json())
  .then(data => {
    renderDelhiTimeseries(data);
  })
  .catch(err => console.error('Delhi data error:', err));

function renderDelhiTimeseries(data) {
  const dates = data.map(d => d.date);
  const aqiVals = data.map(d => d.aqi);
  const pm25Vals = data.map(d => d.pm25);

  // Compute 7-day rolling average strictly ignoring gaps
  const rolling7 = aqiVals.map((val, idx) => {
    if (val === null) return null;
    const windowVals = [];
    for (let k = Math.max(0, idx - 6); k <= idx; k++) {
      if (aqiVals[k] !== null) windowVals.push(aqiVals[k]);
    }
    return windowVals.length >= 4 
      ? +(windowVals.reduce((a, b) => a + b, 0) / windowVals.length).toFixed(1) 
      : null;
  });

  const traces = [
    {
      x: dates,
      y: aqiVals,
      mode: 'markers',
      type: 'scatter',
      name: 'Daily Calculated CPCB AQI',
      marker: { color: 'rgba(155, 163, 175, 0.45)', size: 3.5 },
      connectgaps: false
    },
    {
      x: dates,
      y: rolling7,
      mode: 'lines',
      name: '7-Day Rolling Trendline',
      line: { color: '#22D3EE', width: 2 },
      connectgaps: false
    }
  ];

  const layout = {
    ...OBSIDIAN_LAYOUT,
    yaxis: {
      ...OBSIDIAN_LAYOUT.yaxis,
      title: { text: 'Air Quality Index (AQI)', font: { size: 12, color: '#9BA3AF' } },
      range: [0, 540]
    },
    legend: {
      orientation: 'h',
      y: 1.12,
      font: { size: 11, color: '#9BA3AF' }
    },
    hoverlabel: {
      bgcolor: '#11141A',
      bordercolor: 'rgba(255, 255, 255, 0.15)',
      font: { family: 'Inter', color: '#FFFFFF', size: 12 }
    },
    shapes: [
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 50, y1: 50, line: { color: 'rgba(163, 230, 53, 0.25)', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 100, y1: 100, line: { color: 'rgba(245, 158, 11, 0.25)', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 200, y1: 200, line: { color: 'rgba(249, 115, 22, 0.3)', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 300, y1: 300, line: { color: 'rgba(244, 63, 94, 0.35)', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 400, y1: 400, line: { color: 'rgba(168, 85, 247, 0.4)', width: 1, dash: 'dash' } }
    ],
    annotations: [
      { xref: 'paper', yref: 'y', x: 0.99, y: 415, text: 'Severe (401–500)', showarrow: false, font: { size: 9, color: 'rgba(168, 85, 247, 0.7)', family: 'monospace' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 315, text: 'Very Poor (301–400)', showarrow: false, font: { size: 9, color: 'rgba(244, 63, 94, 0.7)', family: 'monospace' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 215, text: 'Poor (201–300)', showarrow: false, font: { size: 9, color: 'rgba(249, 115, 22, 0.7)', family: 'monospace' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 115, text: 'Moderate (101–200)', showarrow: false, font: { size: 9, color: 'rgba(245, 158, 11, 0.7)', family: 'monospace' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 60, text: 'Satisfactory (51–100)', showarrow: false, font: { size: 9, color: 'rgba(163, 230, 53, 0.7)', family: 'monospace' }, xanchor: 'right' },
      {
        x: '2020-01-01',
        y: 200,
        xref: 'x',
        yref: 'y',
        text: '2019–2020 Monitoring Pause (No Data)',
        showarrow: false,
        font: { size: 10, color: '#6B7280', family: 'monospace' },
        bgcolor: 'rgba(17, 20, 26, 0.85)',
        bordercolor: 'rgba(255, 255, 255, 0.1)'
      }
    ]
  };

  Plotly.newPlot('delhi-chart-timeseries', traces, layout, CONFIG);
}

// Fetch master cleaned dataset to render Indicative Source Signature diagnostic
fetch('../data/cleaned.json')
  .then(r => r.json())
  .then(records => {
    renderSourceBreakdown(records);
  })
  .catch(err => console.error('Sources data error:', err));

function renderSourceBreakdown(records) {
  const counts = {};
  records.forEach(r => {
    const reg = r.Source_Regime;
    if (reg && reg !== 'Unclassified') {
      counts[reg] = (counts[reg] || 0) + 1;
    }
  });

  const labels = Object.keys(counts);
  const values = Object.values(counts);

  const colors = {
    'Industrial Solvent Emissions': '#A855F7',
    'Fugitive & Crustal Dust': '#F59E0B',
    'Biomass & Stubble Smog': '#EF4444',
    'Vehicular & Urban Mixed': '#22D3EE',
    'Regional Background': '#10B981'
  };

  const pieColors = labels.map(l => colors[l] || '#94A3B8');

  const trace = [{
    values: values,
    labels: labels,
    type: 'pie',
    hole: 0.55,
    textinfo: 'label+percent',
    hoverinfo: 'label+value+percent',
    textposition: 'outside',
    automargin: true,
    marker: {
      colors: pieColors,
      line: { color: '#0A0B0D', width: 2 }
    }
  }];

  const layout = {
    ...OBSIDIAN_LAYOUT,
    margin: { t: 30, r: 30, b: 50, l: 30 },
    showlegend: true,
    legend: {
      orientation: 'h',
      y: -0.15,
      x: 0,
      font: { size: 11, color: '#9BA3AF' }
    },
    hoverlabel: {
      bgcolor: '#11141A',
      bordercolor: 'rgba(255, 255, 255, 0.15)',
      font: { family: 'Inter', color: '#FFFFFF', size: 12 }
    }
  };

  Plotly.newPlot('delhi-chart-sources', trace, layout, CONFIG);
}
