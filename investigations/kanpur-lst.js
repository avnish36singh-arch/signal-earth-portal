/* ==========================================================================
   SIGNAL EARTH : KANPUR REANALYSIS TEMPERATURE CONTROLLER
   NASA POWER / MERRA-2 daily model reanalysis skin temperature (TS)
   Grid cell 0.5 x 0.625 degrees centered at 26.4499 N, 80.3319 E (2017 to 2023)
   ========================================================================== */

const LIGHT_LAYOUT = {
  paper_bgcolor: '#FFFFFF',
  plot_bgcolor: '#FFFFFF',
  font: { family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', color: '#374151', size: 12 },
  margin: { t: 30, r: 24, b: 45, l: 55 },
  xaxis: { 
    gridcolor: '#E2E8F0', 
    zerolinecolor: '#CBD5E1',
    tickfont: { size: 11, color: '#4B5563' }
  },
  yaxis: { 
    gridcolor: '#E2E8F0', 
    zerolinecolor: '#CBD5E1',
    tickfont: { size: 11, color: '#4B5563' }
  }
};

const CONFIG = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: ['lasso2d', 'select2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],
  displayModeBar: true
};

fetch('../data/kanpur_lst_daily.json')
  .then(function(r) { return r.json(); })
  .then(function(data) {
    renderKanpurLSTTimeseries(data);
  })
  .catch(function(err) { console.error('Kanpur LST data error:', err); });

function renderKanpurLSTTimeseries(data) {
  var dates = data.map(function(d) { return d.date; });
  var lstVals = data.map(function(d) { return d.lst; });
  var airTVals = data.map(function(d) { return d.air_t; });

  // 30-day moving average
  var rolling30 = lstVals.map(function(val, idx) {
    if (val === null) return null;
    var sum = 0;
    var count = 0;
    for (var k = Math.max(0, idx - 29); k <= idx; k++) {
      if (lstVals[k] !== null) {
        sum += lstVals[k];
        count++;
      }
    }
    return count >= 15 ? +(sum / count).toFixed(1) : null;
  });

  var traces = [
    {
      x: dates,
      y: lstVals,
      mode: 'markers',
      type: 'scatter',
      name: 'Daily Reanalysis Skin Temperature (TS)',
      marker: { color: '#D97706', size: 3.5 }
    },
    {
      x: dates,
      y: airTVals,
      mode: 'lines',
      name: '2m Air Temperature (T2M)',
      line: { color: '#2C5282', width: 1.2, dash: 'dot' }
    },
    {
      x: dates,
      y: rolling30,
      mode: 'lines',
      name: '30-Day Mean Trajectory',
      line: { color: '#991B1B', width: 2.2 }
    }
  ];

  var layout = {
    ...LIGHT_LAYOUT,
    yaxis: {
      ...LIGHT_LAYOUT.yaxis,
      title: { text: 'Temperature (°C)', font: { size: 12, color: '#374151' } },
      range: [0, 48]
    },
    legend: {
      orientation: 'h',
      y: 1.12,
      font: { size: 11, color: '#374151' }
    },
    hoverlabel: {
      bgcolor: '#FFFFFF',
      bordercolor: '#CBD5E1',
      font: { family: 'sans-serif', color: '#111827', size: 12 }
    },
    shapes: [
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 40, y1: 40, line: { color: '#DC2626', width: 1, dash: 'dash' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 15, y1: 15, line: { color: '#2C5282', width: 1, dash: 'dash' } }
    ],
    annotations: [
      { xref: 'paper', yref: 'y', x: 0.99, y: 41, text: 'Heat Threshold (40°C)', showarrow: false, font: { size: 9, color: '#DC2626' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 16, text: 'Winter Baseline Threshold (15°C)', showarrow: false, font: { size: 9, color: '#2C5282' }, xanchor: 'right' }
    ]
  };

  Plotly.newPlot('kanpur-lst-chart-timeseries', traces, layout, CONFIG);
}
