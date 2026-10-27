from pathlib import Path
import streamlit as st
import pandas as pd

import config
from schemas import RequirementStatus, RequirementImportance
from scoring import calculate_coverage_score
from analyzer import analyze_resume

# Page configuration
st.set_page_config(
    page_title="AI Resume Screening Assistant",
    page_icon="📋",
    layout="wide",
)

# App Title & Ethics / Privacy Notice
st.title("📋 AI Resume Screening Assistant")
active_model_name = config.get_gemini_model()
st.caption(f"Evidence-Based Candidate Analysis Powered by Google Gemini • Active Model: `{active_model_name}`")

st.info(
    "⚖️ **Ethical & Decision-Support Notice:**\n"
    "- **Not a hiring decision:** This tool produces evidence-based summaries for decision support only. It never auto-rejects, grades, or makes hiring choices.\n"
    "- **Protected characteristics:** Religion, caste, gender, age, disability, and ethnicity are strictly excluded from analysis.\n"
    "- **Privacy:** Use fictional or anonymized data only unless you have explicit candidate consent."
)

# Initialize Session State
if "jd_input" not in st.session_state:
    st.session_state["jd_input"] = ""
if "resume_input" not in st.session_state:
    st.session_state["resume_input"] = ""
if "analysis_report" not in st.session_state:
    st.session_state["analysis_report"] = None
if "analysis_error" not in st.session_state:
    st.session_state["analysis_error"] = None


# Helper to load sample files
def load_sample_data():
    base_dir = Path(__file__).resolve().parent
    jd_path = base_dir / "sample_data" / "sample_job_description.txt"
    resume_path = base_dir / "sample_data" / "sample_resume.txt"

    if not jd_path.exists():
        st.session_state["analysis_error"] = f"Error: Sample Job Description file not found at {jd_path}"
        return
    if not resume_path.exists():
        st.session_state["analysis_error"] = f"Error: Sample Resume file not found at {resume_path}"
        return

    try:
        jd_content = jd_path.read_text(encoding="utf-8")
        resume_content = resume_path.read_text(encoding="utf-8")
        if not jd_content.strip():
            st.session_state["analysis_error"] = f"Error: Sample Job Description file is empty ({jd_path})"
            return
        if not resume_content.strip():
            st.session_state["analysis_error"] = f"Error: Sample Resume file is empty ({resume_path})"
            return

        st.session_state["jd_input"] = jd_content
        st.session_state["resume_input"] = resume_content
        st.session_state["analysis_report"] = None
        st.session_state["analysis_error"] = None
    except Exception as e:
        st.session_state["analysis_error"] = f"Failed to read sample files: {str(e)}"


# Helper to reset state
def reset_all():
    st.session_state["jd_input"] = ""
    st.session_state["resume_input"] = ""
    st.session_state["analysis_report"] = None
    st.session_state["analysis_error"] = None


# Action bar buttons with on_click callbacks
col_act1, col_act2, col_act3 = st.columns([2, 2, 6])
with col_act1:
    st.button("📁 Load Fictional Sample", on_click=load_sample_data, use_container_width=True)

with col_act2:
    st.button("🔄 Clear / Reset All", on_click=reset_all, use_container_width=True)

st.divider()

# Input Columns
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. Job Description (JD)")
    jd_text = st.text_area(
        "Paste the Job Description:",
        height=320,
        placeholder="Paste role requirements, responsibilities, and must-have/nice-to-have criteria...",
        key="jd_input",
    )
    jd_len = len(jd_text)
    st.caption(f"Characters: {jd_len:,} / {config.MAX_INPUT_LENGTH:,}")
    if jd_len > config.MAX_INPUT_LENGTH:
        st.error(f"⚠️ Job description exceeds max limit of {config.MAX_INPUT_LENGTH:,} characters. Please shorten it.")

with col_right:
    st.subheader("2. Candidate Resume")
    resume_text = st.text_area(
        "Paste Candidate Resume Text:",
        height=320,
        placeholder="Paste plain text resume (fictional or consented only)...",
        key="resume_input",
    )
    res_len = len(resume_text)
    st.caption(f"Characters: {res_len:,} / {config.MAX_INPUT_LENGTH:,}")
    if res_len > config.MAX_INPUT_LENGTH:
        st.error(f"⚠️ Resume exceeds max limit of {config.MAX_INPUT_LENGTH:,} characters. Please shorten it.")

st.markdown("")

# Analyze button
analyze_clicked = st.button("🚀 Analyze Candidate", type="primary", use_container_width=True)

if analyze_clicked:
    # 1. Validation checks
    if not jd_text.strip() and not resume_text.strip():
        st.warning("⚠️ Please provide both a Job Description and a Candidate Resume before analyzing.")
    elif not jd_text.strip():
        st.warning("⚠️ Job Description is empty. Please enter a job description.")
    elif not resume_text.strip():
        st.warning("⚠️ Candidate Resume is empty. Please enter resume text.")
    elif jd_len > config.MAX_INPUT_LENGTH or res_len > config.MAX_INPUT_LENGTH:
        st.error("⚠️ Input character length exceeds limit. Please reduce text length before analyzing.")
    else:
        # Trigger Gemini call with spinner
        with st.spinner("Analyzing candidate against requirements using Gemini..."):
            report, error_msg = analyze_resume(
                job_description=jd_text,
                resume_text=resume_text,
            )
            st.session_state["analysis_report"] = report
            st.session_state["analysis_error"] = error_msg

