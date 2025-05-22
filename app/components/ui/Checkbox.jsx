import React from 'react';

const Checkbox = ({ label, checked, onChange }) => (
  <label className="inline-flex items-center">
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      className="mr-3 h-5 w-5"
    />
    <span className="text-lg text-gray-900 dark:text-gray-100">{label}</span>
  </label>
);

export default Checkbox;
