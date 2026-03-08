# TAKK Project Context for AI Assistants

## Project Overview

**TAKK** (Tecken som Alternativ och Kompletterande Kommunikation) is a Swedish sign language learning web application developed for Betaniahemmet, an organization supporting people with functional disabilities.

**Purpose:** Interactive platform for learning Swedish sign language through video-based instruction, training exercises, quizzes, and competitive gameplay.

**Users:** 80-150 users across 10-15 locations (verksamheter) within Betaniahemmet's network.

**Current Status:** v1.0.0 - Phase 1 (Beta Prep) complete. Ready for beta deployment on local HP Elite Mini server. Remaining: add Introduction video content, final testing, deploy.

### Language Conventions
- **User Interface:** Swedish (all text visible to users is in Swedish)
- **Code:** English (variable names, function names, class names)
- **Comments:** English (all code comments and documentation)
- **Git commits:** English
- **API responses:** English keys, Swedish values where applicable (e.g., error messages may be Swedish for users)

---

## Architecture

### Stack
- **Backend:** Flask (Python 3.10+) with Gunicorn WSGI server
- **Frontend:** React + Vite + Tailwind CSS + Radix UI
- **Web Server:** Nginx (reverse proxy + static file serving)
- **Process Management:** Systemd services
- **Database:** Redis for leaderboard (migrated from JSON); JSON files for manifest/distractors
- **OS:** Ubuntu Server 24.04 LTS

### Application Structure
```
Flask Backend (Port 8000) ← Gunicorn (9 workers)
    ↑
Nginx (Port 80) ← Reverse proxy for /api/* and /media/*
    ↓
React Build (Served from /opt/takk/app/components/dist/)
```

### Data Flow
- API endpoints: `/api/*` → Gunicorn → Flask routes
- Media files: `/media/*` → Nginx direct serving
- Static files: React build served by Nginx
- Videos: Processed locally, stored in git (~100MB total)

---

## Current Hardware & Deployment

### Beta Testing Server (Current - Temporary)
- **Model:** HP Elite Mini 600 G9 Desktop Mini
- **CPU:** Intel i3-12100T (4 cores, 8 threads, 12th gen)
- **RAM:** 16GB
- **Storage:** 256GB SSD
- **Network:** Local WiFi only (192.168.2.66)
- **Hostname:** takk-server (accessible via takk-server.local with Avahi/mDNS)
- **Purpose:** Beta testing with user group before cloud deployment
- **Performance:** Handles 80-100+ concurrent users easily

### Production Server (Planned)
- **Hosting:** Bahnhof VPS (or similar cloud provider)
- **Serves:** All 10-15 locations via internet
- **Users:** 80-150 users across all locations
- **Access:** https://takk.betaniahemmet.se (or similar domain)
- **Database:** Redis for leaderboard (already implemented)
- **SSL:** Let's Encrypt certificate (HTTPS mandatory for public access)

### Deployment Configuration (Beta)
- **Gunicorn Workers:** 9 (formula: 2 × 4 cores + 1)
- **Server Path:** /opt/takk/
- **Service User:** takk (non-root)
- **Logs:** /var/log/takk/ and journalctl -u takk
- **Auto-start:** Enabled (survives reboots, power outages with BIOS setting)
- **Note:** Production VPS will use similar configuration, possibly with adjusted worker count based on VPS specs

---

## Key Design Decisions

### Video Processing
- **Raw videos** (.mov files, 1GB+): Processed locally, NOT in git
- **Processed videos** (.mp4, ~2MB each): Committed to git in media/signs/
- **Processing:** ffmpeg-based batch processor converts raw → square mp4 + thumbnail
- **Total size:** ~100MB of processed content (80+ signs)
- **Workflow:** Process locally → commit processed → push → servers pull

**Rationale:** Keep git repo small, process once, deploy everywhere.

