import React, { useState, useEffect } from 'react';
import { Button, Label, Checkbox, Slider, PageWrapperMobile } from './ui';


const TrackingLog = () => {
  const queryParams = new URLSearchParams(window.location.search);
  const trackingId = queryParams.get('tracking_id');
  const initials = queryParams.get('initials');
  const location = queryParams.get('location');
  const [lastSubmitted, setLastSubmitted] = useState(null);


  const [focus, setFocus] = useState('Mood');
  const [trackingMode, setTrackingMode] = useState("scale");
  const [minLabel, setMinLabel] = useState('Not Anxious');
  const [maxLabel, setMaxLabel] = useState('Extremely Anxious');
  const [value, setValue] = useState(5);
  const [activities, setActivities] = useState([]);
  const [availableActivities, setAvailableActivities] = useState([]);

  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');


  useEffect(() => {
    fetch(`/get-admin-settings?tracking_id=${trackingId}`)
      .then((res) => res.json())
      .then((data) => {
        setFocus(data.focus);
        setMinLabel(data.min_label || 'Not Anxious');
        setMaxLabel(data.max_label || 'Extremely Anxious');
        setAvailableActivities(data.activities.filter((a) => a && a.trim() !== ''));
        setTrackingMode(data.tracking_mode || "scale");
      })
      .catch((err) => console.error('Error loading admin settings:', err));
  }, [trackingId]);

  const handleValueChange = (e) => {
    setValue(parseInt(e.target.value, 10));
  };

  const toggleActivity = (activity) => {
    setActivities((prev) =>
      prev.includes(activity)
        ? prev.filter((a) => a !== activity)
        : [...prev, activity]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setSuccessMessage('');
    setErrorMessage('');

    // Check if last submission was less than 60 seconds ago
    if (lastSubmitted && Date.now() - lastSubmitted < 60000) {
      setErrorMessage('Vänta minst en minut mellan loggningar.');
      return;
    }

    const logData = {
      tracking_id: trackingId,
      initials,
      location,
      focus: focus,
      activities,
      timestamp: new Date().toISOString(),
    };

    if (trackingMode === "scale") {
      logData.value = value;
    } else {
      logData.value = 1; // log event occurrence as +1
    }

    fetch('/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(logData),
    })
      .then((res) => {
      if (!res.ok) throw new Error('Servern returnerar ett fel');
      return res.json();
    })
      .then(() => {
      setSuccessMessage('Loggningen sparades.');
      setLastSubmitted(Date.now());
    })
    .catch(() => {
      setErrorMessage('Kunde inte kontakta servern');
    }); 
  };

  if (!trackingId || !initials || !location) {
    return (
       <PageWrapperMobile>
          <h1 className="text-2xl font-bold text-red-600 dark:text-red-400 mb-2">Invalid QR Link</h1>
          <p className="text-gray-700 dark:text-gray-300 text-sm">
            This link is missing tracking information. Please generate a new QR code.
          </p>
       </PageWrapperMobile> 
    );
  }

  return (
    <PageWrapperMobile>
      <form
        onSubmit={handleSubmit}
        className="relative z-10 w-full bg-white/80 dark:bg-gray-800/80 p-6 rounded-lg shadow-md text-lg"
      >
        <h1 className="text-xl text-black dark:text-gray-100 font-bold mb-4">Mätning av {focus}</h1>
        <p className="text-lg text-gray-700 dark:text-gray-200 mb-6">
          För <strong>{initials}</strong> at <strong>{location}</strong>
        </p>

        {trackingMode === 'scale' && (
          <Slider
            name="slider"
            value={value}
            onChange={handleValueChange}
            minLabel={minLabel}
            maxLabel={maxLabel}
            focus={focus}
          />
        )}


        {availableActivities.length > 0 && (
          <div className="mb-6">
            <Label className="text-lg font-medium mb-2">Aktivitet vid tillfället:</Label>
            <div className="grid grid-cols-1 gap-y-3">
              {availableActivities.map((activity) => (
                <Checkbox
                  key={activity}
                  label={activity}
                  checked={activities.includes(activity)}
                  onChange={() => toggleActivity(activity)}
                />
              ))}
            </div>
          </div>
        )}

        <div className="mt-6">
          {successMessage && <p className="mt-4 text-green-600 dark:text-green-200">{successMessage}</p>}
          {errorMessage && <p className="mt-4 text-red-600 dark:text-red-200">{errorMessage}</p>}

          <Button label="Spara" type="submit" />
        </div>
      </form>
    </PageWrapperMobile>
  );
  };

export default TrackingLog;

