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
import VectorSource from 'ol/source/Vector';
import SideBar from './Sidebar'; // Import the SideBar component

const MapComponent = () => {
  const mapContainer = useRef(null);
  const [isSideBarOpen, setIsSideBarOpen] = useState(false);
  const [selectedTweets, setSelectedTweets] = useState([]);

  const points = [
    { coords: [25.2797, 54.6872], tweetIds: ['1857678637446955410'] },
    { coords: [-74.006, 40.7128], tweetIds: ['1857678637446955410', '1857667809712509218'] },
    { coords: [139.6917, 35.6895], tweetIds: ['1857678637446955410', '1857667809712509218', '1856970322370507183'] },
  ]

  useEffect(() => {
    const features = points.map((point) => {
      const feature = new Feature({
        geometry: new Point(fromLonLat(point.coords)),
      });
      feature.set('tweetIds', point.tweetIds);
      return feature;
    });

    const vectorSource = new VectorSource({
      features: features,
    });

    const heatmapLayer = new VectorLayer({
      source: vectorSource,
      blur: 15,
      radius: 15,
    });

    const map = new Map({
      target: mapContainer.current,
      layers: [
        new TileLayer({
          source: new XYZ({
            url: 'https://{1-4}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
          }),
        }),
        heatmapLayer,
      ],
      view: new View({
        center: [0, 0], // Coordinates in EPSG:3857 projection (use ol/proj for conversions)
        zoom: 2,
      }),
    });

    map.on('click', (event) => {
      const feature = map.forEachFeatureAtPixel(event.pixel, (feature) => feature);

      if (feature) {
        const tweetIds = feature.get('tweetIds');
        setSelectedTweets(tweetIds);
        setIsSideBarOpen(true);
      }
      else {
        setIsSideBarOpen(false);
      }
    });

    return () => {
      map.setTarget(null);
    };
  }, []);

  return (
    <>
      <div
        ref={mapContainer}
        style={{
          width: '100vw',
          height: '100vh',
          position: 'absolute',
          top: 0,
          left: 0,
        }}
      />
      <SideBar isOpen={isSideBarOpen} tweets={selectedTweets} />
    </>
  );
};

export default MapComponent;