# TAKK Project Context for AI Assistants

## Project Overview

**TAKK** (Tecken som Alternativ och Kompletterande Kommunikation) is a Swedish sign language learning web application developed for Betaniahemmet, an organization supporting people with functional disabilities.

**Purpose:** Interactive platform for learning Swedish sign language through video-based instruction, training exercises, quizzes, and competitive gameplay.

**Users:** 80-150 users across 10-15 locations (verksamheter) within Betaniahemmet's network.

**Current Status:** v1.0.0 - Beta testing phase on local server. Cloud production deployment (Bahnhof VPS) planned after beta validation. Redis migration in progress to prepare for cloud multi-worker environment.

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
- **Database:** Currently JSON files (planned migration to Redis for cloud)
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
- **Database:** Redis for leaderboard (required for multiple workers)
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
- **Leaderboard:** JSON file (catalog/leaderboard.json) - top 10 scores
- **Manifest:** JSON file (catalog/manifest.json) - signs, levels, metadata
- **Feedback:** JSON file (feedback.json) - user feedback (kept during beta testing)
- **Distractors:** JSON file (catalog/distractors.json) - quiz wrong answers

**Known Issues:**
- JSON files have race conditions with multiple Gunicorn workers
- Not suitable for cloud deployment with multiple app instances
- Works fine for single-server local deployment
- **Priority:** Migrate leaderboard to Redis for cloud readiness

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
- **Dark Mode:** Auto-adjusts to system preference
- **Version Display:** Shows v1.0.0 at page bottom (from VERSION file + /api/version endpoint)

---

## File Structure & Key Files

### Backend (Flask)
```
app/
├── __init__.py          # App factory, CORS config
├── routes.py            # API endpoints (RESTful)
├── leaderboard.py       # Leaderboard logic (JSON → needs Redis migration)
├── config.py            # Configuration
└── components/          # React frontend
    ├── src/             # React source
    │   ├── app.jsx              # Main app component
    │   ├── AppShell.jsx         # Layout wrapper (mobile)
    │   ├── AppShellCompetition.jsx  # Layout for competition
    │   ├── Home.jsx             # Landing page
    │   ├── Dictionary.jsx       # Browse signs
    │   ├── Practice.jsx         # Practice mode router
    │   ├── Competition.jsx      # Competition mode
    │   ├── Feedback.jsx         # Feedback form
    │   ├── practice/
    │   │   ├── Training.jsx     # Training mode
    │   │   └── Quiz.jsx         # Quiz mode
    │   ├── ui/                  # Reusable components
    │   └── VersionDisplay.jsx   # Version display component
    ├── public/          # Static assets (dev)
    └── dist/            # Built React app (production)
```

### Data & Media
```
catalog/
├── manifest.json        # Signs metadata, levels structure
├── distractors.json     # Wrong answers for quizzes
├── leaderboard.json     # Top scores (migrate to Redis!)
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
├── nginx-takk.conf      # Reverse proxy, static serving
├── takk.service         # Systemd service definition
├── requirements.txt     # Python dependencies
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
- `POST /api/feedback` - Submit feedback (rate limited, will be removed)
- `GET /api/version` - App version (from VERSION file)
- `GET /health` - Health check endpoint
- `GET /media/<path>` - Serve videos/images (path traversal protected)

### SPA Fallback
- All other routes → serve React app (index.html)

---

## Planned Migrations & Future Work

### Cloud Deployment (Two-Phase Strategy)

**Phase 1: Beta Testing Preparation (IN PROGRESS - Before Beta)**
- ✅ **Redis migration** - Implement NOW (fixes race conditions, cloud-ready)
- ✅ **Feature additions** - Introduktion page for beta testers
- ✅ **Bug fixes** - Dictionary search UX improvements
- ❌ **HTTPS/SSL** - Skip for beta (local network only)
- ❌ **Domain config** - Skip for beta (no domain needed yet)

**Beta Testing Phase:**
- Deploy on local HP Elite Mini server
- Test with user group at one location
- Gather feedback via feedback form
- Monitor performance and logs
- Identify issues before cloud deployment

**Phase 2: Cloud Production Deployment (AFTER Beta)**
- ✅ **Deploy to Bahnhof VPS** - Migrate working beta to cloud
- ✅ **HTTPS/SSL Configuration** - Let's Encrypt + Certbot
- ✅ **Domain Configuration** - takk.betaniahemmet.se DNS setup
- ✅ **Apply beta feedback** - Fix issues discovered during testing
- ✅ **Performance tuning** - Optimize based on real usage data
- ✅ **Roll out to all 10-15 locations**

**Target: Bahnhof VPS or similar cloud hosting**

**Critical Migrations (Phase 1 - Before Beta):**

1. **Leaderboard: JSON → Redis** (HIGH PRIORITY - IMPLEMENTING NOW)
   - Current `leaderboard.py` uses JSON file
   - Problem: Race conditions with multiple Gunicorn workers (even on local server with 9 workers)
   - Solution: Redis sorted sets (ZADD, ZREVRANGE)
   - Keep only top 100 scores to prevent unbounded growth
   - Connect to `redis://localhost:6379` (Redis installed locally for beta, on VPS for production)
   - Add `redis>=5.0.0` to requirements.txt
   - **Keep same API:** `get_top(limit)`, `add_score(name, score)`
   - **Status:** Implementing now before beta test

