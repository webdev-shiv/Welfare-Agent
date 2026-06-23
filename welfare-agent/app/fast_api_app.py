import logging
import os
import sys
import sqlite3
import json
from typing import Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# Import ADK FastAPI app builder
from google.adk.cli.fast_api import get_fast_api_app

# Import database helpers
from app.db import get_db_connection, DB_PATH
from app.tools import (
    SCHEMES_DB,
    check_scheme_eligibility,
    detect_fraud_alerts,
    predict_future_life_events,
    verify_uploaded_documents,
    compare_similar_schemes,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
sys_logger = logging.getLogger("welfare-app")

# App directory configuration
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
session_service_uri = None
artifact_service_uri = None

# Initialize FastAPI App from ADK to support standard agent sessions and streaming routes
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=["*"],
    session_service_uri=session_service_uri,
    otel_to_cloud=False,
)

app.title = "welfare-agent"
app.description = "API for interacting with the AI Welfare Operating System Agent"

# Add CORS Middleware explicitly to support Vite/React frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas for API ---

class UserProfile(BaseModel):
    name: str = "Rahul Sharma"
    age: int = 20
    gender: str = "Male"
    state: str = "Delhi"
    district: str = "New Delhi"
    occupation: str = "Student"
    annualIncome: float = 150000.0
    category: str = "General"
    disability: bool = False
    education: str = "B.Tech"
    familyIncome: float = 150000.0
    # Compatibility mapping
    income: Optional[float] = None
    disability_status: Optional[str] = None
    family_info: Optional[str] = ""

class DocumentCheckRequest(BaseModel):
    uploaded_documents: List[str]
    category: str
    disability_status: str
    occupation: str

class FraudCheckRequest(BaseModel):
    content_or_url: str

class PredictTransitionRequest(BaseModel):
    age: int
    occupation: str

class DocumentChatRequest(BaseModel):
    query: str
    scheme_name: str
    chat_history: List[dict] = []

class FeedbackSchema(BaseModel):
    session_id: str
    feedback_text: str
    rating: int

# NGO API models
class NGORequestCreate(BaseModel):
    user_id: int = 1
    ngo_id: int
    request_details: str
    uploaded_docs: List[str]

class NGORequestStatusUpdate(BaseModel):
    status: str
    remarks: Optional[str] = ""

class NGOCreate(BaseModel):
    ngo_name: str
    description: str
    state: str
    district: str
    contact_number: str
    email: str
    website: str
    services_offered: str
    eligibility: str
    beneficiary_category: str
    women_support: int = 0
    child_welfare: int = 0
    education: int = 0
    disability: int = 0
    senior_citizen: int = 0
    healthcare: int = 0
    food_support: int = 0
    skill_development: int = 0
    shelter_homes: int = 0

class ChatbotMessageRequest(BaseModel):
    message: str
    session_id: str = "default_session"
    user_id: int = 1
    profile: UserProfile

# --- Helper to map compatibility fields ---
def normalize_profile(p: UserProfile) -> UserProfile:
    if p.income is not None:
        p.annualIncome = p.income
        p.familyIncome = p.income
    if p.disability_status is not None:
        p.disability = (p.disability_status.lower() == "yes")
    return p

# --- API Endpoints ---

