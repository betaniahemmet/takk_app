import React, { useState } from 'react';
import { Button, Input, Select, Label, PageWrapperDesktop } from './ui';



const AdminPage = () => {
  
  const [trackingMode, setTrackingMode] = useState("scale"); // or "event"
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({
    focus: '',
    min_label: '',
    max_label: '',
    activities: ['', '', '', '', '', ''],
    initials: '',
    location: '',
    duration: '',
    admin_email: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;

    // Auto-uppercase initials
    if (name === 'initials') {
      setFormData((prev) => ({
        ...prev,
        initials: value.toUpperCase(),
      }));
      return;
    }

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleActivityChange = (index, value) => {
    const updated = [...formData.activities];
    updated[index] = value;
    setFormData((prev) => ({ ...prev, activities: updated }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSuccessMessage('');
    setErrorMessage('');

    // Required field validation
    if (!formData.focus.trim()) {
      setErrorMessage("Fältet 'Vad mäts' måste fyllas i.");
      return;
    }

    if (trackingMode === 'scale' && (!formData.min_label.trim() || !formData.max_label.trim())) {
      setErrorMessage("Min och max etikett måste fyllas i.");
      return;
    }

    if (!formData.initials.trim()) {
      setErrorMessage("Initialer måste anges.");
      return;
    }

    if (!formData.location) {
      setErrorMessage("Du måste välja en verksamhet.");
      return;
    }

    if (!formData.duration) {
      setErrorMessage("Du måste välja en tidsperiod.");
      return;
    }

    if (!formData.admin_email.trim()) {
      setErrorMessage("En e-postadress måste anges.");
      return;
    }

    const normalizedEmail = formData.admin_email.toLowerCase();
    if (!normalizedEmail.endsWith("@betaniahemmet.se")) {
      setErrorMessage("E-postadressen måste sluta med @betaniahemmet.se.");
      return;
    }
    setFormData((prev) => ({
      ...prev,
      admin_email: normalizedEmail,
    }));

    const form = new FormData();
    Object.entries(formData).forEach(([key, val]) => {
      if (key === 'activities') {
        formData.activities.forEach((act, i) => {
          form.append(`activity_${i + 1}`, act);
        });
      } else {
        form.append(key, val);
      }
    });

    form.append("tracking_mode", trackingMode);

    for (let pair of form.entries()) {
      console.log(`${pair[0]}: ${pair[1]}`);
    }

    try {
      const res = await fetch('/admin', {
        method: 'POST',
        body: form,
      });
    
    if (!res.ok) {
      const errorText = await res.text();
      if (errorText.includes("finns redan")) {
        setErrorMessage("En kartläggning för dessa initialer och platsen finns redan.");
      } else {
        setErrorMessage("Serverfel – kunde inte skapa QR-kod.");
      }
      return;
    }


      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${formData.initials}_${formData.location}_QR.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();

      setSuccessMessage('QR-koden har skapats och laddats ner.');
      setFormData({
      focus: '',
      min_label: '',
      max_label: '',
      activities: ['', '', '', '', '', ''],
      initials: '',
      location: '',
      duration: '',
      admin_email: '',
      });
    } catch (error) {
      console.error('❌ Error:', error);
      setErrorMessage('Något gick fel. Kontrollera fälten och försök igen.');
    }
  };

  useEffect(() => {
    if (formData.initials && formData.location) {
      fetch(`/list-previous-sessions?initials=${formData.initials}&location=${formData.location}`)
        .then(res => res.json())
        .then(data => setPreviousSessions(data));
    } else {
      setPreviousSessions([]); // Clear if initials/location are cleared
    }
  }, [formData.initials, formData.location]);

  const handleLoadPrevious = async (trackingId) => {
    const res = await fetch(`/load-previous-session?tracking_id=${trackingId}`);
    const data = await res.json();

    if (data) {
      setFormData((prev) => ({
        ...prev,
        focus: data.focus || '',
        min_label: data.min_label || '',
        max_label: data.max_label || '',
        activities: data.activities || ['', '', '', '', '', ''],
      }));
      setTrackingMode(data.tracking_mode || 'scale');
      setSuccessMessage("Fälten är ifyllda från tidigare mätning.");
    }
  };


  return (
    <PageWrapperDesktop>
      <form onSubmit={handleSubmit} className="bg-white/90 dark:bg-gray-800/80 w-full max-w-5xl mx-auto shadow-md rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-200 mb-6">Skapa QR för kartläggning</h1>
        {/* Toggle for Scale / Event */}
        <div className="mb-6">
          {trackingMode === 'scale' ? (
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">
              Skala: Loggar ett värde mellan 1–10
            </p>
          ) : (
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">
              Händelse: Loggar om något har inträffat
            </p>
          )}
          
          <div
            className="inline-flex items-center cursor-pointer bg-gray-200 dark:bg-gray-700 rounded-full p-1 w-56 transition-all hover:ring-2 hover:ring-blue-400 dark:hover:ring-blue-500"
            onClick={() => setTrackingMode(trackingMode === 'scale' ? 'event' : 'scale')}
          >
            <div
              className={`w-1/2 text-center py-1 rounded-full transition-all ${
                trackingMode === 'scale'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-800 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'
              }`}
            >
              Skala
            </div>
            <div
              className={`w-1/2 text-center py-1 rounded-full transition-all ${
                trackingMode === 'event'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-800 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'
              }`}
            >
              Händelse
            </div>
          </div>
        </div>

        {/* Initials + Location */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <Label htmlFor="initials">Initialer:</Label>
            <Input
              type="text"
              name="initials"
              maxLength={2}
              value={formData.initials}
              onChange={handleChange}
              placeholder="Ex: AB"
            />
          </div>
          <div>
            <Label htmlFor="location">Verksamhet:</Label>
            <Select
              name="location"
              value={formData.location}
              onChange={handleChange}
            >
              <option value="">Välj plats</option>
              <option value="Verkstan">Verkstan</option>
              <option value="Kusten">Kusten</option>
              <option value="Konferensen">Konferensen</option>
            </Select>
          </div>
        </div>

        {/* Dropdown for previous sessions */}
        {previousSessions.length > 0 && (
          <div className="mb-6">
            <Label htmlFor="previous_session">Tidigare Mätningar:</Label>
            <Select
              name="previous_session"
              onChange={(e) => {
                if (e.target.value) {
                  handleLoadPrevious(e.target.value);
                }
              }}
            >
              <option value="">Välj en tidigare mätning</option>
              {previousSessions.map((s) => (
                <option key={s.tracking_id} value={s.tracking_id}>
                  {s.created_at} – {s.focus}
                </option>
              ))}
            </Select>
          </div>
        )}

        {/* Focus + Duration */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <Label htmlFor="focus">Vad ska mätas?</Label>
            <Input
              type="text"
              name="focus"
              value={formData.focus}
              onChange={handleChange}
              placeholder="Ex: Energinivå"
            />
          </div>
          <div>
            <Label htmlFor="duration">Mätperiod:</Label>
            <Select
              name="duration"
              value={formData.duration}
              onChange={handleChange}
            >
              <option value="">Välj period</option>
              <option value="week">En vecka</option>
              <option value="month">En månad</option>
            </Select>
          </div>
        </div>

        {/* Min/Max Labels */}
        {trackingMode === 'scale' && (
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <Label htmlFor="min_label">Minsta-Läge:</Label>
              <Input
                type="text"
                name="min_label"
                value={formData.min_label}
                onChange={handleChange}
                placeholder="Ex: Trött"
              />
            </div>
            <div>
              <Label htmlFor="max_label">Mesta-Läge:</Label>
              <Input
                type="text"
                name="max_label"
                value={formData.max_label}
                onChange={handleChange}
                placeholder="Ex: Pigg"
              />
            </div>
          </div>
        )}

        {/* Activities */}
        <div className="mb-6">
          <Label>Aktiviteter (Max 6st):</Label>
          <div className="grid grid-cols-2 gap-2">
            {formData.activities.map((act, i) => (
              <Input
                key={i}
                type="text"
                value={act}
                onChange={(e) => handleActivityChange(i, e.target.value)}
              />
            ))}
          </div>
        </div>

        {/* Email */}
        <div className="mb-6">
          <Label htmlFor="admin_email">E-postadress:</Label>
          <Input
            type="email"
            name="admin_email"
            value={formData.admin_email}
            onChange={handleChange}
            placeholder="Din jobbmail"
          />
        </div>

        {/* Messages */}
        {successMessage && <p className="mt-4 text-green-600 dark:text-green-200">{successMessage}</p>}
        {errorMessage && <p className="mt-4 text-red-600 dark:text-red-200">{errorMessage}</p>}

        {/* Submit Button */}
        <Button label="Generera QR-kod" type="submit" />
      </form>
      
    </PageWrapperDesktop>
  );
};

export default AdminPage;
