import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def analyze_startup_data(extracted_text):
    """
    Analyzes extracted text from a startup pitch deck using Gemini 2.5 Flash
    and returns a structured JSON output.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Analyze the following text from a startup pitch deck and extract the specified data points.
    Return the data in a structured JSON format.

    **Text to Analyze:**
    {extracted_text}

    **Data Points to Extract:**
    1. Company name and tagline
    2. Problem statement
    3. Solution description
    4. Market size (TAM/SAM)
    5. Business model
    6. Team size and key roles
    7. Funding ask amount
    8. Revenue projections (if mentioned)

    **JSON Output Format:**
    {{
        "company_name": "string",
        "problem": "string",
        "solution": "string",
        "market_size": "string",
        "business_model": "string",
        "team_info": "string",
        "funding_ask": "number",
        "revenue_projection": "string"
    }}
    """

    try:
        response = model.generate_content(prompt)
        # Assuming the response contains a JSON string, we need to parse it.
        # The Gemini API might return the JSON in a markdown block, so we clean it up.
        json_string = response.text.strip().replace('```json', '').replace('```', '')
        parsed_json = json.loads(json_string)

        # Validate JSON structure
        required_keys = [
            "company_name", "problem", "solution", "market_size",
            "business_model", "team_info", "funding_ask", "revenue_projection"
        ]
        if not all(key in parsed_json for key in required_keys):
            raise ValueError("JSON output is missing required keys")

        return parsed_json
    except json.JSONDecodeError:
        print("Failed to decode JSON from Gemini response")
        return None
    except ValueError as ve:
        print(f"Validation Error: {ve}")
        return None
    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        return None