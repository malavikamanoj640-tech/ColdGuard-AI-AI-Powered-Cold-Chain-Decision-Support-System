# ColdGuard AI

### AI-Powered Cold-Chain Risk Intelligence & Decision Support System

ColdGuard AI is an intelligent cold-chain supply-chain platform designed to **monitor temperature-sensitive shipments, predict operational risk, explain risk factors, recommend corrective actions, and support recovery decisions**.

The system combines **Machine Learning, predictive analytics, Digital Twin simulation, recovery intelligence, shipment monitoring, and decision-support capabilities** in a Flask-based web application.

It is designed as an academic prototype demonstrating how AI can move cold-chain monitoring beyond simple alerts toward:

**Monitor → Predict → Explain → Decide → Simulate → Recover → Track → Audit**

---

## 🎯 Problem Statement

Cold-chain logistics is essential for transporting temperature-sensitive products such as vaccines, pharmaceuticals, dairy products, frozen products, and other perishables.

Traditional monitoring systems can detect conditions such as temperature excursions or transportation delays, but an alert alone may not answer important operational questions:

- How serious is the current shipment risk?
- What factors are contributing to the risk?
- Which shipment should receive priority?
- What corrective action should be considered?
- How could an intervention affect the predicted risk?
- Which recovery resource is suitable for the affected shipment?

ColdGuard AI was developed to provide an integrated decision-support workflow for these challenges.

---

## ✨ Key Features

### 🤖 AI-Based Risk Prediction

Uses machine-learning-based analysis to estimate shipment risk from environmental and logistics parameters such as temperature conditions, humidity, expiry pressure, refrigeration exposure, transportation stage, and other shipment characteristics.

Risk levels are represented using categories such as:

- Low
- Moderate
- High
- Critical

The predicted risk represents a **model-estimated operational risk**, not confirmed physical spoilage or laboratory-assessed product quality.

---

### 🔍 Explainable Risk Intelligence

Instead of displaying only a risk score, ColdGuard provides contributing risk information to help operators understand **why a shipment may be considered risky**.

This improves the interpretability of AI-assisted decisions.

---

### 📊 AI Control Tower

Provides a centralized operational view of cold-chain shipments, including:

- Active shipment monitoring
- Risk overview
- Critical/high-risk shipment identification
- Alert visibility
- Operational KPIs
- Shipment status

The Control Tower supports a **management-by-exception** approach by directing attention toward shipments requiring intervention.

---

### 📍 Shipment Tracking

Provides shipment location and cold-chain telemetry visualization.

The current academic prototype uses **simulated real-time movement and telemetry** to demonstrate how the platform can operate with live data.

In a production implementation, the same architecture can be extended using real GPS and IoT sensor feeds.

---

### 🚨 Alerts & Incident Management

High-risk conditions can be managed through an incident-response lifecycle:

**Open → Acknowledged → Investigating → Action Taken → Resolved**

This allows the system to track not only the detected problem but also the operational response.

---

### 🧠 AI Decision Center

The Decision Center prioritizes shipment incidents and provides decision-support recommendations based on factors such as:

- Shipment risk
- Temperature conditions
- Delay
- Remaining shelf life
- Operational conditions

This extends the system from **predictive intelligence** toward **prescriptive decision support**.

---

### 🪞 Digital Twin & What-If Simulation

ColdGuard provides a Digital Twin-inspired simulation capability for evaluating possible shipment interventions.

Operators can simulate changes in shipment conditions and observe how those changes may affect the model-estimated risk.

Example:

**Current Shipment → High Risk**

↓

**Simulate Controlled Storage**

↓

**Recalculate Risk**

↓

**Compare Before vs. After**

The resulting values are simulation-based estimates and should not be interpreted as physical confirmation that a product has recovered.

---

### 🛟 Recovery Intelligence

The Recovery Intelligence module helps determine what action could be considered when a shipment experiences a significant cold-chain excursion.

It considers factors such as:

- Temperature deviation
- Exposure duration
- Product sensitivity
- Remaining shelf-life pressure
- Shipment urgency

Potential interventions can include:

- Controlled cold storage
- Refrigerated transportation
- Quality assessment
- Priority dispatch
- Increased monitoring

---

### 🏥 Nearby Support & Emergency Logistics

The system includes a Support Center for identifying and ranking available recovery resources such as:

- Cold-storage facilities
- Refrigerated/reefer support
- Quality-assessment facilities

Resources can be ranked using factors such as:

**Proximity + Capability + Shipment Urgency**

Geographical distance is calculated from shipment and facility coordinates, and an estimated recovery ETA can be generated.

The current project uses a **demonstration recovery-resource registry**. Integration with verified external provider/location APIs can be implemented in a production version.

---

### 🗺️ Map-Based Visualization

Uses **Leaflet.js and OpenStreetMap** for geographic visualization of shipment and support-resource locations.

---

### 📈 Analytics