2. **Introduktion Page** (NEW FEATURE - Before Beta)
   - Add button to Home page: "Introduktion" with suitable icon
   - Create new page/component with introduction videos:
     - Project background (about TAKK and Betaniahemmet)
     - How to use the app (app tutorial)
     - Introduction to sign language basics
   - **Status:** To be implemented before beta

3. **Dictionary Search UX Fix** (BUG FIX - Before Beta)
   - Problem: After searching and clicking a sign, search overlay remains visible
   - Expected: Clicking a sign should clear search and show video
   - Current: User must manually press "Avbryt" to dismiss search
   - **Status:** To be fixed before beta

**Production-Only Changes (Phase 2 - After Beta):**

4. **HTTPS/SSL Configuration**
   - Install Certbot for Let's Encrypt
   - Configure nginx for HTTPS (port 443)
   - Automatic certificate renewal
   - Redirect HTTP → HTTPS
   - **Status:** After beta, during cloud deployment

5. **Domain Configuration**
   - Point takk.betaniahemmet.se (or similar) to VPS IP
   - Update nginx server_name
   - Test DNS propagation
   - **Status:** After beta, during cloud deployment

6. **Feedback System**
   - Currently kept for beta testing with user group
   - Anonymous feedback helps improve the app during beta
   - Will evaluate removal/modification after beta period based on feedback received
   - **Status:** Active during beta, review after

7. **Environment Variables**
   - **Beta (local):** FLASK_ENV=production, DEBUG=False, SANDBOX_MODE=false, REDIS_URL=redis://localhost:6379
   - **Production (cloud):** Same variables, Redis still on localhost (same VPS)

### Future: Production Cloud Deployment

**Final Architecture:**
- **Single Bahnhof VPS** serving all 10-15 locations
- **Estimated cost:** ~150-200 SEK/month (~$15-20/month)
  - Server: ~100 SEK/month (2GB RAM, 2 CPU)
  - Bandwidth: ~50-100 SEK/month (video traffic)
- **Domain:** takk.betaniahemmet.se (or similar)
- **SSL/HTTPS:** Let's Encrypt (free, auto-renewing)
- **Access:** Users at all locations access via internet

**Benefits:**
- ✅ Single server to maintain (one deployment, not 15)
- ✅ Unified leaderboard across all locations
- ✅ Easy updates (git pull, restart)
- ✅ Professional infrastructure
- ✅ Centralized logs and monitoring
- ✅ Cost-effective at scale

**Requirements for Cloud:**
- ✅ Redis for leaderboard (race condition fix) - **IN PROGRESS**
- ✅ HTTPS/SSL certificate (Let's Encrypt + Certbot)
- ✅ Domain name configuration
- ✅ Backup strategy for data
- ⚠️ Bandwidth monitoring (video content)
- ⚠️ Enhanced security (public internet exposure)

**Migration Path:**
1. Beta test on local HP Elite Mini with user group
2. Implement Redis migration (eliminate race conditions)
3. Deploy to Bahnhof VPS
4. Configure domain + SSL
5. Test with small group
6. Roll out to all 10-15 locations

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
```

### Common Issues
- **502 Bad Gateway:** Gunicorn not running (check `systemctl status takk`)
- **Videos not loading:** Check media directory permissions, nginx logs
- **High CPU:** Too many Gunicorn workers for CPU count
- **Leaderboard race conditions:** Multiple workers writing to JSON (need Redis!)

---

## Important Notes for AI Assistants

### When Modifying leaderboard.py
- **Keep the same API:** Functions `get_top(limit=10)` and `add_score(name, score)` must work identically
- **Test with React frontend:** Frontend calls these via `/api/scores` and `/api/score`
- **Consider multiple workers:** Any solution must handle concurrent access safely
- **Maintain top-N constraint:** Leaderboard shows top 10, store top 100 max

### When Modifying Frontend
- **AppShell.jsx** is used by Dictionary, Practice, Feedback
- **AppShellCompetition.jsx** is separate for Competition mode
- **VersionDisplay** component should appear in both shells
- **Dark mode:** Uses Tailwind dark: variants
- **Mobile-first:** Test responsive design

### When Adding Dependencies
- **Python:** Add to `deployment/requirements.txt`
- **Node:** Run `npm install` in `app/components/`
- **System packages:** Document in deployment guide

### When Creating New Features
- **API endpoints:** Add to `app/routes.py`
- **Frontend routes:** Add to `app/components/src/app.jsx`
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

**Last Updated:** November 2025
**Document Version:** 1.0
