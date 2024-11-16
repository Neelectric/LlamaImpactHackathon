'use client';

import React from 'react';
import './Sidebar.css'; // We'll style the sidebar here
import { Tweet } from 'react-tweet';
import LineGraph from './Graph'; // Import the LineGraph component

const Sidebar = ({ isOpen, onClose, tweets }) => {
  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <button className="close-btn" onClick={onClose}>
        &times;
      </button>
      <div className="content">
        <LineGraph />
        {tweets && tweets.length > 0 ? (
          tweets.map((tweetId) => (
            <div key={tweetId} style={{ marginBottom: '20px' }}>
              <Tweet id={tweetId} />
            </div>
          ))
        ) : (
          <p>No tweets available.</p>
        )}
      </div>
    </div>
  );
};

export default Sidebar;