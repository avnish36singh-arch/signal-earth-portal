/* ==========================================================================
   SIGNAL EARTH : DELHI ANALYSIS CONTROLLER
   Archived CPCB Daily Data at Alipur (2017 to 2023)
   Shows documented 732-day gap (2019 to 2020) without artificial interpolation
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

fetch('../data/delhi_daily_gapfixed.json')
  .then(function(r) { return r.json(); })
  .then(function(data) {
    renderDelhiTimeseries(data);
  })
  .catch(function(err) { console.error('Delhi data error:', err); });

function renderDelhiTimeseries(data) {
  var dates = data.map(function(d) { return d.date; });
  var aqiVals = data.map(function(d) { return d.aqi; });

  // 7-day rolling average strictly ignoring gaps
  var rolling7 = aqiVals.map(function(val, idx) {
    if (val === null) return null;
    var windowVals = [];
    for (var k = Math.max(0, idx - 6); k <= idx; k++) {
      if (aqiVals[k] !== null) windowVals.push(aqiVals[k]);
    }
    return windowVals.length >= 4 
      ? +(windowVals.reduce(function(a, b) { return a + b; }, 0) / windowVals.length).toFixed(1) 
      : null;
  });

  var traces = [
    {
      x: dates,
      y: aqiVals,
      mode: 'markers',
      type: 'scatter',
      name: 'Daily Calculated CPCB AQI',
      marker: { color: '#94A3B8', size: 3.5 },
      connectgaps: false
    },
    {
      x: dates,
      y: rolling7,
      mode: 'lines',
      name: '7-Day Rolling Mean',
      line: { color: '#2C5282', width: 2 },
      connectgaps: false
    }
  ];

  var layout = {
    ...LIGHT_LAYOUT,
    yaxis: {
      ...LIGHT_LAYOUT.yaxis,
      title: { text: 'Air Quality Index (AQI)', font: { size: 12, color: '#374151' } },
      range: [0, 520]
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
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 50, y1: 50, line: { color: '#16A34A', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 100, y1: 100, line: { color: '#65A30D', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 200, y1: 200, line: { color: '#D97706', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 300, y1: 300, line: { color: '#EA580C', width: 1, dash: 'dot' } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 400, y1: 400, line: { color: '#DC2626', width: 1, dash: 'dash' } }
    ],
    annotations: [
      { xref: 'paper', yref: 'y', x: 0.99, y: 415, text: 'Severe (401 to 500)', showarrow: false, font: { size: 9, color: '#DC2626' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 315, text: 'Very Poor (301 to 400)', showarrow: false, font: { size: 9, color: '#EA580C' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 215, text: 'Poor (201 to 300)', showarrow: false, font: { size: 9, color: '#D97706' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 115, text: 'Moderate (101 to 200)', showarrow: false, font: { size: 9, color: '#65A30D' }, xanchor: 'right' },
      { xref: 'paper', yref: 'y', x: 0.99, y: 60, text: 'Satisfactory (51 to 100)', showarrow: false, font: { size: 9, color: '#16A34A' }, xanchor: 'right' },
      {
        x: '2020-01-01',
        y: 200,
        xref: 'x',
        yref: 'y',
        text: '2019 to 2020 Monitoring Pause (732 Days Unrecorded)',
        showarrow: false,
        font: { size: 10, color: '#4B5563' },
        bgcolor: '#F3F4F0',
        bordercolor: '#CBD5E1'
      }
    ]
  };

  Plotly.newPlot('delhi-chart-timeseries', traces, layout, CONFIG);
}

// Fetch master cleaned dataset to render Indicative Source Signature diagnostic
fetch('../data/cleaned.json')
  .then(function(r) { return r.json(); })
  .then(function(records) {
    renderSourceBreakdown(records);
  })
  .catch(function(err) { console.error('Sources data error:', err); });

function renderSourceBreakdown(records) {
  var counts = {};
  records.forEach(function(r) {
    var reg = r.Source_Regime;
    if (reg && reg !== 'Unclassified') {
      counts[reg] = (counts[reg] || 0) + 1;
    }
  });

  var labels = Object.keys(counts);
  var values = Object.values(counts);

  // Muted colors with zero purple/violet/indigo
  var colors = {
    'Industrial Solvent Emissions': '#1E293B',
    'Fugitive & Crustal Dust': '#D97706',
    'Biomass & Stubble Smog': '#DC2626',
    'Vehicular & Urban Mixed': '#2C5282',
    'Regional Background': '#1E4E38'
  };

  var pieColors = labels.map(function(l) { return colors[l] || '#64748B'; });

  var trace = [{
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
      line: { color: '#FFFFFF', width: 1.5 }
    }
  }];

  var layout = {
    ...LIGHT_LAYOUT,
    margin: { t: 20, r: 20, b: 30, l: 20 },
    showlegend: true,
    legend: {
      orientation: 'h',
      y: -0.15,
      x: 0,
      font: { size: 11, color: '#374151' }
    },
    hoverlabel: {
      bgcolor: '#FFFFFF',
      bordercolor: '#CBD5E1',
      font: { family: 'sans-serif', color: '#111827', size: 12 }
    }
  };

  Plotly.newPlot('delhi-chart-sources', trace, layout, CONFIG);
}
