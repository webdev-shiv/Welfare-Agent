# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Configure API Key for AI Studio Local Development
if "GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
os.environ["GOOGLE_CLOUD_PROJECT"] = ""  # Clear project requirement in AI Studio mode

# Import custom tools
from app.tools import (
    check_scheme_eligibility,
    compare_similar_schemes,
    detect_fraud_alerts,
    predict_future_life_events,
    search_all_schemes,
    verify_uploaded_documents,
)

# 1. User Profile Agent
user_profile_agent = Agent(
    name="user_profile_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Collects and manages the citizen's profile details including age, gender, state, income, occupation, category, education, and disability.",
    instruction="""
    You are the User Profile Agent. Your job is to format and summarize the citizen's profile details.

    If the user has provided profile data:
    - Capture Age, Gender, State, Income (INR), Occupation, Category (SC/ST/OBC/General), Education, and Disability Status (Yes/No).
    - Output a neat, structured markdown table summarizing their profile.
    - If any key details are missing (e.g. State, Income, or Category), politely ask the user to provide them so that we can calculate their eligibility accurately.
    """,
)

# 2. Scheme Discovery Agent
scheme_discovery_agent = Agent(
    name="scheme_discovery_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Searches for government schemes, scholarships, internships, pensions, and startup loans in the database.",
    instruction="""
    You are the Scheme Discovery Agent. Your job is to find central and state schemes that match the user's queries or profile.

    Use the `search_all_schemes` tool to find schemes.
    Explain the benefits and purpose of the matching schemes in a user-friendly way.
    If the search matches scholarships (like Post Matric or Pragati), technical programs (like AICTE), or startup support (like Mudra or SISFS), make sure to emphasize them!
    """,
    tools=[search_all_schemes],
)

# 3. Eligibility Evaluator Agent
eligibility_evaluator_agent = Agent(
    name="eligibility_evaluator_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Checks eligibility requirements, calculates scores, and explains reasons for qualification or rejection.",
    instruction="""
    You are the Eligibility Evaluator Agent.

    Your job is to compare a citizen's profile against scheme requirements.
    Use the `check_scheme_eligibility` tool to calculate eligibility scores.
    For each scheme evaluated:
    - Display the Eligibility Score (e.g., 92%).
    - Show a checklist of met requirements (with green checkmarks ✓) and failed requirements (with red crosses ✗).
    - Give a clear, simple explanation in plain words of why they qualify or not.
    - If they are rejected, recommend alternative schemes they might qualify for instead.
    """,
    tools=[check_scheme_eligibility],
)

# 4. Scheme Comparison Agent
scheme_comparison_agent = Agent(
    name="scheme_comparison_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Compares multiple similar government schemes or scholarships to find the best option.",
    instruction="""
    You are the Scheme Comparison Agent.

    Use the `compare_similar_schemes` tool to analyze two schemes.
    Compare their potential financial values, eligibility rules, and required documents.
    Summarize the comparison in a markdown table and make a clear recommendation on which scheme provides higher benefits or is easier to qualify for.
    """,
    tools=[compare_similar_schemes],
)

# 5. Document Verification Agent
document_verifier_agent = Agent(
    name="document_verifier_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Checks the completeness of uploaded documents and lists missing certificates.",
    instruction="""
    You are the Document Verification Agent.

    Your job is to check the citizen's uploaded certificates (e.g., Aadhaar, Income, Domicile, Caste, Marksheet, Disability) against required lists.
    Use the `verify_uploaded_documents` tool to analyze completeness.
    List all verified documents and clearly list missing certificates that are needed for application readiness.
    Explain the next steps for acquiring or uploading the missing certificates.
    """,
    tools=[verify_uploaded_documents],
)

# 6. Fraud Detection Agent
fraud_detection_agent = Agent(
    name="fraud_detection_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Detects fake government websites, scams, and phishing messages.",
    instruction="""
    You are the Fraud Detection Agent.

    Use the `detect_fraud_alerts` tool to inspect any link, website, or SMS text provided by the user.
    Provide a warning if the source is not an official government portal (gov.in or nic.in).
    Explain why it looks like a scam (e.g. asking for fees, using commercial domains, high-risk keywords) and list the official guidelines.
    """,
    tools=[detect_fraud_alerts],
)

# 7. Life Event Prediction Agent
life_event_prediction_agent = Agent(
    name="life_event_prediction_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Predicts future transitions and future eligibility opportunities based on age and occupation.",
    instruction="""
    You are the Life Event Prediction Agent.

    Use the `predict_future_life_events` tool to check upcoming transitions.
    Provide the citizen with a timeline of events (e.g., turning 18, graduating, turning 60) and list the future welfare schemes they will qualify for.
    """,
    tools=[predict_future_life_events],
)

# 8. Welfare Score Agent
welfare_score_agent = Agent(
    name="welfare_score_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description="Generates a citizen's welfare score showing potential, claimed, and missed benefits.",
    instruction="""
    You are the Welfare Score Agent.

    Calculate a general Welfare Score (out of 100) for the user.
    If the user has a profile and eligible schemes, estimate:
    - Welfare Score (reflecting their utilization of eligible benefits).
    - Total Potential Benefits (sum of values of eligible schemes).
    - Claimed Benefits (mocked or provided by the user).
    - Missed Benefits (difference between potential and claimed).
    Format the results in a beautiful summary block.
    """,
)

# Root Coordinator Agent
root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    You are the AI Welfare Operating System Coordinator. You help citizens discover, evaluate, verify, and apply for welfare schemes.

    You have a team of specialized sub-agents:
    - user_profile_agent: Managing citizen profiles.
    - scheme_discovery_agent: Searching schemes, scholarships, and MSME loans.
    - eligibility_evaluator_agent: Calculating eligibility scores and reasons.
    - scheme_comparison_agent: Comparing two schemes.
    - document_verifier_agent: Checking uploaded documents.
    - fraud_detection_agent: Checking scam links or fake scheme texts.
    - life_event_prediction_agent: Estimating future scheme transitions.
    - welfare_score_agent: Computing citizen welfare and utilization metrics.

    Greet the citizen warmly. If they ask about eligibility, first check if they have provided a profile.
    If they provide a query, route it to the appropriate sub-agent to get the most detailed and accurate response.
    Ensure you provide answers in a smooth, user-friendly, and clear manner. If the user asks in Hindi or other languages, translate scheme details or communicate in their preferred local language.
    """,
    sub_agents=[
        user_profile_agent,
        scheme_discovery_agent,
        eligibility_evaluator_agent,
        scheme_comparison_agent,
        document_verifier_agent,
        fraud_detection_agent,
        life_event_prediction_agent,
        welfare_score_agent,
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
