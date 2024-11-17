"use client";

import React, { useEffect } from 'react';
import MapComponent from './components/Map';

const Home = () => {
  console.log("hello world");
  useEffect(() => {
    console.log("we are in useeffect!");
    // Create WebSocket connection
    const wsUrl = 'http://127.0.0.1:5001/ws';  // Changed from 3002 to 8000
    console.log("Attempting to connect to:", wsUrl);
    const socket = new WebSocket(wsUrl);

    // Connection opened
    socket.addEventListener('open', (event) => {
      console.log('Connected to WebSocket server');
      // Send initial option to start receiving tweet data
      socket.send(JSON.stringify({ option: 'tweet_feed' }));
    });

    // Listen for messages
    socket.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'tweet') {
          console.log('Received tweet:', {
            id: data.id,
            content: data.content,
            imagePath: data.image_path,
            timestamp: data.timestamp,
            chain_of_thought: data.chain_of_thought,
            final_judgement_out_of_10: data.final_judgement_out_of_10
          });
        } else if (data.status === 'option_set') {
          console.log('Option set:', data.option);
        }
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    });

    // Connection closed
    socket.addEventListener('close', (event) => {
      console.log('Disconnected from WebSocket server');
    });

    // Connection error
    socket.addEventListener('error', (event) => {
      console.error('WebSocket error:', event);
    });

    // Cleanup on component unmount
    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []); // Empty dependency array means this effect runs once on mount

  return <MapComponent />;
};

export default Home;