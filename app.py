import streamlit as st
import PyPDF2
from pptx import Presentation
import io
import re
import google.generativeai as genai

print("Module imported successfully!")

# ---- INIT GEMINI ----
genai.configure(api_key="AIzaSyCH73NYWr6tmKtRc3oEVUkgBZHDjCwTh58")  # replace with your Gemini key
model = genai.GenerativeModel("gemini-1.5-flash")

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="AI Pitch Deck Summariser",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- BEAUTIFUL CUSTOM CSS ----
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Inter', sans-serif;
        }
        
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 0;
            text-align: center;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .main-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(45deg, #fff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            color: #e0e7ff;
            font-size: 1.2rem;
            font-weight: 300;
            margin-bottom: 2rem;
        }
        
        .upload-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            margin-bottom: 2rem;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 3rem;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        .analysis-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.2);
            margin: 2rem 0;
            animation: slideUp 0.8s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .section-header {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 15px;
            font-size: 1.3rem;
            font-weight: 600;
            margin: 1.5rem 0 1rem 0;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .bullet-container {
            background: linear-gradient(135deg, #f8faff, #e0e7ff);
            padding: 1.2rem;
            border-radius: 15px;
            margin: 0.8rem 0;
            border-left: 5px solid #667eea;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s ease;
        }
        
        .bullet-container:hover {
            transform: translateX(5px);
        }
        
        .bullet-point {
            color: #2d3748;
            font-size: 1rem;
            font-weight: 500;
            line-height: 1.6;
            margin: 0;
        }
        
        .highlight-metric {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            display: inline-block;
            font-weight: 600;
            margin: 0.5rem;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            font-size: 0.95rem;
        }
        
        .investment-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 20px;
            margin: 1rem 0;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }
        
        .competitor-badge {
            background: rgba(102, 126, 234, 0.1);
            border: 2px solid #667eea;
            padding: 0.8rem 1.2rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            color: #667eea;
            font-weight: 600;
        }
        
        .loading-text {
            text-align: center;
            color: #667eea;
            font-size: 1.2rem;
            font-weight: 600;
            margin: 2rem 0;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            font-weight: 600;
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---- BEAUTIFUL HEADER ----
st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🚀 AI Pitch Deck Analyzer</h1>
        <p class="subtitle">Transform your pitch deck into actionable insights with AI-powered analysis</p>
    </div>
""", unsafe_allow_html=True)

# ---- UPLOAD SECTION ----
st.markdown('<div class="upload-container">', unsafe_allow_html=True)
st.markdown("### 📁 Upload Your Pitch Deck")
uploaded_file = st.file_uploader("Choose a PDF or PowerPoint file", type=["pdf", "pptx"], help="Supported formats: PDF, PPTX")
st.markdown('</div>', unsafe_allow_html=True)

# ---- ANALYSIS SECTION ----
if uploaded_file:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔍 Generate AI Analysis"):
            text = ""
            
            # File extraction with progress
            with st.spinner("📖 Extracting content from your pitch deck..."):
                # PDF extraction
                if uploaded_file.name.endswith(".pdf"):
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                
                # PPTX extraction
                elif uploaded_file.name.endswith(".pptx"):
                    prs = Presentation(io.BytesIO(uploaded_file.read()))
                    for slide in prs.slides:
                        for shape in slide.shapes:
                            if hasattr(shape, "text") and shape.text:
                                text += shape.text + "\n"
            
            # ---- AI ANALYSIS ----
            if text:
                with st.spinner("🤖 AI is analyzing your pitch deck..."):
                    prompt = f"""
                    You are a senior venture capitalist and business analyst. Analyze this pitch deck and provide precise, actionable insights in the following format:

                    **EXECUTIVE SUMMARY**
                    • Company: [One line company description]
                    • Problem: [Problem they solve in one line]  
                    • Solution: [Solution in one line]
                    • Market: [Target market size/opportunity in one line]

                    **STRENGTHS**
                    • [Strength 1 - max 12 words]
                    • [Strength 2 - max 12 words]
                    • [Strength 3 - max 12 words]

                    **WEAKNESSES**
                    • [Weakness 1 - max 12 words]
                    • [Weakness 2 - max 12 words]
                    • [Weakness 3 - max 12 words]

                    **OPPORTUNITIES**
                    • [Opportunity 1 - max 12 words]
                    • [Opportunity 2 - max 12 words]
                    • [Opportunity 3 - max 12 words]

                    **THREATS**
                    • [Threat 1 - max 12 words]
                    • [Threat 2 - max 12 words]
                    • [Threat 3 - max 12 words]

                    **KEY RISKS**
                    • [Risk 1 - max 15 words]
                    • [Risk 2 - max 15 words]
                    • [Risk 3 - max 15 words]

                    **MAIN COMPETITORS**
                    • [Competitor 1]: [Why they compete - max 10 words]
                    • [Competitor 2]: [Why they compete - max 10 words]
                    • [Competitor 3]: [Why they compete - max 10 words]

                    **INVESTMENT ANALYSIS**
                    • Stage: [Pre-seed/Seed/Series A/B/C]
                    • Range: $[X]M - $[Y]M
                    • Primary Use: [Main use of funds - max 10 words]
                    • Secondary Use: [Second use of funds - max 10 words]
                    • Timeline: [Expected fundraising timeline - max 8 words]

                    Be precise, direct, and actionable. Each bullet point should provide clear value.

                    Pitch Deck Content:
                    {text}
                    """
                    
                    response = model.generate_content(prompt)
                    analysis = response.text

                # ---- DISPLAY BEAUTIFUL ANALYSIS ----
                st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                st.markdown("## 📊 AI Analysis Results")
                
                # Parse and display with beautiful formatting
                sections = analysis.split("**")
                icons = {
                    "EXECUTIVE SUMMARY": "🎯",
                    "STRENGTHS": "💪",
                    "WEAKNESSES": "⚠️",
                    "OPPORTUNITIES": "🚀",
                    "THREATS": "⚡",
                    "KEY RISKS": "🚨",
                    "MAIN COMPETITORS": "🏆",
                    "INVESTMENT ANALYSIS": "💰"
                }
                
                for i in range(1, len(sections), 2):
                    if i < len(sections):
                        section_title = sections[i].strip()
                        section_content = sections[i+1].strip() if i+1 < len(sections) else ""
                        
                        if section_title in icons:
                            st.markdown(f'<div class="section-header">{icons[section_title]} {section_title}</div>', unsafe_allow_html=True)
                            
                            # Special formatting for investment section
                            if section_title == "INVESTMENT ANALYSIS":
                                st.markdown('<div class="investment-card">', unsafe_allow_html=True)
                                for line in section_content.split('\n'):
                                    if line.strip() and line.strip().startswith('•'):
                                        point = line.strip().replace('•', '').strip()
                                        st.markdown(f'<div class="highlight-metric">{point}</div>', unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Special formatting for competitors
                            elif section_title == "MAIN COMPETITORS":
                                for line in section_content.split('\n'):
                                    if line.strip() and line.strip().startswith('•'):
                                        point = line.strip().replace('•', '').strip()
                                        st.markdown(f'<div class="competitor-badge">🏢 {point}</div>', unsafe_allow_html=True)
                            
                            # Regular bullet points for other sections
                            else:
                                for line in section_content.split('\n'):
                                    if line.strip() and line.strip().startswith('•'):
                                        point = line.strip().replace('•', '').strip()
                                        st.markdown(f'<div class="bullet-container"><p class="bullet-point">• {point}</p></div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
                
                # Download button
                col1, col2, col3 = st.columns([1,1,1])
                with col2:
                    st.download_button(
                        label="📄 Download Analysis Report",
                        data=analysis,
                        file_name=f"pitch_analysis_{uploaded_file.name.split('.')[0]}.txt",
                        mime="text/plain",
                        help="Download the complete analysis as a text file"
                    )
            
            else:
                st.error("❌ Could not extract text from the uploaded file. Please ensure it contains readable content.")

# ---- FOOTER ----
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem;'>✨ Powered by Google Gemini AI | Built with Streamlit</p>", 
    unsafe_allow_html=True
)
