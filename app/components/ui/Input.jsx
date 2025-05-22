import React from 'react';

const Input = ({ name, type = 'text', value, onChange, placeholder = '', disabled = false, maxLength }) => {
  return (
    <input
      type={type}
      name={name}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      maxLength={maxLength}
      className="w-full border border-gray-300 dark:border-gray-600 rounded px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring focus:ring-blue-500 transition duration-150 ease-in-out"
      autoComplete="off"
    />
  );
};

export default Input;
