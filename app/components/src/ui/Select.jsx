import React from 'react';

const Select = ({ name, value, onChange, children, disabled = false }) => {
  return (
    <select
      name={name}
      value={value}
      onChange={onChange}
      disabled={disabled}
      className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring focus:ring-blue-500"
    >
      {children}
    </select>
  );
};

export default Select;
