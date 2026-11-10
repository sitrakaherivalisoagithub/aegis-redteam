import streamlit as st
import requests
import os
import json as json_lib

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
        default_path = os.getcwd().replace('\\\\', '/')
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
    st.markdown("Exploitez les endpoints découverts par l'IA lors de la phase d'analyse de code.")
    assessments = get_assessments()
    if not assessments:
        st.info("Aucun audit trouvé. Allez d'abord dans 'Nouvel Audit'.")
        return
        
    selected_ass = st.selectbox("Sélectionnez l'Audit ID pour l'attaque", assessments)
    
    if os.path.exists(f"artifacts/{selected_ass}/FINAL_REPORT.md"):
        st.success("✅ Un rapport a déjà été généré pour cet audit. Consultez l'onglet 'Rapports OWASP'.")
        return

    # Lecture de l'inventaire
    endpoints = []
    inv_path = f"artifacts/{selected_ass}/inventory.json"
    if os.path.exists(inv_path):
        try:
            with open(inv_path, 'r', encoding='utf-8') as f:
                inv_data = json_lib.load(f)
                endpoints = inv_data.get("api_endpoints", [])
        except Exception as e:
            st.error(f"Erreur lors de la lecture de l'inventaire: {e}")

    st.subheader("Configuration de la Cible (Target)")
    
    options = ["Custom (Configuration Manuelle)"] + [e.get("path", "Unknown") for e in endpoints]
    selected_path = st.selectbox("🎯 Endpoints détectés dans le code source", options)
    
    def_path = ""
    def_auth = "none"
    def_header = "X-API-Key"
    def_template = '{\n  "messages": [\n    {"role": "user", "content": "{{PROMPT}}"}\n  ]\n}'
    def_resp = ""
    
    if selected_path != "Custom (Configuration Manuelle)":
        ep = next(e for e in endpoints if e.get("path") == selected_path)
        def_path = ep.get("path", "")
        def_auth = ep.get("authentication_type", "none")
        def_header = ep.get("auth_header") or "X-API-Key"
        
        tpl = ep.get("request_template")
        if isinstance(tpl, dict):
            def_template = json_lib.dumps(tpl, indent=2)
        elif isinstance(tpl, str):
            def_template = tpl
            
        def_resp = ep.get("response_field") or ""
        
        st.info(f"💡 Endpoint importé depuis l'inventaire ! Sources associées : {', '.join(ep.get('source_references', []))}")

    col_a, col_b = st.columns([3, 1])
    base_url = col_a.text_input("Base URL (ex: serveur de prod ou staging)", value="http://127.0.0.1:2024")
    final_path = col_b.text_input("Path", value=def_path)
    
    col1, col2 = st.columns(2)
    auth_opts = ["none", "bearer", "api_key", "custom_header"]
    auth_index = auth_opts.index(def_auth.lower()) if def_auth.lower() in auth_opts else 0
    auth_type = col1.selectbox("Type d'Authentification", auth_opts, index=auth_index)
    auth_header = col2.text_input("Nom du Header (si custom_header/api_key)", value=def_header)
    
    api_key = st.text_input("Clé API / Token / Password (non stockée, utilisée en live)", type="password")
    
    with st.expander("Configuration Avancée (Template JSON)", expanded=True):
        st.markdown("Utilisez `{{PROMPT}}` pour indiquer où la charge malveillante doit être injectée.")
        template_str = st.text_area("Request Template (JSON)", value=def_template, height=150)
        response_field = st.text_input("Response Field Extraction (ex: `response` ou `choices.0.message.content`)", value=def_resp)

    if st.button("🔥 Lancer les Attaques & Générer le Rapport"):
        try:
            req_template = json_lib.loads(template_str) if template_str.strip() else None
        except Exception:
            st.error("Le format du Request Template n'est pas un JSON valide.")
            return

        with st.spinner("Bombardement de la cible et évaluation LLM en cours... (Ceci peut prendre 1 à 2 minutes)"):
            try:
                full_endpoint = base_url.rstrip('/') + "/" + final_path.lstrip('/')
                payload = {
                    "agent_endpoint": full_endpoint,
                    "auth_type": auth_type,
                    "auth_header": auth_header,
                    "api_key": api_key,
                    "request_template": req_template,
                    "response_field": response_field
                }
                response = requests.post(f"{API_BASE_URL}/assessments/{selected_ass}/pentest", json=payload)
                if response.status_code == 200:
                    st.success("Pentest terminé avec succès ! Le rapport est disponible dans l'onglet Rapports OWASP.")
                    st.balloons()
                else:
                    st.error(f"Erreur lors de l'attaque : {response.json().get('detail', response.text)}")
            except Exception as e:
                st.error(f"Impossible de contacter le backend FastAPI : {e}")

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
