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

# 🩺 Explainable Multi-Disease Prediction & Personalized Health Intelligence System

An AI-powered web application for **multi-disease risk assessment, explainable machine learning, longitudinal health-risk tracking, and personalized preventive health intelligence**.

The system currently supports:

- ❤️ Heart Disease Risk Assessment
- 🩸 Diabetes Risk Assessment
- 🔎 Early Diabetes Risk Assessment

It combines machine-learning models, adaptive ensemble learning, Explainable AI (XAI), medical-report processing, longitudinal analytics, and personalized educational recommendations within a Flask-based healthcare application.

> **Important:** This project is intended for educational and research purposes. Model outputs represent machine-learning risk estimates and are not medical diagnoses or substitutes for professional healthcare advice.

---

## 📌 Project Overview

Traditional machine-learning disease prediction applications often provide only a final prediction such as **High Risk** or **Low Risk**, without explaining why the model produced that result or how the user's assessments change over time.

This project extends conventional disease prediction by integrating:

- Multi-disease machine-learning models
- Adaptive ensemble learning
- Explainable AI using SHAP
- Model uncertainty and disagreement analysis
- Longitudinal risk tracking
- What-If risk simulation
- Cross-disease health intelligence
- Personalized risk-reduction recommendations
- Medical-report data extraction
- Prediction audit and model versioning
- AI-assisted health information
- Interactive analytics dashboards

The objective is to provide a more **transparent, research-oriented, and user-friendly health-risk assessment platform**.

---

# ✨ Key Features

## ❤️ 1. Heart Disease Risk Assessment

Predicts model-estimated heart-disease risk using clinical and health-related parameters including:

- Age
- Sex
- Chest Pain Type
- Resting Blood Pressure
- Cholesterol
- Fasting Blood Sugar
- Resting ECG
- Maximum Heart Rate
- Exercise-Induced Angina
- Oldpeak
- ST Slope

The heart module uses multiple machine-learning algorithms together with an adaptive ensemble approach.

---

## 🩸 2. Diabetes Risk Assessment

Provides diabetes risk assessment using parameters such as:

- Pregnancies
- Glucose
- Blood Pressure
- Skin Thickness
- Insulin
- BMI
- Diabetes Pedigree Function
- Age

The module also provides risk-factor analysis, explanations, educational recommendations, and assessment history.

---

## 🔎 3. Early Diabetes Risk Assessment

A separate symptom-oriented model is included for early diabetes risk analysis.

Inputs include factors such as:

- Age
- Gender
- Polyuria
- Polydipsia
- Sudden Weight Loss
- Weakness
- Polyphagia
- Genital Thrush
- Visual Blurring
- Itching
- Irritability
- Delayed Healing
- Partial Paresis
- Muscle Stiffness
- Alopecia
- Obesity

This model is maintained separately from the standard diabetes assessment.

---

# 🧠 Adaptive Ensemble Learning

The heart-disease prediction module combines multiple machine-learning algorithms, including:

- Logistic Regression
- Random Forest
- Gradient Boosting
- Support Vector Machine (SVM)

Instead of relying entirely on a single classifier, the system uses an **adaptive ensemble strategy** that combines predictions from multiple models.

Adaptive weighting considers model-level performance together with prediction confidence to produce the final ensemble output.

---

# 🔍 Explainable AI — SHAP

The system integrates **SHAP-based Explainable AI (XAI)** to improve prediction transparency.

Instead of showing only:

> High Risk

the application can also help explain which input features influenced the machine-learning output.

This allows users and researchers to better understand the model's behaviour.

---

# 📈 Longitudinal Risk Trend Engine

The application stores previous assessments and tracks model-estimated high-risk probability over time.

Users can view:

- Previous assessments
- Latest assessment
- Probability trends
- Change from the previous assessment
- Increasing/decreasing/stable model-output patterns

The trend represents changes in **model output across assessments** and should not be interpreted as clinically validated disease progression.

---

# 🧪 What-If Risk Simulator

The What-If Simulator allows users to modify selected input values and observe how the trained model responds.

Example:

```text
Saved Assessment
Heart high-risk probability: 68%

Hypothetical Scenario
Resting BP: 148 → 130
Cholesterol: 250 → 210

Simulated model probability: 44%

Difference: -24 percentage points
```

