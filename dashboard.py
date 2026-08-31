import streamlit as st
import os
from v0_2 import MAA
from datetime import datetime

st.set_page_config(
    page_title="MAA Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at 50% 0%, #0f172a 0%, #020617 75%);
    color: #e2e8f0;
}
section[data-testid="stSidebar"] {
    background: #020617;
    border-right: 1px solid #1e293b;
}
.agent-card {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# INIT MAA
# ============================================================
@st.cache_resource
def get_maa():
    return MAA()

maa = get_maa()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🧠 MAA")
    st.caption(f"v{maa.version}")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Dashboard", "Run Objective", "Past Runs", "Projects", "Generate Image", "Upload File"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.success("🟢 Online")
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M"))

# ============================================================
# DASHBOARD
# ============================================================
if page == "Dashboard":
    st.title("🧠 MAA Command Center")
    st.caption("Mega Agent Association — v0.2")

    status = maa.status()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Version", status["version"])
    col2.metric("Agents", len(status["agents"]))
    col3.metric("Tools", len(status["tools"]))
    col4.metric("Runs", status["runs"])

    st.markdown("### 🤖 Agent Team")
    agents = status["agents"]
    cols = st.columns(4)
    for i, agent in enumerate(agents):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="agent-card">
                <strong>{agent}</strong><br>
                <span style="color:#4ade80;">● Ready</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🧰 Available Tools")
    st.write(", ".join(status["tools"]))

# ============================================================
# RUN OBJECTIVE
# ============================================================
elif page == "Run Objective":
    st.title("🚀 Run New Objective")

    projects = maa.list_projects()
    project_options = {"None": None}
    for p in projects:
        project_options[f"{p.name} ({p.id})"] = p.id

    selected_project = st.selectbox("Link to Project (optional)", list(project_options.keys()))
    project_id = project_options[selected_project]

    objective = st.text_area("Objective", height=120, placeholder="Enter your objective here...")

    if st.button("🚀 Start MAA", type="primary"):
        if not objective.strip():
            st.warning("Please enter an objective.")
        else:
            with st.spinner("MAA agents are working..."):
                try:
                    results = maa.run(objective, project_id=project_id)
                    st.success("Run completed!")
                    st.balloons()

                    evaluation = results.get("evaluation", {})
                    if evaluation:
                        st.metric("Quality Score", f"{evaluation.get('score', 'N/A')}/10")

                    st.subheader("Final Answer")
                    st.write(results.get("final", "No final answer."))

                    with st.expander("Full Details"):
                        st.write(results)
                except Exception as e:
                    st.error(f"Error: {e}")

# ============================================================
# PAST RUNS
# ============================================================
elif page == "Past Runs":
    st.title("📚 Past Runs")

    runs = maa.memory.list_runs()
    if not runs:
        st.info("No runs found yet.")
    else:
        selected = st.selectbox("Select a run", runs)
        data = maa.memory.load_run(selected)

        if data:
            st.subheader(f"Run: `{data.get('run_id')}`")
            st.caption(data.get("timestamp"))
            st.markdown(f"**Objective:** {data.get('objective')}")

            evaluation = data.get("evaluation", {})
            if evaluation:
                st.success(f"Score: {evaluation.get('score', 'N/A')}/10")

            tabs = st.tabs(["Final", "Research", "Critique", "Verification", "Plan"])
            with tabs[0]:
                st.write(data.get("final", "—"))
            with tabs[1]:
                st.write(data.get("research", "—"))
            with tabs[2]:
                st.write(data.get("critique", "—"))
            with tabs[3]:
                st.write(data.get("verification", "—"))
            with tabs[4]:
                st.write(data.get("plan", "—"))

# ============================================================
# PROJECTS
# ============================================================
elif page == "Projects":
    st.title("📁 Projects")

    with st.expander("➕ Create New Project"):
        name = st.text_input("Project Name")
        goal = st.text_area("Project Goal")
        if st.button("Create Project"):
            if name and goal:
                p = maa.create_project(name, goal)
                st.success(f"Created: {p.name} ({p.id})")
            else:
                st.warning("Please fill both fields.")

    projects = maa.list_projects()
    if not projects:
        st.info("No projects yet.")
    else:
        for p in projects:
            with st.expander(f"{p.name} ({p.status})"):
                st.write(f"**ID:** `{p.id}`")
                st.write(f"**Goal:** {p.goal}")
                st.write(f"**Runs:** {len(p.run_ids)}")

# ============================================================
# GENERATE IMAGE
# ============================================================
elif page == "Generate Image":
    st.title("🎨 Generate Image")

    prompt = st.text_area("Image Prompt", height=100, placeholder="Describe the image you want...")
    
    if st.button("🎨 Generate", type="primary"):
        if not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Generating image..."):
                from tools.image_generator import generate_image
                result = generate_image(prompt)
                
                if result.endswith(".jpg") or result.endswith(".png"):
                    st.success("Image generated!")
                    st.image(result, caption=prompt, use_container_width=True)
                    st.caption(f"Saved as: {result}")
                else:
                    st.error(result)

# ============================================================
# UPLOAD FILE
# ============================================================
elif page == "Upload File":
    st.title("📂 Upload File / Image")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "pdf", "png", "jpg", "jpeg", "md", "csv", "json"]
    )

    if uploaded_file is not None:
        # Save the file
        save_dir = "uploads"
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, uploaded_file.name)

        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File saved: `{filepath}`")

        # Preview
        if uploaded_file.type.startswith("image"):
            st.image(filepath, caption=uploaded_file.name, use_container_width=True)
        else:
            try:
                content = uploaded_file.read().decode("utf-8")
                st.text_area("File Preview", content[:3000], height=300)
            except Exception:
                st.info("File uploaded successfully (binary or unsupported preview).")