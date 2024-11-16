"use client";

import { useState, useEffect } from 'react';

const DataViewer = () => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [data, setData] = useState(null);
  const [socket, setSocket] = useState(null);
  const [error, setError] = useState(null);
  const [tweets, setTweets] = useState([]);  // Store last few tweets


  useEffect(() => {
    // Create WebSocket connection with the correct backend port
    const ws = new WebSocket('ws://localhost:3001/ws');

    ws.onopen = () => {
      console.log('Connected to WebSocket');
      setSocket(ws);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const receivedData = JSON.parse(event.data);
        setData(receivedData);
        
        if (receivedData.type === 'tweet') {
          setTweets(prev => {
            const newTweets = [...prev, receivedData];
            // Keep only last 5 tweets
            return newTweets.slice(-5);
          });
        }
      } catch (e) {
        console.error('Error parsing WebSocket data:', e);
      }
    };

    ws.onclose = () => {
      console.log('Disconnected from WebSocket');
      setError('WebSocket connection closed');
    };

    ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('WebSocket error occurred');
    };

    // Clean up on component unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleOptionSelect = (option) => {
    setSelectedOption(option);
    if (socket) {
      socket.send(JSON.stringify({ option }));
    }
  };

  return (
    <div className="p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-4">Disaster Monitoring Dashboard</h2>
        
        <div className="space-x-4 mb-6">
          {/* Add tweet feed button */}
          <button
            onClick={() => handleOptionSelect('tweet_feed')}
            className={`px-4 py-2 rounded ${
              selectedOption === 'tweet_feed'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            Tweet Feed
          </button>
          <button
            onClick={() => handleOptionSelect('water_level')}
            className={`px-4 py-2 rounded ${
              selectedOption === 'water_level'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            Water Level
          </button>
          <button
            onClick={() => handleOptionSelect('emergency_alerts')}
            className={`px-4 py-2 rounded ${
              selectedOption === 'emergency_alerts'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            Emergency Alerts
          </button>
          <button
            onClick={() => handleOptionSelect('rescue_operations')}
            className={`px-4 py-2 rounded ${
              selectedOption === 'rescue_operations'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
          >
            Rescue Operations
          </button>
        </div>


        {/* Data display */}
        {/* Tweet feed display */}
        {selectedOption === 'tweet_feed' && (
          <div className="space-y-4">
            {tweets.map((tweet, index) => (
              <div key={tweet.id || index} className="border rounded-lg p-4 bg-white shadow">
                <div className="flex space-x-4">
                  {tweet.image_path && (
                    <img 
                      src={tweet.image_path} 
                      alt="Tweet image" 
                      className="w-32 h-32 object-cover rounded"
                    />
                  )}
                  <div className="flex-1">
                    <p className="text-gray-800">{tweet.content}</p>
                    <p className="text-sm text-gray-500 mt-2">
                      Tweet ID: {tweet.id}
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(tweet.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataViewer;