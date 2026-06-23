import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "welfare_navigator.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create schemes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_name TEXT UNIQUE,
        ministry TEXT,
        category TEXT,
        description TEXT,
        benefits TEXT,
        eligibility TEXT,
        income_limit REAL,
        age_limit TEXT,
        gender TEXT,
        state_availability TEXT,
        documents_required TEXT,
        application_link TEXT,
        official_website TEXT,
        last_updated TEXT,
        financial_value REAL,
        education TEXT,
        caste_category TEXT,
        disability_required INTEGER
    )
    """)
    
    # Create ngos table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ngos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ngo_name TEXT,
        description TEXT,
        state TEXT,
        district TEXT,
        contact_number TEXT,
        email TEXT,
        website TEXT,
        services_offered TEXT,
        eligibility TEXT,
        beneficiary_category TEXT,
        approved INTEGER DEFAULT 1,
        women_support INTEGER DEFAULT 0,
        child_welfare INTEGER DEFAULT 0,
        education INTEGER DEFAULT 0,
        disability INTEGER DEFAULT 0,
        senior_citizen INTEGER DEFAULT 0,
        healthcare INTEGER DEFAULT 0,
        food_support INTEGER DEFAULT 0,
        skill_development INTEGER DEFAULT 0,
        shelter_homes INTEGER DEFAULT 0
    )
    """)
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        state TEXT,
        district TEXT,
        occupation TEXT,
        annual_income REAL,
        category TEXT,
        disability INTEGER,
        education TEXT,
        family_income REAL
    )
    """)
    
    # Create applications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        scheme_id INTEGER,
        status TEXT,
        applied_date TEXT,
        remarks TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(scheme_id) REFERENCES schemes(id)
    )
    """)
    
    # Create documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        document_name TEXT,
        file_path TEXT,
        uploaded_date TEXT,
        status TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    # Create chatbot_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chatbot_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_id TEXT,
        sender TEXT,
        message TEXT,
        timestamp TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    # Create ngo_requests table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ngo_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ngo_id INTEGER,
        request_details TEXT,
        uploaded_docs TEXT,
        status TEXT,
        created_at TEXT,
        remarks TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(ngo_id) REFERENCES ngos(id)
    )
    """)
    
    conn.commit()
    conn.close()
    
    # Seed the database
    seed_data()

def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if schemes already seeded
    cursor.execute("SELECT count(*) FROM schemes")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
        
    print("Seeding database with schemes, NGOs, and sample data...")
    
    # 1. 100+ Government Schemes
    # We will categories schemes: Education, Student, Women, Employment, Farmer, Health, Senior Citizen, Housing, Disability, SC/ST/OBC, Financial Inclusion, Additional Central Schemes
    schemes_data = []
    
    # helper to construct scheme dict
    def add_scheme(name, ministry, cat, desc, benefits, eligibility, inc_lim, age_lim, gender, state, docs, app_link, site, val, edu="All", caste="All", dis=0):
        schemes_data.append((
            name, ministry, cat, desc, benefits, eligibility, inc_lim,
            json.dumps(age_lim), gender, state, json.dumps(docs), app_link, site,
            "2026-06-22", val, edu, caste, dis
        ))

    # --- EDUCATION SCHEMES (20 Schemes) ---
    add_scheme("PM Vidya Scheme", "Ministry of Education", "Education Schemes",
               "Covers educational expenses for underprivileged school students through digital aids and direct support.",
               "Free access to E-learning devices and study kits value up to ₹15,000",
               "Underprivileged children studying in class 1-12", 150000.0, {"min": 5, "max": 18}, "All", "All",
               ["Aadhaar Card", "School ID", "Income Certificate"], "https://pmvidya.gov.in/apply", "https://pmvidya.gov.in", 15000.0, "School Student")
               
    add_scheme("National Means Cum Merit Scholarship (NMMSS)", "Ministry of Education", "Education Schemes",
               "Provides scholarship to meritorious students of economically weaker sections to arrest dropouts at class 8.",
               "₹12,000 per annum (₹1,000 per month) for classes 9 to 12",
               "Meritorious students scoring 55% in class 8 with family income below 3.5L", 350000.0, {"min": 12, "max": 16}, "All", "All",
               ["Aadhaar Card", "Class 8 Marksheet", "Income Certificate", "Domicile Certificate"], "https://scholarships.gov.in", "https://education.gov.in", 12000.0, "Student")

    add_scheme("NSP Scholarships", "Ministry of Education", "Education Schemes",
               "Central sector umbrella scheme providing scholarships to poor college and university students.",
               "₹10,000 to ₹20,000 per annum depending on course",
               "Students above 80th percentile in class 12 pursuing regular higher education courses", 450000.0, {"min": 17, "max": 25}, "All", "All",
               ["Aadhaar Card", "Class 12 Marksheet", "Income Certificate", "College Fee Receipt"], "https://scholarships.gov.in", "https://scholarships.gov.in", 20000.0, "Student")

    add_scheme("AICTE Pragati Scholarship for Girl Students", "Ministry of Education", "Education Schemes",
               "Supports technical education advancement for girl students in degree and diploma courses.",
               "₹50,000 per annum for tuition fees and contingency support",
               "Girl students admitted to AICTE approved technical institutions, max 2 girls per family", 800000.0, {"min": 16, "max": 30}, "Female", "All",
               ["Aadhaar Card", "Admission Letter", "Income Certificate", "Marksheet"], "https://aicte-pragati.gov.in", "https://aicte-india.org", 50000.0, "Student")

    add_scheme("AICTE Saksham Scholarship for Specially Abled Students", "Ministry of Education", "Education Schemes",
               "Aims to support specially-abled students to pursue technical education.",
               "₹50,000 per annum for college fees and study material support",
               "Specially-abled students with >= 40% disability admitted to AICTE courses", 800000.0, {"min": 16, "max": 30}, "All", "All",
               ["Aadhaar Card", "Disability Certificate", "Income Certificate", "Admission Letter"], "https://aicte-india.org", "https://aicte-india.org", 50000.0, "Student", "All", 1)

    add_scheme("INSPIRE Scholarship", "Ministry of Science and Technology", "Education Schemes",
               "Scholarship for Higher Education (SHE) to attract students to natural and basic sciences.",
               "₹80,000 per year (₹60,000 cash + ₹20,000 mentorship/project grant)",
               "Meritorious students within top 1% in class 12 board examinations pursuing BSc/MSc courses", 600000.0, {"min": 17, "max": 22}, "All", "All",
               ["Marksheet", "Endorsement Letter", "Caste Certificate"], "https://online-inspire.gov.in", "https://online-inspire.gov.in", 80000.0, "Student")

    add_scheme("PM Yasasvi Scheme", "Ministry of Social Justice and Empowerment", "Education Schemes",
               "Scholarship scheme for OBC, EBC and DNT students studying in Top Class Schools.",
               "Full tuition fee coverage up to ₹75,000 for Class 9 and ₹1,25,000 for Class 11",
               "OBC/EBC/DNT category school students with family income under 2.5L", 250000.0, {"min": 10, "max": 18}, "All", "All",
               ["Caste Certificate", "Income Certificate", "Aadhaar Card", "School Marksheet"], "https://yet.nta.ac.in", "https://socialjustice.gov.in", 125000.0, "Student", "OBC")

    add_scheme("Post Matric Scholarship for SC Students", "Ministry of Social Justice and Empowerment", "Education Schemes",
               "Centrally sponsored scheme providing financial help to SC students for post-matric studies.",
               "Covers 100% compulsory non-refundable fees + monthly maintenance allowance of up to ₹1,200",
               "SC category students pursuing graduation or post-graduation", 250000.0, {"min": 15, "max": 35}, "All", "All",
               ["Caste Certificate", "Income Certificate", "Aadhaar Card", "College Fee Receipt"], "https://scholarships.gov.in", "https://socialjustice.gov.in", 60000.0, "Student", "SC")

    add_scheme("Pre Matric Scholarship for SC/ST Students", "Ministry of Social Justice and Empowerment", "Education Schemes",
               "Aims to support parents of SC/ST children for education of their wards studying in classes 9 and 10.",
               "Annual grant of up to ₹10,000 and hostel fees if applicable",
               "SC/ST students studying in class 9 or 10", 250000.0, {"min": 13, "max": 16}, "All", "All",
               ["Caste Certificate", "Income Certificate", "Aadhaar Card", "School Certificate"], "https://scholarships.gov.in", "https://socialjustice.gov.in", 10000.0, "Student", "SC")

    add_scheme("Merit Cum Means Scholarship for Minorities", "Ministry of Minority Affairs", "Education Schemes",
               "Financial assistance for professional and technical courses to minority community students.",
               "Covers course fees up to ₹20,000/year and maintenance allowance",
               "Minority students (Muslim, Christian, Sikh, Buddhist, Parsi, Jain) with >= 50% marks in previous exam", 250000.0, {"min": 17, "max": 30}, "All", "All",
               ["Minority Declaration Certificate", "Previous Marksheet", "Income Certificate", "Aadhaar"], "https://scholarships.gov.in", "https://minorityaffairs.gov.in", 25000.0, "Student")

    add_scheme("Central Sector Scheme of Scholarship", "Ministry of Education", "Education Schemes",
               "Assists college going students to meet part of their daily expenses while pursuing higher studies.",
               "₹12,000 per annum for graduation, ₹20,000 per annum for post-graduation",
               "Students above 80th percentile in class 12 board and not receiving other scholarships", 450000.0, {"min": 18, "max": 25}, "All", "All",
               ["Aadhaar Card", "Marksheet", "College Fee receipt", "Income Certificate"], "https://scholarships.gov.in", "https://education.gov.in", 12000.0, "Student")

    add_scheme("Vidya Lakshmi Education Loan Scheme", "Ministry of Finance", "Education Schemes",
               "Single window gateway for students seeking education loans and scholarships with easy terms.",
               "Collateral free education loans up to ₹7.5 Lakhs with interest subsidies",
               "Indian citizens who have secured admission to professional/technical courses in India or abroad", 800000.0, {"min": 17, "max": 35}, "All", "All",
               ["Aadhaar Card", "Admission Letter", "Fee Structure document", "Income Certificate"], "https://vidyalakshmi.co.in", "https://vidyalakshmi.co.in", 750000.0, "Student")

    add_scheme("Vidyanjali Portal", "Ministry of Education", "Education Schemes",
               "School volunteer program linking community volunteers to schools for tutoring and sponsoring items.",
               "Direct support in kind, sponsoring school infrastructure, and volunteer tutoring",
               "Public government and government-aided school students", 9999999.0, {"min": 5, "max": 18}, "All", "All",
               ["School ID"], "https://vidyanjali.education.gov.in", "https://vidyanjali.education.gov.in", 5000.0, "School Student")

    add_scheme("Udaan Scheme for Girls", "Ministry of Education", "Education Schemes",
               "Aims to address low enrollment of girl students in prestigious engineering colleges.",
               "Free online learning resources, weekly virtual classes, tablet devices",
               "Girl students of Class 11 and 12 in CBSE/Government schools studying PCM science stream", 600000.0, {"min": 15, "max": 18}, "Female", "All",
               ["CBSE registration proof", "Income Certificate", "Aadhaar Card"], "https://cbse.nic.in/udaan", "https://cbse.nic.in", 30000.0, "Student")

    add_scheme("Super 100 Free Coaching Scheme", "State Education Board", "Education Schemes",
               "Free residential coaching program for meritorious state government school students.",
               "100% free lodging, boarding, and coaching for JEE/NEET exams valued at ₹2,00,000",
               "Meritorious class 10 graduates from state government schools scoring high in Super 100 test", 200000.0, {"min": 15, "max": 18}, "All", "Delhi",
               ["Aadhaar Card", "Class 10 Marksheet", "Income Certificate", "Government School certificate"], "https://edudel.nic.in", "https://edudel.nic.in", 200000.0, "Student")

    add_scheme("Kanya Vidya Dhan Scheme", "State Ministry of Education", "Education Schemes",
               "Supports secondary school completion and university enrollment for girls.",
               "Direct financial assistance of ₹30,000 on passing class 12 boards",
               "Girl students passing intermediate board exams from state board", 200000.0, {"min": 16, "max": 20}, "Female", "Uttar Pradesh",
               ["Aadhaar Card", "Intermediate Marksheet", "Caste Certificate", "Income Certificate"], "https://upmsp.edu.in", "https://upmsp.edu.in", 30000.0, "Student")

    add_scheme("Mukhyamantri Medhavi Vidyarthi Yojana", "State Higher Education", "Education Schemes",
               "State scheme covering university course fees of meritorious students.",
               "100% tuition fee reimbursement for engineering, medical, and professional degree courses",
               "State domicile students with class 12 marks >= 70% (state board) or >= 85% (CBSE)", 600000.0, {"min": 17, "max": 24}, "All", "Madhya Pradesh",
               ["Domicile Certificate", "Class 12 Marksheet", "College Admission Proof", "Income Certificate"], "http://scholarshipportal.mp.nic.in", "http://mp.nic.in", 150000.0, "Student")

    add_scheme("E-Kalyan Bihar Scholarship", "State Welfare Department", "Education Schemes",
               "Encourages higher education among girls by offering graduation bonuses.",
               "One-time cash incentive of ₹50,000 directly to graduating girls",
               "Unmarried girl graduates from Bihar state universities", 9999999.0, {"min": 20, "max": 28}, "Female", "Bihar",
               ["Aadhaar Card", "Graduation Marksheet", "Bihar Domicile Certificate", "Bank Passbook"], "http://ekalyan.bih.nic.in", "http://bih.nic.in", 50000.0, "Student")

    add_scheme("Free Coaching Scheme for SC and OBC Students", "Ministry of Social Justice and Empowerment", "Education Schemes",
               "Offers quality coaching for competitive exams to SC and OBC candidates.",
               "Free coaching for UPSC, JEE, NEET, SSC along with monthly stipend of ₹4,000",
               "SC and OBC candidates pursuing higher education and competitive exams", 800000.0, {"min": 18, "max": 30}, "All", "All",
               ["Aadhaar Card", "Caste Certificate", "Income Certificate", "Marksheet"], "https://coaching.dosje.gov.in", "https://socialjustice.gov.in", 80000.0, "Student", "OBC")

    add_scheme("Top Class Education Scheme for SC Students", "Ministry of Social Justice and Empowerment", "Education Schemes",
               "Provides scholarship to SC students for pursuing engineering, medicine, law, or management.",
               "Full tuition fee reimbursement + ₹3,000/month book and PC allowances",
               "SC category students securing admission in top-ranked institutions like IITs, IIMs, AIIMS", 800000.0, {"min": 17, "max": 25}, "All", "All",
               ["Aadhaar Card", "Caste Certificate", "IIT/IIM Admission Letter", "Income Certificate"], "https://scholarships.gov.in", "https://socialjustice.gov.in", 250000.0, "Student", "SC")


    # --- STUDENT SCHEMES (10 Schemes) ---
    add_scheme("One Student One Laptop Scheme", "Ministry of Education & AICTE", "Student Schemes",
               "Aims to provide technical resources to IT/Engineering students from lower income strata.",
               "Free brand new laptop or ₹40,000 financial support for computing devices",
               "Undergraduate B.Tech, MCA, or Diploma students in AICTE approved colleges", 250000.0, {"min": 18, "max": 25}, "All", "All",
               ["Aadhaar Card", "AICTE College ID Card", "Income Certificate", "Marksheet"], "https://aicte-india.org/student-laptop", "https://aicte-india.org", 40000.0, "B.Tech")

    add_scheme("PM Internship Scheme", "Ministry of Corporate Affairs", "Student Schemes",
               "Provides internship opportunities in top 500 partner companies to youths.",
               "Monthly stipend of ₹5,000 for 12 months + one-time assistance of ₹6,000",
               "Youth aged 21-25 with qualifications like High School, ITI, Diploma, BA, BSc, BTech, not in regular employment", 800000.0, {"min": 21, "max": 25}, "All", "All",
               ["Aadhaar Card", "Educational Marksheet", "Income Certificate"], "https://pminternship.mca.gov.in", "https://pminternship.mca.gov.in", 66000.0, "Student")

    add_scheme("Skill India Training Program", "Ministry of Skill Development", "Student Schemes",
               "Provides industry-relevant skill training to youth to secure jobs.",
               "100% free certification courses + job placement assistance + ₹2,000 incentive",
               "School dropouts or college graduates seeking employability training", 9999999.0, {"min": 15, "max": 45}, "All", "All",
               ["Aadhaar Card", "Highest Qualification Marksheet", "Bank Passbook"], "https://skillindia.gov.in", "https://msde.gov.in", 15000.0, "All")

    add_scheme("Digital India Internship Scheme", "Ministry of Electronics and Information Technology", "Student Schemes",
               "Provides summer internship opportunities in core sectors of electronics and IT.",
               "Stipend of ₹10,000 per month for 2 to 3 months",
               "BTech/MCA students in Computer Science/IT/ECE securing minimum 60% marks", 9999999.0, {"min": 19, "max": 24}, "All", "All",
               ["Aadhaar Card", "College Recommendation Letter", "Semester Marksheets"], "https://meity.gov.in/internship", "https://meity.gov.in", 30000.0, "B.Tech")

    add_scheme("PM Research Fellowship (PMRF)", "Ministry of Education", "Student Schemes",
               "Supports research scholars in science, technology, and doctoral programs.",
               "Monthly fellowship of ₹70,000 to ₹80,000 + research grant of ₹2,000,000 over 5 years",
               "Highly meritorious graduates from IITs, IISc, NITs, IISERs pursuing PhD programs", 9999999.0, {"min": 21, "max": 30}, "All", "All",
               ["Research Proposal", "Marksheet", "PhD Registration Slip", "Recommendations"], "https://pmrf.in", "https://pmrf.in", 4500000.0, "Student")

    add_scheme("National Apprenticeship Training Scheme (NATS)", "Ministry of Education", "Student Schemes",
               "Provides practical skill training to graduate and diploma engineers in core industries.",
               "Monthly stipend of ₹9,000 (Graduate) / ₹8,000 (Diploma) directly via DBT",
               "Engineering graduates or diploma holders in technical streams", 9999999.0, {"min": 18, "max": 26}, "All", "All",
               ["Aadhaar Card", "Engineering Degree", "Bank Account Details"], "https://nats.education.gov.in", "https://education.gov.in", 108000.0, "B.Tech")

    add_scheme("National Apprenticeship Promotion Scheme (NAPS)", "Ministry of Skill Development", "Student Schemes",
               "Promotes apprenticeship by sharing cost of basic training and stipend with industries.",
               "Stipend subsidy up to ₹1,500 per month per apprentice for 1-2 years",
               "Youth over 14 years who have completed ITI or secondary school", 9999999.0, {"min": 15, "max": 35}, "All", "All",
               ["Aadhaar Card", "School Marksheet / ITI Certificate"], "https://apprenticeshipindia.gov.in", "https://apprenticeshipindia.gov.in", 18000.0, "Student")

    add_scheme("Startup India Seed Fund Scheme", "Ministry of Commerce and Industry", "Student Schemes",
               "Provides seed funding to early stage startups for proof of concept and trials.",
               "Grants up to ₹20,00,000 for prototype development, loans up to ₹50,00,000 for commercialization",
               "DPIIT recognized startups incorporated less than 2 years ago", 9999999.0, {"min": 18, "max": 40}, "All", "All",
               ["Aadhaar Card", "DPIIT Registration Certificate", "Pitch Deck", "Business Plan"], "https://seedfund.startupindia.gov.in", "https://startupindia.gov.in", 2000000.0, "All")

    add_scheme("Atal Innovation Mission", "NITI Aayog", "Student Schemes",
               "Promotes innovation and entrepreneurship through Atal Tinkering Labs and Incubators.",
               "Access to research infrastructure, mentorship, and startup grants up to ₹10,00,000",
               "Students, innovators, and early-stage startup founders", 9999999.0, {"min": 10, "max": 35}, "All", "All",
               ["Aadhaar Card", "Project Report", "Innovator Credentials"], "https://aim.gov.in", "https://aim.gov.in", 500000.0, "All")

    add_scheme("National Career Service (NCS)", "Ministry of Labour and Employment", "Student Schemes",
               "Free career counseling, job matching, vocational guidance, and skill courses portal.",
               "Access to job vacancies, career counselling, and skill training workshops valued at ₹10,000",
               "Job seekers, students, and workers seeking employment registration", 9999999.0, {"min": 15, "max": 59}, "All", "All",
               ["Aadhaar Card", "Marksheet", "Resume"], "https://ncs.gov.in", "https://ncs.gov.in", 10000.0, "All")


    # --- WOMEN SCHEMES (10 Schemes) ---
    add_scheme("Beti Bachao Beti Padhao", "Ministry of Women and Child Development", "Women Schemes",
               "National campaign targeting female survival, safety, and higher secondary school enrollment.",
               "Sponsors school supplies, cycle schemes, and direct scholarship benefits of ₹5,000",
               "Girl child residing in any Indian state", 9999999.0, {"min": 0, "max": 18}, "Female", "All",
               ["Aadhaar Card", "School Enrollment Certificate", "Birth Certificate"], "https://wcd.nic.in/bbbp", "https://wcd.nic.in", 5000.0, "School Student")

    add_scheme("Sukanya Samriddhi Yojana", "Ministry of Finance", "Women Schemes",
               "Savings scheme targeting the future higher education and marriage expenses of girl child.",
               "High interest rate (8.2%+) + tax exemptions on deposits up to ₹1,50,000/year",
               "Parents of girl child aged below 10 years", 9999999.0, {"min": 0, "max": 10}, "Female", "All",
               ["Birth Certificate of girl child", "Parent's Aadhaar Card", "Address Proof"], "https://www.indiapost.gov.in", "https://www.nsiindia.gov.in", 150000.0, "All")

    add_scheme("PM Matru Vandana Yojana", "Ministry of Women and Child Development", "Women Schemes",
               "Maternity benefit program offering cash incentives to pregnant and lactating mothers.",
               "₹5,000 paid directly to bank account in 3 installments for first living child",
               "Pregnant women and lactating mothers for their first child, excluding government employees", 800000.0, {"min": 19, "max": 45}, "Female", "All",
               ["MCP Card (Mother & Child Protection Card)", "Aadhaar Card", "Bank Passbook"], "https://pmmvy.wcd.gov.in", "https://pmmvy.wcd.gov.in", 5000.0, "All")

    add_scheme("One Stop Centre Scheme", "Ministry of Women and Child Development", "Women Schemes",
               "Provides shelter, legal aid, medical aid, and counseling to women facing domestic or public violence.",
               "100% free temporary residential shelter, security, medical aid, legal support",
               "Any woman facing violence, distress or requiring temporary protection", 9999999.0, {"min": 0, "max": 100}, "Female", "All",
               ["Aadhaar Card / ID Proof (optional in emergencies)"], "https://wcd.nic.in", "https://wcd.nic.in", 50000.0, "All")

    add_scheme("Mahila Shakti Kendra", "Ministry of Women and Child Development", "Women Schemes",
               "Empowers rural women through community participation and skill training at district blocks.",
               "Free vocational training courses, business mentorship, and digital literacy skills",
               "Rural women looking to start micro enterprises or learn new vocational skills", 9999999.0, {"min": 18, "max": 50}, "Female", "All",
               ["Aadhaar Card", "Ration Card"], "https://wcd.nic.in/msk", "https://wcd.nic.in", 15000.0, "All")

    add_scheme("Pradhan Mantri Ujjwala Yojana (PMUY)", "Ministry of Petroleum and Natural Gas", "Women Schemes",
               "Provides clean cooking fuel (LPG connections) to women from BPL families.",
               "Free LPG connection + first cylinder refill free + ₹1,600 subsidy",
               "Adult women belonging to BPL households or tribal communities", 150000.0, {"min": 18, "max": 65}, "Female", "All",
               ["BPL Card / Ration Card", "Aadhaar Card", "Bank Account linked with Aadhaar"], "https://pmuy.gov.in", "https://pmuy.gov.in", 3200.0, "All")

    add_scheme("Nari Shakti Puraskar", "Ministry of Women and Child Development", "Women Schemes",
               "National award recognizes exceptional achievements and services of women or institutions.",
               "National recognition + cash prize of ₹2,00,000 for exceptional works",
               "Women performing exemplary services for women empowerment and social change", 9999999.0, {"min": 25, "max": 100}, "Female", "All",
               ["Detailed Profile", "Supporting Achievements Documents", "Aadhaar"], "https://narishaktipuraskar.wcd.gov.in", "https://wcd.nic.in", 200000.0, "All")

    add_scheme("Working Women Hostel Scheme", "Ministry of Women and Child Development", "Women Schemes",
               "Provides safe and affordable accommodation to working women in urban centers.",
               "Subsidized safe lodging, daycare for kids, and meals at nominal costs",
               "Single, widowed, divorced, or separated working women with salary under ₹50,000/month", 600000.0, {"min": 18, "max": 60}, "Female", "All",
               ["Salary Slip", "Employment Certificate", "Aadhaar Card"], "https://wcd.nic.in/hostels", "https://wcd.nic.in", 36000.0, "All")

    add_scheme("STEP Scheme for Women", "Ministry of Women and Child Development", "Women Schemes",
               "Support to Training and Employment Programme for Women to provide employability skills.",
               "Free training in agriculture, tailoring, IT, tourism + startup credit linkages",
               "Marginalized women aged 16 and above, especially landless agricultural workers", 180000.0, {"min": 16, "max": 60}, "Female", "All",
               ["Aadhaar Card", "Income Certificate", "Caste Certificate"], "https://wcd.nic.in/step", "https://wcd.nic.in", 20000.0, "All")

    add_scheme("Swadhar Greh Scheme", "Ministry of Women and Child Development", "Women Schemes",
               "Aims to rehabilitate women in difficult circumstances (abandoned, victims of disaster/trafficking).",
               "Free lodging, boarding, legal support, clinical aid, and rehabilitation skills",
               "Women in difficult situations without primary family support system", 9999999.0, {"min": 18, "max": 80}, "Female", "All",
               ["Aadhaar Card / Domicile (if available)"], "https://wcd.nic.in", "https://wcd.nic.in", 72000.0, "All")


    # --- EMPLOYMENT SCHEMES (10 Schemes) ---
    add_scheme("PMKVY Training and Certification", "Ministry of Skill Development", "Employment Schemes",
               "Flagship skill certification scheme to enable Indian youth to take up industry training.",
               "Free skill training courses + assessment fees waiver + reward incentive of ₹3,000",
               "Unemployed youth or school dropouts holding valid ID proofs", 9999999.0, {"min": 15, "max": 40}, "All", "All",
               ["Aadhaar Card", "Marksheet of school", "Bank Account Details"], "https://pmkvyofficial.org", "https://msde.gov.in", 15000.0, "All")

    add_scheme("MUDRA Loan Scheme", "Ministry of Finance", "Employment Schemes",
               "Provides credit to micro enterprises in Shishu (up to 50k), Kishor (50k-5L), Tarun (5L-10L) categories.",
               "Collateral-free business loans up to ₹10,00,000 with low interest rates",
               "Micro business owners, shopkeepers, start-up founders seeking operational funds", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Aadhaar Card", "Business Registration Proof", "Project Report", "Bank Statements"], "https://mudra.org.in", "https://mudra.org.in", 500000.0, "All")

    add_scheme("Stand Up India Scheme", "Ministry of Finance", "Employment Schemes",
               "Promotes entrepreneurship among women and SC/ST communities.",
               "Bank loans between ₹10 Lakhs and ₹1 Crore for setting up greenfield enterprises",
               "SC/ST or female entrepreneurs above 18 years, owning at least 51% stake in business", 9999999.0, {"min": 18, "max": 70}, "All", "All",
               ["Caste Certificate", "Business proposal", "ITR returns", "Aadhaar Card"], "https://standupmitra.in", "https://standupmitra.in", 1000000.0, "All")

    add_scheme("Startup India Initiative", "Ministry of Commerce and Industry", "Employment Schemes",
               "Nurtures startups through tax holidays, self-certification, and patent filing support.",
               "3-year income tax exemption + patent registration support fee waiver + funding support",
               "Registered private limited company or LLP under 10 years old with turnover under ₹100 Crore", 9999999.0, {"min": 18, "max": 60}, "All", "All",
               ["DPIIT Recognition Certificate", "Incorporation Certificate", "Patent files (optional)"], "https://startupindia.gov.in", "https://startupindia.gov.in", 100000.0, "All")

    add_scheme("PM Vishwakarma Scheme", "Ministry of Micro, Small and Medium Enterprises", "Employment Schemes",
               "Supports traditional artisans and craftsmen with training and modern tools.",
               "₹15,000 toolkit incentive + ₹500/day training stipend + ₹3 Lakh collateral-free loan",
               "Artisans working in 18 traditional trades (carpenter, blacksmith, potter, tailor etc.)", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Aadhaar Card", "Artisan Verification ID", "Bank Details"], "https://pmvishwakarma.gov.in", "https://msme.gov.in", 150000.0, "All")

    add_scheme("Deendayal Antyodaya Yojana - NULM", "Ministry of Housing and Urban Affairs", "Employment Schemes",
               "Reduces poverty of urban poor households by enabling self-employment and skilled wage jobs.",
               "Subsidized loans for self-employment (interest subsidy of 5-7%) + free skill training",
               "Urban poor, street vendors, and slum dwellers", 100000.0, {"min": 18, "max": 55}, "All", "All",
               ["Urban BPL Card", "Aadhaar Card", "Address Proof"], "https://nulm.gov.in", "https://mohua.gov.in", 25000.0, "All")

    add_scheme("Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)", "Ministry of Rural Development", "Employment Schemes",
               "Placement linked skill training program for rural poor youth.",
               "100% free residential training + guaranteed placement + tablet computer + post placement support",
               "Rural poor youths belonging to families with BPL or MGNREGA cards", 150000.0, {"min": 15, "max": 35}, "All", "All",
               ["BPL Card / MGNREGA Job Card", "Marksheet", "Aadhaar Card"], "https://ddugky.gov.in", "https://rural.nic.in", 45000.0, "All")

    add_scheme("Rural Self Employment Training Institutes (RSETI)", "Ministry of Rural Development & Banks", "Employment Schemes",
               "Dedicated training centres offering short-term residential training to rural youths to start business.",
               "Free residential training + bank loan linkage + 2 years of continuous hand-holding support",
               "Rural youths from distressed families seeking self-employment setups", 200000.0, {"min": 18, "max": 45}, "All", "All",
               ["Aadhaar Card", "Ration Card", "Residence Proof"], "https://rudsetitraining.org", "https://rural.nic.in", 30000.0, "All")

    add_scheme("PMEGP Loan Subsidy", "Ministry of Micro, Small and Medium Enterprises", "Employment Schemes",
               "Credit-linked subsidy program for setting up new micro-enterprises in manufacturing or service.",
               "Government subsidy up to 35% of project cost (max ₹50 Lakh project value)",
               "Individuals above 18 years, having completed at least class 8 for projects over ₹10 Lakhs", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Aadhaar Card", "Project Report", "Class 8 Pass Certificate", "Caste Certificate"], "https://www.kviconline.gov.in/pmegpeportal", "https://msme.gov.in", 350000.0, "All")

    add_scheme("Atal Pension Yojana for Workers", "Ministry of Finance", "Employment Schemes",
               "Old age income security scheme for workers in the unorganized sector.",
               "Guaranteed minimum pension of ₹1,000 to ₹5,000/month after age 60 based on contributions",
               "Indian citizens working in unorganized sectors and not paying income tax", 9999999.0, {"min": 18, "max": 40}, "All", "All",
               ["Aadhaar Card", "Savings Bank Account details"], "https://npscra.nsdl.co.in", "https://pfrda.org.in", 36000.0, "All")


    # --- FARMER SCHEMES (10 Schemes) ---
    add_scheme("Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Direct income support scheme for all landholding farmer families across India.",
               "₹6,000 per year paid in three equal installments of ₹2,000 directly via DBT",
               "Farmer families holding cultivable land in their names", 9999999.0, {"min": 18, "max": 100}, "All", "All",
               ["Land Ownership documents (Khatauni)", "Aadhaar Card", "Bank Account Details"], "https://pmkisan.gov.in", "https://pmkisan.gov.in", 6000.0, "Farmer")

    add_scheme("PM Fasal Bima Yojana (PMFBY)", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Crop insurance scheme protecting farmers against yield losses due to natural calamities.",
               "Insurance payout based on crop yield losses for nominal premium (1.5% to 5%)",
               "All farmers growing notified crops in notified areas, including tenant farmers", 9999999.0, {"min": 18, "max": 80}, "All", "All",
               ["Land records", "Sowing Certificate", "KCC Details", "Aadhaar Card"], "https://pmfby.gov.in", "https://pmfby.gov.in", 25000.0, "Farmer")

    add_scheme("Kisan Credit Card (KCC)", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Provides timely credit to farmers to meet cultivation and maintenance needs.",
               "Collateral-free agricultural loans up to ₹3,00,000 at low interest rate of 4%",
               "Farmers, joint borrowers, tenant farmers, or self-help groups", 9999999.0, {"min": 18, "max": 75}, "All", "All",
               ["Land holding details", "Aadhaar Card", "No-Dues Certificate from banks"], "https://www.sbi.co.in", "https://agricoop.nic.in", 150000.0, "Farmer")

    add_scheme("Soil Health Card Scheme", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Assists farmers in checking soil nutrient status and recommending fertilizers.",
               "Free soil testing + customized Soil Health Card + fertilizer recommendations report",
               "All farmers owning cultivable lands in India", 9999999.0, {"min": 18, "max": 100}, "All", "All",
               ["Land Details / Survey Number", "Aadhaar Card"], "https://soilhealth.dac.gov.in", "https://soilhealth.dac.gov.in", 1500.0, "Farmer")

    add_scheme("Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Aims to achieve convergence of investments in irrigation at the field level.",
               "Subsidy up to 55% for micro irrigation setups (Drip and Sprinkler systems)",
               "Farmers owning agricultural land with access to water sources", 9999999.0, {"min": 18, "max": 80}, "All", "All",
               ["Land ownership proof", "Irrigation system estimation", "Aadhaar Card"], "https://pmksy.gov.in", "https://pmksy.gov.in", 45000.0, "Farmer")

    add_scheme("National Agriculture Market (eNAM)", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Pan-India electronic trading portal networking the existing APMC mandis.",
               "Access to online trading portal to secure competitive prices for crops",
               "Farmers, traders, and commission agents seeking commodity trading licenses", 9999999.0, {"min": 18, "max": 75}, "All", "All",
               ["Aadhaar Card", "Mandi registration copy", "Bank details"], "https://enam.gov.in", "https://enam.gov.in", 10000.0, "Farmer")

    add_scheme("Paramparagat Krishi Vikas Yojana (PKVY)", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Promotes organic farming through cluster approach and Participatory Guarantee System.",
               "Financial assistance of ₹50,000 per hectare for 3 years for organic inputs",
               "Farmers forming organic farming clusters of minimum 20 hectares", 9999999.0, {"min": 18, "max": 80}, "All", "All",
               ["Cluster membership details", "Aadhaar Card", "Land ownership proof"], "https://dmsdac.nic.in", "https://agricoop.nic.in", 50000.0, "Farmer")

    add_scheme("Rashtriya Gokul Mission", "Ministry of Fisheries, Animal Husbandry and Dairying", "Farmer Schemes",
               "Promotes conservation and development of indigenous bovine breeds.",
               "Up to 50% subsidy (max ₹25 Lakhs) for setting up breed multiplier farms",
               "Individual entrepreneurs, self-help groups, and dairy cooperatives", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Project Report", "Land proof (min 2 acres)", "Artisan/Farmer certificate"], "http://dahd.nic.in", "http://dahd.nic.in", 250000.0, "All")

    add_scheme("Dairy Entrepreneurship Development Scheme", "NABARD & Ministry of Animal Husbandry", "Farmer Schemes",
               "Aims to promote clean milk production and self-employment in dairy sector.",
               "Back-ended capital subsidy of 25% (SC/ST: 33.33%) for dairy units",
               "Farmers, individual entrepreneurs, NGOs, and cooperatives", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Detailed project report", "Land documents", "Bank sanction letter"], "https://www.nabard.org", "http://dahd.nic.in", 120000.0, "All")

    add_scheme("National Beekeeping and Honey Mission", "Ministry of Agriculture and Farmers Welfare", "Farmer Schemes",
               "Promotes scientific beekeeping for crop pollination and honey production.",
               "Subsidy up to 50% for setting up beekeeping equipment and training support",
               "Farmers, self-help groups, and bee breeders", 9999999.0, {"min": 18, "max": 60}, "All", "All",
               ["Beekeeping training certificate", "Aadhaar Card", "Bank Details"], "https://nbhm.gov.in", "https://agricoop.nic.in", 30000.0, "Farmer")


    # --- HEALTH SCHEMES (8 Schemes) ---
    add_scheme("Ayushman Bharat - PM Jan Arogya Yojana", "Ministry of Health and Family Welfare", "Health Schemes",
               "Provides health cover for secondary and tertiary care hospitalization to poor families.",
               "Cashless health insurance coverage up to ₹5,00,000 per family per year",
               "Families listed in Socio-Economic Caste Census (SECC) data or lower income groups", 180000.0, {"min": 0, "max": 100}, "All", "All",
               ["Ration Card", "PM-JAY Letter", "Aadhaar Card"], "https://pmjay.gov.in", "https://pmjay.gov.in", 500000.0, "All")

    add_scheme("PM Jan Aushadhi Yojana", "Ministry of Chemicals and Fertilizers", "Health Schemes",
               "Provides quality generic medicines to all at affordable prices through dedicated outlets.",
               "Access to quality generic medicines at 50% to 90% cheaper prices than branded ones",
               "Open to all citizens seeking affordable clinical medicines", 9999999.0, {"min": 0, "max": 100}, "All", "All",
               ["Doctor Prescription"], "https://janaushadhi.gov.in", "https://janaushadhi.gov.in", 5000.0, "All")

    add_scheme("Janani Suraksha Yojana (JSY)", "Ministry of Health and Family Welfare", "Health Schemes",
               "Safe motherhood intervention reducing maternal and neonatal mortality.",
               "Cash assistance up to ₹1,400 for institutional delivery to pregnant women",
               "Pregnant women from BPL families or SC/ST categories giving birth in government hospitals", 250000.0, {"min": 19, "max": 40}, "Female", "All",
               ["Aadhaar Card", "BPL Ration Card", "Hospital Delivery Discharge card"], "https://nhm.gov.in", "https://mohfw.gov.in", 1400.0, "All")

    add_scheme("Mission Indradhanush", "Ministry of Health and Family Welfare", "Health Schemes",
               "Immunization campaign targeting children and pregnant women with full vaccination.",
               "Free vaccination against 12 life-threatening diseases valued at ₹15,000",
               "Children under 2 years of age and pregnant women", 9999999.0, {"min": 0, "max": 2}, "All", "All",
               ["Immunization Card", "Parent's Aadhaar Card"], "https://nhm.gov.in", "https://mohfw.gov.in", 15000.0, "All")

    add_scheme("Rashtriya Bal Swasthya Karyakram", "Ministry of Health and Family Welfare", "Health Schemes",
               "Identifies child health conditions (Birth defects, Diseases, Deficiencies, Developmental delays).",
               "Free medical screening and secondary/tertiary surgical treatments up to ₹1,50,000",
               "Children aged 0 to 18 years enrolled in government schools or anganwadis", 9999999.0, {"min": 0, "max": 18}, "All", "All",
               ["Anganwadi registration / School ID", "Parent's Aadhaar Card"], "https://nhm.gov.in/rbsk", "https://mohfw.gov.in", 150000.0, "All")

    add_scheme("National Dialysis Program", "Ministry of Health and Family Welfare", "Health Schemes",
               "Aims to provide free dialyzer support services to BPL kidney patients.",
               "100% free dialysis session services at district government hospitals",
               "End-stage renal disease patients belonging to BPL families", 150000.0, {"min": 12, "max": 85}, "All", "All",
               ["BPL Card", "Clinical Report", "Aadhaar Card"], "https://nhm.gov.in", "https://mohfw.gov.in", 48000.0, "All")

    add_scheme("National TB Elimination Program", "Ministry of Health and Family Welfare", "Health Schemes",
               "Provides free TB medicines and nutritional support to patients.",
               "Free DOTS diagnostic and medicines + ₹500/month nutritional incentive (Nikshay Poshan)",
               "Active tuberculosis patients diagnosed under government clinics", 9999999.0, {"min": 0, "max": 100}, "All", "All",
               ["Nikshay ID Registration", "Diagnostic Report", "Bank Account Details"], "https://nikshay.in", "https://tbcindia.gov.in", 6000.0, "All")

    add_scheme("PM National Dialysis Service Scheme", "Ministry of Health and Family Welfare", "Health Schemes",
               "Expansion of renal dialysis coverage in public private partnership mode.",
               "Cashless dialysis services valued at ₹1,500 per session",
               "Chronic kidney patients seeking support under district wellness centers", 250000.0, {"min": 18, "max": 80}, "All", "All",
               ["Aadhaar Card", "Referral letter from nephrologist"], "https://nhm.gov.in", "https://mohfw.gov.in", 36000.0, "All")


    # --- SENIOR CITIZEN SCHEMES (5 Schemes) ---
    add_scheme("Atal Pension Yojana (APY)", "Ministry of Finance", "Senior Citizen Schemes",
               "Pension scheme targeted at workers in the unorganized sector to secure old age.",
               "Monthly pension of ₹1,000 to ₹5,000 after 60 based on contribution during youth",
               "Indian citizens aged 18 to 40 who do not pay income tax", 9999999.0, {"min": 18, "max": 40}, "All", "All",
               ["Aadhaar Card", "Savings Bank Account details"], "https://npscra.nsdl.co.in", "https://pfrda.org.in", 36000.0, "All")

    add_scheme("PM Vaya Vandana Yojana", "Ministry of Finance & LIC", "Senior Citizen Schemes",
               "Retirement pension program guaranteeing returns on lump sum deposits.",
               "Guaranteed interest return rate of 7.4% per annum paid as monthly pension for 10 years",
               "Senior citizens aged 60 years and above", 9999999.0, {"min": 60, "max": 100}, "All", "All",
               ["Aadhaar Card", "Age Proof Certificate", "Lump sum deposit check", "PAN Card"], "https://licindia.in", "https://mof.gov.in", 72000.0, "All")

    add_scheme("Indira Gandhi National Old Age Pension", "Ministry of Rural Development", "Senior Citizen Schemes",
               "Provides monthly pension to senior citizens living below poverty line.",
               "Monthly pension of ₹200 (age 60-79) or ₹500 (age 80+), supplemented by states",
               "Citizens aged 60 years and above living below the poverty line", 150000.0, {"min": 60, "max": 100}, "All", "All",
               ["BPL Card", "Age Proof Certificate", "Aadhaar Card", "Domicile Certificate"], "https://nsap.nic.in", "https://rural.nic.in", 6000.0, "All")

    add_scheme("Senior Citizen Savings Scheme (SCSS)", "Ministry of Finance", "Senior Citizen Schemes",
               "Post Office savings scheme providing high security returns on savings.",
               "High interest rate of 8.2%+ on deposits up to ₹30 Lakhs with quarterly payouts",
               "Individuals aged 60 years and above, or 55 years for VRS retirees", 9999999.0, {"min": 60, "max": 100}, "All", "All",
               ["Aadhaar Card", "PAN Card", "Retirement proof / pension papers"], "https://www.indiapost.gov.in", "https://nsiindia.gov.in", 82000.0, "All")

    add_scheme("Annapurna Scheme for Seniors", "Ministry of Rural Development", "Senior Citizen Schemes",
               "Provides food security to senior citizens who are eligible but not receiving old age pension.",
               "10 kg of food grains (wheat/rice) completely free of cost every month",
               "Indigent senior citizens aged 65 and above without family support system", 100000.0, {"min": 65, "max": 100}, "All", "All",
               ["BPL Card", "Age Proof", "Aadhaar Card"], "https://nsap.nic.in", "https://rural.nic.in", 4000.0, "All")


    # --- HOUSING SCHEMES (5 Schemes) ---
    add_scheme("Pradhan Mantri Awas Yojana - Urban", "Ministry of Housing and Urban Affairs", "Housing Schemes",
               "Aims to provide permanent housing with basic infrastructure to urban poor.",
               "Interest subsidy up to 6.5% on home loans up to ₹6 Lakhs (Credit Linked Subsidy)",
               "Families belonging to EWS or LIG categories not owning a pucca house in India", 600000.0, {"min": 18, "max": 70}, "All", "All",
               ["Aadhaar Card", "Income Certificate", "Affidavit of landless status", "Bank Passbook"], "https://pmay-urban.gov.in", "https://mohua.gov.in", 150000.0, "All")

    add_scheme("Pradhan Mantri Awas Yojana - Gramin", "Ministry of Rural Development", "Housing Schemes",
               "Provides financial assistance to rural households living in kutcha houses.",
               "Grant of ₹1,20,000 (plains) / ₹1,30,000 (hilly areas) for building houses + toilets funding",
               "Rural families listed in SECC 2011 deprivation categories", 300000.0, {"min": 18, "max": 75}, "All", "All",
               ["Aadhaar Card", "SECC verification code", "Bank Account Details"], "https://pmayg.nic.in", "https://rural.nic.in", 130000.0, "All")

    add_scheme("Affordable Rental Housing Complexes", "Ministry of Housing and Urban Affairs", "Housing Schemes",
               "Provides rental housing for urban migrants and poor near their workplaces.",
               "Subsidized rental housing complexes in major cities at 30-50% lower rents",
               "Urban migrants, factory workers, street vendors, and low income laborers", 300000.0, {"min": 18, "max": 60}, "All", "All",
               ["Aadhaar Card", "Employment Certificate / Mandi ID Card"], "https://arhc.mohua.gov.in", "https://mohua.gov.in", 24000.0, "All")

    add_scheme("Credit Linked Subsidy Scheme (CLSS)", "Ministry of Housing and Urban Affairs", "Housing Schemes",
               "Subsidizes home loan interest rates for economically weaker sections.",
               "Interest subsidy up to 6.5% reducing monthly EMI obligations by ₹2,000",
               "Urban families seeking home loan from designated public banks", 600000.0, {"min": 18, "max": 65}, "All", "All",
               ["Salary Slips / Income Proof", "Aadhaar Card", "Loan approval letter"], "https://pmay-urban.gov.in", "https://mohua.gov.in", 120000.0, "All")

    add_scheme("Delhi State Housing Program", "State Development Authority", "Housing Schemes",
               "Allots subsidized flats to registered state citizens belonging to low income groups.",
               "Flat allotment at 30% subsidized rates with easy financing terms",
               "Delhi domicile residents having family income under 3L per year", 300000.0, {"min": 21, "max": 60}, "All", "Delhi",
               ["Delhi Domicile Certificate", "Income Certificate", "Aadhaar Card", "Ration Card"], "https://dda.gov.in", "https://delhi.gov.in", 300000.0, "All")


    # --- DISABILITY SCHEMES (5 Schemes) ---
    add_scheme("ADIP Scheme for Disabled", "Ministry of Social Justice and Empowerment", "Disability Schemes",
               "Assists disabled persons in purchasing modern standard aids and appliances.",
               "Free supply of wheelchairs, hearing aids, artificial limbs, and smartphones",
               "Indian citizens with >= 40% disability certified by medical authorities", 360000.0, {"min": 0, "max": 80}, "All", "All",
               ["Disability Certificate", "Income Certificate", "Aadhaar Card"], "http://www.disabilityaffairs.gov.in", "http://www.disabilityaffairs.gov.in", 15000.0, "All", "All", 1)

    add_scheme("Unique Disability ID (UDID) card", "Ministry of Social Justice and Empowerment", "Disability Schemes",
               "Single document of identification and verification for disabled persons to claim benefits.",
               "UDID smart card containing clinical history to access government concessions",
               "Any person with disability pursuing identity registrations", 9999999.0, {"min": 0, "max": 100}, "All", "All",
               ["Disability Certificate", "Medical Reports", "Aadhaar Card", "Photo"], "https://www.swavlambancard.gov.in", "http://www.disabilityaffairs.gov.in", 2000.0, "All", "All", 1)

    add_scheme("Deendayal Disabled Rehabilitation Scheme", "Ministry of Social Justice and Empowerment", "Disability Schemes",
               "Supports voluntary organizations providing education and vocational skills to disabled.",
               "Sponsors special education schooling fees, clinical care, and hostel fees",
               "Disabled children looking to enroll in special schools", 360000.0, {"min": 5, "max": 25}, "All", "All",
               ["Disability Certificate", "School Admission Proof", "Aadhaar Card"], "http://www.disabilityaffairs.gov.in", "http://www.disabilityaffairs.gov.in", 36000.0, "Student", "All", 1)

    add_scheme("Scholarship for Students with Disabilities", "Ministry of Social Justice and Empowerment", "Disability Schemes",
               "Provides financial assistance to disabled students to complete degree education.",
               "₹2,500/month scholarship + book grant of ₹6,000 per annum",
               "Disabled students with >= 40% disability pursuing post-matric courses", 250000.0, {"min": 16, "max": 30}, "All", "All",
               ["Disability Certificate", "Previous Marksheet", "Income Certificate", "College Fee receipt"], "https://scholarships.gov.in", "http://www.disabilityaffairs.gov.in", 36000.0, "Student", "All", 1)

    add_scheme("Assistance to Disabled Persons for Purchase of Aids", "State Welfare Board", "Disability Schemes",
               "State government scheme providing aids and appliances to local disabled residents.",
               "100% free aids supply for income under 1.5L, 50% subsidy for income 1.5L to 3L",
               "State domicile citizens with certified disability certificate", 300000.0, {"min": 5, "max": 75}, "All", "All",
               ["Disability Certificate", "Domicile Certificate", "Income Certificate", "Aadhaar Card"], "http://www.disabilityaffairs.gov.in", "http://www.disabilityaffairs.gov.in", 10000.0, "All", "All", 1)


    # --- SC/ST/OBC SCHEMES (8 Schemes) ---
    add_scheme("Venture Capital Fund for SC", "Ministry of Social Justice and Empowerment", "SC/ST/OBC Schemes",
               "Promotes entrepreneurship among Scheduled Castes by providing venture funding.",
               "Venture capital loans from ₹50 Lakhs to ₹15 Crores at concessional interest rates",
               "SC entrepreneurs running registered businesses with minimum 51% shareholdings", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["SC Caste Certificate", "Detailed Business Plan", "Company Incorporation Certificate"], "https://vcfsc.in", "https://socialjustice.gov.in", 2500000.0, "All", "SC")

    add_scheme("National Fellowship for SC Students", "Ministry of Social Justice and Empowerment", "SC/ST/OBC Schemes",
               "Provides fellowships to SC students pursuing MPhil and PhD courses.",
               "Monthly fellowship of ₹31,000 (JRF) / ₹35,000 (SRF) + contingency grants",
               "SC students qualified in UGC-NET or CSIR examinations", 9999999.0, {"min": 21, "max": 35}, "All", "All",
               ["SC Caste Certificate", "UGC NET Qualification Certificate", "University Admission Letter"], "https://scholarships.gov.in", "https://socialjustice.gov.in", 380000.0, "Student", "SC")

    add_scheme("National Fellowship for ST Students", "Ministry of Tribal Affairs", "SC/ST/OBC Schemes",
               "Offers financial assistance to ST candidates pursuing higher education (MPhil/PhD).",
               "Monthly fellowship of ₹31,000 to ₹35,000 + academic contingence support",
               "ST students pursuing regular doctoral research courses in Indian universities", 9999999.0, {"min": 21, "max": 35}, "All", "All",
               ["ST Caste Certificate", "Post Graduation Degree", "PhD Registration proof"], "https://tribal.nic.in", "https://tribal.nic.in", 380000.0, "Student", "ST")

    add_scheme("Top Class Education Scheme for SC/ST", "Ministry of Social Justice & Tribal Affairs", "SC/ST/OBC Schemes",
               "Covers full educational expenses of SC/ST students in top class institutions.",
               "Full tuition fee reimbursement + ₹3,000/month book and PC allowances",
               "SC/ST students admitted to IITs, IIMs, IISc, NITs, and other premier colleges", 600000.0, {"min": 17, "max": 25}, "All", "All",
               ["Caste Certificate", "Admission Letter", "Income Certificate", "Aadhaar Card"], "https://scholarships.gov.in", "https://socialjustice.gov.in", 200000.0, "Student", "SC")

    add_scheme("PM AJAY Scheme", "Ministry of Social Justice and Empowerment", "SC/ST/OBC Schemes",
               "Pradhan Mantri Anusuchit Jaati Abhyuday Yojana for SC development.",
               "Grants up to ₹50,000 per beneficiary for income generation assets and skills training",
               "SC category citizens living below poverty line", 250000.0, {"min": 18, "max": 60}, "All", "All",
               ["SC Caste Certificate", "BPL Certificate", "Aadhaar Card"], "https://pmajay.dosje.gov.in", "https://socialjustice.gov.in", 50000.0, "All", "SC")

    add_scheme("Eklavya Model Residential Schools (EMRS)", "Ministry of Tribal Affairs", "SC/ST/OBC Schemes",
               "Provides quality middle and high school education to Scheduled Tribe children.",
               "100% free residential schooling, meals, boarding, books, and uniforms value ₹60,000/year",
               "ST category children passing class 5 entrance exams", 9999999.0, {"min": 10, "max": 18}, "All", "All",
               ["ST Caste Certificate", "School Transfer Certificate", "Aadhaar Card"], "https://tribal.nic.in", "https://tribal.nic.in", 60000.0, "School Student", "ST")

    add_scheme("Post Matric Scholarship for Tribal Students", "Ministry of Tribal Affairs", "SC/ST/OBC Schemes",
               "Financial assistance for tribal students pursuing post-matric courses.",
               "Compulsory fee coverage + maintenance allowance up to ₹1,200/month",
               "ST category students pursuing graduate, diploma or post-graduate courses", 250000.0, {"min": 15, "max": 30}, "All", "All",
               ["ST Caste Certificate", "Income Certificate", "Marksheet", "College Admission Proof"], "https://scholarships.gov.in", "https://tribal.nic.in", 45000.0, "Student", "ST")

    add_scheme("National Fellowship for OBC Students", "Ministry of Social Justice and Empowerment", "SC/ST/OBC Schemes",
               "Provides fellowships to OBC students pursuing higher education (MPhil/PhD).",
               "Monthly stipend of ₹31,000 (JRF) / ₹35,000 (SRF) directly via DBT",
               "OBC category candidates registered in UGC recognized research courses", 600000.0, {"min": 21, "max": 35}, "All", "All",
               ["OBC Caste Certificate (Non-Creamy)", "Post-Graduation degree", "Admission proof"], "https://scholarships.gov.in", "https://socialjustice.gov.in", 380000.0, "Student", "OBC")


    # --- FINANCIAL INCLUSION (6 Schemes) ---
    add_scheme("PM Jan Dhan Yojana", "Ministry of Finance", "Financial Inclusion",
               "Ensures access to financial services (savings accounts, remittance, credit, pension, insurance).",
               "Zero-balance bank account + free RuPay debit card + ₹10,000 overdraft facility + ₹2 Lakh accident cover",
               "Indian citizens who do not own a bank account", 9999999.0, {"min": 10, "max": 100}, "All", "All",
               ["Aadhaar Card / Pan Card", "Photo"], "https://pmjdy.gov.in", "https://pmjdy.gov.in", 12000.0, "All")

    add_scheme("Atal Pension Yojana for All", "Ministry of Finance", "Financial Inclusion",
               "Umbrella pension system for all bank account holders contributing for old age.",
               "Guaranteed minimum pension of ₹1,000 to ₹5,000 after the age of 60",
               "Indian citizens holding active bank accounts and not under tax slabs", 9999999.0, {"min": 18, "max": 40}, "All", "All",
               ["Aadhaar Card", "Savings Bank Account details"], "https://npscra.nsdl.co.in", "https://pfrda.org.in", 36000.0, "All")

    add_scheme("Pradhan Mantri Suraksha Bima Yojana (PMSBY)", "Ministry of Finance", "Financial Inclusion",
               "Accident insurance scheme offering high coverage at extremely low premiums.",
               "Accidental death/disability insurance cover of ₹2,00,000 at premium of only ₹20/year",
               "Indian citizens having active bank accounts", 9999999.0, {"min": 18, "max": 70}, "All", "All",
               ["Bank Account details", "Aadhaar Card", "Consent Form"], "https://jansuraksha.gov.in", "https://mof.gov.in", 200000.0, "All")

    add_scheme("Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)", "Ministry of Finance", "Financial Inclusion",
               "Life insurance scheme offering high risk coverage at affordable premiums.",
               "Life insurance cover of ₹2,00,000 in case of death due to any cause at premium of ₹436/year",
               "Indian citizens having bank accounts consenting to auto-debit of premium", 9999999.0, {"min": 18, "max": 50}, "All", "All",
               ["Aadhaar Card", "Bank Passbook", "Auto-debit authorization form"], "https://jansuraksha.gov.in", "https://mof.gov.in", 200000.0, "All")

    add_scheme("Sukanya Samriddhi Yojana for Minor Girls", "Ministry of Finance", "Financial Inclusion",
               "Girl child savings account scheme with tax benefits under Section 80C.",
               "8.2% annual compounded interest rate + 100% tax exemption on savings",
               "Parents opening account in name of girl child below 10 years old", 9999999.0, {"min": 0, "max": 10}, "Female", "All",
               ["Birth Certificate of girl child", "Parent's Aadhaar Card", "Pan Card"], "https://www.indiapost.gov.in", "https://nsiindia.gov.in", 150000.0, "All")

    add_scheme("Small Savings Scheme", "Ministry of Finance", "Financial Inclusion",
               "Secure investment schemes including National Savings Certificate, Kisan Vikas Patra.",
               "Guaranteed interest returns of 7% to 7.7% on term deposits backed by government",
               "Indian citizens seeking low-risk saving accounts", 9999999.0, {"min": 18, "max": 100}, "All", "All",
               ["Aadhaar Card", "PAN Card", "Deposit Money"], "https://www.indiapost.gov.in", "https://nsiindia.gov.in", 50000.0, "All")


    # --- ADDITIONAL CENTRAL SCHEMES (15 Schemes to reach 102 total) ---
    add_scheme("PM Garib Kalyan Anna Yojana (PMGKAY)", "Ministry of Consumer Affairs, Food and Public Distribution", "Additional Central Schemes",
               "Food security welfare program providing free foodgrains to poor households.",
               "5 kg of free foodgrains (wheat/rice) per person per month to priority households",
               "Families holding Antyodaya Anna Yojana (AAY) or Priority Householders (PHH) ration cards", 150000.0, {"min": 0, "max": 100}, "All", "All",
               ["Ration Card", "Aadhaar Card"], "https://dfpd.gov.in", "https://dfpd.gov.in", 6000.0, "All")

    add_scheme("PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)", "Ministry of Housing and Urban Affairs", "Additional Central Schemes",
               "Provides collateral-free working capital loan to street vendors.",
               "First loan of ₹10,000, subsequent loans of ₹20,000 and ₹50,000 on timely repayment + 7% interest subsidy",
               "Street vendors operating in urban areas on or before March 24, 2020", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Vending Certificate / Urban Body ID", "Aadhaar Card", "Bank Details"], "https://pmsvanidhi.mohua.gov.in", "https://mohua.gov.in", 50000.0, "All")

    add_scheme("PM-POSHAN Scheme", "Ministry of Education", "Additional Central Schemes",
               "Provides hot cooked meal in government schools to improve child nutrition.",
               "Free hot nutritious lunch daily at schools valued at ₹4,000 per school year",
               "Children studying in classes 1 to 8 of government and government-aided schools", 9999999.0, {"min": 5, "max": 14}, "All", "All",
               ["School ID"], "https://education.gov.in", "https://education.gov.in", 4000.0, "School Student")

    add_scheme("PM Gati Shakti National Master Plan", "Ministry of Commerce and Industry", "Additional Central Schemes",
               "Digital platform to coordinate infrastructure planning and logistics.",
               "Supports infrastructure projects optimization, reducing logistics cost for startups",
               "Registered logistics companies and manufacturing startups", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Company registration", "Aadhaar of promoter"], "https://gatishakti.gov.in", "https://dpiit.gov.in", 100000.0, "All")

    add_scheme("PM e-Bus Sewa Scheme", "Ministry of Housing and Urban Affairs", "Additional Central Schemes",
               "Augments city bus operations by deploying 10,000 electric buses in PPP mode.",
               "Subsidized, eco-friendly public transit concessions for students and disabled",
               "Citizens and students utilizing state electric bus transits", 9999999.0, {"min": 5, "max": 85}, "All", "All",
               ["Student ID / Disability card", "Aadhaar Card"], "https://mohua.gov.in", "https://mohua.gov.in", 3000.0, "All")

    add_scheme("PM Janman Yojana", "Ministry of Tribal Affairs", "Additional Central Schemes",
               "Targeted development program for Particularly Vulnerable Tribal Groups (PVTGs).",
               "Free housing, electricity, clean water, mobile connectivity, and skill training support",
               "Citizens belonging to PVTG tribal communities", 150000.0, {"min": 0, "max": 90}, "All", "All",
               ["Tribal PVTG caste certificate", "Aadhaar Card", "Ration Card"], "https://tribal.nic.in", "https://tribal.nic.in", 180000.0, "All")

    add_scheme("PM-PRANAM Yojana", "Ministry of Chemicals and Fertilizers", "Additional Central Schemes",
               "Aims to promote alternative fertilizers and balanced use of chemical fertilizers.",
               "Subsidies on organic compost inputs + soil health upgrades workshops",
               "Farmers practicing crop rotation and using organic compost", 9999999.0, {"min": 18, "max": 80}, "All", "All",
               ["Aadhaar Card", "Land holding docs"], "https://urvarak.nic.in", "https://chemicals.nic.in", 8000.0, "Farmer")

    add_scheme("PM-Vidyalaxmi Education Support", "Ministry of Education", "Additional Central Schemes",
               "Interest subsidy scheme for students in government higher educational institutes.",
               "Full interest subsidy on education loans up to ₹10 Lakhs during study period",
               "Students from family income under 4.5L pursuing higher education in NITs, IITs, Central Universities", 450000.0, {"min": 17, "max": 28}, "All", "All",
               ["Aadhaar Card", "College Admission Slip", "Income Certificate", "Loan Sanction copy"], "https://vidyalakshmi.co.in", "https://education.gov.in", 200000.0, "Student")

    add_scheme("PM-Surya Ghar Muft Bijli Yojana", "Ministry of New and Renewable Energy", "Additional Central Schemes",
               "Provides subsidy to install rooftop solar systems for free electricity.",
               "Subsidy up to ₹78,000 for solar setups + 300 units of free electricity per month",
               "Residential households owning concrete roof structures", 9999999.0, {"min": 18, "max": 80}, "All", "All",
               ["Electricity Bill", "Rooftop ownership proof", "Aadhaar Card", "Bank Details"], "https://pmsuryaghar.gov.in", "https://mnre.gov.in", 78000.0, "All")

    add_scheme("PM Development Initiative for North East (PM-DevINE)", "Ministry of Development of North Eastern Region", "Additional Central Schemes",
               "Funds infrastructure and social development projects in North East India.",
               "Funding for micro-enterprises and social livelihood programs up to ₹5,00,000",
               "Citizens and youths domiciled in North Eastern states (Assam, Mizoram, Sikkim etc.)", 9999999.0, {"min": 18, "max": 45}, "All", "Assam",
               ["North East Domicile certificate", "Business plan", "Aadhaar Card"], "https://mdoner.gov.in", "https://mdoner.gov.in", 500000.0, "All")

    add_scheme("PM SHRI Schools Program", "Ministry of Education", "Additional Central Schemes",
               "Upgrades government schools into smart schools hosting high quality education.",
               "100% free high-quality smart education + coaching kits valued at ₹25,000 per student",
               "Children enrolled in PM SHRI designated public schools", 9999999.0, {"min": 5, "max": 18}, "All", "All",
               ["School ID"], "https://pmshrischools.education.gov.in", "https://education.gov.in", 25000.0, "School Student")

    add_scheme("PM Kisan Maandhan Yojana", "Ministry of Agriculture and Farmers Welfare", "Additional Central Schemes",
               "Old age pension scheme for small and marginal farmers.",
               "Assured monthly pension of ₹3,000 after completing 60 years of age",
               "Small and marginal farmers holding land up to 2 hectares, aged 18 to 40 years", 9999999.0, {"min": 18, "max": 40}, "All", "All",
               ["Land Holding papers", "Aadhaar Card", "Savings Bank details"], "https://pmkmy.gov.in", "https://agricoop.nic.in", 36000.0, "Farmer")

    add_scheme("Sovereign Gold Bond Scheme", "Ministry of Finance", "Additional Central Schemes",
               "Secure government securities denominated in grams of gold as savings tool.",
               "Annual interest yield of 2.5% on investment value + tax exemptions on capital gains",
               "Indian resident individuals and Hindu Undivided Families", 9999999.0, {"min": 18, "max": 90}, "All", "All",
               ["PAN Card", "Aadhaar Card", "Bank Account Details"], "https://rbi.org.in", "https://mof.gov.in", 5000.0, "All")

    add_scheme("PM Matsya Sampada Yojana", "Ministry of Fisheries, Animal Husbandry and Dairying", "Additional Central Schemes",
               "Aims to double fishers and fish farmers income through modern equipment.",
               "Up to 40% (SC/ST/Women: 60%) financial subsidy for buying boats and cold storages",
               "Fishers, fish farmers, fish workers, and self-help groups in coastal/rural zones", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["Fishery cooperative proof", "Boat registration (if applicable)", "Aadhaar Card"], "https://pmmsy.dof.gov.in", "http://dahd.nic.in", 150000.0, "All")

    add_scheme("PM SVANidhi Interest Subsidy", "Ministry of Housing and Urban Affairs", "Additional Central Schemes",
               "Interest subsidy scheme for timely repayment of street vendor loans.",
               "7% interest subsidy directly credited to bank account + cashback up to ₹100/month",
               "Street vendors repayment tracking under PM SVANidhi loans", 9999999.0, {"min": 18, "max": 65}, "All", "All",
               ["PM SVANidhi Loan ID", "Repayment receipt", "Aadhaar Card"], "https://pmsvanidhi.mohua.gov.in", "https://mohua.gov.in", 1200.0, "All")

    # Insert schemes into database
    cursor.executemany("""
    INSERT OR IGNORE INTO schemes (
        scheme_name, ministry, category, description, benefits, eligibility, income_limit,
        age_limit, gender, state_availability, documents_required, application_link,
        official_website, last_updated, financial_value, education, caste_category, disability_required
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, schemes_data)
    
    # 2. NGOs from ALL 36 States & UTs (at least one for each)
    ngos_list = [
        # States
        ("Andhra Rural Development Foundation", "Andhra Pradesh", "Vijayawada", "Women Support, Healthcare", "https://andhradevelopment.org"),
        ("Arunachal Child Welfare Mission", "Arunachal Pradesh", "Itanagar", "Child Welfare, Education", "https://arunachalchildwelfare.org"),
        ("Assam Literacy Society", "Assam", "Guwahati", "Education, Skill Development", "https://assamliteracy.org"),
        ("Bihar Food Support Association", "Bihar", "Patna", "Food Support, Shelter Homes", "https://biharfoodsupport.org"),
        ("Chhattisgarh Tribal Uplift Council", "Chhattisgarh", "Raipur", "Skill Development, Education", "https://chhattisgarh-tribal.org"),
        ("Goa Green Care Foundation", "Goa", "Panaji", "Healthcare, Senior Citizen", "https://goagreencare.org"),
        ("Gujarat Gramin Vikas Kendra", "Gujarat", "Ahmedabad", "Skill Development, Farmer Support", "https://gujaratgraminvikas.org"),
        ("Haryana Women Empowerment Group", "Haryana", "Gurugram", "Women Support, Skill Development", "https://haryanawomen.org"),
        ("Himachal Senior Care", "Himachal Pradesh", "Shimla", "Senior Citizen, Healthcare", "https://himachalseniorcare.org"),
        ("Jharkhand Jan Kalyan Samiti", "Jharkhand", "Ranchi", "Disability, Education", "https://jharkhandjankalyan.org"),
        ("Karnataka Skill Academy", "Karnataka", "Bengaluru", "Skill Development, Education", "https://karnatakaskillacademy.org"),
        ("Kerala Health Initiatives", "Kerala", "Trivandrum", "Healthcare, Disability", "https://keralahealthinitiatives.org"),
        ("Madhya Pradesh Nari Sewa Kendra", "Madhya Pradesh", "Bhopal", "Women Support, Shelter Homes", "https://mpnarisewakendra.org"),
        ("Maharashtra Gramin Sahyog", "Maharashtra", "Washim", "Farmer Support, Food Support", "https://mahagraminsahyog.org"),
        ("Manipur Education Society", "Manipur", "Imphal", "Education, Child Welfare", "https://manipureducation.org"),
        ("Meghalaya Green Livelihoods", "Meghalaya", "Shillong", "Skill Development, Food Support", "https://meghalayalivelihoods.org"),
        ("Mizoram Women Care", "Mizoram", "Aizawl", "Women Support, Healthcare", "https://mizoramwomencare.org"),
        ("Nagaland Tribal Aid", "Nagaland", "Kohima", "Food Support, Shelter Homes", "https://nagalandtribalaid.org"),
        ("Odisha Relief Foundation", "Odisha", "Bhubaneswar", "Disability, Healthcare", "https://odisharelief.org"),
        ("Punjab Kisan Seva Society", "Punjab", "Amritsar", "Skill Development, Food Support", "https://punjabkisanseva.org"),
        ("Rajasthan Desert Welfare Trust", "Rajasthan", "Jaipur", "Women Support, Food Support", "https://rajasthandertwelfare.org"),
        ("Sikkim Organic Farmers Help", "Sikkim", "Gangtok", "Skill Development, Farmer Support", "https://sikkimfarmers.org"),
        ("Tamil Nadu Children Trust", "Tamil Nadu", "Chennai", "Child Welfare, Education", "https://tnchildren.org"),
        ("Telangana Women Skills Center", "Telangana", "Hyderabad", "Women Support, Skill Development", "https://telanganawomenskills.org"),
        ("Tripura Tribal Welfare Society", "Tripura", "Agartala", "Education, Food Support", "https://tripuratribal.org"),
        ("Uttar Pradesh Kanya Seva Trust", "Uttar Pradesh", "Lucknow", "Women Support, Education", "https://upkanyaseva.org"),
        ("Uttarakhand Shelter Homes", "Uttarakhand", "Dehradun", "Shelter Homes, Senior Citizen", "https://uttarakhand-shelter.org"),
        ("West Bengal Child Care Association", "West Bengal", "Kolkata", "Child Welfare, Healthcare", "https://wbchildcare.org"),
        # Union Territories
        ("Delhi Education & Welfare Council", "Delhi", "New Delhi", "Education, Women Support", "https://delhieducationwelfare.org"),
        ("Jammu & Kashmir Relief Mission", "Jammu and Kashmir", "Srinagar", "Healthcare, Shelter Homes", "https://jkrelief.org"),
        ("Ladakh Livelihood Projects", "Ladakh", "Leh", "Skill Development, Food Support", "https://ladakhlivelihood.org"),
        ("Chandigarh Senior Care Foundation", "Chandigarh", "Chandigarh", "Senior Citizen, Healthcare", "https://chandigarhseniorcare.org"),
        ("Puducherry Fishermen Aid Society", "Puducherry", "Puducherry", "Food Support, Skill Development", "https://puducherryfishermen.org"),
        ("Andaman Welfare Group", "Andaman and Nicobar Islands", "Port Blair", "Healthcare, Food Support", "https://andamanwelfare.org"),
        ("Dadra & Nagar Haveli Tribal Care", "Dadra and Nagar Haveli and Daman and Diu", "Silvassa", "Education, Skill Development", "https://dnhd-tribalcare.org"),
        ("Lakshadweep Island Development Society", "Lakshadweep", "Kavaratti", "Healthcare, Food Support", "https://lakshadweepdev.org")
    ]
    
    ngos_data = []
    for name, state, district, services, web in ngos_list:
        desc = f"Dedicated public charity supporting welfare missions in {state} with focused programs."
        eligibility = "Underprivileged groups, residents of local districts."
        beneficiary_category = "SC, ST, OBC, General, Women, Children, Disabled, Senior Citizens"
        
        # flags
        women_support = 1 if "Women Support" in services else 0
        child_welfare = 1 if "Child Welfare" in services else 0
        education = 1 if "Education" in services else 0
        disability = 1 if "Disability" in services else 0
        senior_citizen = 1 if "Senior Citizen" in services else 0
        healthcare = 1 if "Healthcare" in services else 0
        food_support = 1 if "Food Support" in services else 0
        skill_development = 1 if "Skill Development" in services else 0
        shelter_homes = 1 if "Shelter Homes" in services else 0
        
        ngos_data.append((
            name, desc, state, district, "9876543210", f"info@{state.lower().replace(' ', '')}ngo.org",
            web, services, eligibility, beneficiary_category, 1,
            women_support, child_welfare, education, disability, senior_citizen,
            healthcare, food_support, skill_development, shelter_homes
        ))
        
    cursor.executemany("""
    INSERT INTO ngos (
        ngo_name, description, state, district, contact_number, email, website,
        services_offered, eligibility, beneficiary_category, approved,
        women_support, child_welfare, education, disability, senior_citizen,
        healthcare, food_support, skill_development, shelter_homes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ngos_data)

    # 3. Seed Default Testing Profile in Users Table
    # Prefill: Rahul Sharma, 20, Male, Delhi, New Delhi, Student, 150000, General, 0, B.Tech, 150000
    cursor.execute("""
    INSERT INTO users (
        username, password, name, age, gender, state, district, occupation,
        annual_income, category, disability, education, family_income
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "default_user", "password123", "Rahul Sharma", 20, "Male", "Delhi", "New Delhi", "Student",
        150000.0, "General", 0, "B.Tech", 150000.0
    ))
    user_id = cursor.lastrowid
    
    # 4. Seed some sample documents
    cursor.execute("""
    INSERT INTO documents (user_id, document_name, file_path, uploaded_date, status)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Aadhaar Card", "/documents/aadhaar_rahul.pdf", "2026-06-22", "Verified"))
    cursor.execute("""
    INSERT INTO documents (user_id, document_name, file_path, uploaded_date, status)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Previous Marksheet", "/documents/marksheet_rahul.pdf", "2026-06-22", "Verified"))
    
    # 5. Seed some sample applications
    cursor.execute("SELECT id FROM schemes WHERE scheme_name LIKE '%One Student One Laptop%'")
    row = cursor.fetchone()
    if row:
        laptop_scheme_id = row[0]
        cursor.execute("""
        INSERT INTO applications (user_id, scheme_id, status, applied_date, remarks)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, laptop_scheme_id, "Pending", "2026-06-22", "Application under review at college level."))
        
    cursor.execute("SELECT id FROM schemes WHERE scheme_name LIKE '%PM Jan Dhan Yojana%'")
    row = cursor.fetchone()
    if row:
        jandhan_scheme_id = row[0]
        cursor.execute("""
        INSERT INTO applications (user_id, scheme_id, status, applied_date, remarks)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, jandhan_scheme_id, "Approved", "2026-06-22", "Aadhaar-seeded bank account successfully generated."))

    conn.commit()
    conn.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    init_db()