# Display Error if present
if st.session_state["analysis_error"]:
    st.error(st.session_state["analysis_error"])

# Display Report if analysis succeeded
report = st.session_state["analysis_report"]

if report:
    st.divider()
    st.header("📊 Candidate Screening Analysis Report")

    # Section 1: Candidate Summary
    st.subheader("👤 Candidate Summary")
    st.write(report.candidate_summary)

    # Section 2: Coverage Score & Worked Breakdown
    st.subheader("🎯 Requirements Coverage Breakdown")
    scoring_data = calculate_coverage_score(report.requirements)

    col_score1, col_score2 = st.columns([1, 2])
    with col_score1:
        st.metric(
            label="Requirement Coverage Score",
            value=f"{scoring_data['coverage_percent']}%",
            help="Coverage % = (Total Earned Points / Total Possible Weight) * 100",
        )
        st.caption(f"**Points Earned:** {scoring_data['total_earned_points']} / {scoring_data['total_possible_points']}")

    with col_score2:
        st.markdown(f"**Scoring Formula:** `{scoring_data['formula_str']}`")
        st.markdown(f"**Worked Calculation:** `{scoring_data['calculation_steps']}`")
        st.caption("Weights: Must-Have = 2.0 | Nice-To-Have = 1.0  •  Points: Supported = 1.0 | Partial = 0.5 | Not Evidenced = 0.0")

    # Section 3: Requirements Evaluation Table
    st.markdown("#### Requirements Evaluation")
    if report.requirements:
        table_rows = []
        for r in report.requirements:
            # Color badge label with clear textual representation
            if r.status == RequirementStatus.SUPPORTED:
                status_label = "🟢 Supported"
            elif r.status == RequirementStatus.PARTIAL:
                status_label = "🟡 Partial"
            else:
                status_label = "⚪ Not Evidenced"

            importance_label = "⭐ Must-Have" if r.importance == RequirementImportance.MUST_HAVE else "🔹 Nice-To-Have"
            quote_display = f'"{r.evidence_quote}"' if r.evidence_quote else "— (No quote found in text)"

            table_rows.append({
                "Requirement": r.requirement,
                "Importance": importance_label,
                "Status": status_label,
                "Resume Evidence Quote": quote_display,
                "Reasoning": r.reasoning,
            })

        df_reqs = pd.DataFrame(table_rows)
        st.dataframe(df_reqs, use_container_width=True, hide_index=True)
    else:
        st.info("No explicit requirements were found in the job description.")

    # Section 4: Relevant Experience & Projects
    st.subheader("💼 Relevant Experience & Projects")
    if report.relevant_experience:
        for idx, exp in enumerate(report.relevant_experience, 1):
            with st.container(border=True):
                st.markdown(f"**{idx}. {exp.title}**")
                st.markdown(f"**Relevance:** {exp.relevance}")
                if exp.evidence_quote:
                    st.markdown(f"> *Verbatim Quote:* \"{exp.evidence_quote}\"")
    else:
        st.write("No matching relevant experiences highlighted.")

    # Section 5: Follow-Up Interview Questions
    st.subheader("💡 Suggested Follow-Up Interview Questions")
    if report.follow_up_questions:
        for q_idx, q in enumerate(report.follow_up_questions, 1):
            st.markdown(f"**{q_idx}.** {q.question}")
            st.caption(f"🎯 Targets Requirement: *{q.targets_requirement}*")
    else:
        st.write("No specific follow-up questions generated.")

    # Section 6: Limitations
    st.subheader("⚠️ Limitations & Responsible AI Notice")

    # 6a: Model-Generated Limitations
    if report.limitations:
        st.markdown("**Identified in this Resume:**")
        for lim in report.limitations:
            st.markdown(f"- {lim}")

    # 6b: Fixed Hand-written Systemic Limitations
    with st.container(border=True):
        st.markdown("##### 📌 Important Systemic Limitations & Guidelines:")
        st.markdown(
            "1. **Incomplete Resume:** A candidate's resume may omit projects, tools, or skills they possess in practice.\n"
            "2. **Absence of Evidence is NOT Evidence of Absence:** Marking a requirement as *'Not Evidenced'* means only that it was not documented in this submitted text, never that the candidate lacks the ability.\n"
            "3. **Model Accuracy & Hallucinations:** Generative models can make mistakes or misinterpret nuances. Always cross-reference the extracted quotes.\n"
            "4. **Human Review Required:** This software is an assistive tool to speed up document review. All interview and hiring decisions must remain strictly with human recruiters and hiring managers."
        )
