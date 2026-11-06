from src.aegis.domain.schemas.evaluation import Finding
from src.aegis.reporting.generators import MarkdownReportGenerator

def test_report_generation():
    # Mock a finding
    finding = Finding(
        finding_id="FINDING-REPORT-TEST",
        assessment_id="ASSESS-999",
        title="Prompt Injection",
        description="Able to override system prompt via standard chat payload.",
        standard="OWASP LLM Top 10",
        standard_version="2026",
        standard_reference="LLM01",
        affected_component="Chat API",
        severity="high",
        confidence=1.0,
        status="confirmed",
        impact="Adversary bypasses rules.",
        evidence_ids=["EVIDENCE-001"],
        root_cause="Inadequate input validation.",
        recommendations=["Implement robust prompt boundary defenses."]
    )
    
    generator = MarkdownReportGenerator()
    
    executive_md = generator.generate_executive_report(assessment_id="ASSESS-999", findings=[finding])
    assert "Critical/High Risks:** 1" in executive_md
    assert "LLM01" in executive_md
    
    technical_md = generator.generate_technical_report(assessment_id="ASSESS-999", findings=[finding])
    assert "FINDING-REPORT-TEST" in technical_md
    assert "`EVIDENCE-001`" in technical_md
    
    print("Report generation successful! Preview of Executive Report:\n")
    print(executive_md)

if __name__ == "__main__":
    test_report_generation()
