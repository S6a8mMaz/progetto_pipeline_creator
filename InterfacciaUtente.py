import streamlit as st  # Libreria per creare UI web in Python
import requests  # Libreria per chiamare le API FastAPI
import streamlit.components.v1 as components

API_URL = "http://127.0.0.1:8000"  # URL del backend FastAPI

st.set_page_config(page_title="Pipeline Creator", layout="centered")
st.markdown("""
<style>
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* SOLO i tre pulsanti:
   1 = Change Context
   2 = Object Types
   3 = Algorithms
   4 = Saved Pipelines
   5 = Pipeline Builder
   6 = Tutorial
*/

/* dimensione più piccola solo per 2,3,4 */
section[data-testid="stSidebar"] div.stButton:nth-of-type(2) > button,
section[data-testid="stSidebar"] div.stButton:nth-of-type(3) > button,
section[data-testid="stSidebar"] div.stButton:nth-of-type(4) > button {
    min-height: 30px !important;
    padding: 2px 8px !important;
    border-radius: 8px !important;
}

/* testo tutto a sinistra solo per 2,3,4 */
section[data-testid="stSidebar"] div.stButton:nth-of-type(2) > button p,
section[data-testid="stSidebar"] div.stButton:nth-of-type(3) > button p,
section[data-testid="stSidebar"] div.stButton:nth-of-type(4) > button p {
    width: 100% !important;
    margin: 0 !important;
    text-align: left !important;
    font-size: 13px !important;
    line-height: 1.1 !important;
}

/* allinea il contenuto interno a sinistra solo per 2,3,4 */
section[data-testid="stSidebar"] div.stButton:nth-of-type(2) > button > div,
section[data-testid="stSidebar"] div.stButton:nth-of-type(3) > button > div,
section[data-testid="stSidebar"] div.stButton:nth-of-type(4) > button > div {
    justify-content: flex-start !important;
    align-items: center !important;
}

/* meno spazio verticale solo tra 2,3,4 */
section[data-testid="stSidebar"] div.stButton:nth-of-type(2),
section[data-testid="stSidebar"] div.stButton:nth-of-type(3),
section[data-testid="stSidebar"] div.stButton:nth-of-type(4) {
    margin-bottom: 4px !important;
}

</style>
""", unsafe_allow_html=True)

if "app_started" not in st.session_state:
    st.session_state.app_started = False

if not st.session_state.app_started:

    st.title("Welcome to Pipeline Builder")

    st.markdown("""
    **Pipeline Builder** is an application for guided design of data processing pipelines. It allows you to define data types (*Object Types*) and transformation algorithms, and combine them to build consistent pipelines step by step.
                
    ---
                
    ##### ⚙️ How it works
                
    At startup, you will be asked to choose an operating context, and after that, you will have access to the main menu:
    - Object Types: View/Define/Delete data types
    - Algorithms: View/Define/Delete transformations between data types
    - Saved Pipelines: View and reuse previously created pipelines
    - Pipeline Builder: Build pipelines step by step, choosing the initial and the final type. The system will suggest only valid transformations
                
    ---
    ##### 🌳 Context inheritance

    Elements (*Object Types*, *Algorithms*, *Pipelines*) defined in a parent context are automatically available in child contexts.
    A pipeline created in a higher-level context can therefore be reused in derived contexts.
                
    -----    

    🚀 Click **Next** to select a context and start building your pipeline.
    """)

    if st.button("Next"):
        st.session_state.app_started = True
        st.session_state.current_view = "context"
        st.rerun()
    
    st.stop()

# =========================
# INIT SESSION STATE
# =========================
if "show_context_panel" not in st.session_state:
    st.session_state.show_context_panel = False

if "active_context_id" not in st.session_state:
    st.session_state.active_context_id = None

if "current_view" not in st.session_state:
    st.session_state.current_view = "context"  # prima schermata