Provides visual analytical insights into shipment operations and risk patterns to help identify broader trends across the cold-chain network.

---

### 📦 Demand Forecasting & Inventory Intelligence

Includes analytical functionality for:

- Demand forecasting
- Forecast-model comparison
- Inventory planning
- Reorder recommendations
- Stockout-risk analysis

These capabilities demonstrate how predictive analytics can support broader supply-chain planning.

---

### 🛣️ Route Intelligence

Supports route-related decision analysis using factors such as:

- Operational risk
- Transportation cost
- Carbon considerations

This demonstrates multi-objective supply-chain decision support rather than relying only on shortest-distance routing.

---

### 🔐 Tamper-Evident Audit Trail

Important operational events can be recorded using a **SHA-256 chained audit mechanism**.

Each event can reference the hash of the previous event, helping make unauthorized historical modifications detectable during verification.

---

### 📋 Digital Product Passport

Provides shipment/batch-level traceability by maintaining relevant operational and supply-chain information associated with the product journey.

---

## 🧠 System Workflow

```text
Shipment Data
      ↓
Cold-Chain Monitoring
      ↓
AI Risk Prediction
      ↓
Risk Classification
      ↓
Explainable Risk Factors
      ↓
Alert / Incident Detection
      ↓
AI Decision Center
      ↓
Digital Twin / What-If Simulation
      ↓
Recovery Intelligence
      ↓
Nearby Support Resource Ranking
      ↓
Recovery Route & Tracking
      ↓
Incident Resolution
      ↓
Tamper-Evident Audit Trail
```

---

## 🏗️ System Architecture

<img width="921" height="526" alt="image" src="https://github.com/user-attachments/assets/35a4387e-87cd-4c9a-b51f-2c513dea50e1" />


---

## 🛠️ Technology Stack

### Backend

- Python
- Flask
- REST APIs

### Machine Learning & Data Analysis

- Scikit-learn
- Pandas
- NumPy
- Predictive Analytics
- Classification
- Model Evaluation

### Database

- MySQL / MariaDB
- XAMPP

### Frontend

- HTML5
- CSS3
- JavaScript
- Bootstrap

### Maps

- Leaflet.js
- OpenStreetMap

### Additional Concepts

- Digital Twin
- Explainable AI
- Predictive Analytics
- Prescriptive Decision Support
- Recovery Intelligence
- SHA-256 Hashing
- What-If Simulation
- Supply-Chain Analytics

---

## 📊 Model Performance

The shipment outcome model achieved approximately:

| Metric            | Result         |
|---                |---:            |
| Accuracy          | **98.58%**     |
| Weighted F1-Score | **98.58%**     |
| Macro Recall      | **98.04%**     |

> **Important:** These metrics represent experimental performance on the project's evaluation dataset. The current outcome labels include proxy-generated labels rather than independently verified industrial ground-truth outcomes. Therefore, these results should not be interpreted as guaranteed real-world cold-chain performance.

---

## 💡 Intelligence Levels

ColdGuard AI can be understood through four levels of intelligence:

### 1. Descriptive Intelligence

**What is happening?**

Dashboard, shipment monitoring, analytics, telemetry and tracking.

### 2. Predictive Intelligence

**What could happen?**

Machine-learning risk prediction, forecasting and anomaly/risk analysis.

### 3. Prescriptive Intelligence

**What should we do?**

Decision recommendations, intervention ranking, recovery intelligence and optimization.

### 4. Operational Response

**How do we respond and record it?**

Incident management, support-resource selection, recovery routing, reporting and audit history.

---

## 📂 Major Modules

```text
SupplyShield AI
│
├── Dashboard
├── Shipments
├── AI Control Tower
├── Risk Intelligence
├── Analytics
├── Live Tracking
├── Alerts & Incident Response
├── AI Decision Center
├── Digital Twin
├── What-If Simulator
├── Recovery Intelligence
├── Nearby Support Center
├── Recovery Route Tracking
├── Demand Forecasting
├── Inventory Intelligence
├── Route Intelligence
├── Digital Product Passport
├── AI / Explainability Features
├── Governance & Audit
├── System Health
└── Reports
```

---

## ⚙️ Installation

### 1. Clone the repository


git clone ColdGuard-AI-AI-Powered-Cold-Chain-Decision-Support-System
cd ColdGuard


### 2. Create a virtual environment


python -m venv venv


### 3. Activate the environment

**Windows**


venv\Scripts\activate


**Linux/macOS**

source venv/bin/activate


### 4. Install dependencies


pip install -r requirements.txt


### 5. Start MySQL

Start **Apache and MySQL** from XAMPP if the project configuration requires them.

Create/import the project database using the SQL file supplied with the repository.

### 6. Configure database connection

Update the database configuration according to your local MySQL/XAMPP environment.

### 7. Run the Flask application


python app.py


### 8. Open the application

Open the local Flask address displayed in the terminal, typically:


http://127.0.0.1:5000


