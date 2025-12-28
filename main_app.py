# Fixed and Enhanced App - Addresses all user issues
import streamlit as st
import streamlit.components.v1 as st_components
import pandas as pd
import json
import os
import tempfile
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any
import base64
from io import BytesIO
import time

# Import modules with better error handling
try:
    from modules import parser, scoring, jd_handler
    from modules.resume_ranker import ResumeRanker
    
    # Use the enhanced suggestions system as the single source
    from modules.working_suggestions import get_enhanced_suggestions
    
    # Check if running in offline mode
    if hasattr(parser, 'ner') and parser.ner.use_fallback:
        st.info("🔄 Running in offline mode - using fallback parsing methods")
            
except Exception as e:
    st.error(f"❌ Error importing modules: {e}")
    st.stop()

# Configure Streamlit
st.set_page_config(
    page_title="AI Resume Evaluator Pro",
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better styling
st.markdown("""
<style>
/* Modern UI styling */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.suggestion-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.critical-suggestion {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    padding: 1rem;
    border-radius: 8px;
    color: white;
    border-left: 4px solid #c0392b;
    margin: 0.5rem 0;
}

.high-suggestion {
    background: linear-gradient(135deg, #feca57, #ff9f43);
    padding: 1rem;
    border-radius: 8px;
    color: #2c3e50;
    border-left: 4px solid #f39c12;
    margin: 0.5rem 0;
}

.medium-suggestion {
    background: linear-gradient(135deg, #48cae4, #0077b6);
    padding: 1rem;
    border-radius: 8px;
    color: white;
    border-left: 4px solid #0096c7;
    margin: 0.5rem 0;
}
/* Improved spacing controls */
.title-container {
    padding: 2rem 0 1rem 0 !important;
    margin-bottom: 1.5rem !important;
}

.title-container h1 {
    margin-bottom: 0.5rem !important;
}

.title-container p {
    margin-bottom: 0 !important;
}

/* Tight radio button group */
.stRadio > div {
    padding: 0.3rem 0 !important;
    margin: 0 !important;
}

/* Compact separator */
.compact-separator {
    margin: 0.2rem 0 !important;
}

.compact-separator hr {
    margin: 0 !important;
    border-color: #e0e0e0 !important;
}
.score-display {
    background: linear-gradient(45deg, #28a745, #20c997);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

/* Improved centering for main content */
.stApp {
    margin-top: -80px;
}

/* Ensure proper spacing for the main content */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Style for the separator line */
hr {
    margin: 1.5rem 0;
    border: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #667eea, transparent);
}

.progress-container {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    color: white;
}

.progress-step {
    display: flex;
    align-items: center;
    margin: 0.5rem 0;
    transition: all 0.3s ease;
}

.progress-step.active {
    font-weight: bold;
    transform: scale(1.05);
}

.progress-step.completed {
    opacity: 0.7;
}

.resume-preview {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
    max-height: 400px;
    overflow-y: auto;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.clickable-name {
    cursor: pointer;
    color: #1f77b4;
    text-decoration: underline;
    transition: color 0.2s ease;
}

.clickable-name:hover {
    color: #0d47a1;
    font-weight: bold;
}

.editor-container {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #e9ecef;
    margin: 1rem 0;
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #007bff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}
            
.metric-card, .metric-card h2, .metric-card h4, .metric-card p, .metric-card h3 {
    color: #111 !important; 
}
.metric-card .score-value {
    font-weight: 700;
}

.feedback-form {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin: 1rem 0;
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header {
        padding: 1rem;
    }
    
    .suggestion-box, .critical-suggestion, .high-suggestion, .medium-suggestion {
        padding: 0.8rem;
        margin: 0.3rem 0;
    }
}

/* Animation classes */
.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.pulse {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

/* Hide streamlit elements */
.stDeployButton {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.stApp > header {
    background-color: transparent;
}

.stApp {
    margin-top: -80px;
}
            
/* Collapsible sidebar styles */
.sidebar-toggle-btn {
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem;
    font-size: 1.2rem;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.sidebar-toggle-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.floating-toggle {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 1000;
    background: linear-gradient(45deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.floating-toggle:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
}

/* Adjust main content when sidebar is collapsed */
.main-content-expanded {
    margin-left: 0;
    transition: margin-left 0.3s ease;
}

/* Responsive design for mobile */
@media (max-width: 768px) {
    .floating-toggle {
        top: 15px;
        left: 15px;
        width: 45px;
        height: 45px;
        font-size: 1.3rem;
    }
    
    .sidebar-toggle-btn {
        font-size: 1.1rem;
        padding: 0.4rem;
    }
}
            
</style>
""", unsafe_allow_html=True)

# Cache expensive resources
@st.cache_resource
def load_components():
    """Load and cache application components"""
    try:
        return {
            'matcher': scoring.ResumeScorer(method="hybrid"),
            'ranker': ResumeRanker(),
            'jds': jd_handler.load_predefined_jds("data/predefined_jds.json")
        }       
    except Exception as e:
        st.error(f"Error loading components: {e}")
        return None

def init_session_state():
    """Initialize session state variables"""
    defaults = {
        'processed_resumes': {},
        'resume_previews': {},
        'current_suggestions': None,
        'anonymize_mode': False,
        'current_resume_text': "",
        'preview_selector': None,
        'feedback_submitted': False,
        'show_all_results': False,
        'score_threshold': 0.0,
        'active_view': "📝 Resume Evaluation",
        'ranked_df': None,
        'rank_jd_text': "",
        'rank_ready': False,
        'sidebar_collapsed': True,
        'show_reports': False,
        'show_export': False,
        'visualization_mode': "🎮 Game Style (Radar)",
        'eval_chart_cache': {} 
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if 'uploaded_files_store' not in st.session_state:
        st.session_state['uploaded_files_store'] = {}
    

# Feedback system functions
def load_feedback():
    """Load existing feedback from JSON file"""
    feedback_file = "feedback.json"
    if os.path.exists(feedback_file):
        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_feedback(name, email, feedback_text):
    """Save new feedback to JSON file"""
    feedback_file = "feedback.json"
    existing_feedback = load_feedback()
    
    new_feedback = {
        "id": len(existing_feedback) + 1,
        "name": name,
        "email": email,
        "feedback": feedback_text,
        "timestamp": datetime.now().isoformat(),
        "date_formatted": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    existing_feedback.append(new_feedback)
    
    try:
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(existing_feedback, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving feedback: {e}")
        return False

def show_progress_indicator(steps, current_step):
    """Show enhanced progress indicator"""
    progress_html = '<div class="progress-container">'
    progress_html += '<h4>🔄 Processing...</h4>'
    
    for i, step in enumerate(steps):
        if i < current_step:
            status_class = "completed"
            icon = "✅"
        elif i == current_step:
            status_class = "active pulse"
            icon = "🔄"
        else:
            status_class = ""
            icon = "⏳"
        
        progress_html += f'<div class="progress-step {status_class}">{icon} {step}</div>'
    
    progress_html += '</div>'
    return progress_html

def create_section_score_chart(section_scores: Dict[str, Any]) -> go.Figure:
    """Create a beautiful radar chart for section scores"""
    sections = []
    scores = []
    
    for section, analysis in section_scores.items():
        if isinstance(analysis, dict) and 'score' in analysis:
            sections.append(section.title().replace('_', ' '))
            scores.append(analysis['score'])
    
    if not sections:
        return None
    
    fig = go.Figure()
    
    # Add the radar chart trace
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=sections,
        fill='toself',
        name='Your Resume',
        line=dict(color='#667eea', width=3),
        fillcolor='rgba(102, 126, 234, 0.2)',
        marker=dict(size=8, color='#667eea')
    ))
    
    # Add ideal score line
    ideal_scores = [80] * len(sections)  # Target score of 80% for all sections
    fig.add_trace(go.Scatterpolar(
        r=ideal_scores,
        theta=sections,
        fill='none',
        name='Target Score',
        line=dict(color='#28a745', width=2, dash='dash'),
        marker=dict(size=6, color='#28a745')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12),
                gridcolor='rgba(0,0,0,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            ),
            bgcolor='rgba(255,255,255,0.9)'
        ),
        showlegend=True,
        title={
            'text': "📊 Resume Section Performance Analysis",
            'x': 0.5,
            'font': {'size': 18, 'family': 'Arial, sans-serif'},
            'pad': {'b': 20}
        },
        height=500,
        margin=dict(l=80, r=80, t=100, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig
def create_bar_chart(section_scores: Dict[str, Any]) -> go.Figure:
    """Create a simple bar chart for section scores"""
    sections = []
    scores = []
    colors = []
    
    for section, analysis in section_scores.items():
        if isinstance(analysis, dict) and 'score' in analysis:
            sections.append(section.title().replace('_', ' '))
            scores.append(analysis['score'])
            
            # Color coding based on score
            if analysis['score'] >= 80:
                colors.append('#2ecc71')  # Green
            elif analysis['score'] >= 60:
                colors.append('#f39c12')  # Orange
            else:
                colors.append('#e74c3c')  # Red
    
    if not sections:
        return None
    
    fig = go.Figure(data=[go.Bar(
        x=sections,
        y=scores,
        marker_color=colors,
        text=[f"{score}%" for score in scores],
        textposition='auto',
    )])
    
    fig.update_layout(
        title="📊 Resume Section Scores",
        xaxis_title="Sections",
        yaxis_title="Score (%)",
        yaxis=dict(range=[0, 100]),
        showlegend=False,
        height=400
    )
    
    return fig

def create_donut_chart(section_scores: Dict[str, Any]) -> go.Figure:
    """Create a donut chart for section scores"""
    sections = []
    scores = []
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#34495e']
    
    for section, analysis in section_scores.items():
        if isinstance(analysis, dict) and 'score' in analysis:
            sections.append(section.title().replace('_', ' '))
            scores.append(analysis['score'])
    
    if not sections:
        return None
    
    fig = go.Figure(data=[go.Pie(
        labels=sections,
        values=scores,
        hole=0.4,
        marker=dict(colors=colors[:len(sections)]),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Score: %{value}%<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="🍩 Section Performance Distribution",
        showlegend=True,
        height=500
    )
    
    return fig

def create_gauges(section_scores: Dict[str, Any]):
    """Create individual gauge meters for each section"""
    st.markdown("### 🎯 Section Performance Gauges")
    
    cols = st.columns(3)
    section_items = list(section_scores.items())
    
    for i, (section, analysis) in enumerate(section_items):
        if not isinstance(analysis, dict) or 'score' not in analysis:
            continue
            
        with cols[i % 3]:
            score = analysis['score']
            
            # Determine color based on score
            if score >= 80:
                color = "2ecc71"  # Green
            elif score >= 60:
                color = "f39c12"  # Orange
            else:
                color = "e74c3c"  # Red
            
            # Create mini gauge using HTML/CSS
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border: 2px solid #{color}; border-radius: 10px; margin: 5px;">
                <h4 style="margin: 0; color: #{color};">{section.title().replace('_', ' ')}</h4>
                <div style="font-size: 24px; font-weight: bold; color: #{color};">
                    {score}%
                </div>
                <div style="background: #f0f0f0; height: 10px; border-radius: 5px; margin: 5px 0;">
                    <div style="background: #{color}; width: {score}%; height: 100%; border-radius: 5px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
def display_enhanced_suggestions(suggestion_results: Dict[str, Any]):
    """Display AI-enhanced suggestions with better formatting"""
    
    overall_score = suggestion_results.get('overall_score', 0)
    reasoning = suggestion_results.get('reasoning', {})
    
    # Overall Assessment Card
    score_color = "#28a745" if overall_score >= 70 else "#ffc107" if overall_score >= 50 else "#dc3545"
    
    st.markdown(f"""
    <div class="score-display fade-in" style="background: linear-gradient(45deg, {score_color}, {score_color}dd);">
        <h2>🎯 Overall Resume Score: {overall_score:.1f}%</h2>
        <p style="font-size: 1.1rem; margin: 0.5rem 0;">
            {reasoning.get('overall', 'Analysis completed successfully!')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section Analysis with multiple view options
    section_scores = suggestion_results.get('section_scores', {})
    # --- Visualization tabs instead of radio buttons ---
    if section_scores:
        st.subheader("📊 Detailed Section Analysis")

        # Compute charts only once, when new suggestions come in
        if 'eval_chart_cache' not in st.session_state or not st.session_state['eval_chart_cache']:
            st.session_state['eval_chart_cache'] = {
                'radar': create_section_score_chart(section_scores),
                'bar': create_bar_chart(section_scores),
                'donut': create_donut_chart(section_scores),
                'gauges_data': section_scores
            }

        charts = st.session_state['eval_chart_cache']
        
        # Create tabs for each visualization
        tab1, tab2, tab3, tab4 = st.tabs(["🎮 Game Style (Radar)", "📊 Simple Bars", "🍩 Donut Chart", "🎯 Simple Gauges"])
        
        with tab1:
            if charts['radar']:
                st.plotly_chart(charts['radar'], width="stretch")
            else:
                st.info("Radar chart not available")
        
        with tab2:
            if charts['bar']:
                st.plotly_chart(charts['bar'], width="stretch")
            else:
                st.info("Bar chart not available")
        
        with tab3:
            if charts['donut']:
                st.plotly_chart(charts['donut'], width="stretch")
            else:
                st.info("Donut chart not available")
        
        with tab4:
            if charts['gauges_data']:
                create_gauges(charts['gauges_data'])
            else:
                st.info("Gauge data not available")

        # Section details in expandable cards (keep this part as is)
        col1, col2 = st.columns(2)
        section_items = list(section_scores.items())
        
        for i, (section, analysis) in enumerate(section_items):
            if not isinstance(analysis, dict):
                continue
                
            score = analysis.get('score', 0)
            with (col1 if i % 2 == 0 else col2):
                with st.expander(f"📋 {section.title()} (Score: {score:.1f}/100)", expanded=False):
                    
                    # Metrics
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric("Word Count", analysis.get('word_count', 0))
                    with metric_col2:
                        st.metric("JD Keywords", analysis.get('keyword_matches', 0))
                    
                    # Strengths
                    strengths = analysis.get('strengths', [])
                    if strengths:
                        st.success("**✅ Strengths:**")
                        for strength in strengths:
                            st.write(f"• {strength}")
                    
                    # Suggestions
                    suggestions = analysis.get('specific_suggestions', [])
                    if suggestions:
                        st.info("**💡 AI Recommendations:**")
                        for suggestion in suggestions:
                            st.markdown(f"""
                            <div class="suggestion-box" style="margin: 0.3rem 0; padding: 0.8rem;">
                                🤖 {suggestion}
                            </div>
                            """, unsafe_allow_html=True)
    
    # Priority Suggestions
    st.subheader("🎯 Prioritized Action Plan")
    
    priority_suggestions = suggestion_results.get('priority_suggestions', {})
    priorities = [('critical', '🚨'), ('high', '⚠️'), ('medium', '📝'), ('low', '💡')]
    
    for priority, icon in priorities:
        suggestions = priority_suggestions.get(priority, [])
        if suggestions:
            expanded = priority in ['critical', 'high']
            
            with st.expander(f"{icon} {priority.title()} Priority ({len(suggestions)} items)", expanded=expanded):
                
                # Show reasoning if available
                priority_reasoning = reasoning.get(priority, '')
                if priority_reasoning:
                    st.info(f"💭 **Why this matters:** {priority_reasoning}")
                
                for i, suggestion in enumerate(suggestions, 1):
                    css_class = f"{priority}-suggestion"
                    
                    st.markdown(f"""
                    <div class="{css_class}">
                        <strong>{i}.</strong> {suggestion}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Personalized Advice
    personalized_advice = suggestion_results.get('personalized_advice', [])
    if personalized_advice:
        st.subheader("🎯 Personalized Recommendations")
        
        for i, advice in enumerate(personalized_advice, 1):
            st.markdown(f"""
            <div class="suggestion-box">
                <strong>{i}.</strong> {advice}
            </div>
            """, unsafe_allow_html=True)
    
    # Style Feedback
    style_feedback = suggestion_results.get('style_feedback', [])
    if style_feedback:
        with st.expander("✍️ Writing Style Analysis"):
            for feedback in style_feedback:
                st.warning(f"📝 {feedback}")

def display_resume_preview(resume_data: Dict, candidate_name: str):
    """Display formatted resume preview"""
    
    preview_container = st.container()
    
    with preview_container:
        st.markdown(f"""
        <div class="resume-preview">
            <h3 style="color: #1f77b4; margin-bottom: 1rem;">📄 {candidate_name}</h3>
        """, unsafe_allow_html=True)
        
        # Contact Information
        contact = resume_data.get('contact', {})
        if contact:
            st.markdown("**📧 Contact Information**")
            for key, value in contact.items():
                if value:
                    st.write(f"• **{key.title()}:** {value}")
        
        # Skills
        skills = resume_data.get('skills', [])
        if skills:
            st.markdown("**🛠️ Skills**")
            if isinstance(skills, list):
                st.write("• " + " • ".join(skills))
            else:
                st.write(skills)
        
        # Experience
        experience = resume_data.get('experience', []) or resume_data.get('internships', [])
        if experience:
            st.markdown("**💼 Experience**")
            if isinstance(experience, list):
                for exp in experience[:3]:  # Show first 3
                    if isinstance(exp, dict):
                        company = exp.get('company', 'Company')
                        role = exp.get('role', 'Role')
                        duration = exp.get('duration', '')
                        st.write(f"• **{role}** at {company} ({duration})")
                    else:
                        st.write(f"• {exp}")
            else:
                st.write(experience[:200] + "..." if len(str(experience)) > 200 else experience)
        
        # Projects
        projects = resume_data.get('projects', [])
        if projects:
            st.markdown("**🚀 Projects**")
            if isinstance(projects, list):
                for project in projects[:2]:  # Show first 2
                    st.write(f"• {project}")
            else:
                st.write(projects[:200] + "..." if len(str(projects)) > 200 else projects)
        
        # Education
        education = resume_data.get('education', [])
        if education:
            st.markdown("**🎓 Education**")
            if isinstance(education, list):
                for edu in education:
                    if isinstance(edu, dict):
                        degree = edu.get('degree', 'Degree')
                        institution = edu.get('institution', 'Institution')
                        st.write(f"• {degree} from {institution}")
                    else:
                        st.write(f"• {edu}")
            else:
                st.write(education)
        
        st.markdown("</div>", unsafe_allow_html=True)

def enhanced_ranking_display(df: pd.DataFrame, components: Dict, jd_text: str):
    """Enhanced ranking display with all requested features"""
    
    # Header with controls - MUTUALLY EXCLUSIVE sections
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        st.subheader("🏆 Resume Rankings")

    with col2:
        anonymize = st.checkbox(
            "🕶️ Anonymize", 
            value=st.session_state.anonymize_mode,
            help="Hide names and emails to reduce bias",    
            key="anonymize_checkbox_ranking" 
        )
        st.session_state.anonymize_mode = anonymize

    with col3:
        if st.button("📊 Reports", help="Generate detailed analysis reports", 
                    type="primary" if st.session_state.get('show_reports', False) else "secondary"):
            st.session_state.show_reports = True
            st.session_state.show_export = False

    with col4:
        if st.button("📧 Export", help="Export results in multiple formats",
                    type="primary" if st.session_state.get('show_export', False) else "secondary"):
            st.session_state.show_export = True
            st.session_state.show_reports = False
    
    # MUTUALLY EXCLUSIVE: Show either Reports or Export options, not both
    if st.session_state.get('show_reports', False):
        generate_reports(df, jd_text)
        
    if st.session_state.get('show_export', False):
        show_export_options(df)

    # Add this CSS to improve the export buttons layout
    st.markdown("""
    <style>
    .export-buttons-container {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin: 1rem 0;
    }
    .export-button {
        flex: 1;
        min-width: 120px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Success message with stats
    st.markdown(f"""
    <div class="score-display">
        <h4>✅ Successfully Ranked {len(df)} Resumes</h4>
        <p>Average Score: {df['Score (%)'].mean():.1f}% • Top Score: {df['Score (%)'].max():.1f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top 3 candidates showcase
    if len(df) >= 3:
        st.markdown("### 🏆 Top 3 Candidates")
        
        cols = st.columns(3)
        medals = ["🥇", "🥈", "🥉"]
        colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
        
        for i in range(min(3, len(df))):
            candidate = df.iloc[i]
            
            with cols[i]:
                display_name = f"Candidate {i+1}" if anonymize else candidate['Name']
                display_email = "***@***.***" if anonymize else candidate['Email']
                
                # in enhanced_ranking_display(), inside the Top-3 loop
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {colors[i]}; text-align: center;">
                <h2>{medals[i]} Rank {i+1}</h2>
                <h4>{display_name}</h4>
                <p>📧 {display_email}</p>
                <h3 class="score-value" style="color: {colors[i]};">{candidate['Score (%)']}%</h3>
                </div>
                """, unsafe_allow_html=True)

                # Preview button with callback (use basename so key matches resume_previews)
                # if st.button("👁️ Preview", key=f"preview_top_{i}"):
                #     file_name = os.path.basename(candidate.get('Filename', ''))
                #     if file_name in st.session_state.resume_previews:
                #         st.session_state.preview_selector = file_name
                #         st.session_state.pending_active_view = "🏆 Bulk Ranking"
                #         st.rerun()

    
    # Enhanced results table
    st.markdown("### 📋 Complete Rankings")
    
    # Prepare display dataframe
    display_df = df.copy()
    if anonymize:
        display_df['Name'] = [f"Candidate {i}" for i in range(1, len(df) + 1)]
        display_df['Email'] = "***@***.***"
        if 'Phone' in display_df.columns:
            display_df['Phone'] = "***-***-****"
    
    # Interactive table with hover effects
    def highlight_scores(val):
        if isinstance(val, (int, float)):
            if val >= 80:
                return 'background: linear-gradient(90deg, #d4edda, #c3e6cb); color: #155724; font-weight: bold;'
            elif val >= 60:
                return 'background: linear-gradient(90deg, #fff3cd, #ffeaa7); color: #856404; font-weight: bold;'
            elif val >= 40:
                return 'background: linear-gradient(90deg, #f8d7da, #fab1a0); color: #721c24; font-weight: bold;'
            else:
                return 'background: linear-gradient(90deg, #f5c6cb, #e17055); color: #721c24; font-weight: bold;'
        return ''
    
    # Add Rank column first
    display_df.insert(0, "Rank", range(1, len(display_df) + 1))

    # Drop the index entirely
    display_df = display_df.reset_index(drop=True)

    # Apply styling
    styled_df = display_df.style.map(highlight_scores, subset=['Score (%)'])

    # Show in Streamlit
    st.dataframe(styled_df, width="stretch", hide_index=True)


    # Resume preview section
    if st.session_state.resume_previews:
        st.markdown("### 👁️ Resume Preview")
        
        # Build preview options
        preview_options = []
        for idx, row in df.iterrows():
            file_name = os.path.basename(row.get('Filename', ''))
            display_name = f"Candidate {idx+1}" if anonymize else row.get('Name', f"Candidate {idx+1}")
            score = row.get('Score (%)', '')
            if file_name in st.session_state.resume_previews:
                preview_options.append((file_name, f"Rank {idx+1}: {display_name} ({score}%)"))
        
        if preview_options:
            # Create the dropdown selector
            options = ["Select a resume to preview..."] + [opt[1] for opt in preview_options]
            selected_option = st.selectbox(
                "Choose a resume to preview:",
                options=options,
                key="preview_selectbox"
            )

            # Only show preview if a resume is selected (not the placeholder)
            if selected_option and selected_option != "Select a resume to preview...":
                # Find the corresponding file name for the selected option
                selected_preview = None
                for file_name, display_name in preview_options:
                    if display_name == selected_option:
                        selected_preview = file_name
                        break
                
                if selected_preview:
                    # Find the candidate in the dataframe
                    matched_rows = df[df['Filename'].apply(lambda x: os.path.basename(str(x))) == selected_preview]
                    
                    if not matched_rows.empty:
                        candidate_row = matched_rows.iloc[0]
                        rank = matched_rows.index[0] + 1
                        
                        display_name = f"Candidate {rank}" if anonymize else candidate_row.get('Name', f"Candidate {rank}")
                        
                        # Display the preview
                        st.subheader(f"📄 Resume Preview: {display_name}")
                        
                        # Try to show the original uploaded file
                        file_bytes = st.session_state.get('uploaded_files_store', {}).get(selected_preview)
                        
                        if file_bytes:
                            ext = os.path.splitext(selected_preview)[1].lower()
                            
                            if ext == ".pdf":
                                b64 = base64.b64encode(file_bytes).decode("utf-8")
                                pdf_display = f'<embed src="data:application/pdf;base64,{b64}" type="application/pdf" width="100%" height="700px" />'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                                st.download_button(
                                    "Download original PDF", 
                                    data=file_bytes, 
                                    file_name=selected_preview, 
                                    mime="application/pdf"
                                )
                            else:
                                mime = "application/octet-stream"
                                if ext in [".docx", ".doc"]:
                                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                elif ext == ".txt":
                                    mime = "text/plain"
                                
                                st.download_button(
                                    "Download original resume", 
                                    data=file_bytes, 
                                    file_name=selected_preview, 
                                    mime=mime
                                )
                                st.info("Preview of original file may not render in-browser. Showing parsed preview below.")
                                
                                # Show parsed preview as fallback
                                display_resume_preview(
                                    st.session_state['resume_previews'][selected_preview],
                                    display_name
                                )
                        else:
                            # Show parsed preview if original file not available
                            display_resume_preview(
                                st.session_state['resume_previews'][selected_preview],
                                display_name
                            )
            else:
                # Show placeholder message when no resume is selected
                st.info("Select a resume from the dropdown above to view its preview")
def generate_reports(df: pd.DataFrame, jd_text: str):
    """Generate detailed analysis reports with better formatting"""
    
    progress_steps = [
        "Analyzing top candidates...",
        "Generating personalized insights...",
        "Creating detailed reports...",
        "Finalizing recommendations..."
    ]
    
    progress_placeholder = st.empty()
    
    for i, step in enumerate(progress_steps):
        progress_placeholder.markdown(show_progress_indicator(progress_steps, i), unsafe_allow_html=True)
        time.sleep(0.5)  # Simulate processing
        
        if i == 1:  # During analysis phase
            detailed_analysis = {}
            for _, candidate in df.head(5).iterrows():  # Analyze top 5
                if candidate['Filename'] in st.session_state.resume_previews:
                    resume_data = st.session_state.resume_previews[candidate['Filename']]
                    suggestions = get_enhanced_suggestions(resume_data, jd_text)
                    detailed_analysis[candidate['Name']] = {
                        'suggestions': suggestions,
                        'score': candidate['Score (%)'],
                        'email': candidate['Email']
                    }
    
    progress_placeholder.empty()
    
    # Display generated reports in an expandable container
    with st.expander("📋 Executive Summary Report", expanded=True):
        
        st.success("📊 Detailed reports generated successfully!")
        
        # Overall statistics in a nice grid
        st.markdown("### 📈 Batch Analysis Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Resumes", len(df), help="Number of resumes processed")
        with col2:
            st.metric("Average Score", f"{df['Score (%)'].mean():.1f}%", help="Average match score across all resumes")
        with col3:
            st.metric("Top Score", f"{df['Score (%)'].max():.1f}%", help="Highest individual score achieved")
        with col4:
            qualified_count = len(df[df['Score (%)'] >= 60])
            st.metric("Qualified (≥60%)", qualified_count, help="Resumes meeting qualification threshold")
        
        # Score distribution chart with better styling
        st.markdown("### 📊 Score Distribution")
        score_ranges = ['0-40%', '40-60%', '60-80%', '80-100%']
        score_counts = [
            len(df[df['Score (%)'] < 40]),
            len(df[(df['Score (%)'] >= 40) & (df['Score (%)'] < 60)]),
            len(df[(df['Score (%)'] >= 60) & (df['Score (%)'] < 80)]),
            len(df[df['Score (%)'] >= 80])
        ]
        
        colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']  # Red, Orange, Blue, Green
        
        fig = go.Figure(data=[go.Bar(
            x=score_ranges, 
            y=score_counts, 
            marker_color=colors,
            text=score_counts,
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Candidate Score Distribution",
            xaxis_title="Score Range",
            yaxis_title="Number of Candidates",
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True, key="score_distribution_chart")
        
        # Top candidates detailed analysis
        if detailed_analysis:
            st.markdown("### 🏆 Top Candidate Analysis")
            
            for i, (name, analysis) in enumerate(list(detailed_analysis.items())[:3], 1):
                with st.expander(f"{i}. {name} - {analysis['score']}% Match Score", expanded=i==1):
                    
                    # Only show contact info and meaningful suggestions
                    st.write(f"📧 **Contact:** {analysis['email']}")
                    
                    # Only show critical/high suggestions if they exist
                    critical = analysis['suggestions'].get('priority_suggestions', {}).get('critical', [])
                    high = analysis['suggestions'].get('priority_suggestions', {}).get('high', [])
                    
                    if critical:
                        st.warning("**🔴 Critical Improvement Areas:**")
                        for item in critical[:2]:  # Show max 2 critical items
                            st.write(f"• {item}")
                    
                    if high:
                        st.info("**⚠️ High Priority Suggestions:**")
                        for item in high[:2]:  # Show max 2 high priority items
                            st.write(f"• {item}")
                    
                    # Show strengths if available (but only if they exist)
                    section_scores = analysis['suggestions'].get('section_scores', {})
                    if section_scores:
                        strengths = []
                        for section, data in section_scores.items():
                            if isinstance(data, dict) and 'strengths' in data and data['strengths']:
                                strengths.extend(data['strengths'][:1])  # Take top strength per section
                        
                        if strengths:
                            st.success("**✅ Key Strengths:**")
                            for strength in strengths[:3]:
                                st.write(f"• {strength}")
                    
                    # If no meaningful suggestions, show a positive message
                    if not critical and not high:
                        st.success("🎉 Strong candidate! No critical improvement areas identified.")
    
    # Close button for reports
    if st.button("❌ Close Reports", key="close_reports"):
        st.session_state.show_reports = False
        st.rerun()

def show_export_options(df: pd.DataFrame):
    """Show export options for rankings with better layout"""
    
    st.markdown("### 📥 Export Options")
    
    # Use columns for better button layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Export
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📊 Download CSV",
            csv_data,
            f"resume_rankings_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            help="Export rankings as CSV file",
            use_container_width=True
        )
    
    with col2:
        # Excel Export
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Rankings')
        
        st.download_button(
            "📈 Download Excel",
            excel_buffer.getvalue(),
            f"resume_rankings_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Export rankings as Excel file",
            use_container_width=True
        )
    
    with col3:
        # JSON Export (for detailed analysis)
        json_data = df.to_json(orient='records', indent=2)
        st.download_button(
            "🔧 Download JSON",
            json_data.encode('utf-8'),
            f"resume_rankings_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            "application/json",
            help="Export rankings as JSON for further processing",
            use_container_width=True
        )
    
    # Close button
    if st.button("❌ Close Export Options", use_container_width=True):
        st.session_state.show_export = False
        st.rerun()

def feedback_section():
    """Enhanced feedback collection section"""
    
    st.markdown("""
    <div class="main-header">
        <h2>💬 Share Your Feedback</h2>
        <p>Help us improve our AI-powered resume evaluation system!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.feedback_submitted:
        
        with st.form("feedback_form", clear_on_submit=True):
            st.markdown('<div class="feedback-form">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input(
                    "👤 Your Name *",
                    placeholder="Enter your full name",
                    help="We'd like to know who's providing the feedback"
                )
            
            with col2:
                email = st.text_input(
                    "📧 Email Address *",
                    placeholder="your.email@example.com",
                    help="We'll use this to follow up if needed"
                )
            
            feedback_type = st.selectbox(
                "📝 Feedback Type",
                ["General Feedback", "Bug Report", "Feature Request", "Improvement Suggestion", "Complaint"],
                help="Select the type of feedback you're providing"
            )
            
            feedback_text = st.text_area(
                "💭 Your Feedback *",
                placeholder="Please share your thoughts, suggestions, or report any issues you encountered...",
                height=150,
                help="Be as detailed as possible to help us understand your experience"
            )
            
            rating = st.slider(
                "⭐ Overall Rating",
                1, 5, 4,
                help="Rate your overall experience with the tool"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            submitted = st.form_submit_button("📤 Submit Feedback", type="primary")
            
            if submitted:
                if name and email and feedback_text:
                    # Enhanced feedback object
                    feedback_data = {
                        "name": name,
                        "email": email,
                        "feedback_type": feedback_type,
                        "feedback": feedback_text,
                        "rating": rating,
                        "timestamp": datetime.now().isoformat(),
                        "user_agent": "Streamlit App",
                        "session_id": st.session_state.get('session_id', 'unknown')
                    }
                    
                    if save_feedback(name, email, f"[{feedback_type}] Rating: {rating}/5 - {feedback_text}"):
                        st.session_state.feedback_submitted = True
                        st.success("✅ Thank you! Your feedback has been submitted successfully.")
                        st.balloons()
                        
                        # Show appreciation message
                        st.markdown(f"""
                        <div class="score-display">
                            <h4>🙏 Thank You, {name}!</h4>
                            <p>Your {feedback_type.lower()} with {rating}⭐ rating helps us improve our AI system.</p>
                            <p>We'll review your feedback and may reach out to you at {email} if needed.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ Sorry, there was an error saving your feedback. Please try again.")
                else:
                    st.warning("⚠️ Please fill in all required fields (marked with *) before submitting.")
    else:
        # Already submitted
        st.markdown("""
        <div class="score-display">
            <h4>✅ Feedback Already Submitted</h4>
            <p>Thank you for your feedback! We appreciate your input.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Submit Another Feedback"):
            st.session_state.feedback_submitted = False
            st.rerun()
    
    # Recent feedback display (admin/demo view)
    st.markdown("---")
    
    if st.checkbox("👨‍💼 View Recent Feedback (Demo Mode)", help="This would be admin-only in production"):
        feedback_data = load_feedback()
        if feedback_data:
            st.markdown("### 📋 Recent Feedback")
            
            # Show statistics
            if len(feedback_data) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Feedback", len(feedback_data))
                with col2:
                    avg_rating = sum(json.loads(f.get('feedback', '{}').split('Rating: ')[1].split('/')[0]) if 'Rating:' in f.get('feedback', '') else 4 for f in feedback_data) / len(feedback_data)
                    st.metric("Avg Rating", f"{avg_rating:.1f}⭐")
                with col3:
                    recent_count = len([f for f in feedback_data if (datetime.now() - datetime.fromisoformat(f['timestamp'])).days < 7])
                    st.metric("This Week", recent_count)
            
            # Show recent entries
            for feedback in feedback_data[-5:]:  # Show last 5
                with st.expander(f"💬 {feedback['name']} - {feedback['date_formatted']}"):
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Email:** {feedback['email']}")
                        st.markdown(f"**Feedback:** {feedback['feedback']}")
                    
                    with col2:
                        st.markdown(f"**ID:** #{feedback['id']}")
                        if 'Rating:' in feedback['feedback']:
                            rating_match = feedback['feedback'].split('Rating: ')[1].split('/')[0]
                            st.markdown(f"**Rating:** {rating_match}⭐")
        else:
            st.info("📭 No feedback received yet.")

def evaluation_tab(components: Dict):
    """Enhanced single resume evaluation interface"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📝 AI-Powered Resume Evaluation</h1>
        <p>Get instant AI insights and personalized improvement suggestions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload with enhanced UI
    uploaded_file = st.file_uploader(
        "📁 Upload Your Resume",
        type=["pdf", "docx"],
        key="eval_upload",
        help="Upload your resume in PDF or DOCX format for comprehensive AI analysis"
    )
    
    if uploaded_file:
        file_size = len(uploaded_file.getvalue())
        st.success(f"✅ File uploaded successfully! ({file_size:,} bytes)")
    
    # Job description input with enhanced features
    st.subheader("📋 Job Description")
    jd_text = get_jd_input_enhanced(components['jds'], "eval")
    
    # Main evaluation button
    if st.button("🚀 Analyze Resume", type="primary", disabled=not (uploaded_file and jd_text)):
        
        if uploaded_file and jd_text:
            
            # Progress tracking
            progress_steps = [
                "📄 Processing resume content...",
                "🔍 Analyzing structure and format...", 
                "🤖 Computing AI similarity scores...",
                "💡 Generating personalized suggestions...",
                "✨ Finalizing recommendations..."
            ]
            
            progress_placeholder = st.empty()
            
            try:
                # Step-by-step processing with progress updates
                for i, step in enumerate(progress_steps):
                    progress_placeholder.markdown(show_progress_indicator(progress_steps, i), unsafe_allow_html=True)
                    
                    if i == 0:
                        # Parse resume
                        resume_data = process_resume_upload(uploaded_file, "eval")
                        if not resume_data:
                            st.error("❌ Failed to process resume. Please check the file format.")
                            return
                    
                    elif i == 1:
                        # Analyze structure
                        sections_found = len([k for k, v in resume_data.items() if v and k not in ['metadata', 'global_entities', 'section_entities']])
                        st.info(f"📊 Found {sections_found} resume sections to analyze")
                    
                    elif i == 2:
                        # Calculate similarity score
                        # Combine structured resume data first
                        combined_text = parser.combine_structured_resume(resume_data)
                        results = components['matcher'].get_similarity_score(
                            jd_text, [combined_text]
                        )
                        score = results[0][1] if results else 0
                        st.session_state.current_score = score
                    
                    elif i == 3:
                        # Generate enhanced suggestions - FIXED VERSION
                        suggestion_results = get_enhanced_suggestions(resume_data, jd_text)
                        st.session_state.current_suggestions = suggestion_results
                        st.session_state.current_resume_data = resume_data

                        # --- NEW: clear cached charts so we'll compute fresh charts for this analysis ---
                        st.session_state['eval_chart_cache'] = {}

                                        
                    time.sleep(0.3)  # Brief pause for UX
                
                progress_placeholder.empty()
                
                # Display results
                if st.session_state.current_suggestions:
                    
                    # Main score display
                    score_percent = st.session_state.current_score * 100
                    
                    display_enhanced_suggestions(st.session_state.current_suggestions)
                
                
                else:
                    st.error("❌ Failed to generate suggestions. Please try again.")
            
            except Exception as e:
                progress_placeholder.empty()
                st.error(f"❌ An error occurred during analysis: {str(e)}")
                st.write("Please try uploading a different file or contact support if the issue persists.")

def ranking_tab(components: Dict):
    """Enhanced multiple resume ranking interface"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏆 AI-Powered Resume Ranking</h1>
        <p>Upload multiple resumes and get instant AI-powered candidate rankings</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload with enhanced features
    uploaded_files = st.file_uploader(
        "📁 Upload Multiple Resumes",
        accept_multiple_files=True,
        type=["pdf", "docx"],
        key="rank_uploads",
        help="Upload multiple resume files for batch analysis and intelligent ranking"
    )
    # Reset display flag when entering ranking tab or when new files uploaded
    if 'rank_displayed_this_run' not in st.session_state:
        st.session_state['rank_displayed_this_run'] = False

    # If the user uploads new files, reset so the next rank run shows fresh results
    if uploaded_files:
        st.session_state['rank_displayed_this_run'] = False

    
    if uploaded_files:
        # Show upload summary
        total_size = sum(len(f.getvalue()) for f in uploaded_files)
        
        st.markdown(f"""
        <div class="score-display">
            <h4>✅ {len(uploaded_files)} Resumes Uploaded Successfully!</h4>
            <p>Total size: {total_size:,} bytes • Ready for AI analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File list with details
        with st.expander("📋 Uploaded Files Details"):
            for i, file in enumerate(uploaded_files, 1):
                file_size = len(file.getvalue())
                st.write(f"{i}. **{file.name}** ({file_size:,} bytes)")
    
    # Job description input
    st.subheader("📋 Job Requirements")
    jd_text = get_jd_input_enhanced(components['jds'], "rank")

    # ADD THESE CONTROLS HERE:
    st.markdown("---")
    st.subheader("📊 Ranking Filters")

    col1, col2 = st.columns(2)
    with col1:
        st.slider(
            "Minimum Score Threshold (%)", 
            0, 100, 20,
            key="score_threshold",
            help="Show only resumes above this score percentage"
        )
    with col2:
        st.checkbox(
            "Show All Results", 
            value=st.session_state.show_all_results,
            key="show_all_results_checkbox",  
            help="Display all resumes regardless of score"
        )

    if st.button("🚀 Rank All Resumes", type="primary", disabled=not (uploaded_files and jd_text)):
        if uploaded_files and jd_text:
            progress_steps = [
                f"📂 Processing {len(uploaded_files)} resume files.",
                "🔍 Extracting content and metadata.",
                "🤖 Computing AI similarity scores.",
                "📊 Ranking candidates by relevance.",
                "🎯 Preparing detailed results."
            ]
            progress_placeholder = st.empty()

            try:
                file_paths = []
                resume_previews = {}

                # Keep tempdir alive until after ranking
                with tempfile.TemporaryDirectory() as tmp_dir:
                    for i, step in enumerate(progress_steps):
                        progress_placeholder.markdown(show_progress_indicator(progress_steps, i), unsafe_allow_html=True)

                        if i == 1:  # During file processing
                            file_progress = st.progress(0)
                            for idx, file in enumerate(uploaded_files):
                                # make a unique safe filename to avoid collisions
                                safe_name = file.name
                                path = os.path.join(tmp_dir, safe_name)
                                with open(path, "wb") as f:
                                    f.write(file.getbuffer())
                                file_paths.append(path)
                                # store the original uploaded bytes for previewing the real file later
                                try:
                                    file_bytes = file.getbuffer().tobytes()  # raw bytes
                                except Exception:
                                    # fallback if getbuffer isn't available
                                    file.seek(0)
                                    file_bytes = file.read()
                                st.session_state['uploaded_files_store'][file.name] = file_bytes
                                # Parse once for preview (best-effort) and store by basename
                                try:
                                    file.seek(0)
                                    parsed = parser.parse_resume(file)
                                    resume_previews[file.name] = parsed
                                except Exception:
                                    resume_previews[file.name] = {}

                                file_progress.progress((idx + 1) / len(uploaded_files))
                            file_progress.empty()


                        # small UX pause
                        time.sleep(0.3)

                    # Rank while files still exist
                    df = components['ranker'].process_batch(file_paths, jd_text)

                progress_placeholder.empty()

                # Optional: threshold filter
                if not st.session_state.show_all_results:
                    df = df[df['Score (%)'] >= st.session_state.score_threshold]

                if df.empty:
                    st.warning(f"⚠️ No resumes scored above {st.session_state.score_threshold}%")
                else:
                    # Ensure proper order + clean indices
                    df = df.sort_values('Score (%)', ascending=False).reset_index(drop=True)

                    # 🔹 Save results into session_state
                    st.session_state.resume_previews = resume_previews
                    st.session_state.ranked_df = df
                    st.session_state.rank_jd_text = jd_text
                    st.session_state.rank_ready = True

                    # Request navigation to Bulk Ranking on next rerun (applied before the radio widget)
                    st.session_state.pending_active_view = "🏆 Bulk Ranking"


            except Exception as e:
                progress_placeholder.empty()
                st.error(f"❌ An error occurred during batch processing: {e}")

    # Only display rankings if not already shown this run
    if st.session_state.get("rank_ready") and st.session_state.get("ranked_df") is not None:
        if not st.session_state.get("rank_displayed_this_run", False):
            enhanced_ranking_display(st.session_state.ranked_df, components, st.session_state.rank_jd_text)
            st.session_state["rank_displayed_this_run"] = True

def get_jd_input_enhanced(jds: Dict[str, str], tab_prefix: str) -> str:
    """Enhanced job description input with search and validation"""
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Search functionality
        search_term = st.text_input(
            "🔍 Search Job Roles",
            placeholder="e.g., Python, React, Data Science...",
            key=f"{tab_prefix}_search",
            help="Search through available job descriptions"
        )
        
        # Filter JDs based on search
        if search_term:
            filtered_jds = {
                role: desc for role, desc in jds.items()
                if search_term.lower() in role.lower() or search_term.lower() in desc.lower()
            }
            if filtered_jds:
                st.success(f"🎯 Found {len(filtered_jds)} matching roles")
            else:
                st.warning("⚠️ No matching roles found")
                filtered_jds = jds
        else:
            filtered_jds = jds
        
        # Job role selector
        jd_choice = st.selectbox(
            "Select Job Role:",
            options=["Custom Input"] + list(filtered_jds.keys()),
            key=f"{tab_prefix}_jd_choice",
            help="Choose from predefined roles or create custom input"
        )
    
    with col2:
        if jd_choice == "Custom Input":
            jd_text = st.text_area(
                "Enter Custom Job Description:",
                height=200,
                placeholder="Paste the complete job description here...\\n\\nInclude:\\n• Required skills and technologies\\n• Experience level\\n• Specific responsibilities\\n• Preferred qualifications",
                key=f"{tab_prefix}_custom_jd",
                help="💡 Include specific skills, technologies, and requirements for better matching"
            )
            
            # Validation for custom input
            if jd_text:
                word_count = len(jd_text.split())
                if word_count < 50:
                    st.warning(f"⚠️ JD seems short ({word_count} words). Consider adding more details for better analysis.")
                else:
                    st.success(f"✅ Good length ({word_count} words)")
        else:
            jd_text = filtered_jds.get(jd_choice, "")
            
            st.text_area(
                f"Job Description - {jd_choice}:",
                value=jd_text,
                height=200,
                key=f"{tab_prefix}_readonly_jd",
                disabled=True,
                help="This is a predefined job description. You can switch to 'Custom Input' to create your own."
            )
            
            # Show JD statistics
            if jd_text:
                word_count = len(jd_text.split())
                tech_keywords = sum(1 for word in jd_text.lower().split() if word in ['python', 'javascript', 'react', 'java', 'sql', 'aws', 'docker', 'kubernetes'])
                
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.caption(f"📊 {word_count} words")
                with col_stat2:
                    st.caption(f"🛠️ {tech_keywords} tech keywords")
    
    return jd_text

def process_resume_upload(uploaded_file, mode: str) -> Dict:
    """Enhanced resume processing with better error handling"""
    
    # Create a more specific cache key
    file_hash = hash(uploaded_file.getvalue())
    cache_key = f"{mode}_{uploaded_file.name}_{file_hash}"
    
    if cache_key not in st.session_state.processed_resumes:
        try:
            with st.spinner(f"🔄 Processing {uploaded_file.name}..."):
                # Reset file position
                uploaded_file.seek(0)
                
                # Parse the resume
                parsed_data = parser.parse_resume(uploaded_file)
                
                # Validate parsed data
                if not parsed_data or not any(parsed_data.get(k) for k in ['contact', 'skills', 'experience', 'projects', 'education']):
                    st.warning(f"⚠️ Limited content extracted from {uploaded_file.name}. Please ensure the file is not corrupted.")
                    return {}
                
                st.session_state.processed_resumes[cache_key] = parsed_data
                
                # Show parsing success with details
                sections_found = len([k for k, v in parsed_data.items() if v and k not in ['metadata', 'global_entities', 'section_entities']])
                st.success(f"✅ Successfully processed {uploaded_file.name} ({sections_found} sections found)")
                
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
            st.write("**Troubleshooting tips:**")
            st.write("• Ensure the file is not corrupted")
            st.write("• Try converting to PDF if using DOCX")
            st.write("• Check if the file contains readable text")
            return {}
    
    return st.session_state.processed_resumes[cache_key]

def sidebar_content():
    """Enhanced sidebar with app controls and information"""
    
    # Only show sidebar if not collapsed
    if st.session_state.sidebar_collapsed:
        return
    
    with st.sidebar:
        # Add close button at top of sidebar
        close_col1, close_col2 = st.columns([5, 1])
        with close_col1:
            st.markdown("## ⚙️ App Settings")
        with close_col2:
            if st.button("✕", key="sidebar_close", help="Close Sidebar", use_container_width=True):
                st.session_state.sidebar_collapsed = True
                st.rerun()

        # Theme and display options
        anonymize_default = st.checkbox("🕶️ Anonymize by Default", value=st.session_state.anonymize_mode,key="anonymize_checkbox_sidebar" )
        if anonymize_default != st.session_state.anonymize_mode:
            st.session_state.anonymize_mode = anonymize_default
        
        st.markdown("---")
        
        # App statistics
        st.markdown("## 📊 Session Statistics")
        
        processed_count = len(st.session_state.processed_resumes)
        preview_count = len(st.session_state.resume_previews)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Processed", processed_count)
        with col2:
            st.metric("Previews", preview_count)
        
        # Cache management
        if processed_count > 0:
            if st.button("🗑️ Clear Cache"):
                st.session_state.processed_resumes.clear()
                st.session_state.resume_previews.clear()
                st.success("✅ Cache cleared!")
                st.rerun()
        
        st.markdown("---")
        
        # Help and tips
        with st.expander("❓ Help & Tips"):
            st.markdown("""
            **🚀 Getting Started:**
            1. Upload resume files (PDF/DOCX)
            2. Select or enter job description  
            3. Click analyze for AI insights
            
            **💡 Pro Tips:**
            - Use detailed JDs for better matching
            - Try the interactive editor for improvements
            - Enable anonymization to reduce bias
            - Export results for further analysis
            
            **🔧 Troubleshooting:**
            - Clear cache if experiencing issues
            - Ensure files are readable text
            - Check file size limits (10MB max)
            - Try PDF format for better parsing
            """)
        
        # Quick actions
        st.markdown("## 🚀 Quick Actions")
        
        if st.button("🏆 Jump to Ranking"):
            st.session_state.pending_active_view = "🏆 Bulk Ranking"
            st.rerun()
        if st.button("📝 Jump to Evaluation"):
            st.session_state.pending_active_view = "📝 Resume Evaluation"
            st.rerun()
        if st.button("💬 Leave Feedback"):
            st.session_state.pending_active_view = "💬 Feedback & Support"
            st.rerun()

                
        st.markdown("---")
        
        # Version and info
        st.caption("🚀 AI Resume Evaluator")
        st.caption("Powered by advanced NLP & ML")
        st.caption("Built using Streamlit")

def main():
    """Enhanced main application with all fixes"""
    if 'pending_active_view' not in st.session_state:
        st.session_state['pending_active_view'] = ""
    
    # Initialize application
    loaded_components = load_components()
    if not loaded_components:
        st.error("❌ Failed to load application components. Please refresh the page.")
        return
    
    init_session_state()
    
    # Sidebar (only shown if not collapsed)
    if not st.session_state.sidebar_collapsed:
        sidebar_content()
    
    # Main application header with sidebar toggle
    if st.session_state.sidebar_collapsed:
        # When sidebar is collapsed, use full width
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
            <h1 style="background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem;">
                🚀 AI Resume Evaluator Pro
            </h1>
            <p style="font-size: 1.3rem; color: #666; margin: 0;">
                Advanced AI-powered resume analysis and optimization platform
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # When sidebar is open, adjust for sidebar width
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0; margin-bottom: 2rem;">
                <h1 style="background: linear-gradient(90deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem;">
                    🚀 AI Resume Evaluator 
                </h1>
                <p style="font-size: 1.3rem; color: #666; margin: 0;">
                    Advanced AI-powered resume analysis and optimization platform
                </p>
            </div>
            """, unsafe_allow_html=True)

    # Main navigation tabs
    views = ["📝 Resume Evaluation", "🏆 Bulk Ranking", "💬 Feedback & Support"]
    # views = ["📝 Resume Evaluation", "💬 Feedback & Support"]

    # Use .get() so missing keys don't raise AttributeError
    pending = st.session_state.get('pending_active_view', "")
    if pending:
        # apply pending and clear it safely
        st.session_state['active_view'] = pending
        st.session_state['pending_active_view'] = ""

    # Determine current active view safely (fallback to first view)
    current_view = st.session_state.get('active_view', views[0])
    index = views.index(current_view) if current_view in views else 0

    nav = st.radio(
        "Navigation",
        views,
        index=index,
        key="active_view",
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("""
        <div style="margin: 0.5rem 0;">
            <hr style="border: 1px solid #ddd; margin: 0;">
        </div>
        """, unsafe_allow_html=True)
    
    if nav == "📝 Resume Evaluation":
        evaluation_tab(loaded_components)
    elif nav == "🏆 Bulk Ranking":
        ranking_tab(loaded_components)
    else:
        feedback_section()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem 0;">
        <p style="font-size: 1.1rem; margin-bottom: 1rem;">
            🤖 Powered by Advanced AI • 📊 Enhanced with Machine Learning 
        </p>
        <p style="margin: 0;">
            <small>© 2024 AI Resume Evaluator Pro - Empowering careers through intelligent analysis</small>
        </p>
        <p style="margin-top: 1rem;">
            <span style="background: linear-gradient(45deg, #667eea, #764ba2); padding: 0.5rem 1rem; border-radius: 20px; color: white; font-size: 0.9rem;">
                🚀 Made for job seekers worldwide
            </span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Floating sidebar toggle button (shown when sidebar is collapsed)
    if st.session_state.sidebar_collapsed:
        # Render the button at top-level (avoid wrapping it inside columns)
        if st.button("📋", key="floating_toggle", help="Open Sidebar"):
            st.session_state.sidebar_collapsed = False
            st.rerun()

        # Single, robust components.html block (CSS + JS) to pin the toggle
        _components_top_left = """
        <style>
        /* target many potential selectors and force top-left */
        button[key="floating_toggle"],
        div[data-testid="column"] button[key="floating_toggle"],
        button[aria-label="Toggle sidebar"],
        button[title*="sidebar"],
        div[data-testid="stToggleSidebar"] button,
        div[role="button"][data-testid*="toggle"],
        button#floating_toggle_btn {
            position: fixed !important;
            top: 16px !important;
            left: 16px !important;
            bottom: auto !important;
            right: auto !important;
            margin: 0 !important;
            transform: none !important;
            z-index: 2147483647 !important; /* max z-index to beat everything */
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 48px !important;
            height: 48px !important;
            border-radius: 50% !important;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35) !important;
            background: transparent !important;
        }
        @media (max-width: 768px) {
            button[key="floating_toggle"],
            button[aria-label="Toggle sidebar"] {
                top: 12px !important;
                left: 12px !important;
            }
        }
        </style>

        <script>
        (function(){
            function findAndFix() {
                // 1) Try robust selectors first
                const selectors = [
                    'button[aria-label="Toggle sidebar"]',
                    'button[title*="sidebar"]',
                    'div[data-testid="stToggleSidebar"] button',
                    'div[role="button"][data-testid*="toggle"]'
                ];
                let btn = null;
                for (const s of selectors) {
                    const found = document.querySelector(s);
                    if (found) { btn = found; break; }
                }

                // 2) Fallback: find any button whose visible text is exactly the 📋 icon
                if (!btn) {
                    const candidates = Array.from(document.querySelectorAll('button'));
                    btn = candidates.find(b => (b.innerText || '').trim() === '📋') || null;
                }

                // 3) Fallback heuristic: small button with an icon or short text
                if (!btn) {
                    const candidates = Array.from(document.querySelectorAll('button'));
                    btn = candidates.find(b => {
                        const w = b.offsetWidth, h = b.offsetHeight;
                        const txt = (b.innerText || '').trim();
                        const looksLikeIcon = txt.length <= 3; // emoji or short
                        return (w && h && Math.max(w,h) <= 80 && (b.querySelector('svg') || looksLikeIcon));
                    }) || null;
                }

                if (!btn) return false;

                function applyStyles() {
                    const important = 'important';
                    btn.style.setProperty('position', 'fixed', important);
                    btn.style.setProperty('top', '16px', important);
                    btn.style.setProperty('left', '16px', important);
                    btn.style.setProperty('bottom', 'auto', important);
                    btn.style.setProperty('right', 'auto', important);
                    btn.style.setProperty('transform', 'none', important);
                    btn.style.setProperty('margin', '0', important);
                    btn.style.setProperty('z-index', '2147483647', important);
                    btn.style.setProperty('width', '48px', important);
                    btn.style.setProperty('height', '48px', important);
                    btn.style.setProperty('border-radius', '50%', important);
                    btn.style.setProperty('box-shadow', '0 6px 18px rgba(0,0,0,0.35)', important);
                }
                applyStyles();

                // clear positional styles from ancestors (safe loop limit)
                let p = btn.parentElement;
                let safety = 0;
                while (p && safety < 40) {
                    try {
                        if (p.style) {
                            p.style.transform = 'none';
                            p.style.bottom = '';
                            p.style.right = '';
                            p.style.left = '';
                        }
                    } catch(e) {}
                    p = p.parentElement;
                    safety++;
                }

                // observe DOM and reapply when Streamlit rerenders
                if (!window.__toggle_observer_installed) {
                    const mo = new MutationObserver(() => applyStyles());
                    mo.observe(document.body, { childList: true, subtree: true, attributes: true });
                    window.__toggle_observer_installed = true;
                }
                return true;
            }

            // try repeatedly to handle delayed render
            let tries = 0;
            const interval = setInterval(() => {
                tries++;
                const ok = findAndFix();
                if (ok || tries > 60) clearInterval(interval);
            }, 250);
        })();
        </script>
        """

        st_components.html(_components_top_left, height=0, scrolling=False)



if __name__ == "__main__":
    main()