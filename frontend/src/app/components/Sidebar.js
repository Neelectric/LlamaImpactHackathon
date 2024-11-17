'use client';

import React from 'react';
import './Sidebar.css'; // We'll style the sidebar here
import { Tweet } from 'react-tweet';
import LineGraph from './Graph'; // Import the LineGraph component

const Sidebar = ({ isOpen, tweets, judgements}) => {
    return (
        <div className={`sidebar ${isOpen ? 'open' : ''}`}>
            <div className="content">
                <div className="sticky-graph">
                    <LineGraph judgements={judgements}/>
                    <LineGraph judgements={judgements}/>
                </div>
                {tweets && tweets.length > 0 ? (
                    tweets.map((tweetId) => (
                        <div key={tweetId.id}>
                            <Tweet id={tweetId.id} />
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