### Data Storage (Current State)
- **Leaderboard:** Redis sorted sets (migrated from JSON) — race-condition-free, cloud-ready
- **Manifest:** JSON file (catalog/manifest.json) - signs, levels, metadata
- **Feedback:** JSON file (feedback.json) - user feedback (kept during beta testing)
- **Distractors:** JSON file (catalog/distractors.json) - quiz wrong answers

### Security Features (Current - Beta)
- **Rate limiting:** 10 requests per 60 seconds per IP on POST endpoints (/api/score, /api/feedback)
- **Input validation:** Name max 10 chars, score validation, message length limits
- **Path traversal protection:** Media file serving sanitized
- **Firewall:** UFW enabled (SSH port 22, HTTP port 80 only)
- **fail2ban:** Blocks brute force SSH attempts
- **Auto updates:** unattended-upgrades enabled
- **No HTTPS:** Local network only for beta, HTTP sufficient

### Security Features (Production - Required)
- **HTTPS/SSL:** Let's Encrypt certificate (mandatory for public access)
- **Rate limiting:** Same as beta (already implemented)
- **Input validation:** Same as beta (already implemented)
- **Firewall:** UFW (SSH 22, HTTP 80, HTTPS 443)
- **fail2ban:** Essential for public server
- **Auto updates:** Critical for public-facing server
- **Monitoring:** Consider adding uptime monitoring
- **Backups:** Regular database backups (Redis persistence)

### Application Features
- **Dictionary:** Browse all signs with videos and pictogram breakdowns
- **Training Mode:** Practice signs with immediate feedback
- **Quiz Mode:** Multiple choice questions with distractors
- **Competition Mode:** Timed challenges with leaderboard
- **Introduction:** Overview page with 3 video sections (placeholders, content TBD)
- **Dark Mode:** Auto-adjusts to system preference
- **Version Display:** Shows v1.0.0 at page bottom (from VERSION file + /api/version endpoint)

---

## File Structure & Key Files

### Backend (Flask)
```
app/
├── __init__.py          # App factory, CORS config
├── routes.py            # API endpoints (RESTful)
├── leaderboard.py       # Leaderboard logic (Redis sorted sets)
├── config.py            # Configuration
└── components/          # React frontend
    ├── src/             # React source
    │   ├── main.jsx             # Router + lazy route loading
    │   ├── app.jsx              # Placeholder (routing is in main.jsx)
    │   ├── AppShell.jsx         # Layout wrapper (mobile)
    │   ├── AppShellCompetition.jsx  # Layout for competition
    │   ├── Home.jsx             # Landing page
    │   ├── Dictionary.jsx       # Browse signs
    │   ├── Practice.jsx         # Practice mode router (GameLevels, LevelDetail)
    │   ├── Competition.jsx      # Competition mode
    │   ├── Feedback.jsx         # Feedback form
    │   ├── Introduction.jsx     # Introduction page (video placeholders)
    │   ├── VideoPlayer.jsx      # Shared video player (preload prop)
    │   ├── practice/
    │   │   ├── Training.jsx     # Training mode
    │   │   └── Quiz.jsx         # Quiz mode
    │   ├── ui/                  # Reusable components
    │   └── VersionDisplay.jsx   # Version display component
    ├── vite.config.js   # Vite build config (vendor/icons chunk splitting)
    ├── public/          # Static assets (dev)
    └── dist/            # Built React app (production)
```

### Data & Media
```
catalog/
├── manifest.json        # Signs metadata, levels structure
├── distractors.json     # Wrong answers for quizzes
└── (not in git) feedback.json  # User feedback

media/
├── signs/               # Processed sign videos (in git)
│   ├── hej/
│   │   ├── hej_square.mp4    # 2MB processed video
│   │   └── hej.jpg           # Thumbnail
│   └── ...
└── ui/                  # UI assets (backgrounds, sounds)

raw_clips/               # NOT IN GIT - raw source videos
├── Hej.mov             # 50MB+ raw footage
└── ...
```

