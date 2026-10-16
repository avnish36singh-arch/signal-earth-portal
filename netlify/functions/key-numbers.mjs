/**
 * Netlify Serverless Function: /api/key-numbers
 * Delivers verified planetary telemetry (Copernicus, NOAA, NSIDC, NASA)
 * Caches responses with a 1-hour TTL and provides CORS headers.
 */

const KEY_NUMBERS_PAYLOAD = {
  status: "success",
  retrieved_on: "2026-10-16",
  source_initiative: "Signal Earth Planetary Telemetry",
  metrics: [
    {
      id: "global_temp_anomaly",
      title: "Global Temperature Anomaly",
      value: "+1.47°C",
      unit: "°C above pre-industrial",
      baseline: "1850–1900 reference period",
      subtext: "2025 full-year anomaly. September 2026 reached +1.63°C.",
      source: "Copernicus Climate Change Service (C3S) / ERA5",
      url: "https://climate.copernicus.eu",
      year: 2026
    },
    {
      id: "atmospheric_co2",
      title: "Atmospheric CO₂",
      value: "426.07 ppm",
      unit: "parts per million",
      baseline: "Pre-industrial ~280 ppm",
      subtext: "September 2026 monthly mean at Mauna Loa Observatory, Hawaii.",
      source: "NOAA Global Monitoring Laboratory (GML)",
      url: "https://gml.noaa.gov/ccgg/trends/data.html",
      year: 2026
    },
    {
      id: "arctic_sea_ice",
      title: "Arctic Sea Ice Minimum",
      value: "4.60M km²",
      unit: "million square kilometers",
      baseline: "1981–2010 median ~6.3M km²",
      subtext: "Annual minimum extent recorded September 12, 2026; tied 10th lowest on satellite record.",
      source: "National Snow and Ice Data Center (NSIDC)",
      url: "https://nsidc.org/arcticseaicenews/",
      year: 2026
    },
    {
      id: "sea_level_rise_rate",
      title: "Global Sea Level Rise Rate",
      value: "+4.5 mm/yr",
      unit: "millimeters per year",
      baseline: "Satellite altimetry era (1993–present)",
      subtext: "Rate has doubled from 2.1 mm/yr in 1993; +103 mm cumulative rise.",
      source: "NASA Sea Level Change Portal",
      url: "https://climate.nasa.gov/vital-signs/sea-level/",
      year: 2026
    }
  ]
};

// Netlify v2 functions export
export default async function (request, context) {
  const headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Cache-Control": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"
  };

  if (request && request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers });
  }

  return new Response(JSON.stringify(KEY_NUMBERS_PAYLOAD, null, 2), {
    status: 200,
    headers
  });
}

// Fallback compatibility for Netlify Functions v1 handler syntax
export async function handler(event, context) {
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"
    },
    body: JSON.stringify(KEY_NUMBERS_PAYLOAD, null, 2)
  };
}