@app.get("/api/schemes")
def get_schemes(
    search: Optional[str] = None,
    category: Optional[str] = None,
    state: Optional[str] = None,
    page: int = 1,
    limit: int = 10
) -> dict[str, Any]:
    """Retrieve all pre-loaded welfare schemes with optional search, category filters, and pagination."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_parts = []
    params = []
    
    if search:
        query_parts.append("(scheme_name LIKE ? OR description LIKE ? OR benefits LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if category:
        query_parts.append("category = ?")
        params.append(category)
    if state:
        query_parts.append("(state_availability = 'All' OR state_availability = ?)")
        params.append(state)
        
    where_clause = " WHERE " + " AND ".join(query_parts) if query_parts else ""
    
    # Get total count
    cursor.execute(f"SELECT count(*) FROM schemes{where_clause}", params)
    total_count = cursor.fetchone()[0]
    
    # Retrieve with pagination
    offset = (page - 1) * limit
    params.extend([limit, offset])
    cursor.execute(f"SELECT * FROM schemes{where_clause} LIMIT ? OFFSET ?", params)
    rows = cursor.fetchall()
    conn.close()
    
    schemes = [SCHEMES_DB._parse_row(r) for r in rows]
    return {
        "status": "success",
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "schemes": schemes
    }


@app.post("/api/profile/evaluate")
def evaluate_profile(profile: UserProfile) -> dict[str, Any]:
    """Calculates eligibility, benefits, and welfare scores for a citizen profile against all database schemes."""
    p = normalize_profile(profile)
    
    # Save/Update profile in DB for testing
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, name, age, gender, state, district, occupation, annual_income, category, disability, education, family_income)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, age=excluded.age, gender=excluded.gender, state=excluded.state, district=excluded.district,
            occupation=excluded.occupation, annual_income=excluded.annual_income, category=excluded.category,
            disability=excluded.disability, education=excluded.education, family_income=excluded.family_income
    """, (p.name, p.age, p.gender, p.state, p.district, p.occupation, p.annualIncome, p.category, 1 if p.disability else 0, p.education, p.familyIncome))
    
    # Get all schemes
    cursor.execute("SELECT scheme_name FROM schemes")
    rows = cursor.fetchall()
    conn.close()
    
    eligible_schemes = []
    ineligible_schemes = []
    total_benefits = 0.0
    claimed_benefits = 0.0
    
    # Evaluate each scheme
    for row in rows:
        scheme_name = row["scheme_name"]
        disability_str = "Yes" if p.disability else "No"
        result = check_scheme_eligibility(
            scheme_name=scheme_name,
            age=p.age,
            gender=p.gender,
            state=p.state,
            income=p.annualIncome,
            category=p.category,
            occupation=p.occupation,
            education=p.education,
            disability_status=disability_str,
        )
        
        if result.get("status") == "error":
            continue
            
        if result["is_eligible"]:
            eligible_schemes.append(result)
            total_benefits += result["financial_value"]
        else:
            ineligible_schemes.append(result)
            
    # Calculate Welfare Score based on number of eligible schemes matched
    eligible_count = len(eligible_schemes)
    total_count = len(rows) if rows else 1
    welfare_score = min(100, int((eligible_count / total_count) * 150))
    welfare_score = max(35, min(95, welfare_score))
    
    # Simulated claimed benefits based on seeded applications
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.financial_value FROM applications a
        JOIN schemes s ON a.scheme_id = s.id
        WHERE a.user_id = 1 AND a.status = 'Approved'
    """)
    claimed_rows = cursor.fetchall()
    conn.close()
    
    claimed_benefits = sum(r["financial_value"] for r in claimed_rows)
    missed_benefits = total_benefits - claimed_benefits
    
    return {
        "status": "success",
        "welfare_score": welfare_score,
        "total_potential_benefits": total_benefits,
        "claimed_benefits": claimed_benefits,
        "missed_benefits": missed_benefits,
        "eligible_schemes": eligible_schemes,
        "ineligible_schemes": ineligible_schemes,
    }


@app.post("/api/document/verify")
def verify_documents(req: DocumentCheckRequest) -> dict[str, Any]:
    """Checks completeness of uploaded certificates."""
    return verify_uploaded_documents(
        uploaded_document_names=req.uploaded_documents,
        citizen_category=req.category,
        disability_status=req.disability_status,
        occupation=req.occupation,
    )


@app.post("/api/fraud/detect")
def detect_fraud(req: FraudCheckRequest) -> dict[str, Any]:
    """Inspects URLs or messages for scams."""
    return detect_fraud_alerts(content_or_url=req.content_or_url)


@app.post("/api/predict")
def predict_transitions(req: PredictTransitionRequest) -> dict[str, Any]:
    """Predicts future scheme eligibility timelines."""
    return predict_future_life_events(age=req.age, occupation=req.occupation)


@app.post("/api/document/chat")
def chat_with_document(req: DocumentChatRequest) -> dict[str, Any]:
    """RAG-based chat simulation over a scheme's official guidelines."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schemes WHERE scheme_name = ?", (req.scheme_name,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Scheme not found")
        
    scheme = SCHEMES_DB._parse_row(row)
    context = (
        f"Scheme Name: {scheme['scheme_name']}\n"
        f"Ministry: {scheme['ministry']}\n"
        f"Category: {scheme['category']}\n"
        f"Description: {scheme['description']}\n"
        f"Benefits: {scheme['benefits']}\n"
        f"Required Documents: {', '.join(scheme['documents_required'])}."
    )
    
    q_lower = req.query.lower()
    if "document" in q_lower or "paper" in q_lower or "caste" in q_lower or "income" in q_lower:
        answer = f"According to the official guidelines for {scheme['scheme_name']}, you will need the following documents to apply: {', '.join(scheme['documents_required'])}. Ensure these certificates are in verified status."
    elif "eligible" in q_lower or "qualify" in q_lower:
        answer = f"The eligibility criteria for {scheme['scheme_name']} are as follows: {scheme['eligibility']}. Maximum income permitted is ₹{scheme['income_limit']:,.2f} if applicable."
    elif "benefit" in q_lower or "money" in q_lower or "rupees" in q_lower:
        answer = f"Under {scheme['scheme_name']}, you will receive: {scheme['benefits']}. This has a modeled financial valuation of ₹{scheme['financial_value']:,.2f} per term."
    else:
        answer = f"Official Guidelines summary for {scheme['scheme_name']}: {scheme['description']} The scheme is managed by the {scheme['ministry']}."
        
    return {
        "status": "success",
        "query": req.query,
        "scheme_name": scheme["scheme_name"],
        "answer": answer,
        "context_used": context,
    }


