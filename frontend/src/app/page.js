"use client";

import React, { useEffect, useState } from 'react';
import MapComponent from './components/Map';

const Home = () => {
  const [tweets, setTweets] = useState([]);
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
          const newTweetId = data.id
          console.log('Received tweet:', newTweetId);
          setTweets((prevTweets) => [newTweetId, ...prevTweets]);
          // console.log('Received tweet:', {
          //   id: data.id,
          //   content: data.content,
          //   imagePath: data.image_path,
          //   timestamp: data.timestamp
          // });
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

  return <MapComponent tweets={tweets} />
};

export default Home;