import React from 'react';

const PageWrapperMobile = ({ children }) => {
  return (
    <div className="relative min-h-screen bg-gray-100 dark:bg-gray-900 px-4 py-6 flex justify-center items-center overflow-hidden">
      {/* Subtle background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-white to-gray-200 dark:from-gray-900 dark:to-gray-700 opacity-40 z-0" />

      {/* Blurred logo watermark */}
      <img
        src="/webblogo.png"
        alt="Logo background"
        className="absolute top-2/3 left-0 right-0 bottom-0 m-auto w-[90%] opacity-50 blur-sm pointer-events-none select-none z-0"
      />

      {/* Main content area */}
      <div className="relative z-10 w-full max-w-xl">
        {children}
      </div>
    </div>
  );
};

export default PageWrapperMobile;