# --- NGO Assistance Module Endpoints ---

@app.get("/api/ngos")
def get_ngos(
    state: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    women_support: int = 0,
    child_welfare: int = 0,
    education: int = 0,
    disability: int = 0,
    senior_citizen: int = 0,
    healthcare: int = 0,
    food_support: int = 0,
    skill_development: int = 0,
    shelter_homes: int = 0
) -> dict[str, Any]:
    """Retrieve NGOs based on state, district, services categories and flags."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM ngos WHERE approved = 1"
    params = []
    
    if state and state != "All":
        query += " AND state = ?"
        params.append(state)
    if district:
        query += " AND district LIKE ?"
        params.append(f"%{district}%")
    if category:
        query += " AND services_offered LIKE ?"
        params.append(f"%{category}%")
        
    # Service tags checkboxes
    if women_support:
        query += " AND women_support = 1"
    if child_welfare:
        query += " AND child_welfare = 1"
    if education:
        query += " AND education = 1"
    if disability:
        query += " AND disability = 1"
    if senior_citizen:
        query += " AND senior_citizen = 1"
    if healthcare:
        query += " AND healthcare = 1"
    if food_support:
        query += " AND food_support = 1"
    if skill_development:
        query += " AND skill_development = 1"
    if shelter_homes:
        query += " AND shelter_homes = 1"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    ngos = [dict(r) for r in rows]
    return {"status": "success", "count": len(ngos), "ngos": ngos}


@app.post("/api/ngos/request")
def submit_ngo_request(req: NGORequestCreate) -> dict[str, Any]:
    """Citizen submits an assistance request to an NGO with attached documents."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if NGO exists
    cursor.execute("SELECT ngo_name FROM ngos WHERE id = ?", (req.ngo_id,))
    ngo = cursor.fetchone()
    if not ngo:
        conn.close()
        raise HTTPException(status_code=404, detail="NGO not found")
        
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO ngo_requests (user_id, ngo_id, request_details, uploaded_docs, status, created_at, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (req.user_id, req.ngo_id, req.request_details, json.dumps(req.uploaded_docs), "Pending", created_at, ""))
    
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "request_id": request_id,
        "message": f"Assistance request successfully submitted to {ngo['ngo_name']}."
    }