### Deployment
```
deployment/
├── gunicorn.conf.py     # 9 workers, port 8000, logging
├── nginx-takk.conf      # Reverse proxy, caching headers, gzip
├── takk.service         # Systemd service definition
├── requirements.txt     # Python dependencies (includes redis>=5.0.0)
├── DEPLOYMENT.md        # Step-by-step deployment guide
└── deployment-check.sh  # Verification script
```

### Configuration
```
.env                     # Environment variables (not in git)
.env.example             # Template
.env.production          # Production settings template
VERSION                  # Version string (1.0.0)
```

---

## API Endpoints

### Signs & Levels
- `GET /api/levels` - List all levels
- `GET /api/levels/:id` - Get level detail with signs
- `GET /api/levels/:id/cumulative` - Level signs + all previous levels (for distractors)
- `GET /api/signs` - All signs (sorted alphabetically)

### Leaderboard
- `GET /api/scores` - Top 10 scores
- `POST /api/score` - Submit score (rate limited)
  - Body: `{name: string, score: float}`
  - Returns: `{ok: bool, madeTop: bool, scores: array}`

### Other
- `GET /api/distractors` - Wrong answers for quiz mode
- `POST /api/feedback` - Submit feedback (rate limited, will be removed after beta)
- `GET /api/version` - App version (from VERSION file)
- `GET /health` - Health check endpoint
- `GET /media/<path>` - Serve videos/images (path traversal protected)

### SPA Fallback
- All other routes → serve React app (index.html)

---

## Completed Optimizations

All Phase 1 work is done. Documented here for future AI assistant context.

### Redis Leaderboard Migration
- `leaderboard.py` now uses Redis sorted sets (ZADD, ZREVRANGE)
- Eliminates race conditions with 9 Gunicorn workers
- `redis>=5.0.0` added to `deployment/requirements.txt`
- API unchanged: `get_top(limit=10)` and `add_score(name, score)` work identically
- Stores top 100, displays top 10

### Introduction Page
- New component: `src/Introduction.jsx`
- Route: `/introduktion`
- Three sections with video placeholders: "Om projektet", "Så använder du appen", "Introduktion till TAKK"
- **Pending:** Actual video content to be recorded and added

### Dictionary Search UX Fix
- Clicking a sign in search overlay now auto-closes the overlay and selects the sign
- Light/dark mode styling fixed for search overlay
- `query` state cleared on sign selection so search resets correctly

### Video Loading Optimization
`VideoPlayer.jsx` now accepts a `preload` prop (default `"metadata"`):
- **Quiz & Competition:** `preload="auto"` — video buffers immediately when question renders; user must watch before answering
- **Dictionary & Training:** `preload="none"` — user taps "Spela video" manually; no unnecessary prefetch
- **Training:** hidden `<video preload="auto">` renders next sign's video while current is displayed
- **Competition:** hidden `<video preload="auto">` renders next sign's video during the 800ms CONFIRM_MS pause between questions

### Bundle Code-Splitting
`vite.config.js` now has `rollupOptions.output.manualChunks`:
- `vendor` chunk: `react`, `react-dom`, `react-router-dom` (~44KB, cached across deploys)
- `icons` chunk: `lucide-react` (~5KB, cached across deploys)

`main.jsx` uses `React.lazy` + `Suspense` for all routes except `Home` (which stays eager):
- Route chunks: `Competition.js` 7KB, `Dictionary.js` 4KB, `Quiz.js` 3KB, `Training.js` 3KB, etc.
- `<Suspense fallback={<Loading />}>` wraps all routes; shows "Laddar…" during first-visit chunk fetch

**Build output before/after:**
- Before: 1 file × 252KB
- After: `vendor` 44KB + `icons` 5KB + `index` 184KB (Home + shell + react-dom) + tiny per-route chunks

