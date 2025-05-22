import React from 'react';
import Label from './Label';

const Slider = ({ name, value, onChange, min = 1, max = 10, minLabel, maxLabel, focus }) => (
  <div className="mb-6">
    <Label htmlFor={name} className="text-lg font-medium mb-2">
      {focus}: {value}
    </Label>
    <input
      id={name}
      type="range"
      name={name}
      min={min}
      max={max}
      value={value}
      onChange={onChange}
      className="w-full h-2 bg-gray-300 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer focus:outline-none accent-blue-600"
    />
    <div className="flex justify-between text-lg text-gray-600 dark:text-gray-300 mt-2">
      <span>{minLabel}</span>
      <span>{maxLabel}</span>
    </div>
  </div>
);

export default Slider;
