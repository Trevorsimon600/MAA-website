import streamlit as st
import os
import json
import plotly.graph_objects as go
from datetime import datetime
from v0_2 import MAA

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="MAA Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# FUTURISTIC COMMAND CENTER CSS STYLING
# ============================================================
st.markdown("""
<style>
    /* Dark Sci-Fi Palette */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;800&family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    .stApp {
        background: radial-gradient(ellipse at 50% 0%, #0c1427 0%, #050816 80%);
        color: #c8d6e5;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: #060b19 !important;
        border-right: 1px solid rgba(0, 217, 255, 0.15);
    }
    
    /* Header Bar */
    .command-header {
        background: linear-gradient(90deg, rgba(10, 16, 32, 0.95), rgba(15, 23, 42, 0.85));
        border: 1px solid rgba(0, 217, 255, 0.2);
        border-radius: 12px;
        padding: 18px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 0 25px rgba(0, 217, 255, 0.05);
    }

    .brand-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 800;
        letter-spacing: 2px;
        color: #00D9FF;
        text-shadow: 0 0 12px rgba(0, 217, 255, 0.4);
    }

    .brand-sub {
        font-size: 11px;
        color: #64748b;
        letter-spacing: 3px;
        text-transform: uppercase;
        display: block;
    }

    .status-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        background: rgba(34, 197, 94, 0.1);
        color: #22C55E;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        letter-spacing: 1px;
    }

    /* Cyber Panel Card */
    .cyber-card {
        background: rgba(10, 16, 32, 0.75);
        border: 1px solid rgba(0, 217, 255, 0.15);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .cyber-card:hover {
        border-color: rgba(0, 217, 255, 0.4);
        box-shadow: 0 0 15px rgba(0, 217, 255, 0.1);
    }

    .cyber-card-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #00D9FF;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    /* Animated Central Intelligence Core */
    .core-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px;
        position: relative;
    }

    .core-orb {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        background: radial-gradient(circle, #00D9FF 0%, #7C3AED 60%, transparent 70%);
        box-shadow: 0 0 40px rgba(0, 217, 255, 0.5), inset 0 0 20px rgba(124, 58, 237, 0.8);
        animation: pulseCore 3s infinite alternate;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
        font-weight: bold;
        font-size: 14px;
        letter-spacing: 2px;
    }

    @keyframes pulseCore {
        0% { transform: scale(0.95); box-shadow: 0 0 30px rgba(0, 217, 255, 0.4); }
        100% { transform: scale(1.05); box-shadow: 0 0 60px rgba(0, 217, 255, 0.8), 0 0 90px rgba(124, 58, 237, 0.5); }
    }

    /* Agent Badge */
    .agent-node {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(0, 217, 255, 0.25);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        transition: all 0.2s ease;
    }

    .agent-node:hover {
        border-color: #00D9FF;
        transform: translateY(-2px);
    }

    .agent-status-online {
        color: #22C55E;
        font-size: 11px;
        display: block;
        margin-top: 4px;
    }

    /* Terminal Console Output */
    .terminal-console {
        background: #030712;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #38bdf8;
        max-height: 350px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INITIALIZATION
# ============================================================
@st.cache_resource
def get_maa_instance():
    return MAA()

maa = get_maa_instance()

# ============================================================
# TOP HEADER BAR
# ============================================================
st.markdown(f"""
<div class="command-header">
    <div>
        <span class="brand-title">◉ MAA COMMAND CENTER</span>
        <span class="brand-sub">MEGA AGENT ASSOCIATION • SYSTEM VER {maa.version}</span>
    </div>
    <div>
        <span class="status-badge">● SYSTEM ONLINE • ALL SYSTEMS OK</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# NAVIGATION SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("<h3 style='color:#00D9FF; font-family:monospace;'>NAVIGATION</h3>", unsafe_allow_html=True)
    page = st.radio(
        "Select Module",
        [
            "◉ Overview & Core",
            "🚀 Mission Control",
            "◎ Agent Network",
            "📁 Projects",
            "🧠 Memory & Knowledge",
            "📜 Mission History",
            "⚙️ System & Tools"
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    
    # System Telemetry Panel
    st.markdown("<div class='cyber-card-title'>TELEMETRY</div>", unsafe_allow_html=True)
    status_info = maa.status()
    st.caption(f"🤖 Active Agents: **{len(status_info['agents'])}**")
    st.caption(f"🛠️ Tool Registry: **{len(status_info['tools'])}**")
    st.caption(f"📁 Linked Projects: **{status_info['projects']}**")
    st.caption(f"💾 Total Saved Runs: **{status_info['runs']}**")
    st.markdown("---")
    st.caption(f"🕒 UTC: {datetime.utcnow().strftime('%H:%M:%S')}")

# ============================================================
# MODULE 1: OVERVIEW & INTELLIGENCE CORE
# ============================================================
if page == "◉ Overview & Core":
    st.markdown("<h2 style='color:#00D9FF;'>CORE INTELLIGENCE & TELEMETRY</h2>", unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1.2, 1])

    with col_left:
        st.markdown("""
        <div class="cyber-card">
            <div class="cyber-card-title">SYSTEM METRICS</div>
            <div style="font-size:28px; font-weight:bold; color:#00D9FF;">8 AGENTS</div>
            <div style="color:#64748b; font-size:12px; margin-bottom:12px;">Fully Autonomous Mesh</div>
            <div style="font-size:24px; font-weight:bold; color:#7C3AED;">DYNAMIC</div>
            <div style="color:#64748b; font-size:12px;">Graph Orchestration V2</div>
        </div>
        """, unsafe_allow_html=True)

    with col_center:
        st.markdown("""
        <div class="cyber-card core-container">
            <div class="cyber-card-title">INTELLIGENCE CORE</div>
            <div class="core-orb">MAA CORE</div>
            <div style="margin-top:15px; color:#22C55E; font-family:monospace; font-size:12px;">● STANDBY / READY</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="cyber-card">
            <div class="cyber-card-title">COLLABORATION ENGINE</div>
            <div style="color:#38bdf8; font-family:monospace; font-size:13px;">
                📨 Typed MessageBus: ENABLED<br>
                🛠️ Universal Tool Access: ACTIVE<br>
                💾 Persistent RunState: ONLINE<br>
                ⚡ Model Router: GROQ / OPENAI
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h3 style='color:#00D9FF; margin-top:20px;'>🤖 AGENT MESH STATUS</h3>", unsafe_allow_html=True)
    agents = status_info["agents"]
    cols = st.columns(4)
    for i, agent_name in enumerate(agents):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="agent-node">
                <span style="color:#ffffff; font-weight:600;">{agent_name}</span>
                <span class="agent-status-online">● READY</span>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# MODULE 2: MISSION CONTROL (RUN OBJECTIVE & LIVE VIEW)
# ============================================================
elif page == "🚀 Mission Control":
    st.markdown("<h2 style='color:#00D9FF;'>MISSION CONTROL</h2>", unsafe_allow_html=True)
    
    projects = maa.list_projects()
    project_options = {"None (Standalone)": None}
    for p in projects:
        project_options[f"{p.name} ({p.id})"] = p.id

    c1, c2 = st.columns([2, 1])
    with c1:
        objective = st.text_area("MISSION OBJECTIVE", height=130, placeholder="Describe the complex task or objective for MAA agents to solve...")
    with c2:
        selected_proj = st.selectbox("LINK TO PROJECT", list(project_options.keys()))
        proj_id = project_options[selected_proj]
        max_steps = st.slider("MAX DYNAMIC STEPS", min_value=2, max_value=10, value=6)

    if st.button("🔴 INITIATE MAA MISSION", type="primary", use_container_width=True):
        if not objective.strip():
            st.warning("Please enter a valid mission objective.")
        else:
            st.markdown("---")
            st.markdown("### 📡 LIVE MISSION EXECUTION LOG")
            
            with st.spinner("Executing dynamic agent mesh..."):
                try:
                    results = maa.run(objective, project_id=proj_id, max_steps=max_steps)
                    
                    st.success("🎉 MISSION COMPLETED SUCCESSFULLY!")
                    st.balloons()

                    st.markdown("### 🏆 FINAL VERIFIED SOLUTION")
                    st.markdown(f"""
                    <div class="cyber-card">
                        <div style="color:#e2e8f0; font-size:15px; line-height:1.6;">
                            {results.get('final', 'No output generated.')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if "evaluation" in results and results["evaluation"]:
                        score = results["evaluation"].get("score", "N/A")
                        st.metric("QUALITY ASSURANCE SCORE", f"{score}/10")

                    with st.expander("🔍 VIEW FULL STEP TRACE & MESSAGES"):
                        st.json(results)

                except Exception as e:
                    st.error(f"Execution Error: {e}")

# ============================================================
# MODULE 3: AGENT NETWORK MAP
# ============================================================
elif page == "◎ Agent Network":
    st.markdown("<h2 style='color:#00D9FF;'>AGENT NETWORK & COLLABORATION GRAPH</h2>", unsafe_allow_html=True)

    # Plotly interactive Network Graph visualization
    fig = go.Figure()
    
    agent_names = status_info["agents"]
    # Coordinates in radial layout
    import math
    n = len(agent_names)
    r = 2.0
    x_nodes = [0.0] + [r * math.cos(2 * math.pi * i / (n - 1)) for i in range(n - 1)]
    y_nodes = [0.0] + [r * math.sin(2 * math.pi * i / (n - 1)) for i in range(n - 1)]

    # Draw edges from center (Coordinator) to all agents
    edge_x = []
    edge_y = []
    for i in range(1, n):
        edge_x.extend([x_nodes[0], x_nodes[i], None])
        edge_y.extend([y_nodes[0], y_nodes[i], None])

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(color='#00D9FF', width=1.5),
        hoverinfo='none'
    ))

    fig.add_trace(go.Scatter(
        x=x_nodes, y=y_nodes,
        mode='markers+text',
        text=agent_names,
        textposition="top center",
        marker=dict(
            size=[32] + [24] * (n - 1),
            color=['#00D9FF'] + ['#7C3AED'] * (n - 1),
            line=dict(color='#ffffff', width=2)
        ),
        textfont=dict(color='#ffffff', family='JetBrains Mono', size=12)
    ))

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# MODULE 4: PROJECTS
# ============================================================
elif page == "📁 Projects":
    st.markdown("<h2 style='color:#00D9FF;'>PROJECT COMMAND CENTER</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ CREATE NEW PROJECT"):
        name = st.text_input("Project Name")
        goal = st.text_area("Project Goal / Scope")
        if st.button("Create Project"):
            if name and goal:
                p = maa.create_project(name, goal)
                st.success(f"Project Created: {p.name} (`{p.id}`)")
            else:
                st.warning("Please specify both name and goal.")

    projects = maa.list_projects()
    if not projects:
        st.info("No active projects.")
    else:
        for p in projects:
            st.markdown(f"""
            <div class="cyber-card">
                <div class="cyber-card-title">{p.name} [{p.status.upper()}]</div>
                <div style="font-size:12px; color:#94a3b8;">ID: <code>{p.id}</code></div>
                <div style="margin-top:8px;"><strong>Goal:</strong> {p.goal}</div>
                <div style="margin-top:6px; color:#00D9FF;">Linked Runs: {len(p.run_ids)}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# MODULE 5: MEMORY & KNOWLEDGE BASE
# ============================================================
elif page == "🧠 Memory & Knowledge":
    st.markdown("<h2 style='color:#00D9FF;'>LONG-TERM KNOWLEDGE BASE</h2>", unsafe_allow_html=True)
    
    if hasattr(maa.memory, "load_knowledge_base"):
        kb_data = maa.memory.load_knowledge_base()
    else:
        try:
            with open("knowledge_base.json", "r", encoding="utf-8") as f:
                kb_data = json.load(f).get("entries", [])
        except Exception:
            kb_data = []
    st.write(f"Total Preserved Knowledge Entries: **{len(kb_data)}**")
    
    query = st.text_input("🔍 Search Knowledge Base", placeholder="Enter topic or keyword...")
    if query:
        results = maa.memory.retrieve_relevant_knowledge(query)
        st.markdown("### Matching Knowledge")
        st.write(results)
    else:
        st.json(kb_data)

# ============================================================
# MODULE 6: MISSION HISTORY
# ============================================================
elif page == "📜 Mission History":
    st.markdown("<h2 style='color:#00D9FF;'>MISSION HISTORY & RUN TRACES</h2>", unsafe_allow_html=True)
    
    runs = maa.memory.list_runs()
    if not runs:
        st.info("No saved runs found.")
    else:
        selected_run = st.selectbox("Select Mission Run ID", runs)
        run_data = maa.memory.load_run(selected_run)
        
        if run_data:
            st.markdown(f"### Mission Objective: {run_data.get('objective')}")
            st.caption(f"Run ID: `{run_data.get('run_id')}`")
            
            t1, t2, t3 = st.tabs(["Final Solution", "Step Trace", "Raw JSON"])
            with t1:
                st.write(run_data.get("final", "—"))
            with t2:
                steps = run_data.get("steps", [])
                if steps:
                    for s in steps:
                        st.markdown(f"**Step {s.get('step_number')}: [{s.get('agent_name')}]** — *{s.get('task_title')}*")
                        st.info(s.get("output", ""))
                else:
                    st.write("Legacy run trace.")
            with t3:
                st.json(run_data)

# ============================================================
# MODULE 7: SYSTEM & TOOLS
# ============================================================
elif page == "⚙️ System & Tools":
    st.markdown("<h2 style='color:#00D9FF;'>SYSTEM CAPABILITIES & FILE MANAGEMENT</h2>", unsafe_allow_html=True)
    
    t_tools, t_upload, t_image = st.tabs(["🧰 Universal Tool Matrix", "📂 Upload Files / PDFs", "🎨 Image Generation"])
    
    with t_tools:
        st.markdown("### Registered Tools")
        st.write(maa.tools.get_tool_info())
        
    with t_upload:
        st.markdown("### File Ingestion")
        up_file = st.file_uploader("Upload document for agent mesh access", type=["txt", "pdf", "md", "csv", "json", "jpg", "png"])
        if up_file is not None:
            os.makedirs("uploads", exist_ok=True)
            path = os.path.join("uploads", up_file.name)
            with open(path, "wb") as f:
                f.write(up_file.getbuffer())
            st.success(f"File uploaded to: `{path}`")

    with t_image:
        st.markdown("### Pollinations Image Engine")
        img_prompt = st.text_area("Prompt", placeholder="A futuristic cybernetic core glowing with blue light...")
        if st.button("Generate Image"):
            if img_prompt.strip():
                from tools.image_generator import generate_image
                img_path = generate_image(img_prompt)
                if img_path.endswith((".jpg", ".png")):
                    st.image(img_path, caption=img_prompt, use_container_width=True)
                else:
                    st.error(img_path)