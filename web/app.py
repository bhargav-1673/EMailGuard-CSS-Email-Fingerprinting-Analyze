import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request
from eml_parser import parse_eml
from css_extractor import extract_all_css

# detectors
from detectors.import_detector import detect_import_rules
from detectors.media_detector import detect_media_queries
from detectors.container_detector import detect_container_queries
from detectors.calc_detector import detect_calc
from detectors.fontface_detector import detect_fontface
from detectors.supports_detector import detect_supports

# pipeline
from correlation_engine import CorrelationEngine
from risk_scoring import calculate_risk_score
from reporter.html_reporter import generate_html_report

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded"

        file = request.files["file"]

        filepath = f"temp_{file.filename}"
        file.save(filepath)

        # Step 1: Parse
        html, metadata = parse_eml(filepath)

        # 🟢 Plain text email (UI improved)
        if html is None:
            return f"""
            <html>
            <head>
                <title>Email Analysis</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>

            <body class="bg-light">

            <div class="container mt-5">
                <div class="card shadow p-4 text-center">

                    <h3>📄 Plain Text Email</h3>

                    <p>This email contains <b>no HTML or CSS</b>.</p>
                    <p>No CSS-based fingerprinting possible.</p>

                    <span class="badge bg-success fs-5">SAFE</span>

                    <hr>

                    <p><b>Subject:</b> {metadata.get("subject", "N/A")}</p>
                    <p><b>From:</b> {metadata.get("from", "N/A")}</p>
                    <p><b>Date:</b> {metadata.get("date", "N/A")}</p>

                    <a href="/" class="btn btn-secondary mt-3">⬅ Analyze Another Email</a>

                </div>
            </div>

            </body>
            </html>
            """

        # Step 2: Extract CSS
        css_snippets = extract_all_css(html)

        # Step 3: Run detectors
        findings = []
        findings.extend(detect_import_rules(css_snippets))
        findings.extend(detect_media_queries(css_snippets))
        findings.extend(detect_container_queries(css_snippets))
        findings.extend(detect_calc(css_snippets))
        findings.extend(detect_fontface(css_snippets))
        findings.extend(detect_supports(css_snippets))

        # Step 4: Correlation
        corr_engine = CorrelationEngine(findings)
        insights = corr_engine.get_correlation_insights()

        # Step 5: Risk scoring
        risk = calculate_risk_score(findings, insights)

        # Step 6: Generate report
        output_path = "temp_report.html"
        generate_html_report(findings, metadata, risk, insights, output_path)

        with open(output_path, "r", encoding="utf-8") as f:
            html_report = f.read()

        # 🧹 OPTIONAL CLEANUP (safe)
        try:
            os.remove(filepath)
            os.remove(output_path)
        except:
            pass

        return html_report

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)