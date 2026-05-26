# TAKK - Tecken som Alternativ och Kompletterande Kommunikation

<p align="center">
  <img src="media/takklogocrop.png" alt="TAKK mobil" width="600">
</p>

<p align="center">
  <em>En mobilanpassad webbapplikation för att lära ut och träna svenskt teckenspråk som stöd (TAKK).<br>Utvecklad för intern användning inom Betaniahemmet.</em>
</p>

## 📖 Om TAKK

Betanias TAKK-app är en interaktiv lärplattform som hjälper användare att lära sig teckenspråk genom videobaserat material och interaktiva övningar. Appen innehåller över 80 tecken organiserade i progressiva nivåer.

### Funktioner

- **📚 Ordbok** - Bläddra genom alla tillgängliga tecken med videodemonstrationer
- **🎯 Träningsläge** - Öva på tecken i din egen takt med omedelbar feedback
- **📝 Quiz** - Testa dina kunskaper med flervalsfrågor
- **🏆 Tävlingsläge** - Utmana dig själv mot klockan och ta plats på leaderboarden
- **🌓 Mörkt läge** - Automatisk anpassning till systemets tema
- **📱 Mobilanpassad** - Responsiv design som fungerar på alla enheter

## 🛠️ Teknisk Stack

### Backend
- **Flask** - Python web framework
- **Gunicorn** - WSGI HTTP server för produktion
- **Redis** - Leaderboard och analytics-data

### Frontend
- **React** - UI framework
- **Vite** - Build tool och dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Tillgängliga UI-komponenter

