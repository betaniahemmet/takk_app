import './src/index.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import AdminPage from './AdminPage';
import TrackingLog from './TrackingLog';
import useDarkMode from './Shared/useDarkMode';

const AppLayout = () => {
  useDarkMode(); // 🌓 Automatically apply system dark mode

  return (
    <Routes>
      <Route path="/admin" element={<AdminPage />} />
      <Route path="/log" element={<TrackingLog />} />
      <Route path="*" element={<div className="p-4 text-center text-red-500 dark:text-red-300">404 - Not Found</div>} />
    </Routes>
  );
};

const root = ReactDOM.createRoot(document.getElementById('app'));

root.render(
  <BrowserRouter>
    <AppLayout />
  </BrowserRouter>
);