# =========================
# SIDEBAR + CONTEXT CORE
# =========================
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 300px !important;
}
</style>
""", unsafe_allow_html=True)

# carica contexts
try:
    res = requests.get(f"{API_URL}/contexts")
    contexts = res.json() if res.status_code == 200 else []
except:
    contexts = []

context_map = {c["id"]: c["name"] for c in contexts}

# init active context
if st.session_state.active_context_id is None and contexts:
    st.session_state.active_context_id = contexts[0]["id"]

context_id = st.session_state.active_context_id
if not context_id and not st.session_state.show_context_panel:
    st.error("❌ ERROR: no context found")
    st.stop()

# ===== SIDEBAR =====
st.sidebar.markdown("## Context")

if st.sidebar.button("Change Context"):
    st.session_state.current_view = "context"
    st.rerun()

if context_id:
    st.sidebar.info(f"Active context: {context_map.get(context_id)} ")
else:
    st.sidebar.warning("No context selected")

if st.session_state.current_view == "main":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Menu")

    menu_options = [
        "Object Types",
        "Algorithms",
        "Saved Pipelines"
    ]

    if "page" not in st.session_state:
        st.session_state.page = "Object Types"

    if "menu_page" not in st.session_state:
        st.session_state.menu_page = "Object Types"

    selected_page = st.sidebar.radio(
        "Vai a:",
        menu_options,
        index=menu_options.index(st.session_state.menu_page)
    )

    # cambia pagina solo se l'utente cambia davvero il radio
    if selected_page != st.session_state.menu_page:
        st.session_state.menu_page = selected_page
        st.session_state.page = selected_page
        st.rerun()

    if st.sidebar.button("🔗⚙️ Pipeline Builder 🔗⚙️", use_container_width=True):
        st.session_state.page = "Pipeline Builder"
        st.rerun()

st.sidebar.markdown("---")

if st.sidebar.button("📘 Tutorial"):
    st.session_state.app_started = False
    st.rerun()

#################################################################################################

def show_context_page():

    st.title("Contexts")
    st.caption("Select your context")

    try:
        res = requests.get(f"{API_URL}/contexts")
        contexts = res.json() if res.status_code == 200 else []
    except:
        contexts = []

    tab1, tab2, tab3 = st.tabs(["📄 List", "➕ Create", "🗑️ Delete"])

    # ===== LISTA =====
    with tab1:
        if not contexts:
            st.info("No context available")
        else:
            header1, header2, header3 = st.columns([1, 1, 1])
            with header1:st.markdown("**Name**")
            with header2:st.markdown("**ID**")
            with header3:st.markdown("")

            for c in contexts:
                col1, col2, col3 = st.columns([1,1,1])

                with col1:
                    st.write(c["name"])
                with col2:
                    st.write(c["id"]) 

                with col3:
                    if st.button("Select", key=f"sel_ctx_main_{c['id']}"):
                        st.session_state.active_context_id = c["id"]
                        st.session_state.current_view = "main"
                        st.rerun()

    # ===== CREA =====
    with tab2:
        new_name = st.text_input("Name")

        parent_options = {
            "None": None,
            **{c['name']: c["id"] for c in contexts}
        }

        selected_parent = st.selectbox("Parent", list(parent_options.keys()))
        parent_id = parent_options[selected_parent]

        if st.button("Create context"):
            res = requests.post(
                f"{API_URL}/contexts",
                json={"name": new_name, "parent_id": parent_id}
            )
            if res.status_code == 200:
                st.success("Created")
                st.rerun()
            else:
                st.error(res.text)

    # ===== DELETE =====
    with tab3:
        if contexts:
            ctx_map = {c['name']: c["id"] for c in contexts}
            selected = st.selectbox("Select", list(ctx_map.keys()))

            if st.button("Delete"):
                res = requests.delete(f"{API_URL}/contexts/{ctx_map[selected]}")
                if res.status_code == 200:
                    st.success("Deleted")
                    st.rerun()
                else:
                    st.error(res.text)
    
        st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
    st.subheader("Contexts Hierarchy")

    if not contexts:
        st.info("No context available")
        return

    children_map = {}

    for c in contexts:
        children_map.setdefault(c["id"], [])

    roots = []
    for c in contexts:
        parent_id = c["parent_id"]
        if parent_id is None:
            roots.append(c)
        else:
            children_map.setdefault(parent_id, []).append(c)

    # opzionale: ordina alfabeticamente i figli
    for context_id in children_map:
        children_map[context_id] = sorted(
            children_map[context_id],
            key=lambda x: x["name"].lower()
        )

    roots = sorted(roots, key=lambda x: x["name"].lower())

    def build_ascii_tree(node, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        line = f"{prefix}{connector}{node['name']}"

        children = children_map.get(node["id"], [])
        lines = [line]

        child_prefix = prefix + ("    " if is_last else "│   ")

        for i, child in enumerate(children):
            last_child = (i == len(children) - 1)
            lines.extend(build_ascii_tree(child, child_prefix, last_child))

        return lines

    tree_lines = []

    for root in roots:
        tree_lines.append(root["name"])
        children = children_map.get(root["id"], [])

        for i, child in enumerate(children):
            last_child = (i == len(children) - 1)
            tree_lines.extend(build_ascii_tree(child, "", last_child))

        tree_lines.append("")

    tree_text = "\n".join(tree_lines)

    html = f"""
    <div style="
        font-family: Consolas, 'Courier New', monospace;
        font-size: 16px;
        line-height: 1.6;
        white-space: pre;
        padding: 10px 0 0 0;
    ">{tree_text}</div>
    """

    height = max(220, 40 + len(tree_lines) * 24)
    components.html(html, height=height, scrolling=False)

def show_pipeline_builder():

    st.markdown("""
    <style>
    h1 {
        font-size: 28px !important;
    }
    h2 {
        font-size: 22px !important;
    }
    h3 {
        font-size: 18px !important;
    }

    /* riduce spazi verticali */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Pipeline Builder")

    if "session_id" not in st.session_state:  # Se non esiste una sessione attiva
        st.session_state.session_id = None  # Inizializza la sessione a None

    # ========================
    # CARICA OBJECT TYPES DAL BACKEND
    # ========================
    try:  # Prova a contattare il backend
        response = requests.get(
            f"{API_URL}/object-types/",
            params={"context_id": context_id},
            timeout=5
        )

        if response.status_code == 200:  # Se la risposta è OK
            object_types = [obj["name"] for obj in response.json()]  # Estrae i nomi dei tipi
        else:
            object_types = []  # Fallback a lista vuota se errore HTTP

    except Exception as e:  # Gestisce errori di connessione o timeout
        st.error(f"Backend non attivo: {e}")  # Mostra messaggio di errore
        object_types = []  # Imposta lista vuota

    # ========================
    # DROPDOWN DI SELEZIONE
    # ========================
    start_type = st.selectbox(
        "Start Type",  # Etichetta menu start
        object_types,  # Lista dei tipi disponibili
        index=None,  # Nessuna selezione iniziale
        placeholder="Select type"  # Testo mostrato prima della selezione
    )

    end_type = st.selectbox(
        "Target Type",  # Etichetta menu end
        [t for t in object_types if t != start_type] if start_type else object_types,  # Esclude start_type da end_type
        index=None,  # Nessuna selezione iniziale
        placeholder="Select type"  # Testo mostrato prima della selezione
    )

    if "pipeline_name" not in st.session_state:
        st.session_state.pipeline_name = ""

    st.text_input(
        "Pipeline name",
        key="pipeline_name"
    )

    disabled = (start_type is None or end_type is None)  # Disabilita il bottone se manca una selezione

    if not st.session_state.session_id:

        if st.button("Start Pipeline", disabled=disabled):
            response = requests.post(
                f"{API_URL}/pipelines/start-composition",
                params={
                    "start_type": start_type,
                    "end_type": end_type,
                    "context_id": context_id
                },
                timeout=5
            )

            if response.status_code == 200:
                st.session_state.session_id = response.json()["session_id"]
                st.success("Session started!")
                st.rerun()
            else:
                error_detail = response.json().get("detail", "Errore sconosciuto")
                st.error(f"❌ {error_detail}")

    else:
        # 🔥 SESSIONE ATTIVA
        if st.button("🔄 Restart pipeline", key="restart_main"):

            st.session_state.session_id = None

            if "pipeline_name" in st.session_state:
                del st.session_state["pipeline_name"]

            st.rerun()

    # ========================
    # STEP 2: COMPOSIZIONE
    # ========================
    if st.session_state.session_id:  # Se esiste una sessione attiva

        response = requests.get(
            f"{API_URL}/pipelines/next-steps/{st.session_state.session_id}",  # Endpoint per ottenere il prossimo stato della pipeline
            timeout=5  # Timeout richiesta
        )

        if response.status_code != 200:
            if response.status_code == 404:
                st.warning("Sessione scaduta o non valida")
                # reset controllato
                st.session_state.session_id = None

                if st.button("🔄 Restart pipeline", key="restart_404"):
                    st.rerun()

                st.stop()

            st.error("Errore nel recupero degli step")
            st.stop()
        else:
            data = response.json()  # Estrae JSON dalla risposta
            total_cost = data.get("total_cost", 0)

            # ========================
            # MOSTRA PIPELINE
            # ========================
            st.subheader("Current Pipeline")

            col_main, col_side = st.columns([10, 3])
            with col_main:

                if data["pipeline"]:
                    html = """
                    <style>
                    .pipeline-table {
                        border-collapse: collapse;
                        font-family: monospace;
                    }

                    .pipeline-table td {
                        padding: 1px 4px;
                        white-space: nowrap;
                    }

                    .arrow {
                        text-align: center;
                        font-size: 10px;
                    }
                    </style>

                    <table class="pipeline-table">
                    """

                    for i, step in enumerate(data["pipeline"], start=1):
                        parts = step.split("--")
                        input_type = parts[0].strip()
                        alg_part = parts[1]
                        output_type = parts[2].replace(">", "").strip()
                        algorithm = alg_part.replace("[", "").replace("]", "").strip()

                        html += f"""
                        <tr>
                            <td>{i}</td>
                            <td>{input_type}</td>
                            <td class="arrow">──▶</td>
                            <td><b>{algorithm}</b></td>
                            <td class="arrow">──▶</td>
                            <td>{output_type}</td>
                        </tr>
                        """

                    html += "</table>"

                    height = 10 + len(data["pipeline"]) * 17
                    components.html(html, height=height, scrolling=False)

                else:
                    st.write("*Pipeline Empty*")
            
            with col_side:
                st.markdown("""
                <style>
                .info-box {
                    border: 1px solid #e6e6e6;
                    border-radius: 10px;
                    padding: 10px;
                    text-align: center;
                    background-color: #fafafa;
                    margin-top: -10px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                }
                .info-title {
                    font-size: 10px;
                    color: #888;
                    margin-bottom: 5px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .info-value {
                    font-size: 15px;
                    font-weight: bold;
                }
                </style>
                """, unsafe_allow_html=True)

                # 🎯 LOGICA DINAMICA
                if data["is_complete"]:
                    content = f"""
                    <div class="info-box">
                        <div class="info-title">Total Cost</div>
                        <div class="info-value" style="color:#2e7d32;">
                            {total_cost}
                        </div>
                    </div>
                    """
                else:
                    content = f"""
                    <div class="info-box">
                        <div class="info-title">Current Type</div>
                        <div class="info-value" style="color:#1565c0;">
                            {data['current_type']}
                        </div>
                    </div>
                    """

                st.markdown(content, unsafe_allow_html=True)

            if data["is_complete"]:
                st.markdown("<div style='margin-top:30px'></div>", unsafe_allow_html=True)
                st.success("Pipeline completed")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("💾 Save pipeline"):

                        if not st.session_state.pipeline_name:
                            st.warning("Inserisci un nome per la pipeline")
                        else:
                            res = requests.post(
                                f"{API_URL}/pipelines/save-pipeline/{st.session_state.session_id}",
                                json={
                                    "name": st.session_state.pipeline_name
                                },
                                timeout=5
                            )
                            if res.status_code == 200:
                                st.session_state["pipeline_saved"] = (
                                    f'✅ Pipeline "{st.session_state.pipeline_name}" '
                                    f'(from "{start_type}" to "{end_type}") saved!'
                                )
                                st.session_state.session_id = None
                                st.session_state.page = "Saved Pipelines"
                                del st.session_state["pipeline_name"]
                                st.rerun()
                            else:
                                st.error("Errore salvataggio")

                with col2:
                    if st.button("⬅️ Back"):
                        st.session_state.session_id = None
                        del st.session_state["pipeline_name"]
                        st.rerun()

            elif data.get("is_stuck"):
                st.error("❌ ERROR: no possible transformations exist to reach the target")

                # 🔙 Pulsante per tornare indietro
                if st.button("⬅️ Back"):
                    st.session_state.session_id = None
                    st.rerun()

            else:
                st.subheader("Possible Algorithms:")  # Titolo sezione algoritmi disponibili

                for alg in data["next_algorithms"]:  # Itera sugli algoritmi disponibili

                    col1, col2 = st.columns([3, 2])  # Crea layout su due colonne

                    with col1:  # Prima colonna per descrizione
                        st.write(
                            f"{alg['name']} → Cost: {alg['cost']}"  # Mostra info algoritmo
                        )

                    with col2:  # Seconda colonna per pulsante
                        if st.button("Select", key=f"{alg['name']}_{alg['output_type']}"):  # Bottone selezione univoco
                            res = requests.post(
                                f"{API_URL}/pipelines/select-step/{st.session_state.session_id}",  # Endpoint selezione step
                                json={  # Body JSON della richiesta
                                    "algorithm_name": alg["name"]  # Nome algoritmo scelto
                                },
                                timeout=5  # Timeout richiesta
                            )

                            if res.status_code == 200:  # Se selezione riuscita
                                st.rerun()  # Ricarica la pagina per aggiornare pipeline
                            else:
                                st.error("Errore selezione step")  # Mostra errore se selezione fallisce