### Deployment
- **Nginx** - Reverse proxy och SSL (Let's Encrypt, `takk.betaniahemmet.se`)
- **Systemd** - Service management
- **Ubuntu Server** - OS (VPS, Ubuntu 24.04)

## 🚀 Kom Igång

### Utvecklingsmiljö

#### Krav
- Python 3.10+
- Node.js 18+
- npm eller yarn

#### Installation

1. **Klona repot**
```bash
git clone https://github.com/betaniahemmet/takk_app.git
cd takk_app
```

2. **Sätt upp Python-miljö**
```bash
python3 -m venv venv
source venv/bin/activate  # På Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

3. **Installera frontend-dependencies**
```bash
cd app/components
npm install
cd ../..
```

4. **Starta utvecklingsservrar**

I en terminal (Flask):
```bash
python run.py
```

I en annan terminal (React):
```bash
cd app/components
npm run dev
```

Appen körs nu på:
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:5173`

### Produktion

För produktionsdeploy, se detaljerade instruktioner i:
- **[deployment/PRODUCTION_DEPLOY.md](deployment/PRODUCTION_DEPLOY.md)** - Komplett guide (nginx, SSL, Redis, fail2ban)

## 📁 Projektstruktur

```
takk_app/
├── app/                          # Flask-applikation
│   ├── __init__.py              # App factory
│   ├── routes.py                # API endpoints
│   ├── leaderboard.py           # Leaderboard-logik
│   └── components/              # React frontend
│       ├── src/                 # React källkod
│       ├── public/              # Statiska filer
│       └── dist/                # Byggd frontend (skapas vid build)
├── catalog/                     # Data
│   ├── manifest.json           # Tecken och nivåer (v3)
│   ├── distractors.json        # Distraktorer för quiz
│   └── mouth_coordinates.json  # Munpositioner för blur-overlay
├── media/                       # Media-filer
│   ├── signs/                  # Teckenvideoer + piktogram per tecken
│   ├── intro/                  # Introduktionsvideo + textning
│   └── ui/                     # UI-resurser (favicon, OG-bild)
├── tools/                       # Underhållsverktyg
│   ├── add_signs.py            # Guidad: lägg till tecken (för alla)
│   ├── remove_sign.py          # Guidad: ta bort tecken (för alla)
│   ├── audit_signs.py          # Rapport: vad saknas i media/signs/?
│   └── validate_catalog.py     # Validera manifest mot disk
├── video_processing/            # Videobearbetning (ffmpeg)
│   ├── process_sign.py         # Bearbeta enstaka tecken
│   ├── batch_silent.py         # Batch: tysta tecken
│   └── batch_regular.py        # Batch: vanliga tecken
├── incoming/                    # Staging för nya tecken (ej i git)
├── raw_clips/                   # Råa videofiler (ej i git)
├── requirements.txt             # Runtime-dependencies
├── requirements-dev.txt         # Dev/test-dependencies
├── deployment/                  # Produktionskonfiguration
└── run.py                       # Entry point
```

## 🎬 Videohantering

### Lägga till nya tecken (guidad)

För icke-tekniska användare — ett interaktivt skript som hjälper steg för steg:

1. Skapa en mapp i `incoming/` för varje nytt tecken (t.ex. `incoming/glad/`)
2. Lägg videofil(er) och piktogram i mappen enligt namnkonventionen:
   - Vanlig video: `glad.mov`
   - Tyst video: `glad_tyst.mov`
   - Piktogram: `glad.jpg` (eller `1_glad.jpg`, `2_ord.jpg` för sammansatta tecken)
3. Kör det guidade skriptet:
```bash
python tools/add_signs.py
```
Skriptet validerar, bearbetar video, uppdaterar manifest och påminner om att bygga om appen.

### Ta bort tecken

```bash
python tools/remove_sign.py
```

Visar en numrerad lista över alla tecken — välj vilka som ska tas bort.

### Lägga till tecken (developer)

För att bearbeta enstaka tecken direkt:
```bash
# Vanlig video + tyst video
python video_processing/process_sign.py glad --regular raw_clips/glad.mov --silent tysta_tecken/glad_tyst.mp4

# Bara tyst video
python video_processing/process_sign.py glad --silent tysta_tecken/glad_tyst.mp4
```

### Videokrav
- Format: `.mov` eller `.mp4`
- Rekommenderad upplösning: 1080p
- Processerade videor sparas i `media/signs/` (1080×1080, H.264)

### Kontrollera status

```bash
# Vad saknas? (piktogram, video, manifest-entry)
python tools/audit_signs.py

# Validera att alla sökvägar i manifestet finns på disk
python tools/validate_catalog.py
```

## 🔧 Konfiguration

### Miljövariabler

Skapa `.env`-fil baserad på `.env.example`:

```bash
# Development
FLASK_ENV=development
FLASK_DEBUG=1

# Production  
FLASK_ENV=production
FLASK_DEBUG=0
```

### Anpassa innehåll

- **Tecken och nivåer**: Redigera `catalog/manifest.json`
- **Distraktorer**: Redigera `catalog/distractors.json`
- **Styling**: Anpassa i `app/components/tailwind.config.js`

## 📊 API Endpoints

### Tecken och Nivåer
- `GET /api/levels` - Hämta alla nivåer
- `GET /api/levels/:id` - Hämta specifik nivå
- `GET /api/levels/:id/cumulative` - Nivå + kumulativa tecken
- `GET /api/signs` - Hämta alla tecken

### Leaderboard
- `GET /api/scores` - Topp 10 scores
- `POST /api/score` - Lägg till ny score

### Analytics
- `GET /analytics` - Analytics dashboard (lösenordsskyddad)

### Övrigt
- `GET /api/distractors` - Hämta distraktorer
- `POST /api/feedback` - Skicka feedback
- `GET /health` - Health check

## 🧪 Testning

```bash
# Kör alla tester
pytest

# Kör specifikt test
pytest tests/test_api.py

# Med coverage
pytest --cov=app tests/
```

## 📝 Utvecklingsworkflow

1. **Skapa feature branch**
```bash
git checkout -b feature/ny-funktion
```

2. **Gör ändringar och testa lokalt**
```bash
python run.py
cd app/components && npm run dev
```

3. **Bygg frontend för produktion**
```bash
cd app/components
npm run build
```

4. **Commit och push**
```bash
git add .
git commit -m "Lägg till ny funktion"
git push origin feature/ny-funktion
```

5. **Deploy till server**
```bash
# På servern
cd /opt/takk
sudo -u takk git pull
cd /opt/takk/app/components && sudo -u takk npm run build
sudo systemctl restart takk
```

## 🔒 Säkerhet

- Rate limiting på POST-endpoints (10 req/60s)
- Path traversal-skydd på mediaförfrågningar
- Input-validering på alla användardata
- CORS konfigurerad för lokal användning

## 🐛 Felsökning

### Backend
```bash
# Kolla Flask-loggar
tail -f /var/log/takk/error.log

# Kolla service status
sudo systemctl status takk

# Restart service
sudo systemctl restart takk
```

### Frontend
```bash
# Bygg om React-appen
cd app/components
npm run build

# Kolla build-fel
npm run build -- --debug
```

### Nginx
```bash
# Testa konfiguration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Kolla loggar
sudo tail -f /var/log/nginx/takk-error.log
```

## 📦 Byggprocess

### Produktion build
```bash
# Backend - ingen build behövs för Flask
# Frontend - bygg React-appen
cd app/components
npm run build

# Output: app/components/dist/
```

## 🤝 Bidra

Detta projekt är för intern användning, men förslag och förbättringar är välkomna!

1. Diskutera förslaget i ett issue
2. Forka repot
3. Skapa din feature branch
4. Commita dina ändringar
5. Pusha till branchen
6. Öppna en Pull Request

## 📄 Licens

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) för detaljer.

## 👥 Utvecklat för

**Betaniahemmet**  
En ideell förening som arbetar med stöd och boende för personer med funktionsnedsättning.

## 🙏 Tack till

- Alla som bidragit med teckenspråksvideoer
- Användarnas feedback och idéer
- Open source-communityn för de fantastiska verktygen

---

**Version:** 1.1.1  
**Status:** ✅ Produktionsklar  
**Senast uppdaterad:** Maj 2026