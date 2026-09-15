/* ==========================================================================
   SIGNAL EARTH — KANPUR LST INVESTIGATION CONTROLLER
   Fetches continuous daily NASA POWER LST telemetry and renders interactive Plotly time series
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

fetch('../data/kanpur_lst_daily.json')
  .then(r => r.json())
  .then(data => {
    renderKanpurLSTTimeseries(data);
  })
  .catch(err => console.error('Kanpur LST data error:', err));

function renderKanpurLSTTimeseries(data) {
  const dates = data.map(d => d.date);
  const lstVals = data.map(d => d.lst);
  const airTVals = data.map(d => d.air_t);

  // 30-day moving average
  const rolling30 = lstVals.map((val, idx) => {
    if (val === null) return null;
    let sum = 0;
    let count = 0;
    for (let k = Math.max(0, idx - 29); k <= idx; k++) {
      if (lstVals[k] !== null) {
        sum += lstVals[k];
        count++;
      }
    }
    return count >= 15 ? +(sum / count).toFixed(1) : null;
  });

  const traces = [
    {
      x: dates,
      y: lstVals,
      mode: 'markers',
      type: 'scatter',
      name: 'Daily Satellite LST (Skin Temp)',
      marker: { color: 'rgba(245, 158, 11, 0.45)', size: 3.5 }
    },
    {
      x: dates,
      y: airTVals,
      mode: 'lines',
      name: '2m Air Temperature',
      line: { color: 'rgba(59, 130, 246, 0.65)', width: 1.2, dash: 'dot' }
    },
    {
      x: dates,
      y: rolling30,
      mode: 'lines',
      name: '30-Day LST Trajectory',
      line: { color: '#EF4444', width: 2.2 }
    }
  ];

  const layout = {
    ...OBSIDIAN_LAYOUT,
    yaxis: {
      ...OBSIDIAN_LAYOUT.yaxis,
      title: { text: 'Temperature (°C)', font: { size: 12, color: '#9BA3AF' } },
      range: [0, 48]
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
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 40, y1: 40, line: { color: 'rgba(239, 68, 68, 0.35)', width: 1, dash: 'dash' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 15, y1: 15, line: { color: 'rgba(59, 130, 246, 0.35)', width: 1, dash: 'dash' } }
    ],
    annotations: [
      { xref: 'paper', yref: 'y', x: 0.99, y: 41, text: 'Heatwave Threshold (40°C)', showarrow: false, font: { size: 9, color: 'rgba(239, 68, 68, 0.8)', family: 'monospace' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 16, text: 'Inversion Onset Threshold (15°C)', showarrow: false, font: { size: 9, color: 'rgba(59, 130, 246, 0.8)', family: 'monospace' }, xanchor: 'right' }
    ]
  };

  Plotly.newPlot('kanpur-lst-chart-timeseries', traces, layout, CONFIG);
}
