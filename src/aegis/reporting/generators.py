from jinja2 import Template
from src.aegis.domain.schemas.evaluation import Finding
from typing import List
from datetime import datetime

FRENCH_OWASP_TEMPLATE = """Rapport d'Évaluation de Sécurité — OWASP Top 10 pour LLM

• Nom du Projet / Application : {{ project_name }}
• Date de l'évaluation : {{ date }}
• Évaluateur(s) / Auditeur(s) : Aegis AI Red Team
• Version du référentiel OWASP : OWASP Top 10 for LLM Applications (2025/2026)

1. Résumé exécutif (Executive Summary)

• Score de risque global : {{ global_risk }}
• Nombre de vulnérabilités identifiées : {{ findings|length }}
• Objectif du rapport : Présenter l'état de la sécurité de l'application LLM face aux dix principaux vecteurs de menaces identifiés par l'OWASP, évaluer l'impact métier et proposer un plan de remédiation priorisé.

2. Tableau de Synthèse des Vulnérabilités (OWASP Top 10 LLM)

| ID | Vulnérabilité (OWASP) | Statut / Risque | Sévérité |
|---|---|---|---|
{% for f in findings %}| {{ f.standard_reference }} | {{ f.title }} | {{ 'vulnérable' if f.status == 'confirmed' else 'conforme' }} | {{ f.severity|capitalize }} |
{% endfor %}

3. Détail des Constats et Plan de Remédiation

{% for f in findings %}
[{{ f.standard_reference }}] — {{ f.title }}

• Niveau de risque : {{ f.severity|capitalize }}
• Description du risque : {{ f.description }}
• Preuve de concept (PoC) / Scénario testé :
    • Entrée injectée / Prompt utilisé : Reportez-vous aux logs d'exécution.
    • Réponse obtenue du modèle : L'agent a renvoyé une réponse évaluée comme vulnérable.
• Impact potentiel : {{ f.impact }}
• Recommandations / Mesures correctives :
{% for r in f.recommendations %}    • {{ r }}
{% endfor %}
{% endfor %}

4. Recommandations Générales & Architecture de Sécurité

1. Cloisonnement des flux (Trust Boundaries) : Cartographier tous les points d'entrée (prompt utilisateur, documents RAG, résultats d'outils/API, mémoire de session) et ne jamais traiter du contenu externe comme du code ou une instruction fiable.
2. Principe de moindre privilège (Agency) : Limiter les capacités d'action du LLM (outils, appels API, base de données) et exiger une validation déterministe (humaine ou logicielle) avant toute action critique.
3. Validation des sorties : Traiter le texte généré par le LLM comme des données non fiables avant de l'afficher dans une interface web (prévention XSS) ou de l'exécuter.
4. Monitoring et rate-limiting : Surveiller les volumes de tokens consommés et détecter les boucles ou les attaques par déni de service (LLM10).
Pour plus de détails sur le référentiel officiel, consultez le document de référence OWASP Top 10 for LLM Applications ou explorez les ressources du OWASP GenAI Security Project.
"""

class MarkdownReportGenerator:
    def generate_executive_report(self, assessment_id: str, findings: List[Finding]) -> str:
        template = Template(FRENCH_OWASP_TEMPLATE)
        
        # Calculate global risk
        critical_high = sum(1 for f in findings if f.severity in ["critical", "high"])
        global_risk = "Critique/Élevé" if critical_high > 0 else "Moyen/Faible"
        
        return template.render(
            project_name=f"Audit {assessment_id}",
            date=datetime.utcnow().strftime("%d/%m/%Y"),
            findings=findings,
            global_risk=global_risk
        )

    def generate_technical_report(self, assessment_id: str, findings: List[Finding]) -> str:
        return self.generate_executive_report(assessment_id, findings)
