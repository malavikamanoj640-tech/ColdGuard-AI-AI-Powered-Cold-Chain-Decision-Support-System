# SupplyShield AI 5.0 — Real-Time Cold Chain Control Tower

SupplyShield AI is a Flask-based AI supply-chain decision support application for cold-chain monitoring, risk prediction, demand forecasting, inventory optimization, route intelligence, computer-vision screening, digital product passports and AI-assisted operational decisions.

## 5.0 additions
- Real-time shipment tracking **simulation mode** with moving GPS markers.
- Live temperature, humidity, delay, ETA, weather-risk and shelf-life indicators.
- Dynamic AI priority queue ranked by live risk and time sensitivity.
- Live decision feed with recommended actions.
- Temperature watch and operational forecast panels.
- Automatic refresh every 3 seconds.
- Leaflet/OpenStreetMap map visualization.
- Existing visual analytics, forecast model comparison, inventory optimizer, route optimizer, CV inspection, digital passport, audit verification and Qwen/Ollama Copilot retained.

## Important demo note
The live GPS, weather and telemetry values are simulated. This makes the project demonstrable without GPS/IoT hardware. The `/api/live-tracking` contract can later be connected to actual GPS, MQTT or telematics data without redesigning the UI.

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000/live-tracking`.

## Ollama
Run `setup_qwen_ollama.bat` on Windows if you want the local Qwen Copilot.


## SupplyShield AI 6.0 — AI Decision Center
- `/decision-center` converts live simulated telemetry into ranked interventions.
- `/api/decision-center` returns explainable decision priorities.
- `/api/decision-agent` sends the decision context to Qwen/Ollama when available, with a local fallback.
- Live GPS/telemetry remains simulation-mode by default; the API boundary is ready for GPS/MQTT/IoT integration.

## SupplyShield AI 7.0 — Phase 1 to Phase 6 Upgrade
This package extends 6.0 with an integrated MCA-oriented predictive/prescriptive pipeline.

### Phase 1 — Research & Explainability
- Existing risk model retained for compatibility.
- Explainability is exposed in the AI 7.0 Lab; the architecture is SHAP-ready for a validated trained model.
- Root-cause ranking and model/version governance are included.
- IMPORTANT: existing enhanced demo data contains synthetic enrichment/proxy labels; do not claim industrial validation from proxy-label metrics.

### Phase 2 — Predictive Intelligence
- Six-hour temperature/risk forecast.
- Time-to-potential-violation early warning.
- Robust telemetry anomaly detector.

### Phase 3 — Prescriptive AI
- Multi-objective intervention optimizer balancing predicted risk reduction, cost, delay and carbon index.
- Counterfactual analysis for actionable “what must change?” explanations.

### Phase 4 — Digital Twin 2.0
- Intervention options are evaluated on cloned shipment states before recommendation.
- Existing simulator/digital-twin modules remain available.

### Phase 5 — Closed Loop Decision Center
- Intervention outcome API stores baseline, predicted post-action and actual post-action risk.
- Alert action endpoint records acknowledgement/escalation in the audit chain.

### Phase 6 — Governance & Software Engineering
- IoT Device Manager demo registry.
- Model registry schema, outcome history, responsible-AI notice and SHA-256 audit verification.
- Database schema includes users/roles for RBAC integration. (Authentication enforcement is intentionally not enabled by default so the classroom demo remains one-click runnable.)

### New pages
- `/ai-7` — integrated AI 7.0 analysis lab
- `/governance` — devices, model governance and feedback overview

### New APIs
- `POST /api/phase7/analyze`
- `POST /api/intervention-outcome`
- `POST /api/alerts/<id>/action`

### Run
1. `cd app`
2. `pip install -r requirements.txt`
3. `python app.py`
4. Open `http://127.0.0.1:5000/dashboard`

## SupplyShield AI 8.1 — XAMPP / MySQL edition
This build replaces the SQLite persistence layer with MySQL/MariaDB for XAMPP. The default database is `supplyshield_ai` on `127.0.0.1:3306`, user `root`, blank password. Tables are auto-created at startup, and `database/schema.sql` is included for manual phpMyAdmin import. See `XAMPP_SETUP.txt` for setup steps.

## SupplyShield AI 9.0 — Prescriptive Recovery Intelligence
This build adds a generalized recovery layer inspired by the strongest ColdFix concepts while retaining the SupplyShield 8.1 XAMPP/MySQL architecture.

New capabilities:
- Excursion Severity Index (0–100) using temperature deviation, exposure duration, product sensitivity and shelf-life pressure.
- Prescriptive intervention ranking: hold/assess, controlled storage, reefer recovery, priority dispatch and enhanced monitoring.
- MySQL-backed recovery resource registry (cold storage, reefer and quality-lab capabilities).
- Capability/proximity/urgency intervention scoring with estimated distance and ETA when a known city can be resolved.
- Before-vs-after intervention simulation using the existing SupplyShield risk model.
- Predicted post-action status: RECOVERED, STABILIZED, MONITOR or STILL CRITICAL.
- Human-in-the-loop recovery plans: save as PROPOSED or APPROVED.
- Recovery decisions are recorded in shipment events and the tamper-evident audit chain.

### Run with XAMPP
1. Start **MySQL** in XAMPP (Apache is optional for the Flask app).
2. Keep XAMPP's default MySQL user `root` with blank password, or set the `SUPPLYSHIELD_DB_*` environment variables in `config.py`/your shell.
3. Open a terminal in this folder and run `pip install -r requirements.txt`.
4. Run `python app.py` or double-click `run.bat`.
5. Open `http://127.0.0.1:5000`. Tables and the bundled academic demo recovery-resource records are created automatically.

> Important: bundled recovery resources are demonstration data, not verified live facilities. Replace them with verified partner/provider data before any real-world use.

## SupplyShield AI 9.1 — Incident Response & Logistics Support
Added in 9.1:
- Redesigned Alerts & Actions as an Incident Response Center.
- Incident workflow: Open → Acknowledged → Investigating → Action Taken → Resolved.
- Support & Emergency Logistics page with Leaflet/OpenStreetMap map support.
- Nearby recovery-resource ranking using current shipment coordinates, urgency, capability and distance.
- Cold storage, reefer and quality-lab capability display.
- Assign recovery destination and start a recovery route.
- Animated route tracking with progress and ETA for demonstration.
- Recovery assignment is written to shipment events and audit history.
- Transparent simulation labels: map tiles are real OpenStreetMap tiles; shipment GPS movement and bundled facilities are demonstration data until real GPS/provider APIs are connected.
