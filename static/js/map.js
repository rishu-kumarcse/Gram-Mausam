/**
 * GramMausam Leaflet Map Controller.
 * Handles GeoJSON rendering, choropleth gradients, and polygon click interactions.
 */

let mapInstance = null;
let geojsonLayer = null;
let currentMetric = "rainfall_mm";

function initMap() {
  if (mapInstance) return;

  // Initialize centered on Maharashtra / Western Ghats (Pune/Satara region)
  mapInstance = L.map("map", {
    zoomControl: true,
    scrollWheelZoom: true
  }).setView([18.25, 74.35], 10);

  // Basemap tiles: Standard OpenStreetMap
  const osmStandard = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors | IMD-GKMS',
    maxZoom: 19
  }).addTo(mapInstance);

  const osmHOT = L.tileLayer("https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors, Tiles style by Humanitarian OpenStreetMap Team',
    maxZoom: 19
  });

  const baseMaps = {
    "OpenStreetMap (Standard)": osmStandard,
    "OpenStreetMap (Humanitarian/Terrain)": osmHOT
  };

  L.control.layers(baseMaps, null, { position: "topright" }).addTo(mapInstance);
}

function getMetricColor(val, metric) {
  if (metric === "rainfall_mm") {
    return val > 25.0 ? "#084594" :
           val > 15.0 ? "#2171b5" :
           val > 10.0 ? "#4292c6" :
           val > 5.0  ? "#6baed6" :
           val > 2.0  ? "#9ecae1" :
           val > 0.5  ? "#c6dbef" : "#f7fbff";
  } else if (metric === "tmax_c") {
    return val > 38.0 ? "#990000" :
           val > 35.0 ? "#d7301f" :
           val > 32.0 ? "#ef6548" :
           val > 29.0 ? "#fdbb84" :
           val > 26.0 ? "#fdd49e" : "#fef0d9";
  } else if (metric === "rh_max_pct") {
    return val > 90 ? "#014636" :
           val > 80 ? "#02818a" :
           val > 70 ? "#67a9cf" :
           val > 60 ? "#bdc9e1" : "#f1eef6";
  } else if (metric === "wind_speed_kmh") {
    return val > 25 ? "#b30000" :
           val > 18 ? "#e34a33" :
           val > 12 ? "#fdbb84" : "#fee8c8";
  }
  return "#3388ff";
}

function renderPanchayatsOnMap(panchayatsList, metric = "rainfall_mm") {
  initMap();
  currentMetric = metric;

  if (geojsonLayer) {
    mapInstance.removeLayer(geojsonLayer);
  }

  // Build GeoJSON FeatureCollection
  const features = panchayatsList.map(p => {
    const weather = p.downscaled_weather || {};
    return {
      type: "Feature",
      geometry: p.geometry || {
        type: "Point",
        coordinates: [p.centroid_lon, p.centroid_lat]
      },
      properties: {
        panchayat_id: p.panchayat_id,
        panchayat_name: p.panchayat_name,
        elevation_m: p.elevation_m,
        area_km2: p.area_km2,
        weather: weather,
        uncertainty: p.uncertainty || {},
        metric_value: weather[metric] !== undefined ? weather[metric] : 0.0
      }
    };
  });

  const geoData = {
    type: "FeatureCollection",
    features: features
  };

  geojsonLayer = L.geoJSON(geoData, {
    style: function (feature) {
      const val = feature.properties.metric_value;
      return {
        fillColor: getMetricColor(val, currentMetric),
        weight: 1.5,
        opacity: 0.9,
        color: "#ffffff",
        dashArray: "1",
        fillOpacity: 0.75
      };
    },
    onEachFeature: function (feature, layer) {
      const props = feature.properties;
      const w = props.weather || {};

      // Hover tooltip
      const tooltipContent = `
        <strong>${props.panchayat_name}</strong><br>
        Elev: ${Math.round(props.elevation_m)} m | Area: ${props.area_km2} km²<br>
        <strong>Rain:</strong> ${w.rainfall_mm !== undefined ? w.rainfall_mm + " mm" : "N/A"}<br>
        <strong>Tmax:</strong> ${w.tmax_c !== undefined ? w.tmax_c + "°C" : "N/A"} | 
        <strong>Wind:</strong> ${w.wind_speed_kmh !== undefined ? w.wind_speed_kmh + " km/h" : "N/A"}<br>
        <span style="font-size:0.75rem; color:#0288d1">Click to view full advisory</span>
      `;
      layer.bindTooltip(tooltipContent, { sticky: true, className: "custom-map-tooltip" });

      layer.on({
        mouseover: function (e) {
          const l = e.target;
          l.setStyle({
            weight: 3,
            color: "#ff9800",
            fillOpacity: 0.9
          });
          l.bringToFront();
        },
        mouseout: function (e) {
          geojsonLayer.resetStyle(e.target);
        },
        click: function () {
          if (window.selectPanchayatFromMap) {
            window.selectPanchayatFromMap(props);
          }
        }
      });
    }
  }).addTo(mapInstance);

  try {
    const bounds = geojsonLayer.getBounds();
    if (bounds.isValid()) {
      mapInstance.fitBounds(bounds, { padding: [20, 20] });
    }
  } catch (err) {
    console.warn("Bounds fit error:", err);
  }
}
