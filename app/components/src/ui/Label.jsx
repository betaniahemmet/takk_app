import React from 'react';

const Label = ({ htmlFor, children }) => {
  return (
    <label
      htmlFor={htmlFor}
      className="block font-medium mb-1 text-gray-800 dark:text-gray-200"
    >
      {children}
    </label>
  );
};

export default Label;