### Nginx Caching & Gzip
`deployment/nginx-takk.conf` updated:
- **`/assets/` (Vite-hashed JS/CSS):** `Cache-Control: public, max-age=31536000, immutable` — 1-year cache, safe because Vite changes filename hash on content change
- **`/index.html`:** `Cache-Control: no-cache, must-revalidate` — always fresh; contains hashed asset filenames
- **`/media/` (videos, images, audio):** `Cache-Control: public, max-age=2592000` (30 days) — removed incorrect `immutable` flag (media filenames have no hash; ETag handles revalidation after window)
- **Gzip:** enabled for JS, CSS, JSON, SVG with `gzip_comp_level 6`
- **Security headers:** explicitly repeated in each location block that sets `Cache-Control` (nginx `add_header` inheritance quirk)

### UI Improvements
- **Card styling:** increased opacity (`bg-white/85 dark:bg-slate-900/75`) for better contrast
- **Home buttons:** added to Training and Quiz views for easy navigation back to home

---

## Deployment Strategy

### Phase 1: Beta Prep — COMPLETE ✅
All code changes merged and built. Ready to deploy to beta server.

| Item | Status |
|---|---|
| Redis leaderboard migration | ✅ Done |
| Introduction page (structure) | ✅ Done |
| Dictionary search UX fix | ✅ Done |
| Video smart preloading | ✅ Done |
| Bundle code-splitting | ✅ Done |
| Nginx caching & gzip | ✅ Done |
| Card contrast fix | ✅ Done |
| Home buttons everywhere | ✅ Done |
| Introduction video content | ⏳ Pending — videos to be recorded |
| Deploy to beta server | ⏳ Pending |
| Beta user testing | ⏳ Pending |

### Beta Testing Phase (Next)
- Deploy on local HP Elite Mini (`takk-server.local`)
- Test with user group at one location
- Gather feedback via feedback form
- Monitor performance and logs
- Identify issues before cloud deployment

