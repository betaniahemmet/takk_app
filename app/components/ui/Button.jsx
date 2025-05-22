// button.jsx
import React from 'react';

// A simple reusable button component with props for flexibility
export const Button = ({ label, onClick, type = 'button', className = '' }) => {
    return (
        <button
            type={type}
            onClick={onClick}
            className={`px-4 py-2 bg-blue-500 text-white rounded ${className}`}
        >
            {label}
        </button>
    );
};

export default Button;
