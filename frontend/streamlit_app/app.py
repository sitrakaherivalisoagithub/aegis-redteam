import streamlit as st
import requests
import os

st.set_page_config(page_title="Aegis AI Red Team", layout="wide")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

def get_assessments():
    artifacts_dir = "artifacts"
    if not os.path.exists(artifacts_dir): return []
    return [d for d in os.listdir(artifacts_dir) if os.path.isdir(os.path.join(artifacts_dir, d))]

def dashboard():
    st.title("🛡️ Aegis AI Red Team - Dashboard")
    st.markdown("Bienvenue sur la plateforme d'audit de sécurité des applications IA.")
    
    col1, col2, col3, col4 = st.columns(4)
    ass_list = get_assessments()
    col1.metric("Total Assessments", len(ass_list))
    col2.metric("Running", "0")
    col3.metric("Reports Generated", sum(1 for a in ass_list if os.path.exists(f"artifacts/{a}/FINAL_REPORT.md")))
    col4.metric("High Findings", "0")

def new_assessment():
    st.title("➕ Nouvel Audit (Découverte & Modélisation)")
    st.markdown("Lancez une nouvelle analyse de dépôt. L'IA va scanner le dossier, modéliser les menaces et générer un plan de test.")
    
    with st.form("new_assessment_form"):
        name = st.text_input("Nom de l'Audit", value="Mon Audit Local")
        desc = st.text_area("Description")
        default_path = os.getcwd().replace('\\', '/')
        repo_path = st.text_input("Chemin du dépôt (Local)", value=default_path)
        submitted = st.form_submit_button("🚀 Lancer le Pipeline d'Analyse (Phase 1)")
        
        if submitted:
            try:
                payload = {"name": name, "description": desc, "repo_path": repo_path}
                response = requests.post(f"{API_BASE_URL}/assessments/", json=payload)
                if response.status_code == 201:
                    st.success(f"Audit créé ! Le pipeline tourne en arrière-plan (ID: {response.json()['id']}).")
                else:
                    st.error(f"Erreur: {response.text}")
            except Exception as e:
                st.error("API inaccessible. Avez-vous lancé FastAPI ?")

def artifacts_view():
    st.title("📂 Artefacts Générés")
    st.markdown("Consultez les fichiers d'analyse de l'IA.")
    assessments = get_assessments()
    if not assessments:
        st.info("Aucun audit trouvé.")
        return
        
    selected_ass = st.selectbox("Sélectionnez l'Audit ID", assessments)
    target_dir = os.path.join("artifacts", selected_ass)
    files = os.listdir(target_dir)
    
    for f in files:
        if f.endswith('.json'):
            with st.expander(f"📄 {f}"):
                with open(os.path.join(target_dir, f), 'r', encoding='utf-8') as file:
                    st.json(file.read())

def pentest_view():
    st.title("⚔️ Exécution de l'Attaque (Red Team)")
    st.markdown("Lancez les attaques générées dans le plan de test contre votre agent et évaluez les résultats.")
    assessments = get_assessments()
    if not assessments:
        st.info("Aucun audit trouvé. Allez d'abord dans 'Nouvel Audit'.")
        return
        
    selected_ass = st.selectbox("Sélectionnez l'Audit ID pour l'attaque", assessments)
    
    # Check if report already exists
    if os.path.exists(f"artifacts/{selected_ass}/FINAL_REPORT.md"):
        st.success("✅ Un rapport a déjà été généré pour cet audit. Consultez l'onglet 'Rapports'.")
        return
        
    endpoint = st.text_input("Endpoint de l'Agent cible", value="http://127.0.0.1:2024/chat")
    
    if st.button("🔥 Lancer les Attaques & Générer le Rapport"):
        with st.spinner("Exécution des attaques, requêtage de l'agent et évaluation LLM en cours... (Ceci peut prendre 1 à 2 minutes)"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/assessments/{selected_ass}/pentest", 
                    json={"agent_endpoint": endpoint}
                )
                if response.status_code == 200:
                    st.success("Pentest terminé avec succès ! Le rapport et les logs sont générés.")
                    st.balloons()
                else:
                    st.error(f"Erreur lors de l'attaque : {response.json().get('detail', response.text)}")
            except Exception as e:
                st.error("Impossible de contacter le backend FastAPI.")

def reports_view():
    st.title("📄 Rapport Final OWASP")
    assessments = get_assessments()
    if not assessments: return
    
    report_assessments = [a for a in assessments if os.path.exists(f"artifacts/{a}/FINAL_REPORT.md")]
    
    if not report_assessments:
        st.info("Aucun rapport généré. Allez dans l'onglet 'Exécution (Red Team)' pour lancer les tests.")
        return
        
    selected_ass = st.selectbox("Sélectionnez l'Audit", report_assessments)
    report_path = f"artifacts/{selected_ass}/FINAL_REPORT.md"
    logs_path = f"artifacts/{selected_ass}/execution_logs.json"
    
    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()
        
    st.download_button(
        label="📥 Télécharger le Rapport (Markdown)",
        data=report_content,
        file_name=f"OWASP_Report_{selected_ass}.md",
        mime="text/markdown",
        type="primary"
    )
    
    st.markdown("---")
    st.markdown(report_content)
    
    st.markdown("---")
    st.subheader("🕵️ Logs d'Exécution & Preuves")
    if os.path.exists(logs_path):
        with st.expander("Voir les requêtes exactes envoyées par le runner et les raisons de l'évaluateur"):
            with open(logs_path, "r", encoding="utf-8") as f:
                st.json(f.read())

st.sidebar.title("Aegis Platform")
page = st.sidebar.radio("Navigation", ["Dashboard", "Nouvel Audit", "Artefacts (JSON)", "Exécution (Red Team)", "Rapports OWASP"])

if page == "Dashboard": dashboard()
elif page == "Nouvel Audit": new_assessment()
elif page == "Artefacts (JSON)": artifacts_view()
elif page == "Exécution (Red Team)": pentest_view()
elif page == "Rapports OWASP": reports_view()