---

## 📸 Screenshots
## Landing Page
<img width="1827" height="891" alt="image" src="https://github.com/user-attachments/assets/185fc0b6-4baf-4a2f-8137-dba0f8bb0b27" />

## Main Dashboard
<img width="1906" height="896" alt="image" src="https://github.com/user-attachments/assets/47b93262-a7bb-472d-9610-f213fd3920b8" />

## AI Control Tower
<img width="1892" height="875" alt="image" src="https://github.com/user-attachments/assets/e81e886f-e592-4384-969a-f9c9cc73cc60" />

<img width="1871" height="892" alt="image" src="https://github.com/user-attachments/assets/d5c97cf7-f05f-4271-9a37-993cdeef8864" />

## Shipment Risk Intelligence
<img width="1891" height="897" alt="image" src="https://github.com/user-attachments/assets/e0861d36-12c0-44f3-bd77-46650cf10354" />

## Live Tracking
<img width="1892" height="876" alt="image" src="https://github.com/user-attachments/assets/da556c9a-816e-45b1-baf2-6741ad37f068" />

<img width="1892" height="901" alt="image" src="https://github.com/user-attachments/assets/b50cf4f5-8dfd-41d2-9e62-6f36d615704b" />

<img width="1871" height="886" alt="image" src="https://github.com/user-attachments/assets/91c9697b-39d0-45a5-b377-b83385edd15b" />

## AI Decision Center
<img width="1881" height="902" alt="image" src="https://github.com/user-attachments/assets/7797d58a-5079-401d-8958-2a38933cfe2b" />

## Digital Twin Simulation
<img width="1870" height="897" alt="image" src="https://github.com/user-attachments/assets/87acc88c-1bac-41c1-982a-e2e55cbf8fb9" />

<img width="1861" height="880" alt="image" src="https://github.com/user-attachments/assets/bea06bb3-d8da-4de4-8fcf-697145aa5a9e" />

## Nearby Support Center
<img width="1867" height="886" alt="image" src="https://github.com/user-attachments/assets/9c10ef08-697c-4c19-bdae-5fbaca6bc092" />

<img width="1872" height="882" alt="image" src="https://github.com/user-attachments/assets/7746ce0d-1d37-49ef-9f78-44c18e0ddad4" />

## Analytics
<img width="1867" height="900" alt="image" src="https://github.com/user-attachments/assets/7c5480e8-4223-4f8a-a4d6-1974e011e1ec" />

## Incident Management

<img width="1872" height="902" alt="image" src="https://github.com/user-attachments/assets/b2962dc9-4075-4d0b-b90f-9b8fe0ee0aee" />


---

## ⚠️ Current Limitations

ColdGuard AI is currently an **academic prototype**.

Some important limitations are:

- Live GPS and telemetry are simulated for demonstration.
- Recovery-resource records are demonstration data rather than a verified live provider directory.
- Model performance is based on the available academic/project dataset.
- Some outcome labels are proxy-generated rather than independently verified real-world shipment outcomes.
- Digital Twin intervention results represent model-based what-if estimates.
- Real deployment would require validated IoT sensors, GPS/telematics integration, verified facility data and industrial validation.

---

## 🚀 Future Scope

Future enhancements can include:

- Real IoT temperature and humidity sensors
- Real GPS/telematics integration
- MQTT-based telemetry streaming
- Verified cold-storage and logistics-provider APIs
- Real-time weather and traffic APIs
- Larger real-world cold-chain datasets
- Industrial model validation
- Advanced deep-learning forecasting
- Cloud deployment
- Role-based access control
- Mobile application support
- Advanced optimization for recovery routing

---

## 🎓 Project Purpose

ColdGuard AI was developed as an academic project to explore how **Machine Learning, web technologies, predictive analytics and decision-support techniques** can be integrated into a cold-chain supply-chain application.

The primary objective is to move beyond simple monitoring toward an intelligent workflow:

> **SEE → PREDICT → EXPLAIN → DECIDE → SIMULATE → RECOVER → TRACK → AUDIT**

---

## 👩‍💻 Skills Demonstrated

- Python Development
- Flask Web Development
- Machine Learning
- Data Analysis
- MySQL / SQL
- REST API Development
- Full-Stack Development
- Predictive Analytics
- Model Evaluation
- Data Visualization
- Decision Support Systems
- Digital Twin Concepts
- Supply-Chain Analytics
- Database Design
- Frontend Development

---

## 📜 Disclaimer

ColdGuard AI is an **academic and research prototype**. Risk scores, intervention recommendations, recovery outcomes, facility information, and simulated tracking should not be treated as validated industrial, pharmaceutical, medical, or logistics decisions without appropriate real-world validation and expert oversight.

---

## 👥 Author

Developed as an MCA academic project

**Project:** ColdGuard AI  
**Domain:** Artificial Intelligence / Machine Learning / Cold-Chain Supply Chain  
**Type:** Academic Project
