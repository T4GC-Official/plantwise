import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import * as turf from '@turf/turf';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

export default function DiffMap({ point, onSelect }) {
  const container = useRef(null), map = useRef(null), marker = useRef(null), select = useRef(onSelect);
  const [error, setError] = useState('');
  select.current = onSelect;
  useEffect(() => {
    const controller = new AbortController();
    const instance = L.map(container.current, { center: [12.189703804004086, 75.94048174979808], zoom: 7 });
    map.current = instance;
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(instance);
    fetch('/wgg.geojsonl.json', { signal: controller.signal }).then(r => { if (!r.ok) throw new Error('Boundary unavailable'); return r.text(); }).then(text => {
      const features = text.split('\n').filter(line => line.trim()).map(JSON.parse).filter(f => f.geometry);
      L.geoJSON(features, { style: { color: '#176a58', weight: 2, fillColor: '#42a68b', fillOpacity: .13 } }).addTo(instance);
      instance.on('click', e => {
        if (features.some(f => turf.booleanPointInPolygon(turf.point([e.latlng.lng, e.latlng.lat]), f))) {
          setError(''); select.current({ latitude: e.latlng.lat, longitude: e.latlng.lng });
        } else setError('Choose a point inside the highlighted Western Ghats area.');
      });
    }).catch(e => { if (e.name !== 'AbortError') setError('The boundary could not load. You can still enter coordinates below.'); });
    return () => { controller.abort(); instance.remove(); map.current = null; marker.current = null; };
  }, []);
  useEffect(() => {
    if (!map.current || !point) return;
    const position = [point.latitude, point.longitude];
    if (marker.current) marker.current.setLatLng(position);
    else marker.current = L.marker(position, { icon: L.icon({ iconUrl: markerIcon, shadowUrl: markerShadow, iconSize: [25, 41], iconAnchor: [12, 41], shadowSize: [41, 41] }) }).addTo(map.current);
    if (!map.current.getBounds().contains(position)) map.current.panTo(position);
  }, [point]);
  return <div className="diff-map-wrap"><div ref={container} className="diff-map" aria-label="Choose a comparison location" />{error && <div className="diff-map-error" role="alert">{error}</div>}</div>;
}
