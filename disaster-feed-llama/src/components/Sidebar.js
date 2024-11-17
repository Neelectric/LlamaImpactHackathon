import React from 'react';
import { Tweet } from 'react-tweet';
import { X } from 'lucide-react';

const Sidebar = ({ location, isOpen, onClose }) => {
  return (
    <div 
      className={`fixed left-0 h-full w-96 bg-white shadow-lg z-10 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div className="p-4 h-full overflow-y-auto">
        <div className="flex justify-between items-center mb-4 sticky top-0 bg-white z-20 pb-2 border-b">
          <h2 className="text-xl font-bold">{location?.name}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors duration-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        {location && (
          <div>
            {/* <Tweet id={location.tweetId} /> */}
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">
                Coordinates: {location.lat.toFixed(4)}°N, {location.lon.toFixed(4)}°E
              </p>
              <p className="text-sm text-gray-600">
                Heat Intensity: {(location.intensity * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;