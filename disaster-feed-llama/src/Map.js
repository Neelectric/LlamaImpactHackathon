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
import Sidebar from './components/Sidebar';

const MapCompopnent = () => {
    const mapRef = useRef(null);
    const [selectedLocation, setSelectedLocation] = useState(null);
    const [showSidebar, setShowSidebar] = useState(false);

    useEffect(() => {
        // Sample Data: 7 Locations with varying heat intensity
        const locations = [
            { lon: -0.1276, lat: 51.5074, intensity: 0.5, name: 'London', tweetId: '1683920951807971329' },
            { lon: -74.006, lat: 40.7128, intensity: 0.8, name: 'New York', tweetId: '1683920951807971329' },
            { lon: 139.6917, lat: 35.6895, intensity: 0.6, name: 'Tokyo', tweetId: '1683920951807971329' },
            { lon: 151.2093, lat: -33.8688, intensity: 0.7, name: 'Sydney', tweetId: '1683920951807971329' },
            { lon: 2.3522, lat: 48.8566, intensity: 0.4, name: 'Paris', tweetId: '1683920951807971329' },
            { lon: 12.4964, lat: 41.9028, intensity: 0.9, name: 'Rome', tweetId: '1683920951807971329' },
            { lon: 103.8198, lat: 1.3521, intensity: 0.3, name: 'Singapore', tweetId: '1683920951807971329' },
        ];

        // Create features with intensities
        const features = locations.map((loc) => {
            const feature = new Feature({
                geometry: new Point(fromLonLat([loc.lon, loc.lat])), // Convert to map projection
                weight: loc.intensity, // Set intensity
                properties: loc,
            });
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

        // Initialize the OpenLayers map
        const map = new Map({
            target: mapRef.current,
            layers: [
                new TileLayer({
                    source: new XYZ({
                        url: 'https://{1-4}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                    }), // Base map layer
                }),
                heatmapLayer, // Heatmap layer
            ],
            view: new View({
                center: fromLonLat([0, 0]), // Default map center
                zoom: 2, // Default zoom level
            }),
        });

        // Add click interaction
        map.on('click', (event) => {
            const feature = map.forEachFeatureAtPixel(event.pixel, (feature) => feature);

            if (feature) {
                const properties = feature.get('properties');
                setSelectedLocation(properties);
                setShowSidebar(true);
            } else {
                setShowSidebar(false);
                setSelectedLocation(null);
            }
        });

        return () => map.setTarget(null); // Clean up the map on unmount
    }, []);

    const handleCloseSidebar = () => {
        setShowSidebar(false);
        setSelectedLocation(null);
    }

    return (
        <div className="relative h-screen w-full">
            <Sidebar
                location={selectedLocation}
                isOpen={showSidebar}
                onClose={handleCloseSidebar}
            />
            <div
                ref={mapRef}
                style={{ width: '100%', height: '100vh' }} // Full-page map
                className={`w-full h-full transition-all duration-300 ${
                    showSidebar ? 'ml-96' : 'ml-0'
                }`}
            />
        </div>
    );
};

export default MapCompopnent;