def show_object_types():

    st.markdown("""
    <style>
    h1 {
        font-size: 28px !important;
    }
    h2 {
        font-size: 22px !important;
    }
    h3 {
        font-size: 18px !important;
    }

    /* riduce spazi verticali */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Object Types")

    tab1, tab2, tab3 = st.tabs(["📄 List", "➕ Create", "🗑️ Delete"])

    # ===== LISTA =====
    with tab1:
        response = requests.get(f"{API_URL}/object-types/", params={"context_id": context_id})

        if response.status_code == 200:
            data = response.json()

            if not data:
                st.info("Nessun Object Type salvato")
            else:
                html = """
                <style>
                body {
                    margin: 0;
                    font-family: monospace;
                }

                .obj-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 15px;
                }

                .obj-table td {
                    padding: 6px 20px 6px 4px;
                    border: none;
                }

                .obj-row:hover {
                    background-color: #f5f5f5;
                }

                .obj-header td {
                    color: #d32f2f;
                    font-style: italic;
                    padding-bottom: 8px;
                    border-bottom: 1px solid #eee;
                }

                .obj-table td:nth-child(1) {
                    font-weight: 500;
                }
                </style>

                <table class="obj-table">

                <tr class="obj-header">
                    <td>Name</td>
                    <td>Desciption</td>
                    <td>Context</td>
                </tr>
                """

                for obj in data:
                    description = obj["description"] if obj["description"] else "-"
                    context_name = context_map.get(obj["context_id"], "N/A")

                    html += f"""
                    <tr class="obj-row">
                        <td>{obj['name']}</td>
                        <td>{description}</td>
                        <td>{context_name}</td>
                    </tr>
                    """

                html += "</table>"

                components.html(html, height=400, scrolling=True)

        else:
            st.error("Errore nel recupero dei dati dal backend")

    # ===== CREAZIONE =====
    with tab2:
        
        if "obj_success" in st.session_state:
            st.success(st.session_state["obj_success"])
            del st.session_state["obj_success"]

        name = st.text_input("Name")
        description = st.text_input("Desciption")

        create_context_id = context_id

        if st.button("Create Object Type", key="create_obj"):
            if not name:
                st.warning("Inserisci un nome")
            else:
                res = requests.post(
                    f"{API_URL}/object-types/",
                    params={"context_id": create_context_id},
                    json={
                        "name": name,
                        "description": description
                    }
                )

                if res.status_code == 200:
                    data = res.json()
                    st.session_state["obj_success"] = (
                        f"{data['message']} in context {context_map.get(context_id)}"
                    )
                    st.rerun()
                else:
                    st.error(res.text)
    
    # ===== CANCELLA OBJECT TYPE =====
    with tab3:

        st.subheader("🗑️ Delete Object Type")

        # 🔥 messaggio dopo eliminazione
        if "obj_deleted" in st.session_state:
            st.success(st.session_state["obj_deleted"])
            del st.session_state["obj_deleted"]

        # 🔥 carica object types
        try:
            res = requests.get(f"{API_URL}/object-types/", params={"context_id": context_id})
            if res.status_code == 200:
                object_types = res.json()
                object_types = [
                    obj for obj in object_types
                    if obj["context_id"] == context_id
                ]
                obj_names = [obj["name"] for obj in object_types]
                
            else:
                obj_names = []
        except:
            obj_names = []

        if not obj_names:
            st.info("Nessun Object Type disponibile")
        else:
            selected_obj = st.selectbox(f"You can select only the Object Types of context '{context_map.get(context_id)}'", obj_names)

            if st.button("Delete Object Type"):

                res = requests.delete(f"{API_URL}/object-types/{selected_obj}", params={"context_id": context_id})

                if res.status_code == 200:
                    st.session_state["obj_deleted"] = f"🗑️ ObjectType '{selected_obj}' eliminato"
                    st.rerun()
                else:
                    st.error("Errore eliminazione")

def show_algorithms():

    st.markdown("""
    <style>
    h1 {
        font-size: 28px !important;
    }
    h2 {
        font-size: 22px !important;
    }
    h3 {
        font-size: 18px !important;
    }

    /* riduce spazi verticali */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Algorithms")

    tab1, tab2, tab3 = st.tabs(["📄 List", "➕ Create", "🗑️ Delete"])

    # ===== LISTA =====
    with tab1:
        response = requests.get(f"{API_URL}/algorithms/", params={"context_id": context_id})

        if response.status_code == 200:
            data = response.json()

            if not data:
                st.info("Nessun algoritmo salvato")
            else:
                html = """
                <style>
                body {
                    margin: 0;
                    font-family: monospace;
                }

                .alg-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 15px;
                }

                .alg-table td {
                    padding: 6px 20px 6px 4px;
                    border: none;
                }

                .alg-row:hover {
                    background-color: #f5f5f5;
                }

                .alg-header td {
                    color: #d32f2f;
                    font-style: italic;
                    padding-bottom: 8px;
                }

                .alg-table td:nth-child(1) {
                    font-weight: 500;
                }

                .alg-table td:nth-child(4) {
                    text-align: right;
                }
                </style>

                <table class="alg-table">

                <tr class="alg-header">
                    <td>Name</td>
                    <td>Input Type</td>
                    <td>Output Type</td>
                    <td>Cost</td>
                    <td>Context</td>
                </tr>
                """

                for alg in data:
                    context_name = context_map.get(alg["context_id"], "N/A")

                    html += f"""
                    <tr class="alg-row">
                        <td>{alg['name']}</td>
                        <td>{alg['input_type']}</td>
                        <td>{alg['output_type']}</td>
                        <td>{alg['cost']}</td>
                        <td>{context_name}</td>
                    </tr>
                    """

                html += "</table>"

                components.html(html, height=400, scrolling=True)

        else:
            st.error("Errore nel recupero dei dati dal backend")

    # ===== CREAZIONE =====
    with tab2:

        if "alg_success" in st.session_state:
            st.success(st.session_state["alg_success"])
            del st.session_state["alg_success"]

        name = st.text_input("Algorithm Name")

        create_alg_context_id = context_id

        # carica object types del contesto selezionato
        try:
            res = requests.get(
                f"{API_URL}/object-types/",
                params={"context_id": create_alg_context_id}
            )
            if res.status_code == 200:
                types = [o["name"] for o in res.json()]
            else:
                types = []
        except:
            types = []

        input_type = st.selectbox("Input Type", types, key="alg_input_type")
        output_type = st.selectbox("Output Type", types, key="alg_output_type")

        cost = st.number_input("Cost", min_value=0.0, value=1.0)

        if st.button("Create algorithm", key="create_alg"):
            if not name:
                st.warning("Insert the algorithm name")
            elif not types:
                st.warning("No available ObjectType in the context")
            else:
                res = requests.post(
                    f"{API_URL}/algorithms/",
                    params={"context_id": create_alg_context_id},
                    json={
                        "name": name,
                        "input_type": input_type,
                        "output_type": output_type,
                        "cost": cost
                    }
                )

                if res.status_code == 200:
                    data = res.json()
                    st.session_state["alg_success"] = (
                        f"✅ Algorithm '{data['name']}' created "
                    )
                    st.rerun()
                else:
                    st.error(res.text)
    
    # ===== CANCELLA =====
    with tab3:

        st.subheader("🗑️ Delete algorithm")

        # 🔥 messaggio dopo eliminazione
        if "alg_deleted" in st.session_state:
            st.success(st.session_state["alg_deleted"])
            del st.session_state["alg_deleted"]

        # 🔥 carica algoritmi
        try:
            res = requests.get(f"{API_URL}/algorithms/", params={"context_id": context_id})
            if res.status_code == 200:
                algorithms = res.json()
                algorithms = [
                    alg for alg in algorithms
                    if alg["context_id"] == context_id
                ]
                alg_names = [alg["name"] for alg in algorithms]
            else:
                alg_names = []
        except:
            alg_names = []

        if not alg_names:
            st.info("No algorithm available")
        else:
            selected_alg = st.selectbox(f"You can select only the Algorithms of context '{context_map.get(context_id)}'", alg_names)

            if st.button("Delete algorithm"):
                res = requests.delete(f"{API_URL}/algorithms/{selected_alg}", params={"context_id": context_id})

                if res.status_code == 200:
                    st.session_state["alg_deleted"] = f"🗑️ Algorithm '{selected_alg}' deleted"
                    st.rerun()
                else:
                    st.error("❌ Delete: ERROR")

