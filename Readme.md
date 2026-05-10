# EMailGuard – CSS Email Fingerprinting Analyzer

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![NDSS 2025](https://img.shields.io/badge/NDSS-2025-red)](https://www.ndss-symposium.org/)

**EMailGuard** is a static analysis tool that detects CSS‑based fingerprinting techniques in HTML email (`.eml`) files. Based on the research paper *Cascading Spy Sheets* (NDSS 2025) by Trampert et al., it identifies six distinct fingerprinting vectors, correlates them to uncover multi‑stage attacks, and produces a risk‑scored HTML report with actionable mitigations.

> 🛡️ **No JavaScript, no network requests, no rendering** – pure static analysis.

---

## 📖 Table of Contents
- [EMailGuard – CSS Email Fingerprinting Analyzer](#emailguard--css-email-fingerprinting-analyzer)
  - [📖 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🧠 How It Works](#-how-it-works)
  - [📄 Research Basis](#-research-basis)
  - [🔬 Novel Contributions (Beyond the Paper)](#-novel-contributions-beyond-the-paper)
    - [1. 🔗 Correlation Engine — Multi-Stage Attack Detection](#1--correlation-engine--multi-stage-attack-detection)
    - [2. 📊 Unified Risk Scoring Model](#2--unified-risk-scoring-model)
    - [3. 🛡️ Defender-Perspective Static Analysis Tool](#3-️-defender-perspective-static-analysis-tool)
    - [4. 🧪 Synthetic Attack Dataset](#4--synthetic-attack-dataset)
    - [5. 📄 Actionable HTML Report with Per-Finding Mitigations](#5--actionable-html-report-with-per-finding-mitigations)
    - [6. 🖥️ Productized CLI + Flask Web Interface](#6-️-productized-cli--flask-web-interface)
  - [👥 Team \& Roles](#-team--roles)
    - [👤 J V M Bhargav (2023UCP1673) – Pipeline \& Core Logic](#-j-v-m-bhargav-2023ucp1673--pipeline--core-logic)
    - [👤 Pathi Jahnavi (2023UCP1595) – Detection \& Output](#-pathi-jahnavi-2023ucp1595--detection--output)
    - [🤝 Shared Responsibilities](#-shared-responsibilities)
  - [🛠 Installation](#-installation)
  - [🚀 Usage](#-usage)
    - [Command Line](#command-line)
    - [Web Interface (Flask)](#web-interface-flask)
  - [📂 Dataset](#-dataset)
  - [🏗 Architecture](#-architecture)
  - [🧪 Testing \& Evaluation](#-testing--evaluation)
  - [🔮 Future Work](#-future-work)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [📄 License](#-license)

---

## ✨ Features

- **6 CSS Fingerprinting Detectors** (directly from the paper):
  - `@import` external URL chain
  - `@media` conditional resource loading (viewport probing)
  - `@container` queries (font detection + exfiltration)
  - `calc()` with trigonometric functions (OS/architecture leakage)
  - `@font-face` remote font loading
  - `@supports` browser feature probing
- **Correlation Engine** – identifies multi‑stage fingerprinting (e.g., `@supports` → `@media` → `calc()`)
- **Risk Scoring** – weighted base scores + correlation boosts → final risk label (Safe / Moderate / High / Critical)
- **Command‑Line Interface (CLI)** – process single `.eml` files, output JSON or HTML
- **Web Interface** – upload `.eml` via Flask, view/download rich HTML report
- **Offline & Safe** – never fetches external resources or executes JavaScript

---

## 🧠 How It Works

```
.eml → Parser → CSS Extractor → 6 Detectors → Correlation → Risk Scoring → Report (CLI/Web)
```

1. **Parse** – extract HTML body and metadata (subject, sender, date) from `.eml`.
2. **Extract CSS** – from `<style>` tags, inline `style=""` attributes, `<link>` references, and `@import` statements.
3. **Detect** – run six pattern‑based detectors; each returns a `Finding` with snippet, risk level, and paper reference.
4. **Correlate** – combine findings to detect advanced attack patterns (e.g., progressive probing, exfiltration chains).
5. **Score** – calculate overall risk (0–100) and assign label.
6. **Report** – generate standalone HTML report (or print to console with `--verbose`).

---

## 📄 Research Basis

This project directly implements techniques from:

> **Leon Trampert, Daniel Weber, Lukas Gerlach, Christian Rossow, Michael Schwarz.** *Cascading Spy Sheets: Exploiting the Complexity of Modern CSS for Email and Browser Fingerprinting*. NDSS 2025.  
> [Paper PDF](https://www.ndss-symposium.org/ndss-paper/cascading-spy-sheets/) | [Official Artifact](https://github.com/cispa/cascading-spy-sheets)

| Technique | Paper Section |
|-----------|---------------|
| `@import` chain | IV‑B, VIII‑C2 |
| `@media` conditional | III‑B, IV‑A3 |
| `@container` query | IV‑A, Listing 1 |
| `calc()` expressions | V‑A, Listing 3 |
| `@font-face` remote | III‑B, IV‑C1 |
| `@supports` probe | IV‑B, IV‑C2 |
| Correlation & Scoring | – (our extension) |
| Mitigations | IX‑B |

We used the **official NDSS 2025 artifact** only for test `.eml` files (email PoCs). No code was copied; all detectors are original implementations.

---

## 🔬 Novel Contributions (Beyond the Paper)

The *Cascading Spy Sheets* paper is an **offensive research** work — it demonstrates that CSS fingerprinting attacks exist and are effective. EMailGuard is built on top of that foundation but contributes original work that the paper does not contain, flipping the perspective from attacker to **defender**.

### 1. 🔗 Correlation Engine — Multi-Stage Attack Detection

The paper analyzes each CSS fingerprinting technique **in isolation**. EMailGuard introduces an original **Correlation Engine** (`correlation_engine.py`) that detects when multiple techniques are combined into a coordinated, multi-stage fingerprinting chain.

For example, it detects the progressive profiling pattern `@supports` → `@media` → `calc()`, where the attacker first identifies the browser, then narrows the OS, then leaks the CPU architecture. This correlation-based detection is not present in the paper and is our most significant novel addition.

**Correlation boosts** are added to the risk score when chained patterns are found, distinguishing a casually-risky email from one that appears to be a deliberate, structured fingerprinting attempt.

### 2. 📊 Unified Risk Scoring Model

The paper evaluates fingerprinting accuracy across browser-OS combinations but provides **no unified risk metric** for individual emails. EMailGuard introduces an original **Risk Scoring System** (`risk_scoring.py`) that:

- Assigns weighted **base scores** per technique based on severity (e.g., `@import` chain scores higher than an isolated `@supports` probe).
- Applies **correlation boosts** from the Correlation Engine when chained patterns are detected.
- Produces a **normalized 0–100 score** with a four-tier label: **Safe / Moderate / High / Critical**.

This model gives email administrators and security researchers a single, actionable signal rather than a list of raw technique detections.

### 3. 🛡️ Defender-Perspective Static Analysis Tool

The paper's artifact is a set of proof-of-concept attack `.eml` files and browser evaluation scripts. There is **no tool for defenders** to analyze emails they receive. EMailGuard is an entirely original implementation that:

- Runs **fully offline** — no network calls, no CSS rendering, no JavaScript execution.
- Performs **pure static pattern analysis** against a `.eml` file, making it safe to run on untrusted emails.
- Maps every finding back to its specific **paper section** (e.g., `Section IV-B`), creating a traceable, research-grade output.

### 4. 🧪 Synthetic Attack Dataset

The paper's artifact includes PoC emails for the techniques it describes. EMailGuard adds **7 original synthetic attack emails** created by modifying and combining those PoCs to cover patterns the paper does not explicitly test:

| Variant | Description |
|---------|-------------|
| Nested `@media` | Multiple layers of conditional viewport probing |
| Obfuscated `calc()` | Trigonometric expressions split across nested expressions |
| Multiple `@import` | Chained import chains with recursive loading potential |
| Inline-only CSS | Fingerprinting via `style=""` attributes only (no `<style>` block) |
| Malformed CSS | Partially broken CSS that still triggers detection |
| Mixed inline + external | CSS split across `<style>` tags and `<link>` references |
| Multi-technique chain | Deliberate combination of ≥3 techniques to test the Correlation Engine |

These cover edge cases that any real-world static analyzer must handle, and they drive a separate suite of tests not present in the paper's artifact.

### 5. 📄 Actionable HTML Report with Per-Finding Mitigations

The paper describes two mitigations (unconditional preloading for browsers; email privacy proxy for email clients) in Section IX at a high level. EMailGuard produces a **self-contained HTML report** (via Jinja2) that:

- Surfaces the **exact matched CSS snippet** for each finding with an expandable view.
- Provides a **per-finding mitigation** drawn from the paper, customized to the specific technique detected (not just a generic summary).
- Includes a **Correlation Insights** section explaining why chained techniques raise the risk score.
- Is **fully self-contained** (no external CSS/JS) so it can be safely opened or shared without network access.

### 6. 🖥️ Productized CLI + Flask Web Interface

The paper's artifact is a research prototype intended for reproduction of results. EMailGuard is a **productized tool** with:

- A **CLI** (`main.py`) supporting `--verbose`, `--summary`, and `--output` modes.
- A **Flask web app** with file upload, in-browser report rendering, and HTML report download.
- **Deployment on Render**, making it accessible without local installation.
- Proper **error handling** for malformed MIME, non-UTF-8 encodings, empty CSS bodies, and invalid file types.

---

## 👥 Team & Roles

### 👤 J V M Bhargav (2023UCP1673) – Pipeline & Core Logic
- `.eml` parser & CSS extractor
- Detectors: `@import`, `@media`, `@container`
- Correlation engine
- CLI interface
- Integration & deployment (Render)

### 👤 Pathi Jahnavi (2023UCP1595) – Detection & Output
- Detectors: `calc()`, `@font-face`, `@supports`
- Risk scoring
- Flask web app backend
- HTML report generation (Jinja2, styling)

### 🤝 Shared Responsibilities
- Unit & integration tests
- Edge‑case testing
- Dataset creation (synthetic + clean)
- Documentation & PPT

---

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/EMailGuard.git
cd EMailGuard

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**`requirements.txt`**:
```
beautifulsoup4>=4.12
lxml>=4.9
jinja2>=3.1
flask>=2.3
pytest>=7.4
tinycss2>=1.2
```

---

## 🚀 Usage

### Command Line

```bash
# Basic analysis – generates HTML report
python main.py --input sample.eml --output report.html

# Verbose output (prints findings to console)
python main.py --input sample.eml --verbose

# Summary only (risk score + label)
python main.py --input sample.eml --summary
```

**Example output (verbose):**
```
[!] CRITICAL: @import chain
    Snippet: @import url("http://evil.com/tracker.css");
    Paper: Section IV-B, VIII-C2
    Mitigation: Use a proxy that inlines external resources.

[!] HIGH: calc() expression with trig functions
    Snippet: width: calc(sin(45deg) * 100px);
    Paper: Section V-A, Listing 3
    Mitigation: Preload all dynamic resources.

Risk score: 72/100 (Critical)
Report saved to report.html
```

### Web Interface (Flask)

```bash
python web/app.py
# Open http://127.0.0.1:5000 in your browser
```

Upload an `.eml` file, and you'll get a detailed HTML report with expandable CSS snippets, correlation insights, and mitigation advice.

---

## 📂 Dataset

We evaluated EMailGuard on a curated dataset of **23 emails** across three categories:

| Category | Count | Source |
|----------|-------|--------|
| Paper PoCs | 6 | Official NDSS 2025 artifact (`pocs/email/`) |
| Synthetic attacks | 7 | Created by modifying PoCs (nested `@media`, obfuscated `calc()`, multiple `@import`, inline‑only CSS, malformed CSS) |
| Clean emails | 10 | Exported newsletters (no CSS fingerprinting) |

All test emails are in the `test_samples/` folder of this repository.

---

## 🏗 Architecture

![EMailGuard Architecture](architecture.png)

The pipeline flows as follows:
1. `.eml file` → `eml_parser.py` → `css_extractor.py`
2. CSS snippets fed in parallel to all **6 detectors**
3. Each detector returns `Finding` patterns → `correlation_engine.py`
4. Correlation boost → `risk_scoring.py` → `html_reporter.py`
5. Output via **CLI** (`main.py`), **Flask Web App**, or standalone **HTML Report**

---

## 🧪 Testing & Evaluation

Run all tests:
```bash
pytest tests/
```

**Test coverage:**
- Unit tests for each detector (positive & negative cases)
- Integration tests for the full pipeline on all dataset emails
- Edge cases: malformed HTML, empty CSS, only inline styles
- False‑positive measurement on clean emails

**Evaluation metrics (from our runs):**

| Metric | Result |
|--------|--------|
| Paper PoCs detection rate | **100%** (6/6) |
| Synthetic attacks detection rate | **85.7%** (6/7) |
| False positive rate on clean emails | **0%** (0/10) |
| Average processing time | **1.2s** (range: 0.8–2.0s, on i7‑1255U) |

*Detailed results and per-detector accuracy are in the [project report](report.pdf).*


---

## 🔮 Future Work

- **Visualization:** Charts showing technique distribution per email.
- **Explainability:** Plain‑English explanations of what each finding reveals about the user.
- **Automated mitigation:** Integrate with email filters (e.g., rewrite suspicious CSS to `style` attributes).
- **Browser extension:** Real‑time scanning of email in web clients (Gmail, Outlook).
- **ML‑based classification:** For obfuscated or novel patterns.

---

## 🙏 Acknowledgments

- The authors of *Cascading Spy Sheets* for their groundbreaking research and publicly available artifact.
- Dr. Ramesh Babu Bathula for guidance and feedback throughout the project.

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ by J V M Bhargav & Pathi Jahnavi for the Computer and Network Security course (22CST352), MNIT Jaipur.*