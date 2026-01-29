

# 🛡️ FinTech Risk Intelligence  
**AI-Powered Fraud & Customer Vulnerability Risk Platform (FCA-Aligned)**

FinTech Risk Intelligence is a **production-oriented AI system** designed to identify **fraud, customer vulnerability, and compliance risks** in financial interactions.

The platform combines **machine learning, NLP, and explainable AI** to generate **audit-ready risk decisions** aligned with **UK FCA expectations**, ensuring every automated decision is **traceable, explainable, and reviewable**.

This project was built as a **client-style ML system**, focusing on real-world constraints: accuracy, explainability, latency, auditability, and operational robustness.

---

## 🎯 Problem Statement

Financial institutions face increasing regulatory pressure to:
- Detect fraud and risky behaviour early  
- Identify vulnerable customers from unstructured text  
- Provide **clear evidence** for every automated decision  
- Avoid black-box AI systems that regulators cannot audit  

Traditional rule-based systems are brittle, while many ML models lack transparency.

**FinTech Risk Intelligence bridges this gap.**

---

## 🧠 Solution Overview

The system evaluates financial events using **two complementary AI pipelines**:

### 1️⃣ Fraud Risk Detection (Structured ML)
- Transaction-level features
- Behavioural signals
- Anomaly indicators

### 2️⃣ Textual Risk & Vulnerability Detection (NLP)
- Customer messages, complaints, support conversations
- Detection of stress, confusion, coercion, or financial vulnerability
- Context-aware NLP classification (not keyword matching)

The outputs are **combined into a unified risk decision**, supported by **evidence and explanations**.

---

## 🧱 System Architecture

Incoming Events
│
├── Structured Data (Transactions)
│       └── Fraud ML Model
│
├── Unstructured Text (Messages / Notes)
│       └── NLP Risk Classifier
│
└── Combined Risk Engine
├── Risk Score
├── Risk Category
├── Evidence & Features
└── LLM Explanation
│
Audit-Ready Decision Store

---

## ⚙️ Core Capabilities

### 🔍 Fraud Detection
- Supervised ML model trained on synthetic financial patterns
- Achieved **92% precision** on validation data
- Optimized for **low false positives** (critical for compliance)

---

### 📝 NLP-Based Risk & Vulnerability Analysis
- Contextual text classification (not keyword rules)
- Achieved **87% recall** on vulnerable-case detection
- Designed for compliance use cases (fair treatment, clarity, consent)

---

### 🧾 Audit & Explainability Layer
Every decision includes:
- Model outputs
- Key features contributing to risk
- NLP evidence snippets
- Human-readable explanation (LLM-generated)

This enables:
- Regulatory reviews
- Internal audits
- Analyst trust and transparency

---

### ⚡ Production-Focused Design
- Stateless inference services
- Deterministic scoring logic
- Clear separation between models, logic, and explanations
- Designed for **sub-200ms p95 latency**

---

## 📊 Example Risk Output

```json
{
  "risk_level": "HIGH",
  "risk_type": ["FRAUD", "CUSTOMER_VULNERABILITY"],
  "confidence": 0.91,
  "evidence": {
    "transaction_features": ["amount_spike", "geo_anomaly"],
    "text_signals": ["confusion_about_charges", "financial_distress"]
  },
  "explanation": "The customer shows signs of financial stress while the transaction pattern deviates significantly from historical behaviour."
}
```


⸻

🛠️ Tech Stack

Core
	•	Python
	•	FastAPI

Machine Learning
	•	PyTorch
	•	scikit-learn
	•	Fraud classification models
	•	Feature-based anomaly detection

NLP & LLMs
	•	Transformer-based text models
	•	LangChain (LLM orchestration)
	•	Embeddings for semantic analysis

Explainability & Audit
	•	Evidence logging
	•	LLM-generated explanations
	•	Deterministic scoring rules

⸻

📁 Project Structure

fintech-risk/
├── api/                # FastAPI routes
├── models/             # ML & NLP models
├── risk_engine/        # Risk aggregation logic
├── explainability/     # LLM explanations
├── synthetic_data/     # Generated datasets (non-sensitive)
├── notebooks/          # Experiments & validation
├── scripts/            # Data generation & utilities
└── README.md


⸻

🚀 Getting Started

git clone https://github.com/amanramasharma/fintech-risk.git

cd fintech-risk

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn api.main:app --reload

API available at:

http://127.0.0.1:8000


⸻

🔐 Data & Security Notes
	•	No real customer data is used
	•	All datasets are synthetic and non-identifiable
	•	Secrets are managed via environment variables
	•	Designed with privacy-by-design principles

⸻

📈 Why This Project Matters

This project demonstrates:
	•	Production ML thinking, not notebook experiments
	•	Regulatory-aware AI design
	•	End-to-end ownership: data → models → APIs → explanations
	•	Realistic fintech constraints: accuracy, latency, auditability

It reflects how ML systems are actually built and deployed in regulated financial environments.

⸻

👨‍💻 Author

- Aman Sharma
- Machine Learning Engineer
- MSc Data Science — University of Surrey
	•	GitHub: https://github.com/amanramasharma
	•	LinkedIn: https://www.linkedin.com/in/amanramasharma/

⸻

📌 Disclaimer

This project is for educational and portfolio purposes only and does not constitute financial or regulatory advice.

