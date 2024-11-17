import React from 'react';

const Popup = ({ content, isVisible }) => {
  return (
    <div
      style={{
        position: 'absolute',
        background: 'white',
        padding: '5px 10px',
        border: '1px solid black',
        borderRadius: '5px',
        display: isVisible ? 'block' : 'none',
        pointerEvents: 'none',
      }}
    >
      {content}
    </div>
  );
};

export default Popup;
