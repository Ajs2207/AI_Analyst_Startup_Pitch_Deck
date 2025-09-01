import streamlit as st
import requests
import time
import json

BACKEND_URL = "http://127.0.0.1:8000"

def main():
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(page_title="Startup Analyst MVP", layout="wide")

    # Load custom CSS
    with open("startup-analyst-mvp/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.sidebar.title("About")
    st.sidebar.info(
        "This application uses AI to analyze startup pitch decks and extract key information."
    )
    st.sidebar.markdown("---")
    st.sidebar.subheader("Technologies Used")
    st.sidebar.markdown(
        "- **Streamlit:** for the web interface\n"
        "- **FastAPI:** for the backend API\n"
        "- **Google Cloud Document AI:** for text extraction\n"
        "- **Gemini:** for data analysis"
    )

    st.title("🚀 AI-Powered Startup Pitch Deck Analyst")
    st.markdown("Upload a pitch deck in PDF format to extract key insights.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a pitch deck (max 10MB)",
    )

    if uploaded_file is not None:
        st.info(f"📄 File uploaded: **{uploaded_file.name}**")

        if st.button("Analyze Pitch Deck", key="analyze_button"):
            with st.spinner("Uploading and processing..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)

                    if response.status_code == 200:
                        job_id = response.json()["job_id"]
                        st.success(f"✅ File uploaded successfully. Job ID: {job_id}")

                        # Poll for results
                        with st.spinner("Analyzing startup data... This may take a moment."):
                            while True:
                                result_response = requests.get(f"{BACKEND_URL}/analyze/{job_id}")
                                if result_response.status_code == 200:
                                    result = result_response.json()
                                    if result["status"] == "completed":
                                        st.success("✅ Analysis complete!")
                                        analysis_result = result["analysis"]
                                        
                                        st.subheader("Startup Analysis Results")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.info("Company Information")
                                            st.markdown(f"**Company Name:** {analysis_result.get('company_name', 'N/A')}")
                                            st.markdown(f"**Problem:** {analysis_result.get('problem', 'N/A')}")
                                            st.markdown(f"**Solution:** {analysis_result.get('solution', 'N/A')}")
                                        with col2:
                                            st.info("Financials")
                                            st.markdown(f"**Market Size:** {analysis_result.get('market_size', 'N/A')}")
                                            st.markdown(f"**Business Model:** {analysis_result.get('business_model', 'N/A')}")
                                            st.markdown(f"**Funding Ask:** {analysis_result.get('funding_ask', 'N/A')}")
                                            st.markdown(f"**Revenue Projection:** {analysis_result.get('revenue_projection', 'N/A')}")
                                        
                                        st.info("Team")
                                        st.markdown(f"**Team Info:** {analysis_result.get('team_info', 'N/A')}")

                                        st.download_button(
                                            label="Download Results",
                                            data=json.dumps(analysis_result, indent=4),
                                            file_name="analysis_results.json",
                                            mime="application/json",
                                        )
                                        break
                                    elif result["status"] == "failed":
                                        st.error(f"⚠️ Analysis failed: {result.get('error', 'Unknown error')}")
                                        break
                                time.sleep(2)  # Wait for 2 seconds before polling again
                    else:
                        st.error(f"⚠️ Error uploading file: {response.text}")

                except requests.exceptions.RequestException as e:
                    st.error(f"An error occurred while communicating with the backend: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()