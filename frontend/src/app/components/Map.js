'use client';

import React, { useEffect, useRef, useState } from 'react';
import 'ol/ol.css';
import Map from 'ol/Map';
import View from 'ol/View';
import TileLayer from 'ol/layer/Tile';
import XYZ from 'ol/source/XYZ';
import { fromLonLat } from 'ol/proj';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import VectorLayer from 'ol/layer/Vector';
import HeatmapLayer from 'ol/layer/Heatmap';
import VectorSource from 'ol/source/Vector';
import SideBar from './Sidebar'; // Import the SideBar component
import { set } from 'ol/transform';

const MapComponent = ({ tweets, judgements }) => {
  const mapRef = useRef();
  const mapInstanceRef = useRef(null);
  const heatmapLayerRef = useRef(null);
  const [isSideBarOpen, setIsSideBarOpen] = useState(false);
  const [selectedJudgements, setSelectedJudgements] = useState(judgements);
  const [selectedTweets, setSelectedTweets] = useState(tweets);
  const [selectedLocation, setSelectedLocation] = useState(null);

  useEffect(() => {
    // Initialize map if it hasn't been created yet
    if (!mapInstanceRef.current) {
      // Create vector source and layer for points
      const vectorSource = new VectorSource();
      const heatmapLayer = new HeatmapLayer({
        source: vectorSource,
        blur: 15,
        radius: 5,
      });
      heatmapLayerRef.current = heatmapLayer;

      // Create map instance
      const map = new Map({
        target: mapRef.current,
        layers: [
          new TileLayer({
            source: new XYZ({
              url: 'https://{1-4}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            })
          }),
          heatmapLayer
        ],
        view: new View({
          center: fromLonLat([0, 0]),
          zoom: 2
        })
      });

      // Add click interaction
      map.on('click', (event) => {
        // Get all features at the clicked pixel
        const clickedFeatures = map.getFeaturesAtPixel(event.pixel, {
          hitTolerance: 5,  // Make it slightly easier to click points
          layerFilter: (layer) => layer === heatmapLayer
        });

        console.log(clickedFeatures);

        if (clickedFeatures && clickedFeatures.length > 0) {
          // Extract the location name from the clicked feature
          const locationName = clickedFeatures[0].get('location');
          setSelectedLocation(locationName);
          setIsSideBarOpen(true);
        }
        else {
          setIsSideBarOpen(false);
        }
      });
      mapInstanceRef.current = map;
    }

    // Update points on the map
    if (heatmapLayerRef.current && tweets) {
      const vectorSource = heatmapLayerRef.current.getSource();

      // Clear existing features
      vectorSource.clear();

      // Add new features for each point
      const features = tweets.map(point => {
        return new Feature({
          geometry: new Point(fromLonLat(point.location)), // Convert to map projection
          // Add any additional properties you want to store with the feature
          weight: point.final_judgement_out_of_10 / 10,
          location: point.location_name,
        });
      });

      const selectedTweets = tweets.filter(tweet => tweet.location_name === selectedLocation);
      console.log(selectedTweets);
      setSelectedTweets(selectedTweets);

      vectorSource.addFeatures(features);
    }
  }, [tweets]); // Re-run effect when points array changes

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.setTarget(null);
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <>
      <div
        ref={mapRef}
        style={{
          width: '100vw',
          height: '100vh',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
      />
      <SideBar isOpen={isSideBarOpen} tweets={selectedTweets} judgements={judgements}/>
    </>
  );
};

export default MapComponent;