import React, { useEffect, useRef, useState } from 'react';
import 'ol/ol.css';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';
import HeatmapLayer from 'ol/layer/Heatmap';
import VectorSource from 'ol/source/Vector';
import { Feature } from 'ol';
import Point from 'ol/geom/Point';
import { fromLonLat } from 'ol/proj';
import Overlay from 'ol/Overlay';

const HeatmapComponent = () => {
    const mapRef = useRef(null);
    const popupRef = useRef(null);
    const [popupContent, setPopupContent] = useState('');

    useEffect(() => {
        // Sample Data: 7 Locations with varying heat intensity
        const locations = [
            { lon: -0.1276, lat: 51.5074, intensity: 0.5 }, // London
            { lon: -74.006, lat: 40.7128, intensity: 0.8 }, // New York
            { lon: 139.6917, lat: 35.6895, intensity: 0.6 }, // Tokyo
            { lon: 151.2093, lat: -33.8688, intensity: 0.7 }, // Sydney
            { lon: 2.3522, lat: 48.8566, intensity: 0.4 }, // Paris
            { lon: 12.4964, lat: 41.9028, intensity: 0.9 }, // Rome
            { lon: 103.8198, lat: 1.3521, intensity: 0.3 }, // Singapore
        ];

        // Create features with intensities
        const features = locations.map((loc) => {
            const feature = new Feature({
                geometry: new Point(fromLonLat([loc.lon, loc.lat])), // Convert to map projection
                weight: loc.intensity, // Set intensity
            });
            feature.setProperties({
                intensity: loc.intensity, // Set intensity
                location: `${loc.lat}, ${loc.lon}`, // Set location
            })
            return feature;
        });

        // Create a vector source and add features
        const vectorSource = new VectorSource({
            features: features,
        });

        // Create the heatmap layer
        const heatmapLayer = new HeatmapLayer({
            source: vectorSource,
            blur: 15, // Adjust blur size for heatmap effect
            radius: 15, // Adjust radius for points
        });

        const popup = new Overlay({
            element: popupRef.current,
            positioning: 'bottom-center',
            stopEvent: false,
            offset: [0, -15],
        })

        // Initialize the OpenLayers map
        const map = new Map({
            target: mapRef.current,
            layers: [
                new TileLayer({
                    source: new XYZ({
                        url: 'https://{1-4}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', // Base map source
                    }), // Base map layer
                }),
                heatmapLayer, // Heatmap layer
            ],
            overlays: [popup],
            view: new View({
                center: fromLonLat([0, 0]), // Default map center
                zoom: 2, // Default zoom level
            }),
        });

        map.on('click', (e) => {
            const feature = map.forEachFeatureAtPixel(e.pixel, (feature) => feature);
            if (feature) {
                const coordinates = feature.getGeometry().getCoordinates();
                popup.setPosition(coordinates);
                setPopupContent(`Intensity: ${feature.get('intensity')}<br>Location: ${feature.get('location')}`);
            } else {
                popup.setPosition(undefined);
            }
        });

        return () => map.setTarget(null); // Clean up the map on unmount
    }, []);

    return (
        <div
            ref={mapRef}
            style={{ width: '100%', height: '100vh' }} // Full-page map
        />
    );
};

export default HeatmapComponent;