What-If simulations are kept separate from genuine prediction history.

> The simulator demonstrates model behaviour under hypothetical inputs. It does not predict the medical benefit of a treatment or lifestyle intervention.

---

# ⚖️ Model Uncertainty & Disagreement Analysis

For ensemble-based assessments, the system can expose individual model outputs and adaptive weights.

This allows analysis of:

- Individual model probabilities
- Adaptive model weights
- Probability spread
- Model agreement/disagreement
- Prediction uncertainty

This improves transparency compared with presenting only a single ensemble probability.

---

# 🔗 Cross-Disease Health Intelligence

A unified intelligence layer combines the latest available information from:

- Heart Disease
- Diabetes
- Early Diabetes

The module provides:

- Disease-specific latest predictions
- Disease-specific longitudinal trends
- Shared recorded attention signals
- Assessment counts
- Cross-disease overview

The application does **not** treat probabilities from different disease models as directly equivalent clinical risks.

Any descriptive combined index is presented only as a research-oriented summary and not as a medical risk score.

---

# 📄 Medical Report Processing

The system supports medical-report upload and structured data extraction.

The workflow can:

1. Upload a medical report
2. Extract available supported parameters
3. Normalize detected values
4. Identify missing parameters
5. Pre-fill compatible assessment fields
6. Allow the user to verify or complete missing information
7. Continue with disease-risk assessment

This reduces repetitive manual data entry while keeping user verification part of the workflow.

---

# 💡 Personalized Risk-Reduction Recommendations

After an assessment, the system generates educational recommendations based on:

- Model output
- Recorded risk-related inputs
- Rule-based attention signals
- Explainability information

The recommendation layer is designed for **preventive-health education** and does not prescribe medication or replace professional medical advice.

---

# 📊 Prediction History Center

The system stores previous assessments in MySQL and provides structured prediction history.

History functionality includes:

- Disease-specific records
- Prediction result
- High-risk probability
- Assessment date
- Historical report access
- Longitudinal trend analysis

The multi-disease architecture supports separate tracking of Heart Disease, Diabetes, and Early Diabetes assessments.

---

# 🧾 Prediction Audit & Model Versioning

Prediction records can be associated with audit information such as:

- Prediction ID
- Disease module
- Model name
- Model version
- Model artifact
- Dataset reference
- Decision threshold
- Model probability
- Prediction result
- Input snapshot
- Timestamp

This improves **traceability and reproducibility** of machine-learning assessments.

---

# 🤖 AI Health Assistant

The application contains an AI-assisted health-information interface capable of answering supported questions about:

- Latest prediction
- Values used in an assessment
- Previous disease assessments
- Model-related risk factors
- General educational health information

The assistant is designed with safety limitations and does not provide medical diagnosis or prescriptions.

---

# 🏥 Healthcare Facility Locator

The healthcare locator helps users discover nearby healthcare facilities such as:

- Hospitals
- Doctors/clinics
- Pharmacies
- Diagnostic laboratories

The module supports location-based searching, map visualization, distance information, and external navigation/directions.

---

# 🔔 Notification Center

The application includes a notification system for relevant system and assessment events.

Features include:

- Read/unread status
- Notification categories
- Priority indicators
- Search/filtering
- Links to relevant assessments or reports

---

# 🔐 Authentication & Security

The application includes:

- User registration
- Secure login
- Password hashing using bcrypt
- Flask session management
- Forgot-password workflow
- Email OTP verification
- OTP expiration
- Limited OTP attempts
- One-time OTP usage
- Secure password reset

---

# 📊 Research & Model Evaluation

The project contains research-oriented model evaluation using metrics such as:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Brier Score
- Confusion Matrix
- Cross-validation stability

Repeated cross-validation is used to compare ensemble strategies more reliably than relying on a single train/test split.

The project intentionally avoids claiming that adaptive weighting always outperforms static ensemble methods; results are interpreted according to the measured experimental performance.

---

# 🛠️ Technology Stack

### Backend

- Python
- Flask
- Flask-MySQLdb
- Flask-Bcrypt

### Machine Learning

- Scikit-learn
- Pandas
- NumPy
- SHAP
- Logistic Regression
- Random Forest
- Gradient Boosting
- Support Vector Machine
- Adaptive Ensemble Learning

