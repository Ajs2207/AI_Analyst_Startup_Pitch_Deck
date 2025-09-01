import os
from analyzer import analyze_startup_data

def test_analyzer_with_sample_data():
    """
    Tests the analyze_startup_data function with sample pitch deck text.
    """
    sample_text = """
    Company: InnovateTech
    Tagline: Revolutionizing the future of AI.
    Problem: Businesses struggle to analyze large datasets efficiently.
    Solution: Our platform provides a scalable and intuitive solution for data analysis.
    Market Size: The global market for data analytics is projected to reach $200 billion by 2025.
    Business Model: We offer a subscription-based service with tiered pricing.
    Team: Our team consists of 10 experts in AI and data science.
    Funding Ask: We are seeking $2 million in seed funding.
    Revenue Projections: We project $5 million in annual recurring revenue within three years.
    """

    analysis_result = analyze_startup_data(sample_text)

    print("Analysis Result:")
    print(analysis_result)

    # Basic assertion to check if the result is a dictionary
    assert isinstance(analysis_result, dict), "The result should be a dictionary."

    # Check for the presence of all required keys in the result
    required_keys = [
        "company_name", "problem", "solution", "market_size",
        "business_model", "team_info", "funding_ask", "revenue_projection"
    ]
    for key in required_keys:
        assert key in analysis_result, f"The key '{key}' should be in the result."

    print("\nTest passed: The analysis result is a dictionary and contains all required keys.")

if __name__ == "__main__":
    test_analyzer_with_sample_data()