def show_saved_pipelines():

    st.markdown("""
    <style>
    h1 {
        font-size: 28px !important;
    }
    h2 {
        font-size: 22px !important;
    }
    h3 {
        font-size: 18px !important;
    }

    /* riduce spazi verticali */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.get("delete_mode"):
        show_delete_pipeline_section()
        return

    col1, col2 = st.columns([8, 3])
    with col1:
        st.title("Saved Pipelines")
        if "pipeline_saved" in st.session_state:
            st.success(st.session_state["pipeline_saved"])
            del st.session_state["pipeline_saved"]
    with col2:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("Delete Pipeline", help="Gestisci eliminazione pipeline"):
            st.session_state["delete_mode"] = True
            st.rerun()

    try:
        response = requests.get(
            f"{API_URL}/pipelines/",
            params={"context_id": context_id}
            )

        if response.status_code != 200:
            st.error("Errore nel recupero delle pipeline")
            return

        pipelines = response.json()

    except Exception as e:
        st.error(f"Backend non attivo: {e}")
        return

    if not pipelines:
        st.info("Nessuna pipeline salvata")
        return

    html = """
    <style>
    body {
        margin: 0;
        font-family: monospace;
    }

    .pipe-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 15px;
    }

    .pipe-table td {
        padding: 6px 20px 6px 4px;
        border: none;
    }

    .pipe-row:hover {
        background-color: #f5f5f5;
    }

    .pipe-header td {
        color: #d32f2f;
        font-style: italic;
        padding-bottom: 8px;
        border-bottom: 1px solid #eee;
    }

    .pipe-table td:nth-child(1) {
        font-weight: 500;
    }

    .pipe-table td:nth-child(4) {
        text-align: right;
    }

    .pipeline-table {
        border-collapse: collapse;
        font-family: monospace;
        margin-top: 5px;
    }

    .pipeline-table td {
        padding: 2px 8px;
        white-space: nowrap;
    }

    .arrow {
        text-align: center;
        font-size: 16px;
    }

    .separator {
        height: 1px;
        background-color: #e0e0e0;
    }

    .pipe-row td {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>

    <table class="pipe-table">
    """

    for i, p in enumerate(pipelines):
        name = p.get("name") or f"Pipeline_{p['id']}"

        html += f"""
        <tr class="pipe-row">
            <td colspan="4" style="padding:10px 0;">
                <div style="display:grid;grid-template-columns: repeat(3, 1fr);gap: 20px;font-family: monospace;">

                    <div style="min-width:0; word-break: break-word;">
                        <span style="color:#d32f2f; font-style:italic;">Name</span><br>
                        <b>{name}</b>
                    </div>                    

                    <div style="min-width:0; word-break: break-word;">
                        <span style="color:#d32f2f; font-style:italic;">Start Type</span><br>
                        {p['start_type']}
                    </div>

                    <div style="min-width:0; word-break: break-word;">
                        <span style="color:#d32f2f; font-style:italic;">Context Name</span><br>
                        {p['context_name']}
                    </div>

                    <div style="min-width:0; word-break: break-word;">
                        <span style="color:#d32f2f; font-style:italic;">Cost</span><br>
                        {p['total_cost']}
                    </div>

                    <div style="min-width:0; word-break: break-word;">
                        <span style="color:#d32f2f; font-style:italic;">Target Type</span><br>
                        {p['end_type']}
                    </div>

                    <div style="min-width:0; word-break: break-word;">
                        <span style="color:#d32f2f; font-style:italic;">Context ID</span><br>
                        {p['context_id']}
                    </div>                    

                </div>
            </td>
        </tr>
        """

        # 🔹 Riga "steps" label
        html += """
        <tr>
            <td colspan="4" style="padding-top:8px;">
                <span style="color:#d32f2f; font-style:italic;">Steps</span>
            </td>
        </tr>
        """

        # 🔹 Steps vari
        html += """
        <tr>
            <td colspan="4" style="padding-left:30px; padding-bottom:12px;">
        """

        if p["steps"]:
            html += render_pipeline_table(p["steps"])
        else:
            html += "<div style='color:#999;'>No steps</div>"

        html += """
            </td>
        </tr>
        """

        if i < len(pipelines) - 1:
            html += """
            <tr>
                <td colspan="4" style="padding-top:10px; padding-bottom:10px;">
                    <div class="separator"></div>
                </td>
            </tr>
            """

    html += "</table>"

    components.html(html, height=800, scrolling=True)

#---

def show_delete_pipeline_section():

    st.title("🗑️ Delete Pipeline")

    if "pipeline_deleted" in st.session_state:
        st.success(st.session_state["pipeline_deleted"])
        del st.session_state["pipeline_deleted"]

    try:
        res = requests.get(
            f"{API_URL}/pipelines/",
            params={"context_id": context_id}
        )

        if res.status_code == 200:
            pipelines = res.json()
            pipelines = [
                p for p in pipelines
                if p["context_id"] == context_id
            ]
        else:
            pipelines = []
    except:
        pipelines = []

    if not pipelines:
        st.info("No pipeline available in this context")
        return

    # Costruzione etichette selezionabili
    options = []
    label_to_pipeline = {}

    for p in pipelines:
        name = p.get("name") or f"Pipeline_{p['id']}"
        options.append(name)
        label_to_pipeline[name] = p

    selected = st.selectbox(
        f"You can delete only the pipelines of context '{context_map.get(context_id)}'",
        options
    )

    selected_pipeline = label_to_pipeline[selected]

    if st.button("Delete Pipeline"):
        res = requests.delete(
            f"{API_URL}/pipelines/{selected_pipeline['id']}",
            params={"context_id": context_id}
        )

        if res.status_code == 200:
            pipeline_name = selected_pipeline.get("name") or f"Pipeline_{selected_pipeline['id']}"
            st.session_state["pipeline_deleted"] = (
                f"🗑️ Pipeline '{pipeline_name}' deleted"
            )
            st.rerun()
        else:
            st.error("❌ Delete: ERROR")

    if st.button("⬅️ Back"):
        st.session_state["delete_mode"] = False
        st.rerun()

#---

def render_pipeline_table(steps):
    html = "<table class='pipeline-table'>"
    for i, step in enumerate(steps, start=1):
        html += f"""
        <tr>
            <td>{i}</td>
            <td>{step['input_type']}</td>
            <td class="arrow">──▶</td>
            <td>{step['algorithm']}</td>
            <td class="arrow">──▶</td>
            <td>{step['output_type']}</td>
        </tr>
        """
    html += "</table>"
    return html

#################################################################################################

if st.session_state.current_view == "context":
    show_context_page()
    
elif st.session_state.current_view == "main":

    if st.session_state.page == "Pipeline Builder":
        show_pipeline_builder()

    elif st.session_state.page == "Object Types":
        show_object_types()

    elif st.session_state.page == "Algorithms":
        show_algorithms()

    elif st.session_state.page == "Saved Pipelines":
        show_saved_pipelines()