### Database

- MySQL
- XAMPP

### Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript
- Jinja2
- Chart.js

### Additional Technologies

- REST/API integration
- SMTP Email Integration
- PDF/Medical Report Processing
- Leaflet Maps
- OpenStreetMap-based location services
- Ollama-based local AI integration

---

# 🏗️ System Architecture

```text
                     USER
                       │
                       ▼
                Flask Web Application
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
 Authentication   Disease Models   Report Processing
       │               │                │
       │       ┌───────┼────────┐       │
       │       ▼       ▼        ▼       │
       │     Heart  Diabetes  Early     │
       │                    Diabetes    │
       │               │                │
       │               ▼                │
       │        Prediction Engine       │
       │               │                │
       │       ┌───────┼────────┐       │
       │       ▼       ▼        ▼       │
       │      XAI   Uncertainty What-If │
       │               │                │
       └───────────────┼────────────────┘
                       │
                       ▼
              Health Intelligence
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
        History      Trends    Recommendations
           │           │           │
           └───────────┼───────────┘
                       ▼
                     MySQL
```

---

# 📂 Project Structure

```text
MultiDiseasePrediction/
│
├── app.py
├── config.py
├── database_setup.py
│
├── algorithms/
│   ├── adaptive_ensemble.py
│   ├── diabetes_engine.py
│   ├── early_diabetes_engine.py
│   ├── recommendation.py
│   ├── research_validation.py
│   ├── xai_explainer.py
│   ├── report_parser.py
│   ├── report_normalizer.py
│   └── validation.py
│
├── ai/
│   └── health_assistant.py
│
├── models/
│   ├── heart/
│   ├── diabetes/
│   └── early_diabetes/
│
├── dataset/
│
├── templates/
│
├── static/
│
└── utils/
```

> The exact structure can vary slightly depending on the project version.

---

# 🚀 Installation & Setup

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd MultiDiseasePrediction
```

## 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure MySQL

Start **Apache and MySQL** using XAMPP.

Create/configure the project database according to `config.py`.

Run the database setup script if required:

```bash
python database_setup.py
```

## 5. Configure Email OTP

For password-reset email functionality, configure the required mail environment variables instead of committing credentials to GitHub.

Example:

```text
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email
```

**Never commit email passwords or app passwords to GitHub.**

## 6. Optional — Start Ollama

If using the local AI Health Assistant, ensure Ollama and the configured local model are available.

## 7. Run the Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 🔬 Research Contribution

The project explores whether a conventional disease-risk prediction system can be enhanced by combining:

1. Adaptive ensemble learning
2. Explainable AI
3. Model disagreement analysis
4. Longitudinal model-output tracking
5. Hypothetical What-If simulation
6. Personalized preventive-health information
7. Cross-disease intelligence
8. Prediction auditing and reproducibility

Rather than focusing only on classification accuracy, the project emphasizes **transparency, interpretability, longitudinal context, and responsible presentation of machine-learning predictions**.

---

# 🌍 Sustainable Development Goal Alignment

The project primarily aligns with:

### SDG 3 — Good Health and Well-Being

It explores the use of AI and data-driven systems for preventive-health awareness, early risk assessment, and accessible health information.

It also has supporting relevance to:

### SDG 9 — Industry, Innovation and Infrastructure

through the application of machine learning, explainable AI, and digital-health technologies.

---

# ⚠️ Disclaimer

This application is an **academic and research project**.

Predictions, probabilities, explanations, recommendations, simulations, and AI-generated information are intended for educational and research purposes only.

They:

- Do not constitute a medical diagnosis
- Do not confirm the presence or absence of disease
- Do not prescribe treatment or medication
- Should not be used as a substitute for professional medical evaluation

Users should consult qualified healthcare professionals for medical concerns.

---

# 👩‍💻 Author

**Malavika Manoj**  
Master of Computer Applications (MCA)

---

## ⭐ Support

If you find this academic project useful, consider giving the repository a ⭐.

Contributions, suggestions, and constructive feedback are welcome.

**Project:** ColdGuard AI  
**Domain:** Artificial Intelligence / Machine Learning / Cold-Chain Supply Chain  
**Type:** Academic Project