### Phase 2: Cloud Production (After Beta)
- Deploy to Bahnhof VPS
- Configure HTTPS/SSL (Let's Encrypt + Certbot)
- Configure domain: takk.betaniahemmet.se
- Apply feedback from beta
- Roll out to all 10-15 locations

**Production-Only Changes Still Needed:**

1. **HTTPS/SSL Configuration**
   - Install Certbot for Let's Encrypt
   - Configure nginx for HTTPS (port 443)
   - Redirect HTTP → HTTPS
   - Update nginx `server_name`

2. **Domain Configuration**
   - Point takk.betaniahemmet.se to VPS IP
   - Test DNS propagation

3. **Feedback System Review**
   - Active during beta; evaluate removal after based on feedback received

4. **Environment Variables**
   - **Beta (local):** `FLASK_ENV=production, DEBUG=False, SANDBOX_MODE=false, REDIS_URL=redis://localhost:6379`
   - **Production (cloud):** Same variables; Redis on same VPS

### Future: Production Cloud Architecture
- **Single Bahnhof VPS** serving all 10-15 locations
- **Estimated cost:** ~150-200 SEK/month (~$15-20/month)
- **Domain:** takk.betaniahemmet.se
- **SSL:** Let's Encrypt (free, auto-renewing)

**Requirements for Cloud (status):**
- ✅ Redis for leaderboard — done
- ⏳ HTTPS/SSL certificate — Phase 2
- ⏳ Domain configuration — Phase 2
- ⚠️ Backup strategy for Redis data
- ⚠️ Bandwidth monitoring (video content)
- ⚠️ Enhanced security review (public internet exposure)

---

## Development Workflow

### Local Development
```bash
# Backend (Flask)
python run.py  # Runs on http://localhost:5000

# Frontend (React)
cd app/components
npm run dev   # Runs on http://localhost:5173
```

### Adding New Signs
```bash
# 1. Add raw video to raw_clips/
cp ~/Downloads/Glad.mov raw_clips/

# 2. Process video
python video_processing/batch_processor.py
# Creates: media/signs/glad/glad_square.mp4 + glad.jpg

# 3. Update manifest
# Edit catalog/manifest.json - add sign to appropriate level

# 4. Commit processed files only
git add media/signs/glad/
git add catalog/manifest.json
git commit -m "Add sign: glad"
git push

# 5. Update server
ssh henri@takk-server.local
cd /opt/takk && sudo -u takk git pull
sudo systemctl restart takk
```

### Deployment Updates
```bash
# After code changes
git push

# On server
ssh henri@takk-server.local
cd /opt/takk
sudo -u takk git pull
cd app/components && sudo -u takk npm run build && cd ../..
sudo systemctl restart takk
```

---

## Coding Conventions

### Python (Backend)
- Flask best practices
- Type hints where appropriate
- Functions prefixed with `_` for internal helpers
- Docstrings for public functions
- Error handling with try/except and proper HTTP status codes
- Rate limiting on user-facing POST endpoints
- Input validation on all user data

### React (Frontend)
- Functional components only (no class components)
- Hooks for state management (useState, useEffect)
- Tailwind CSS for styling (utility-first)
- Lucide React for icons
- Components organized by user journey (Practice, Competition, Dictionary)
- Dark mode support via CSS variables
- Mobile-first responsive design
- Route-level code splitting via `React.lazy` + `Suspense` (all routes except Home)

### API Design
- RESTful conventions
- JSON responses
- Consistent error format: `{ok: false, error: "message"}`
- Success format: `{ok: true, ...data}`
- Rate limiting responses: HTTP 429

### File Naming
- Python: snake_case
- React: PascalCase for components, camelCase for utilities
- Config files: kebab-case

---

## Testing & Verification

### Health Checks
```bash
# API health
curl http://localhost/health  # Should return {"ok":true}

# Service status
sudo systemctl status takk
sudo systemctl status nginx

# Version check
curl http://localhost/api/version  # {"version":"1.0.0"}

# Redis connectivity
redis-cli ping  # Should return PONG
```

### Common Issues
- **502 Bad Gateway:** Gunicorn not running (check `systemctl status takk`)
- **Videos not loading:** Check media directory permissions, nginx logs
- **High CPU:** Too many Gunicorn workers for CPU count
- **Leaderboard not saving:** Check Redis is running (`systemctl status redis`)

---

## Important Notes for AI Assistants

### When Modifying leaderboard.py
- **Keep the same API:** Functions `get_top(limit=10)` and `add_score(name, score)` must work identically
- **Redis is the backend:** Uses sorted sets; `redis>=5.0.0` in requirements.txt
- **Test with React frontend:** Frontend calls these via `/api/scores` and `/api/score`
- **Maintain top-N constraint:** Leaderboard shows top 10, store top 100 max

### When Modifying Frontend
- **AppShell.jsx** is used by Dictionary, Practice, Feedback, Introduction
- **AppShellCompetition.jsx** is separate for Competition mode
- **VersionDisplay** component should appear in both shells
- **Dark mode:** Uses Tailwind dark: variants
- **Mobile-first:** Test responsive design
- **Routing:** All routes are in `main.jsx` (not `app.jsx`); new routes need a `React.lazy` import and a `<Route>` entry inside `<Suspense>`
- **VideoPlayer:** Pass `preload="auto"` for modes where video must be watched, `preload="none"` for manual-play modes

### When Adding Dependencies
- **Python:** Add to `deployment/requirements.txt`
- **Node:** Run `npm install` in `app/components/`
- **System packages:** Document in deployment guide

### When Creating New Features
- **API endpoints:** Add to `app/routes.py`
- **Frontend routes:** Add to `app/components/src/main.jsx` (lazy import + Route)
- **New data:** Consider JSON vs Redis based on access pattern
- **Rate limiting:** Add to POST endpoints that accept user input

---

## Repository Information

**GitHub:** https://github.com/betaniahemmet/takk_app
**License:** MIT
**Version:** 1.0.0 (see VERSION file)
**Main Developer:** Henrik
**Organization:** Betaniahemmet

---

**Last Updated:** March 2026
**Document Version:** 2.0
