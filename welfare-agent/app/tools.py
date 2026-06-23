from typing import Any
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "welfare_navigator.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class SchemesDbProxy(list):
    def __iter__(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schemes")
        rows = cursor.fetchall()
        conn.close()
        return (self._parse_row(r) for r in rows)
        
    def __len__(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM schemes")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def __getitem__(self, index):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schemes")
        rows = cursor.fetchall()
        conn.close()
        if isinstance(index, slice):
            return [self._parse_row(r) for r in rows[index]]
        return self._parse_row(rows[index])

    def _parse_row(self, row):
        d = dict(row)
        try:
            d["documents_required"] = json.loads(d["documents_required"])
        except:
            d["documents_required"] = d["documents_required"].split(",") if d["documents_required"] else []
        try:
            d["age_limit"] = json.loads(d["age_limit"])
        except:
            pass
        # Aliases for compatibility
        d["name"] = d["scheme_name"]
        d["documents"] = d["documents_required"]
        
        # Populate rules dict
        d["rules"] = {
            "income_max": d["income_limit"] if d["income_limit"] else 9999999.0,
            "gender": [d["gender"]] if d["gender"] != "All" else None,
            "occupation": [d["education"]] if d["education"] != "All" else None,
            "category": [d["caste_category"]] if d["caste_category"] != "All" else None,
            "disability_required": "Yes" if d["disability_required"] else "No"
        }
        if isinstance(d["age_limit"], dict):
            d["rules"]["age_min"] = d["age_limit"].get("min", 0)
            d["rules"]["age_max"] = d["age_limit"].get("max", 100)
        return d

# Create the global compatibility proxy
SCHEMES_DB = SchemesDbProxy()

def search_all_schemes(query: str) -> dict[str, Any]:
    """Searches the database for government schemes matching a keyword, category, or state.

    Args:
        query: The search term.

    Returns:
        A dictionary containing the list of matching schemes.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    q = f"%{query}%"
    cursor.execute("""
        SELECT * FROM schemes 
        WHERE scheme_name LIKE ? 
           OR ministry LIKE ? 
           OR category LIKE ? 
           OR description LIKE ? 
           OR benefits LIKE ?
    """, (q, q, q, q, q))
    
    rows = cursor.fetchall()
    conn.close()
    
    schemes = [SCHEMES_DB._parse_row(r) for r in rows]
    
    # Fallback to all schemes if none found
    if not schemes:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schemes LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        schemes = [SCHEMES_DB._parse_row(r) for r in rows]
        
    return {"status": "success", "count": len(schemes), "schemes": schemes}


def check_scheme_eligibility(
    scheme_name: str,
    age: int,
    gender: str,
    state: str,
    income: float,
    category: str,
    occupation: str,
    education: str,
    disability_status: str,
) -> dict[str, Any]:
    """Evaluates eligibility criteria for a specific welfare scheme based on citizen profile.

    Args:
        scheme_name: The exact name of the scheme to evaluate.
        age: The citizen's age in years.
        gender: The citizen's gender (Male, Female, Other).
        state: The citizen's state of residence.
        income: The annual family income in Rupees (INR).
        category: The social category (SC, ST, OBC, General).
        occupation: The occupation.
        education: The highest education level.
        disability_status: Yes or No regarding disability status.

    Returns:
        A dictionary containing eligibility score, reasons, status, and required documents.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schemes WHERE scheme_name = ?", (scheme_name,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"status": "error", "message": f"Scheme '{scheme_name}' not found."}
        
    scheme = SCHEMES_DB._parse_row(row)
    
    # 6 Matches calculations
    checklist = []
    reasons_eligible = []
    reasons_ineligible = []
    
    # 1. State Match (20 points)
    state_match_score = 0
    scheme_state = scheme["state_availability"]
    if scheme_state == "All" or scheme_state.lower() == "national" or scheme_state.lower() == state.lower():
        state_match_score = 20
        checklist.append({"rule": "Domicile Requirement", "status": "Passed", "value": f"Resident of {state} (Allowed: {scheme_state})"})
        reasons_eligible.append("State availability matched.")
    else:
        checklist.append({"rule": "Domicile Requirement", "status": "Failed", "value": f"Resident of {state} (Allowed: {scheme_state})"})
        reasons_ineligible.append(f"Only available in {scheme_state}.")

    # 2. Age Match (20 points)
    age_match_score = 0
    age_lim = scheme["age_limit"]
    if isinstance(age_lim, dict):
        age_min = age_lim.get("min", 0)
        age_max = age_lim.get("max", 100)
        if age_min <= age <= age_max:
            age_match_score = 20
            checklist.append({"rule": "Age Limit Check", "status": "Passed", "value": f"Age {age} (Limit: {age_min}-{age_max})"})
            reasons_eligible.append("Age is within the permitted range.")
        else:
            checklist.append({"rule": "Age Limit Check", "status": "Failed", "value": f"Age {age} (Limit: {age_min}-{age_max})"})
            reasons_ineligible.append(f"Age must be between {age_min} and {age_max}.")
    else:
        age_match_score = 20
        checklist.append({"rule": "Age Limit Check", "status": "Passed", "value": f"Age {age} (No limit)"})
        reasons_eligible.append("No age restriction.")

    # 3. Income Match (20 points)
    income_match_score = 0
    income_max = scheme["income_limit"]
    if income_max and income_max > 0:
        if income <= income_max:
            income_match_score = 20
            checklist.append({"rule": "Income Limit Check", "status": "Passed", "value": f"Income ₹{income:,.2f} (Limit: ₹{income_max:,.2f})"})
            reasons_eligible.append("Income is below the maximum limit.")
        else:
            checklist.append({"rule": "Income Limit Check", "status": "Failed", "value": f"Income ₹{income:,.2f} (Limit: ₹{income_max:,.2f})"})
            reasons_ineligible.append(f"Income exceeds the maximum limit of ₹{income_max:,.2f}.")
    else:
        income_match_score = 20
        checklist.append({"rule": "Income Limit Check", "status": "Passed", "value": f"Income ₹{income:,.2f} (No limit)"})
        reasons_eligible.append("No income restriction.")

    # 4. Gender Match (15 points)
    gender_match_score = 0
    scheme_gender = scheme["gender"]
    if scheme_gender == "All" or scheme_gender.lower() == gender.lower():
        gender_match_score = 15
        checklist.append({"rule": "Gender Requirement", "status": "Passed", "value": f"Gender {gender} (Allowed: {scheme_gender})"})
        reasons_eligible.append("Gender matched.")
    else:
        checklist.append({"rule": "Gender Requirement", "status": "Failed", "value": f"Gender {gender} (Allowed: {scheme_gender})"})
        reasons_ineligible.append(f"Only available to {scheme_gender} applicants.")

    # 5. Education Match (15 points)
    edu_match_score = 0
    scheme_edu = scheme["education"]
    # Check if matched
    if scheme_edu == "All" or scheme_edu.lower() == education.lower() or scheme_edu.lower() == occupation.lower():
        edu_match_score = 15
        checklist.append({"rule": "Education/Occupation Match", "status": "Passed", "value": f"{education}/{occupation} (Allowed: {scheme_edu})"})
        reasons_eligible.append("Education/Occupation criteria met.")
    elif scheme_edu.lower() == "student" and (occupation.lower() == "student" or education.lower() == "student" or "matric" in education.lower() or "b.tech" in education.lower()):
        edu_match_score = 15
        checklist.append({"rule": "Education/Occupation Match", "status": "Passed", "value": f"{education}/{occupation} (Student course)"})
        reasons_eligible.append("Education/Occupation criteria met.")
    else:
        checklist.append({"rule": "Education/Occupation Match", "status": "Failed", "value": f"{education}/{occupation} (Required: {scheme_edu})"})
        reasons_ineligible.append(f"Requires education/occupation to be {scheme_edu}.")

    # 6. Category Match (10 points)
    cat_match_score = 0
    scheme_cat = scheme["caste_category"]
    if scheme_cat == "All" or scheme_cat.lower() == category.lower():
        cat_match_score = 10
        checklist.append({"rule": "Social Category Check", "status": "Passed", "value": f"Category {category} (Allowed: {scheme_cat})"})
        reasons_eligible.append("Social category criteria met.")
    else:
        checklist.append({"rule": "Social Category Check", "status": "Failed", "value": f"Category {category} (Allowed: {scheme_cat})"})
        reasons_ineligible.append(f"Only open to {scheme_cat} category.")

    # 7. Additional check for disability (hard reject or explanation, not in main formula points, but logged)
    dis_req = scheme["disability_required"]
    dis_user = 1 if disability_status.lower() == "yes" else 0
    if dis_req == 1 and dis_user == 0:
        checklist.append({"rule": "Disability Condition", "status": "Failed", "value": "No disability (Disability required)"})
        reasons_ineligible.append("This scheme is exclusively for Persons with Disabilities.")
        # Hard fail could impact eligibility status directly
        is_eligible_override = False
    else:
        checklist.append({"rule": "Disability Condition", "status": "Passed", "value": f"Disability: {disability_status}"})
        is_eligible_override = True

    # Calculate final eligibility score
    final_score = state_match_score + age_match_score + income_match_score + gender_match_score + edu_match_score + cat_match_score
    
    # Override eligibility if crucial matches failed
    is_eligible = final_score >= 70 and is_eligible_override
    
    # Adjust score range categorisation
    if final_score >= 90:
        tier = "Highly Eligible (90-100)"
    elif final_score >= 70:
        tier = "Eligible (70-89)"
    elif final_score >= 50:
        tier = "Partially Eligible (50-69)"
    else:
        tier = "Check Manually (<50)"
        
    return {
        "id": scheme["id"],
        "scheme_name": scheme["scheme_name"],
        "name": scheme["scheme_name"], # Compatibility alias
        "ministry": scheme["ministry"],
        "category": scheme["category"],
        "description": scheme["description"],
        "benefits": scheme["benefits"],
        "financial_value": scheme["financial_value"],
        "eligibility": scheme["eligibility"],
        "income_limit": scheme["income_limit"],
        "age_limit": scheme["age_limit"],
        "gender": scheme["gender"],
        "state_availability": scheme["state_availability"],
        "documents_required": scheme["documents_required"],
        "application_link": scheme["application_link"],
        "official_website": scheme["official_website"],
        "last_updated": scheme["last_updated"],
        "eligibility_score": final_score,
        "is_eligible": is_eligible,
        "eligibility_tier": tier,
        "checklist": checklist,
        "reasons_eligible": reasons_eligible,
        "reasons_ineligible": reasons_ineligible,
        "required_documents": scheme["documents_required"],
    }


def compare_similar_schemes(scheme_name_a: str, scheme_name_b: str) -> dict[str, Any]:
    """Compares details and financial values of two government welfare schemes.

    Args:
        scheme_name_a: Name of the first scheme.
        scheme_name_b: Name of the second scheme.

    Returns:
        A dictionary comparing benefits, rules, and recommended option.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schemes WHERE scheme_name = ?", (scheme_name_a,))
    row_a = cursor.fetchone()
    cursor.execute("SELECT * FROM schemes WHERE scheme_name = ?", (scheme_name_b,))
    row_b = cursor.fetchone()
    conn.close()

    if not row_a or not row_b:
        return {
            "status": "error",
            "message": "One or both schemes not found in database.",
        }

    s_a = SCHEMES_DB._parse_row(row_a)
    s_b = SCHEMES_DB._parse_row(row_b)

    val_a = float(s_a["financial_value"])
    val_b = float(s_b["financial_value"])

    name_a = str(s_a["scheme_name"])
    name_b = str(s_b["scheme_name"])
    recommendation = name_a if val_a >= val_b else name_b
    diff = abs(val_a - val_b)

    return {
        "scheme_a": {
            "name": name_a,
            "category": str(s_a["category"]),
            "benefits": str(s_a["benefits"]),
            "value": val_a,
            "documents": list(s_a["documents_required"]),
        },
        "scheme_b": {
            "name": name_b,
            "category": str(s_b["category"]),
            "benefits": str(s_b["benefits"]),
            "value": val_b,
            "documents": list(s_b["documents_required"]),
        },
        "comparison": {
            "value_difference": diff,
            "recommended": recommendation,
            "reason": f"Provides a higher potential benefit value (Difference of ₹{diff:,}).",
        },
    }


def verify_uploaded_documents(
    uploaded_document_names: list[str],
    citizen_category: str,
    disability_status: str,
    occupation: str,
) -> dict[str, Any]:
    """Analyzes a checklist of uploaded documents to check completeness and detect missing ones."""
    required = ["Aadhaar Card", "Income Certificate", "Domicile Certificate"]

    if citizen_category in ["SC", "ST", "OBC"]:
        required.append("Caste Certificate")

    if disability_status.lower() == "yes":
        required.append("Disability Certificate")

    if occupation.lower() == "student":
        required.append("Previous Marksheet")
    elif occupation.lower() == "farmer":
        required.append("Land Ownership Documents")
    elif occupation.lower() == "startup founder":
        required.append("DPIIT Recognition Certificate")

    verified = []
    missing = []

    for doc in required:
        match_found = False
        for u_doc in uploaded_document_names:
            if doc.lower() in u_doc.lower():
                match_found = True
                break
        if match_found:
            verified.append(doc)
        else:
            missing.append(doc)

    total_req = len(required)
    met_req = len(verified)
    readiness_score = int((met_req / total_req) * 100) if total_req > 0 else 100

    return {
        "status": "success",
        "readiness_score": readiness_score,
        "verified_documents": verified,
        "missing_documents": missing,
        "next_steps": "Please upload the missing certificates to complete your application readiness status."
        if missing
        else "All required certificates are verified! You are ready to apply.",
    }


def predict_future_life_events(age: int, occupation: str) -> dict[str, Any]:
    """Predicts future scheme eligibility transitions based on citizen's age and life events."""
    predictions = []

    if age < 18:
        predictions.append(
            {
                "event": "Reaching Age of Majority (18 Years)",
                "timeline": f"In {18 - age} years",
                "icon": "🎓",
                "scheme": "Atal Pension Yojana (APY), Mudra Business Loans",
                "description": "Financial independence programs, business credit, and pension eligibility unlocks."
            }
        )

    if occupation.lower() == "student":
        predictions.append(
            {
                "event": "Graduation / Career Transition",
                "timeline": "Post Education",
                "icon": "🏢",
                "scheme": "PM Internship Scheme, Startup India Seed Fund",
                "description": "Stipend supported corporate internship programs and early stage startup funding access."
            }
        )

    if age < 60:
        predictions.append(
            {
                "event": "Senior Citizenship (60 Years)",
                "timeline": f"In {60 - age} years",
                "icon": "👴",
                "scheme": "Indira Gandhi National Old Age Pension, PM Vaya Vandana Yojana",
                "description": "Monthly retirement stipends and high-yield savings plans exclusively for seniors."
            }
        )
    else:
        predictions.append(
            {
                "event": "Super Senior Milestones (80 Years)",
                "timeline": "Later Stage",
                "icon": "🏥",
                "scheme": "Indira Gandhi National Pension (Higher Slab)",
                "description": "Elevated monthly pension rates and direct medical wellness outreach programs."
            }
        )

    return {
        "status": "success",
        "current_state": f"Age: {age}, Occupation: {occupation}",
        "predictions": predictions,
    }


def detect_fraud_alerts(content_or_url: str) -> dict[str, Any]:
    """Analyzes a URL or text content to verify if it represents an official government site or a fraud scam."""
    scam_keywords = [
        "free cash",
        "click link to claim",
        "whatsapp group win",
        "pay registration fee",
        "lottery",
        "urgent verify key",
        "aadhaar otp transfer",
    ]
    is_url = (
        "http" in content_or_url or ".com" in content_or_url or ".in" in content_or_url
    )

    safety = "Safe"
    warning = "None"
    explanation = "This represents a verified official government channel/portal."

    if is_url:
        if not (".gov.in" in content_or_url or ".nic.in" in content_or_url):
            safety = "Dangerous"
            warning = "HIGH ALERT: Fake Portal Detected"
            explanation = "Official Indian Government websites always end with '.gov.in' or '.nic.in'. This site uses a commercial domain which is likely a phishing scam to steal personal details."
    else:
        matches = [kw for kw in scam_keywords if kw in content_or_url.lower()]
        if matches:
            safety = "Suspicious"
            warning = "MEDIUM ALERT: Potential Scheme Scam"
            explanation = f"This message contains high-risk keywords ({', '.join(matches)}). Real government schemes never require payment of a 'registration fee' via SMS."

    return {
        "input_checked": content_or_url,
        "safety_rating": safety,
        "alert_title": warning,
        "explanation": explanation,
        "official_guideline": "Always verify schemes on the official portal 'myscheme.gov.in' before providing Aadhaar or OTP details.",
    }