@app.get("/api/ngos/requests")
def get_ngo_requests(
    user_id: Optional[int] = None,
    ngo_id: Optional[int] = None
) -> dict[str, Any]:
    """Retrieve assistance requests submitted by citizens or received by NGOs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT r.*, n.ngo_name, n.contact_number as ngo_phone, u.name as citizen_name, u.age, u.gender, u.occupation, u.annual_income, u.state as citizen_state
        FROM ngo_requests r
        JOIN ngos n ON r.ngo_id = n.id
        JOIN users u ON r.user_id = u.id
    """
    params = []
    
    if user_id:
        query += " WHERE r.user_id = ?"
        params.append(user_id)
    elif ngo_id:
        query += " WHERE r.ngo_id = ?"
        params.append(ngo_id)
        
    query += " ORDER BY r.id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    requests = []
    for r in rows:
        d = dict(r)
        d["uploaded_docs"] = json.loads(d["uploaded_docs"]) if d["uploaded_docs"] else []
        requests.append(d)
        
    return {"status": "success", "count": len(requests), "requests": requests}


@app.post("/api/ngos/requests/{request_id}/status")
def update_ngo_request_status(request_id: int, req: NGORequestStatusUpdate) -> dict[str, Any]:
    """NGO dashboard accepts, rejects, or completes a citizen's assistance request."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM ngo_requests WHERE id = ?", (request_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Request not found")
        
    cursor.execute("""
        UPDATE ngo_requests
        SET status = ?, remarks = ?
        WHERE id = ?
    """, (req.status, req.remarks, request_id))
    
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Request status updated to {req.status}."}


# --- Admin NGO Management Endpoints ---

@app.post("/api/ngos/add")
def admin_add_ngo(ngo: NGOCreate) -> dict[str, Any]:
    """Admin registers a new NGO into the database directory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO ngos (
            ngo_name, description, state, district, contact_number, email, website,
            services_offered, eligibility, beneficiary_category, approved,
            women_support, child_welfare, education, disability, senior_citizen,
            healthcare, food_support, skill_development, shelter_homes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ngo.ngo_name, ngo.description, ngo.state, ngo.district, ngo.contact_number, ngo.email, ngo.website,
        ngo.services_offered, ngo.eligibility, ngo.beneficiary_category,
        ngo.women_support, ngo.child_welfare, ngo.education, ngo.disability, ngo.senior_citizen,
        ngo.healthcare, ngo.food_support, ngo.skill_development, ngo.shelter_homes
    ))
    
    ngo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"status": "success", "ngo_id": ngo_id, "message": "NGO created and approved by Admin."}


