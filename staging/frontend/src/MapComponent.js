import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import * as turf from '@turf/turf';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
L.Marker.prototype.options.icon = L.icon({iconUrl:markerIcon,iconRetinaUrl:markerIcon2x,shadowUrl:markerShadow,iconSize:[25,41],iconAnchor:[12,41],shadowSize:[41,41]});

const MapComponent = ({ onMapClick }) => {
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const geoJsonLayerRef = useRef(null);
  const initializedRef = useRef(false);

  useEffect(() => {
    if (!initializedRef.current) { // Initialize only once
      const map = L.map('map', {
        center: [15.5, 75.5],
        zoom: 7,
        inertia: false
      });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
      }).addTo(map);

      // Load GeoJSON
      fetch('/wgg.geojsonl.json')
        .then(response => { if (!response.ok) throw new Error('Boundary unavailable'); return response.text(); })
        .then(text => {
          const features = text.split('\n')
            .filter(line => line.trim())
            .map(JSON.parse)
            .filter(feature => feature?.geometry);

//          if (features.length > 0) {
//            geoJsonLayerRef.current = L.geoJSON(features, {
//              style: {
//                color: 'blue',
//                weight: 2,
//                fillColor: 'blue',
//                fillOpacity: 0.5
//              }
//            }).addTo(map);
//          }

          // Convert to Turf-compatible FeatureCollection
          geoJsonLayerRef.current = {
            type: 'FeatureCollection',
            features: features
          };

          // Add to map
          L.geoJSON(geoJsonLayerRef.current, {
            style: {
              color: 'blue',
              weight: 2,
              fillColor: 'blue',
              fillOpacity: 0.5
            }
          }).addTo(map);

        }).catch(error => { console.error(error); document.getElementById('map').setAttribute('aria-label', 'WG boundary failed to load'); });

      mapRef.current = map;
      initializedRef.current = true;
    }

    const handleClick = (e) => {

//      if (!geoJsonLayerRef.current?.getBounds()?.contains(e.latlng)) return;


//      // Convert click point to Leaflet LatLng
//      const clickedPoint = e.latlng;
//      console.log('Clicked at:', clickedPoint);
//      let isInside = false;
//      geoJsonLayerRef.current.eachLayer(layer => {
//        if (layer instanceof L.Polygon) {
//          const polygonCoords = layer.getLatLngs()[0];
//          if (L.latLngBounds(polygonCoords).contains(clickedPoint)) {
//            isInside = true;
//          }
//        }
//      });


      if (!geoJsonLayerRef.current?.features?.length) return;
      // Create Turf point (GeoJSON uses [lng, lat])
      const clickedPoint = turf.point([e.latlng.lng, e.latlng.lat]);

      // Check against all features
      const isInside = geoJsonLayerRef.current.features.some(feature => {
        try {
          return turf.booleanPointInPolygon(clickedPoint, feature);
        } catch (error) {
          console.error('Error checking containment:', error);
          return false;
        }
      });

      console.log('Marker inside:', isInside);

      if (!isInside) {
          return;
      }

      // Update marker
      if (markerRef.current) {
        markerRef.current.setLatLng(e.latlng);
      } else {
        markerRef.current = L.marker(e.latlng).addTo(mapRef.current);
      }

      // Propagate coordinates
      onMapClick(e.latlng.lat, e.latlng.lng);
    };

    mapRef.current?.on('click', handleClick);

    return () => {
      mapRef.current?.off('click', handleClick);
    };
  }, [onMapClick]); // Only dependency is the memoized onMapClick

  return <div id="map" style={{ height: '100vh' }} />;
};

export default MapComponent;
