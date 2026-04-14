import os

from eml_parser import parse_eml
from css_extractor import extract_all_css

from detectors.import_detector import detect_import_rules
from detectors.media_detector import detect_media_queries
from detectors.container_detector import detect_container_queries
from detectors.calc_detector import detect_calc
from detectors.fontface_detector import detect_fontface
from detectors.supports_detector import detect_supports

from correlation_engine import CorrelationEngine
from risk_scoring import calculate_risk_score


def analyze_email(filepath):
    html, metadata = parse_eml(filepath)

    # Handle plain text
    if html is None:
        return {
            "score": 0,
            "label": "Safe"
        }

    css_snippets = extract_all_css(html)

    findings = []
    findings.extend(detect_import_rules(css_snippets))
    findings.extend(detect_media_queries(css_snippets))
    findings.extend(detect_container_queries(css_snippets))
    findings.extend(detect_calc(css_snippets))
    findings.extend(detect_fontface(css_snippets))
    findings.extend(detect_supports(css_snippets))

    corr = CorrelationEngine(findings)
    insights = corr.get_correlation_insights()

    risk = calculate_risk_score(findings, insights)

    return risk


def run_tests():
    base_path = "test_samples"

    total = 0
    safe_count = 0
    high_count = 0

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".eml"):
                total += 1
                path = os.path.join(root, file)

                result = analyze_email(path)

                print("-----")
                print("File:", file)
                print("Score:", result["score"])
                print("Label:", result["label"])

                if result["label"] == "Safe":
                    safe_count += 1
                if result["label"] in ["High", "Critical"]:
                    high_count += 1

    print("\n===== SUMMARY =====")
    print("Total Emails:", total)
    print("Safe:", safe_count)
    print("High/Critical:", high_count)


if __name__ == "__main__":
    run_tests()