@app.post("/api/ngos/edit/{ngo_id}")
def admin_edit_ngo(ngo_id: int, ngo: NGOCreate) -> dict[str, Any]:
    """Admin updates details of an existing NGO."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM ngos WHERE id = ?", (ngo_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="NGO not found")
        
    cursor.execute("""
        UPDATE ngos SET
            ngo_name=?, description=?, state=?, district=?, contact_number=?, email=?, website=?,
            services_offered=?, eligibility=?, beneficiary_category=?,
            women_support=?, child_welfare=?, education=?, disability=?, senior_citizen=?,
            healthcare=?, food_support=?, skill_development=?, shelter_homes=?
        WHERE id = ?
    """, (
        ngo.ngo_name, ngo.description, ngo.state, ngo.district, ngo.contact_number, ngo.email, ngo.website,
        ngo.services_offered, ngo.eligibility, ngo.beneficiary_category,
        ngo.women_support, ngo.child_welfare, ngo.education, ngo.disability, ngo.senior_citizen,
        ngo.healthcare, ngo.food_support, ngo.skill_development, ngo.shelter_homes, ngo_id
    ))
    
    conn.commit()
    conn.close()
    return {"status": "success", "message": "NGO details successfully updated."}


@app.delete("/api/ngos/delete/{ngo_id}")
def admin_delete_ngo(ngo_id: int) -> dict[str, Any]:
    """Admin deletes an NGO record from the system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM ngos WHERE id = ?", (ngo_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="NGO not found")
        
    cursor.execute("DELETE FROM ngos WHERE id = ?", (ngo_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "NGO successfully removed from registry."}


@app.get("/api/ngos/analytics")
def get_ngo_analytics() -> dict[str, Any]:
    """Retrieve request statuses statistics for NGO administration dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT status, count(*) as count FROM ngo_requests GROUP BY status")
    rows = cursor.fetchall()
    
    cursor.execute("SELECT count(*) FROM ngos")
    total_ngos = cursor.fetchone()[0]
    conn.close()
    
    stats = {"Pending": 0, "Accepted": 0, "Rejected": 0, "Completed": 0}
    total_requests = 0
    for r in rows:
        stats[r["status"]] = r["count"]
        total_requests += r["count"]
        
    return {
        "status": "success",
        "total_ngos": total_ngos,
        "total_requests": total_requests,
        "requests_breakdown": stats
    }


# --- Advanced Dashboard Analytics & Charts API ---

@app.get("/api/dashboard/analytics")
def get_dashboard_analytics(user_id: int = 1) -> dict[str, Any]:
    """Returns analytics data and charts breakdown for the advanced user dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total Schemes
    cursor.execute("SELECT count(*) FROM schemes")
    total_schemes = cursor.fetchone()[0]
    
    # 2. Applied Schemes
    cursor.execute("SELECT count(*) FROM applications WHERE user_id = ?", (user_id,))
    applied_schemes = cursor.fetchone()[0]
    
    # 3. NGO Requests
    cursor.execute("SELECT count(*) FROM ngo_requests WHERE user_id = ?", (user_id,))
    ngo_requests = cursor.fetchone()[0]
    
    # 4. User Profile Details to calculate eligible schemes dynamically
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    
    eligible_schemes_count = 0
    categories_dist = {}
    eligibility_tiers = {"Highly Eligible (90-100)": 0, "Eligible (70-89)": 0, "Partially Eligible (50-69)": 0, "Check Manually (<50)": 0}
    
    # Category list to capture distribution
    cursor.execute("SELECT category, count(*) as count FROM schemes GROUP BY category")
    cat_rows = cursor.fetchall()
    for cat in cat_rows:
        categories_dist[cat["category"]] = cat["count"]
        
    # Get all schemes for evaluation details
    cursor.execute("SELECT * FROM schemes")
    all_schemes = cursor.fetchall()
    
    # If user exists, compute real metrics
    if user_row:
        u = dict(user_row)
        dis_str = "Yes" if u["disability"] == 1 else "No"
        
        for sc in all_schemes:
            ev = check_scheme_eligibility(
                scheme_name=sc["scheme_name"],
                age=u["age"],
                gender=u["gender"],
                state=u["state"],
                income=u["annual_income"],
                category=u["category"],
                occupation=u["occupation"],
                education=u["education"],
                disability_status=dis_str
            )
            if ev.get("is_eligible"):
                eligible_schemes_count += 1
            
            # Map to tier counters
            tier = ev.get("eligibility_tier", "Check Manually (<50)")
            eligibility_tiers[tier] = eligibility_tiers.get(tier, 0) + 1
    else:
        eligible_schemes_count = 5
        eligibility_tiers["Highly Eligible (90-100)"] = 3
        eligibility_tiers["Eligible (70-89)"] = 2
        
    # 5. State Coverage
    cursor.execute("SELECT state_availability, count(*) as count FROM schemes GROUP BY state_availability")
    state_rows = cursor.fetchall()
    state_coverage = {r["state_availability"]: r["count"] for r in state_rows}
    
    # 6. Success Rate
    cursor.execute("SELECT status, count(*) as count FROM applications GROUP BY status")
    app_status_rows = cursor.fetchall()
    app_status = {r["status"]: r["count"] for r in app_status_rows}
    approved = app_status.get("Approved", 0)
    total_apps = sum(app_status.values())
    success_rate = int((approved / total_apps) * 100) if total_apps > 0 else 100
    
    conn.close()
    
    return {
        "status": "success",
        "metrics": {
            "total_schemes": total_schemes,
            "eligible_schemes": eligible_schemes_count,
            "applied_schemes": applied_schemes,
            "ngo_requests": ngo_requests,
            "success_rate": success_rate
        },
        "charts": {
            "category_distribution": categories_dist,
            "eligibility_breakdown": eligibility_tiers,
            "state_coverage": state_coverage,
            "application_success_rate": success_rate
        }
    }


# --- WhatsApp AI Chatbot Endpoint ---

@app.post("/api/chatbot")
async def chat_welfare_bot(req: ChatbotMessageRequest) -> dict[str, Any]:
    """WhatsApp-style chatbot endpoint executing RAG searches and answering queries via Gemini."""
    p = normalize_profile(req.profile)
    query_text = req.message.strip()
    
    if not query_text:
        return {"status": "error", "message": "Query cannot be empty."}
        
    # Query database to find schemes that match the query
    conn = get_db_connection()
    cursor = conn.cursor()
    
    q_param = f"%{query_text}%"
    cursor.execute("""
        SELECT * FROM schemes 
        WHERE scheme_name LIKE ? OR category LIKE ? OR description LIKE ? 
        LIMIT 3
    """, (q_param, q_param, q_param))
    scheme_rows = cursor.fetchall()
    
    # Also find nearby NGOs if they are asking about NGOs or help
    ngo_rows = []
    if "ngo" in query_text.lower() or "help" in query_text.lower() or "assistance" in query_text.lower() or "support" in query_text.lower():
        cursor.execute("SELECT * FROM ngos WHERE state = ? LIMIT 3", (p.state,))
        ngo_rows = cursor.fetchall()
        
    conn.close()
    
    # Build matched details context
    context_str = f"User Profile: Name {p.name}, Age {p.age}, Gender {p.gender}, State {p.state}, Occupation {p.occupation}, Income ₹{p.annualIncome:,.2f}, Category {p.category}, Disability: {'Yes' if p.disability else 'No'}, Education {p.education}.\n\n"
    
    if scheme_rows:
        context_str += "Relevant Schemes found in database:\n"
        for r in scheme_rows:
            s = SCHEMES_DB._parse_row(r)
            eval_res = check_scheme_eligibility(
                scheme_name=s["scheme_name"],
                age=p.age,
                gender=p.gender,
                state=p.state,
                income=p.annualIncome,
                category=p.category,
                occupation=p.occupation,
                education=p.education,
                disability_status="Yes" if p.disability else "No"
            )
            
            context_str += (
                f"- Name: {s['scheme_name']}\n"
                f"  Ministry: {s['ministry']}\n"
                f"  Category: {s['category']}\n"
                f"  Benefits: {s['benefits']}\n"
                f"  Financial Value: ₹{s['financial_value']:,.2f}\n"
                f"  Eligibility Criteria: {s['eligibility']}\n"
                f"  Income Limit: ₹{s['income_limit']:,.2f} if applicable\n"
                f"  Required Documents: {', '.join(s['documents_required'])}\n"
                f"  AI Eligibility Score for User: {eval_res['eligibility_score']}% ({eval_res['eligibility_tier']})\n"
                f"  AI Eligibility Check Reasons: {', '.join(eval_res['reasons_eligible'] + eval_res['reasons_ineligible'])}\n\n"
            )
            
    if ngo_rows:
        context_str += f"Nearby NGOs in {p.state} found in database:\n"
        for n in ngo_rows:
            context_str += (
                f"- NGO Name: {n['ngo_name']}\n"
                f"  Description: {n['description']}\n"
                f"  District: {n['district']}\n"
                f"  Contact: {n['contact_number']}, Email: {n['email']}\n"
                f"  Website: {n['website']}\n"
                f"  Services: {n['services_offered']}\n\n"
            )

    # Initialize Gemini API Client
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    ai_response_text = ""
    
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            system_instruction = (
                "You are the Government Scheme Eligibility Agent. You help citizens discover, evaluate, and apply for government welfare schemes and connect with NGOs.\n"
                "Your tone should be helpful, professional, clear, and reassuring, resembling a fast WhatsApp consultant.\n"
                "When requested, provide detailed steps, eligibility reasoning, application checklists (with square brackets for boxes), scheme comparisons (with small markdown tables), or nearby NGO recommendations.\n"
                "Always format the output in clean, readable markdown. Keep paragraphs short."
            )
            
            prompt = (
                f"{context_str}\n\n"
                f"User Question: {query_text}\n\n"
                f"Generate a customized response addressing their question directly based on the context provided above. "
                f"If the database rows do not cover the requested scheme details, search your internal knowledge to answer accurately but note that they should verify the details on the official website."
            )
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                )
            )
            ai_response_text = response.text
        except Exception as e:
            sys_logger.error(f"Error calling Gemini API: {e}")
            ai_response_text = ""
            
    # Fallback to simulated local logic if API fails or no API Key
    if not ai_response_text:
        ql = query_text.lower()
        if "laptop" in ql or "one student" in ql:
            ai_response_text = (
                "🏛️ *One Student One Laptop Scheme* \n\n"
                "You are highly eligible (100% Match) for this scheme!\n\n"
                "*Benefits:* Free brand new laptop or ₹40,000 financial support for computing devices.\n"
                "*Eligibility:* B.Tech/Diploma/MCA students in AICTE approved colleges.\n\n"
                "📋 *Your Application Checklist:*\n"
                "- [x] Aadhaar Card (Verified)\n"
                "- [ ] AICTE College ID Card\n"
                "- [x] Income Certificate (Verified)\n"
                "- [x] Previous Marksheet (Verified)\n\n"
                "Would you like me to guide you through applying?"
            )
        elif "ngo" in ql or "help" in ql:
            ngo_list_str = ""
            if p.state == "Delhi":
                ngo_list_str = "• *Delhi Education & Welfare Council* (New Delhi)\n  Services: Education, Women Support\n  Contact: 9876543210 | Website: https://delhieducationwelfare.org"
            else:
                ngo_list_str = f"• *{p.state} Welfare Association*\n  Services: Food Support, Healthcare\n  Contact: 9876543210"
            ai_response_text = (
                f"🤝 *NGO Assistance recommendations in {p.state}:*\n\n"
                f"{ngo_list_str}\n\n"
                "You can submit an assistance request directly through the *NGO Village Portal* tab or ask me to draft a request details letter!"
            )
        elif "scholarship" in ql:
            ai_response_text = (
                "🎓 *Scholarships Recommendations matching your B.Tech student profile:*\n\n"
                "1. *Post Matric Scholarship Scheme for SC/ST/OBC Students*\n"
                "   Value: Up to ₹1,20,000/year. (Requires SC/ST/OBC category and income < 2.5L).\n"
                "2. *Central Sector Scheme of Scholarship*\n"
                "   Value: ₹12,000/year. Open to all categories based on Class 12 marks.\n"
                "3. *AICTE Pragati Scholarship for Girl Students*\n"
                "   Value: ₹50,000/year. (Female only).\n\n"
                "Since your category is *General*, you are highly eligible for the *Central Sector Scheme of Scholarship* or the *One Student One Laptop* resource."
            )
        elif "compare" in ql:
            ai_response_text = (
                "⚖️ *Scheme Comparison:* \n\n"
                "| Criteria | NSP Scholarship | PM Internship |\n"
                "| :--- | :--- | :--- |\n"
                "| *Benefits* | ₹20,000 / year | ₹66,000 / year (stipends) |\n"
                "| *Eligibility* | College students | Aged 21-25, not in regular jobs |\n"
                "| *Category* | General / SC / ST / OBC | Open to All |\n\n"
                "*Recommendation:* The *PM Internship Scheme* offers significantly higher financial returns (₹66,000) and valuable work experience."
            )
        else:
            ai_response_text = (
                f"Hello {p.name}! I am evaluating your question: '{query_text}'.\n\n"
                f"Based on your profile as a {p.education} student from {p.state}, "
                f"I recommend checking out the *One Student One Laptop Scheme* (₹40,000 benefit) and *Central Sector Scholarship*. "
                f"Let me know if you want me to explain their eligibility or list required documents!"
            )

    # Save chatbot history in DB
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO chatbot_history (user_id, session_id, sender, message, timestamp)
        VALUES (?, ?, 'user', ?, ?)
    """, (req.user_id, req.session_id, query_text, timestamp))
    cursor.execute("""
        INSERT INTO chatbot_history (user_id, session_id, sender, message, timestamp)
        VALUES (?, ?, 'bot', ?, ?)
    """, (req.user_id, req.session_id, ai_response_text, timestamp))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "answer": ai_response_text,
        "session_id": req.session_id,
        "timestamp": timestamp
    }


# Root /feedback endpoint checked by integration tests
@app.post("/feedback")
def collect_feedback(feedback: FeedbackSchema) -> dict[str, str]:
    """Collect and log feedback."""
    sys_logger.info(f"Feedback collected: {feedback.model_dump()}")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.fast_api_app:app", host="0.0.0.0", port=8000, reload=True)
