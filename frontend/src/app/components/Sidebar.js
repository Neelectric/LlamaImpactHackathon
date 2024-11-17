'use client';

import React from 'react';
import './Sidebar.css'; // We'll style the sidebar here
import { Tweet } from 'react-tweet';
import LineGraph from './Graph'; // Import the LineGraph component

const Sidebar = ({ isOpen, tweets }) => {
    console.log(tweets);
    return (
        <div className={`sidebar ${isOpen ? 'open' : ''}`}>
            <div className="content">
                <div className="sticky-graph">
                    <LineGraph />
                </div>
                {/* {tweets && tweets.length > 0 ? (
                    tweets.map((tweetId) => (
                        <div key={tweetId.id}>
                            <Tweet id={tweetId.id} />
                        </div>
                    ))
                ) : (
                    <p>No tweets available.</p>
                )} */}
                <div>
                    <Tweet id={tweets[0]} />
                </div>
            </div>
        </div>
    );
};

export default Sidebar;