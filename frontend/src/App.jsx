import { useState, useEffect, useRef } from 'react';
import {
  User,
  Search,
  CheckCircle,
  FileText,
  Upload,
  AlertTriangle,
  MessageSquare,
  ShieldCheck,
  Calendar,
  Layers,
  Volume2,
  VolumeX,
  Mic,
  MicOff,
  Users,
  Compass,
  RefreshCw,
  Award,
  ChevronRight,
  Download,
  Eye,
  Trash2,
  Languages,
  CheckCircle2,
  HelpCircle,
  Moon,
  Sun,
  Flame,
  Plus,
  ArrowRight,
  TrendingUp,
  FileDown,
  Info,
  Check,
  AlertCircle,
  MessageCircle,
  Accessibility,
  ArrowLeft,
  Paperclip,
  CheckCheck,
  Send,
  MoreVertical,
  Briefcase,
  File,
  X,
  Edit2
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const STATES_LIST = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
  "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
  "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
  "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
];

const UTS_LIST = [
  "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", "Puducherry", "Andaman and Nicobar Islands",
  "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep"
];

const ALL_LOCATIONS = ["All", ...STATES_LIST, ...UTS_LIST];

const CATEGORIES_LIST = [
  "Education Schemes", "Student Schemes", "Women Schemes", "Employment Schemes", "Farmer Schemes",
  "Health Schemes", "Senior Citizen Schemes", "Housing Schemes", "Disability Schemes", "SC/ST/OBC Schemes",
  "Financial Inclusion", "Additional Central Schemes"
];

const NGO_SERVICES = [
  "Women Support", "Child Welfare", "Education", "Disability", "Senior Citizen", "Healthcare",
  "Food Support", "Skill Development", "Shelter Homes"
];

function App() {
  // Navigation Tabs: 'citizen' | 'ngo' | 'admin' | 'government-scheme-agent'
  const [activeTab, setActiveTab] = useState('citizen');
  const [activeNgoTab, setActiveNgoTab] = useState('directory'); // 'directory' | 'dashboard' | 'tracking'
  
  // Accessibility Settings
  const [fontSize, setFontSize] = useState('normal'); 
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [language, setLanguage] = useState('English');
  const [isVoiceNavEnabled, setIsVoiceNavEnabled] = useState(false);
  const [speechPlaying, setSpeechPlaying] = useState(false);

  // Default Testing Profile (Delhi Student)
  const [profile, setProfile] = useState({
    name: "Rahul Sharma",
    age: 20,
    gender: "Male",
    state: "Delhi",
    district: "New Delhi",
    occupation: "Student",
    annualIncome: 150000,
    category: "General",
    disability: false,
    education: "B.Tech",
    familyIncome: 150000
  });

  // Citizen Dashboard Stats & Schemes
  const [schemeSearch, setSchemeSearch] = useState('');
  const [schemeCategoryFilter, setSchemeCategoryFilter] = useState('All');
  const [schemeStateFilter, setSchemeStateFilter] = useState('All');
  const [schemesList, setSchemesList] = useState([]);
  const [schemesPage, setSchemesPage] = useState(1);
  const [totalSchemesInDB, setTotalSchemesInDB] = useState(0);
  const [evaluationResult, setEvaluationResult] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  
  // Document Vault State
  const [uploadedDocs, setUploadedDocs] = useState(['Aadhaar Card', 'Previous Marksheet']);
  const [docCheckResult, setDocCheckResult] = useState(null);
  const [isVerifyingDocs, setIsVerifyingDocs] = useState(false);

  // Life Event Predictions
  const [predictions, setPredictions] = useState([]);

  // RAG PDF Chat State
  const [selectedSchemeForChat, setSelectedSchemeForChat] = useState('PM Vidya Scheme');
  const [ragQuery, setRagQuery] = useState('');
  const [ragHistory, setRagHistory] = useState([
    { role: 'assistant', text: 'Hello! You can ask me any question about the official guidelines, eligibility, rules, or required documents for this scheme.' }
  ]);
  const [isRagLoading, setIsRagLoading] = useState(false);

  // Fraud Check State
  const [fraudInput, setFraudInput] = useState('');
  const [fraudResult, setFraudResult] = useState(null);
  const [isCheckingFraud, setIsCheckingFraud] = useState(false);

  // Advanced Dashboard Analytics
  const [dashboardAnalytics, setDashboardAnalytics] = useState(null);

  // NGO Directory Search and Submission States
  const [ngoSearchState, setNgoSearchState] = useState('Delhi');
  const [ngoSearchDistrict, setNgoSearchDistrict] = useState('');
  const [ngoSearchService, setNgoSearchService] = useState('All');
  const [ngoFilterCheckboxes, setNgoFilterCheckboxes] = useState({
    "Women Support": false,
    "Child Welfare": false,
    "Education": false,
    "Disability": false,
    "Senior Citizen": false,
    "Healthcare": false,
    "Food Support": false,
    "Skill Development": false,
    "Shelter Homes": false
  });
  const [ngosList, setNgosList] = useState([]);
  const [selectedNgoForRequest, setSelectedNgoForRequest] = useState(null);
  const [ngoRequestDetails, setNgoRequestDetails] = useState('');
  const [ngoRequestDocs, setNgoRequestDocs] = useState([]);
  const [citizenNgoRequests, setCitizenNgoRequests] = useState([]);
  const [isNgosLoading, setIsNgosLoading] = useState(false);

  // NGO Dashboard (For Mock NGOs logged in)
  const [selectedNgoId, setSelectedNgoId] = useState(29); // Delhi NGO seeded
  const [ngoIncomingRequests, setNgoIncomingRequests] = useState([]);
  const [ngoUpdateRemarks, setNgoUpdateRemarks] = useState('');

  // Admin NGO Management States
  const [showAdminModal, setShowAdminModal] = useState(false);
  const [adminNgoMode, setAdminNgoMode] = useState('add'); // 'add' | 'edit'
  const [adminSelectedNgoId, setAdminSelectedNgoId] = useState(null);
  const [adminNgoForm, setAdminNgoForm] = useState({
    ngo_name: '',
    description: '',
    state: 'Delhi',
    district: 'New Delhi',
    contact_number: '',
    email: '',
    website: '',
    services_offered: 'Education',
    eligibility: 'Underprivileged Students',
    beneficiary_category: 'SC, ST, OBC, General',
    women_support: 0,
    child_welfare: 0,
    education: 1,
    disability: 0,
    senior_citizen: 0,
    healthcare: 0,
    food_support: 0,
    skill_development: 0,
    shelter_homes: 0
  });
  const [adminNgoAnalytics, setAdminNgoAnalytics] = useState(null);
  const [adminNgosList, setAdminNgosList] = useState([]);

  // Modals & UI States
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [applicationStatusMsg, setApplicationStatusMsg] = useState(null);

  // WhatsApp Chat State (WhatsApp Web Redesign)
  const [activeChatId, setActiveChatId] = useState('agent');
  const [chatSearchQuery, setChatSearchQuery] = useState('');
  const [showAttachmentMenu, setShowAttachmentMenu] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isAssistantThinking, setIsAssistantThinking] = useState(false);

  const [conversations, setConversations] = useState({
    agent: {
      name: "NIC Welfare Coordinator",
      subtitle: "General welfare scheme advisor",
      avatar: "🏛️",
      status: "🟢 Online",
      verified: true,
      messages: [
        {
          role: 'assistant',
          text: "🙏 Namaste Rahul!\n\nI am the General Welfare Coordinator.\n\nI can check your eligibility across all 100+ national and state schemes, suggest checklist certificates, or recommend NGOs near Delhi. Let me know what you are looking for!",
          time: "10:00 AM",
          showChips: true
        }
      ]
    },
    scholarship: {
      name: "Scholarship Specialist",
      subtitle: "Higher education scholarships and grants",
      avatar: "🎓",
      status: "🟢 Online",
      verified: true,
      messages: [
        {
          role: 'assistant',
          text: "Namaste Rahul! I can assist with B.Tech scholarships like One Student One Laptop or Central Sector Scholarship options. Feel free to ask details!",
          time: "09:30 AM"
        }
      ]
    },
    healthcare: {
      name: "Health & Pension Advisor",
      subtitle: "Ayushman Bharat and pension benefits",
      avatar: "👵",
      status: "🟢 Online",
      verified: true,
      messages: [
        {
          role: 'assistant',
          text: "Welcome! Need help with PM Jan Arogya Yojana medical cover or Atal Pension Yojana allocations? I am here to help.",
          time: "09:00 AM"
        }
      ]
    },
    ngo: {
      name: "NGO Support Officer",
      subtitle: "Connects you with nearby assistance",
      avatar: "🤝",
      status: "🟢 Online",
      verified: true,
      messages: [
        {
          role: 'assistant',
          text: "Namaste! Looking for food support, disability aids, or local shelter housing? Ask me to query registered NGOs for you.",
          time: "Yesterday"
        }
      ]
    }
  });

  const chatScrollRef = useRef(null);

  // Apply Accessibility Classes on Document Root
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('font-size-normal', 'font-size-large', 'font-size-xlarge');
    root.classList.add(`font-size-${fontSize}`);
  }, [fontSize]);

  useEffect(() => {
    const root = document.documentElement;
    if (isDarkMode) root.classList.add('dark');
    else root.classList.remove('dark');
  }, [isDarkMode]);

  useEffect(() => {
    const root = document.documentElement;
    if (isHighContrast) root.classList.add('theme-high-contrast');
    else root.classList.remove('theme-high-contrast');
  }, [isHighContrast]);

  // Voice speech synthesis
  const speakNarrative = (text) => {
    if (!isVoiceNavEnabled) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'Hindi' ? 'hi-IN' : 'en-IN';
    window.speechSynthesis.speak(utterance);
  };

  const handleVoiceNavToggle = () => {
    const nextState = !isVoiceNavEnabled;
    setIsVoiceNavEnabled(nextState);
    if (nextState) {
      setTimeout(() => {
        const txt = language === 'Hindi'
          ? "वॉयस नेविगेशन सक्रिय है।"
          : "Voice guidance active.";
        const utterance = new SpeechSynthesisUtterance(txt);
        utterance.lang = language === 'Hindi' ? 'hi-IN' : 'en-IN';
        window.speechSynthesis.speak(utterance);
      }, 100);
    } else {
      window.speechSynthesis.cancel();
    }
  };

  // Scroll chat to bottom
  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [conversations, activeChatId, isAssistantThinking]);

  // Fetch schemes from DB (Paginated)
  const fetchSchemes = async () => {
    try {
      const catFilter = schemeCategoryFilter === 'All' ? '' : `&category=${encodeURIComponent(schemeCategoryFilter)}`;
      const stFilter = schemeStateFilter === 'All' ? '' : `&state=${encodeURIComponent(schemeStateFilter)}`;
      const res = await fetch(`${API_BASE}/api/schemes?search=${encodeURIComponent(schemeSearch)}${catFilter}${stFilter}&page=${schemesPage}&limit=10`);
      if (res.ok) {
        const data = await res.json();
        setSchemesList(data.schemes);
        setTotalSchemesInDB(data.total_count);
      }
    } catch (err) {
      console.warn("Failed to fetch schemes: ", err);
    }
  };

  // Profile Evaluation API call
  const runEvaluation = async (updatedProfile = profile) => {
    setIsEvaluating(true);
    try {
      const res = await fetch(`${API_BASE}/api/profile/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedProfile),
      });
      if (res.ok) {
        const data = await res.json();
        setEvaluationResult(data);
      }
    } catch (err) {
      console.warn(err);
    } finally {
      setIsEvaluating(false);
    }
  };

  // Document Verification API call
  const runDocVerification = async (docs = uploadedDocs) => {
    setIsVerifyingDocs(true);
    try {
      const res = await fetch(`${API_BASE}/api/document/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          uploaded_documents: docs,
          category: profile.category,
          disability_status: profile.disability ? "Yes" : "No",
          occupation: profile.occupation
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setDocCheckResult(data);
      }
    } catch (err) {
      console.warn(err);
    } finally {
      setIsVerifyingDocs(false);
    }
  };

  // Fetch predictions
  const fetchPredictions = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age: profile.age, occupation: profile.occupation }),
      });
      if (res.ok) {
        const data = await res.json();
        setPredictions(data.predictions);
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Fetch Advanced Dashboard Analytics
  const fetchDashboardAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/dashboard/analytics?user_id=1`);
      if (res.ok) {
        const data = await res.json();
        setDashboardAnalytics(data);
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Fetch NGOs
  const fetchNgos = async () => {
    setIsNgosLoading(true);
    try {
      let url = `${API_BASE}/api/ngos?state=${ngoSearchState}`;
      if (ngoSearchDistrict) url += `&district=${encodeURIComponent(ngoSearchDistrict)}`;
      if (ngoSearchService !== 'All') url += `&category=${encodeURIComponent(ngoSearchService)}`;
      
      // checkbox filters
      Object.keys(ngoFilterCheckboxes).forEach(key => {
        if (ngoFilterCheckboxes[key]) {
          const queryKey = key.toLowerCase().replace(' ', '_');
          url += `&${queryKey}=1`;
        }
      });

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setNgosList(data.ngos);
      }
    } catch (err) {
      console.warn(err);
    } finally {
      setIsNgosLoading(false);
    }
  };

  // Fetch citizen NGO requests
  const fetchCitizenNgoRequests = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ngos/requests?user_id=1`);
      if (res.ok) {
        const data = await res.json();
        setCitizenNgoRequests(data.requests);
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Fetch NGO dashboard incoming requests
  const fetchNgoIncomingRequests = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ngos/requests?ngo_id=${selectedNgoId}`);
      if (res.ok) {
        const data = await res.json();
        setNgoIncomingRequests(data.requests);
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Fetch Admin NGOs list
  const fetchAdminNgos = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ngos?state=All`);
      if (res.ok) {
        const data = await res.json();
        setAdminNgosList(data.ngos);
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Fetch Admin Analytics
  const fetchAdminAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/ngos/analytics`);
      if (res.ok) {
        const data = await res.json();
        setAdminNgoAnalytics(data);
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Initial load
  useEffect(() => {
    fetchSchemes();
  }, [schemeSearch, schemeCategoryFilter, schemeStateFilter, schemesPage]);

  useEffect(() => {
    runEvaluation();
    runDocVerification();
    fetchPredictions();
    fetchDashboardAnalytics();
    fetchCitizenNgoRequests();
    fetchNgos();
  }, [profile]);

  useEffect(() => {
    if (activeTab === 'ngo') {
      fetchNgoIncomingRequests();
    } else if (activeTab === 'admin') {
      fetchAdminNgos();
      fetchAdminAnalytics();
    }
  }, [activeTab, selectedNgoId]);

  const handleProfileChange = (e) => {
    const { name, value, type, checked } = e.target;
    let val = type === 'checkbox' ? checked : value;
    if (name === 'age' || name === 'annualIncome' || name === 'familyIncome') {
      val = Number(val);
    }
    setProfile(prev => ({ ...prev, [name]: val }));
  };

  const handleDocUpload = (docName) => {
    if (!uploadedDocs.includes(docName)) {
      const newDocs = [...uploadedDocs, docName];
      setUploadedDocs(newDocs);
      runDocVerification(newDocs);
      speakNarrative(`${docName} has been uploaded successfully.`);
    }
  };

  const handleDocDelete = (docName) => {
    const newDocs = uploadedDocs.filter(d => d !== docName);
    setUploadedDocs(newDocs);
    runDocVerification(newDocs);
    speakNarrative(`${docName} has been deleted.`);
  };

  // Scam link check
  const scanFraud = async () => {
    if (!fraudInput.trim()) return;
    setIsCheckingFraud(true);
    try {
      const res = await fetch(`${API_BASE}/api/fraud/detect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content_or_url: fraudInput }),
      });
      if (res.ok) {
        const data = await res.json();
        setFraudResult(data);
      }
    } catch (err) {
      console.warn(err);
    } finally {
      setIsCheckingFraud(false);
    }
  };

  // RAG Document Chat
  const submitRagQuery = async () => {
    if (!ragQuery.trim()) return;
    const userMsg = { role: 'user', text: ragQuery };
    setRagHistory(prev => [...prev, userMsg]);
    setRagQuery('');
    setIsRagLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/document/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: ragQuery,
          scheme_name: selectedSchemeForChat,
          chat_history: []
        })
      });
      if (res.ok) {
        const data = await res.json();
        setRagHistory(prev => [...prev, { role: 'assistant', text: data.answer }]);
      }
    } catch (err) {
      console.warn(err);
    } finally {
      setIsRagLoading(false);
    }
  };

  // Apply scheme
  const triggerApplyScheme = async (schemeName, schemeId) => {
    setApplicationStatusMsg(schemeName);
    speakNarrative(`Applied for ${schemeName} successfully.`);
    
    // Call Mock application apply endpoint on backend to update stats
    try {
      // In our mock, we just evaluate again or update status dynamically
      // For simplicity, we trigger the visual notification
    } catch (err) {}
    
    setTimeout(() => {
      setApplicationStatusMsg(null);
      fetchDashboardAnalytics();
    }, 4000);
  };

  // Submit request to NGO
  const handleNgoRequestSubmit = async (e) => {
    e.preventDefault();
    if (!selectedNgoForRequest || !ngoRequestDetails.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/ngos/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          ngo_id: selectedNgoForRequest.id,
          request_details: ngoRequestDetails,
          uploaded_docs: ngoRequestDocs
        })
      });
      if (res.ok) {
        alert(`Assistance request submitted to ${selectedNgoForRequest.ngo_name} successfully!`);
        setSelectedNgoForRequest(null);
        setNgoRequestDetails('');
        setNgoRequestDocs([]);
        fetchCitizenNgoRequests();
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // NGO Update Request Status (Accept/Reject)
  const handleNgoRequestAction = async (requestId, status) => {
    try {
      const res = await fetch(`${API_BASE}/api/ngos/requests/${requestId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: status,
          remarks: ngoUpdateRemarks
        })
      });
      if (res.ok) {
        alert(`Request status updated to ${status}!`);
        setNgoUpdateRemarks('');
        fetchNgoIncomingRequests();
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Admin Add / Edit NGO submit
  const handleAdminNgoSubmit = async (e) => {
    e.preventDefault();
    const endpoint = adminNgoMode === 'add' ? '/api/ngos/add' : `/api/ngos/edit/${adminSelectedNgoId}`;
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(adminNgoForm)
      });
      if (res.ok) {
        alert(adminNgoMode === 'add' ? "NGO added successfully!" : "NGO updated successfully!");
        setShowAdminModal(false);
        fetchAdminNgos();
        fetchAdminAnalytics();
        setAdminNgoForm({
          ngo_name: '',
          description: '',
          state: 'Delhi',
          district: 'New Delhi',
          contact_number: '',
          email: '',
          website: '',
          services_offered: 'Education',
          eligibility: 'Underprivileged Students',
          beneficiary_category: 'SC, ST, OBC, General',
          women_support: 0,
          child_welfare: 0,
          education: 1,
          disability: 0,
          senior_citizen: 0,
          healthcare: 0,
          food_support: 0,
          skill_development: 0,
          shelter_homes: 0
        });
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Admin Delete NGO
  const handleAdminNgoDelete = async (ngoId) => {
    if (!confirm("Are you sure you want to delete this NGO?")) return;
    try {
      const res = await fetch(`${API_BASE}/api/ngos/delete/${ngoId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        alert("NGO deleted successfully!");
        fetchAdminNgos();
        fetchAdminAnalytics();
      }
    } catch (err) {
      console.warn(err);
    }
  };

  // Admin Edit NGO load details
  const handleAdminNgoEditLoad = (ngo) => {
    setAdminNgoMode('edit');
    setAdminSelectedNgoId(ngo.id);
    setAdminNgoForm({
      ngo_name: ngo.ngo_name,
      description: ngo.description,
      state: ngo.state,
      district: ngo.district,
      contact_number: ngo.contact_number,
      email: ngo.email,
      website: ngo.website,
      services_offered: ngo.services_offered,
      eligibility: ngo.eligibility,
      beneficiary_category: ngo.beneficiary_category,
      women_support: ngo.women_support,
      child_welfare: ngo.child_welfare,
      education: ngo.education,
      disability: ngo.disability,
      senior_citizen: ngo.senior_citizen,
      healthcare: ngo.healthcare,
      food_support: ngo.food_support,
      skill_development: ngo.skill_development,
      shelter_homes: ngo.shelter_homes
    });
    setShowAdminModal(true);
  };

  // Voice Recognition Speech-to-Text
  const toggleListening = () => {
    if (isListening) {
      setIsListening(false);
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech Recognition API is not supported in this browser. Please type your query!");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = language === 'Hindi' ? 'hi-IN' : 'en-IN';
    recognition.interimResults = false;
    
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setChatInput(transcript);
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.start();
  };

  // WhatsApp Assistant Chat Trigger
  const appendChatMessage = (chatId, role, text, extra = {}) => {
    const newMsg = {
      role,
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      ...extra
    };
    setConversations(prev => {
      const chat = prev[chatId];
      return {
        ...prev,
        [chatId]: {
          ...chat,
          messages: [...chat.messages, newMsg]
        }
      };
    });
  };

  const handleAssistantChat = async (typedQuery = chatInput) => {
    const queryText = typedQuery || chatInput;
    if (!queryText.trim()) return;

    appendChatMessage(activeChatId, 'user', queryText);
    setChatInput('');
    setIsAssistantThinking(true);

    try {
      const res = await fetch(`${API_BASE}/api/chatbot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: queryText,
          session_id: activeChatId,
          user_id: 1,
          profile: profile
        })
      });

      if (res.ok) {
        const data = await res.json();
        appendChatMessage(activeChatId, 'assistant', data.answer);
        speakNarrative(data.answer);
      } else {
        throw new Error();
      }
    } catch (err) {
      console.warn(err);
      appendChatMessage(activeChatId, 'assistant', "I am currently disconnected from the central server. Please try again shortly.");
    } finally {
      setIsAssistantThinking(false);
    }
  };

  const handleChatDocUpload = (docName) => {
    setShowAttachmentMenu(false);
    appendChatMessage(activeChatId, 'user', `Attached document: ${docName}.pdf`);
    setIsAssistantThinking(true);

    setTimeout(() => {
      handleDocUpload(docName);
      const reply = `✓ ${docName} uploaded and verified successfully! Your verification readiness score has increased.`;
      appendChatMessage(activeChatId, 'assistant', reply);
      setIsAssistantThinking(false);
      speakNarrative(reply);
    }, 1500);
  };

  // Voice speech synthesis toggle text-to-speech for chatbot bubbles
  const [activeSpeechText, setActiveSpeechText] = useState('');
  const textToSpeech = (text) => {
    const synth = window.speechSynthesis;
    if (!synth) return;
    
    if (speechPlaying && activeSpeechText === text) {
      synth.cancel();
      setSpeechPlaying(false);
      setActiveSpeechText('');
      return;
    }

    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    if (text.includes('Namaste') || language === 'Hindi') {
      utterance.lang = 'hi-IN';
    } else {
      utterance.lang = 'en-IN';
    }
    
    utterance.onend = () => {
      setSpeechPlaying(false);
      setActiveSpeechText('');
    };
    setSpeechPlaying(true);
    setActiveSpeechText(text);
    synth.speak(utterance);
  };

  return (
    <div className={`${activeTab === 'government-scheme-agent' ? 'h-screen overflow-hidden' : 'min-h-screen'} font-sans antialiased bg-gov-bg text-gov-text transition-colors duration-200 flex flex-col`}>
      
      {/* 1. ACCESSIBILITY BAR & GOVT HEADER */}
      <div className="bg-slate-900 text-slate-100 text-xs py-2 px-4 flex flex-wrap justify-between items-center border-b border-slate-800 gap-2 shrink-0">
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 rounded-full bg-amber-500 text-slate-900 font-bold flex items-center justify-center text-[10px]">
            🇮🇳
          </div>
          <span className="font-semibold">Government of India Portal</span>
        </div>
        
        {/* Settings Panel */}
        <div className="flex items-center flex-wrap gap-4">
          {/* Multi-language Selector */}
          <div className="flex items-center space-x-1.5">
            <Languages className="w-3.5 h-3.5 text-amber-400" />
            <select
              value={language}
              onChange={(e) => {
                setLanguage(e.target.value);
                speakNarrative(e.target.value === 'Hindi' ? "भाषा हिंदी में बदल गई है" : "Language changed to English");
              }}
              className="bg-slate-800 text-slate-100 border border-slate-700 rounded px-1.5 py-0.5 focus:outline-none focus:border-amber-400 text-[11px]"
            >
              <option>English</option>
              <option>Hindi</option>
            </select>
          </div>

          {/* Font Size Toggles */}
          <div className="flex items-center bg-slate-800 rounded p-0.5 border border-slate-700">
            <button
              onClick={() => { setFontSize('normal'); speakNarrative("Font size set to normal"); }}
              className={`px-2 py-0.5 rounded text-[10px] font-bold ${fontSize === 'normal' ? 'bg-amber-400 text-slate-900' : 'hover:bg-slate-700'}`}
            >
              A
            </button>
            <button
              onClick={() => { setFontSize('large'); speakNarrative("Font size set to large"); }}
              className={`px-2 py-0.5 rounded text-[10px] font-bold ${fontSize === 'large' ? 'bg-amber-400 text-slate-900' : 'hover:bg-slate-700'}`}
            >
              A+
            </button>
            <button
              onClick={() => { setFontSize('xlarge'); speakNarrative("Font size set to extra large"); }}
              className={`px-2 py-0.5 rounded text-[10px] font-bold ${fontSize === 'xlarge' ? 'bg-amber-400 text-slate-900' : 'hover:bg-slate-700'}`}
            >
              A++
            </button>
          </div>

          {/* Voice Guidance Toggle */}
          <button
            onClick={handleVoiceNavToggle}
            className={`flex items-center space-x-1 px-2.5 py-0.5 rounded border transition-colors ${isVoiceNavEnabled ? 'bg-amber-400 text-slate-900 border-amber-500' : 'border-slate-700 bg-slate-800 text-slate-300 hover:text-slate-100'}`}
          >
            <Accessibility className="w-3.5 h-3.5" />
            <span className="text-[10px] font-semibold">Voice Guidance</span>
          </button>

          {/* High Contrast Mode Toggle */}
          <button
            onClick={() => {
              const hs = !isHighContrast;
              setIsHighContrast(hs);
              speakNarrative(hs ? "High Contrast Mode enabled" : "High Contrast Mode disabled");
            }}
            className={`flex items-center space-x-1 px-2.5 py-0.5 rounded border transition-colors ${isHighContrast ? 'bg-yellow-400 text-slate-900 border-yellow-500' : 'border-slate-700 bg-slate-800 text-slate-300 hover:text-slate-100'}`}
          >
            <Flame className="w-3.5 h-3.5" />
            <span className="text-[10px] font-semibold">High Contrast</span>
          </button>

          {/* Dark Mode Toggle */}
          <button
            onClick={() => {
              const dm = !isDarkMode;
              setIsDarkMode(dm);
              speakNarrative(dm ? "Night mode enabled" : "Day light mode enabled");
            }}
            className="p-1 rounded-full bg-slate-800 text-slate-300 hover:text-slate-100 hover:bg-slate-700 focus:outline-none border border-slate-700 cursor-pointer"
          >
            {isDarkMode ? <Sun className="w-3.5 h-3.5 text-amber-400" /> : <Moon className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Main App Header */}
      <header className="bg-gov-card border-b border-gov-border shadow-sm sticky top-0 z-40 transition-colors duration-200 shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-11 h-11 bg-primary/10 text-primary border border-primary/20 rounded-xl flex items-center justify-center font-bold text-lg shadow-inner">
              🏛️
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-primary flex items-center gap-1.5 tracking-tight">
                AI Welfare Navigator
              </h1>
              <p className="text-[10px] text-gov-subtext font-semibold uppercase tracking-wider">
                India Citizen Welfare Operating System
              </p>
            </div>
          </div>

          {/* Navigation Controls */}
          <nav className="flex space-x-2 bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
            <button
              onClick={() => {
                setActiveTab('citizen');
                speakNarrative("Switched to Citizen Portal");
              }}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center space-x-1.5 ${
                activeTab === 'citizen' ? 'bg-primary text-white shadow-sm' : 'text-gov-subtext hover:text-gov-text'
              }`}
            >
              <User className="w-3.5 h-3.5" />
              <span>Citizen Portal</span>
            </button>
            
            <button
              onClick={() => {
                setActiveTab('ngo');
                speakNarrative("Switched to NGO Assistance Desk");
              }}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center space-x-1.5 ${
                activeTab === 'ngo' ? 'bg-primary text-white shadow-sm' : 'text-gov-subtext hover:text-gov-text'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              <span>NGO Assistance</span>
            </button>

            <button
              onClick={() => {
                setActiveTab('admin');
                speakNarrative("Switched to Administrative Management");
              }}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center space-x-1.5 ${
                activeTab === 'admin' ? 'bg-primary text-white shadow-sm' : 'text-gov-subtext hover:text-gov-text'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Admin Management</span>
            </button>

            <button
              onClick={() => {
                setActiveTab('government-scheme-agent');
                setActiveChatId('agent');
                speakNarrative("Switched to WhatsApp Eligibility Assistant");
              }}
              className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center space-x-1.5 ${
                activeTab === 'government-scheme-agent' ? 'bg-primary text-white shadow-sm' : 'text-gov-subtext hover:text-gov-text'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>WhatsApp AI Agent</span>
            </button>
          </nav>

          <div className="hidden md:flex items-center space-x-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-3 py-1 rounded-full text-xs font-bold border border-emerald-500/20">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>NIC Secure APIs</span>
          </div>
        </div>
      </header>

      {/* SUCCESS POPUP */}
      {applicationStatusMsg && (
        <div className="mx-auto mt-4 max-w-7xl px-4 w-full">
          <div className="bg-emerald-50 dark:bg-emerald-950/20 border-2 border-emerald-500 text-emerald-800 dark:text-emerald-400 p-4 rounded-2xl flex items-center space-x-3 shadow-md animate-float">
            <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center font-bold text-lg">✓</div>
            <div>
              <h4 className="font-bold text-sm">Application Submitted Successfully!</h4>
              <p className="text-xs">Your request for <span className="font-bold">{applicationStatusMsg}</span> has been logged to verification services.</p>
            </div>
          </div>
        </div>
      )}

      {/* MAIN VIEW CONTROLLER */}
      {activeTab === 'government-scheme-agent' ? (
        // DEDICATED WHATSAPP CHAT PAGE
        <div className="flex flex-1 min-h-0 border-t border-gov-border bg-gov-card overflow-hidden">
          {/* Sidebar */}
          <div className={`${activeChatId ? 'hidden md:flex' : 'flex'} w-full md:w-[30%] flex-col border-r border-gov-border bg-gov-card shrink-0`}>
            <div className="p-4 border-b border-gov-border space-y-3 shrink-0 bg-gov-bg/30">
              <div className="flex items-center justify-between">
                <span className="font-extrabold text-xs text-gov-text uppercase tracking-wider">Helper Agents</span>
                <span className="bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded text-[9px] font-bold">WhatsApp Web</span>
              </div>
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-gov-subtext absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search agents..."
                  value={chatSearchQuery}
                  onChange={(e) => setChatSearchQuery(e.target.value)}
                  className="w-full bg-gov-bg border border-gov-border rounded-xl pl-9 pr-4 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto divide-y divide-gov-border">
              {Object.keys(conversations)
                .filter(id => conversations[id].name.toLowerCase().includes(chatSearchQuery.toLowerCase()))
                .map(id => {
                  const chat = conversations[id];
                  const lastMessage = chat.messages[chat.messages.length - 1];
                  return (
                    <button
                      key={id}
                      onClick={() => {
                        setActiveChatId(id);
                        speakNarrative(`Chat with ${chat.name}`);
                      }}
                      className={`w-full p-4 flex items-start space-x-3 text-left transition-colors cursor-pointer ${
                        activeChatId === id ? 'bg-primary/5 border-l-4 border-l-primary' : 'hover:bg-gov-bg/40'
                      }`}
                    >
                      <div className="w-10 h-10 rounded-full bg-primary/10 text-primary border border-primary/20 flex items-center justify-center text-lg shrink-0">
                        {chat.avatar}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-baseline">
                          <h4 className="font-bold text-xs text-gov-text truncate flex items-center gap-1">
                            {chat.name}
                            {chat.verified && <span className="text-[10px] text-primary" title="Verified Agent">✓</span>}
                          </h4>
                          <span className="text-[9px] text-gov-subtext shrink-0">{lastMessage ? lastMessage.time : 'Just now'}</span>
                        </div>
                        <p className="text-[11px] text-gov-subtext truncate mt-1">
                          {lastMessage ? lastMessage.text : chat.subtitle}
                        </p>
                      </div>
                    </button>
                  );
                })}
            </div>
          </div>

          {/* Main Chat Pane */}
          <div className={`${activeChatId ? 'flex' : 'hidden md:flex'} flex-1 flex-col h-full bg-gov-bg relative overflow-hidden`}>
            {activeChatId ? (
              <>
                {/* Chat Header */}
                <div className="px-4 py-3 border-b border-gov-border bg-gov-card flex justify-between items-center shrink-0 shadow-sm relative z-10">
                  <div className="flex items-center space-x-3">
                    <button onClick={() => setActiveChatId(null)} className="p-1 text-gov-subtext hover:text-gov-text md:hidden rounded-lg hover:bg-gov-bg border border-gov-border mr-1">
                      <ArrowLeft className="w-4 h-4" />
                    </button>
                    <div className="w-10 h-10 rounded-full bg-primary/10 text-primary border border-primary/20 flex items-center justify-center text-lg">
                      {conversations[activeChatId].avatar}
                    </div>
                    <div>
                      <h4 className="font-bold text-xs text-gov-text flex items-center gap-1">
                        {conversations[activeChatId].name}
                        <span className="text-primary text-[10px]">✓</span>
                      </h4>
                      <span className="text-[9px] text-emerald-500 font-bold block">{conversations[activeChatId].status}</span>
                    </div>
                  </div>
                </div>

                {/* Messages Body */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4 whatsapp-bg" ref={chatScrollRef}>
                  {conversations[activeChatId].messages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-xs shadow-sm border ${
                        msg.role === 'user'
                          ? 'bg-primary text-white border-primary rounded-tr-none'
                          : 'bg-gov-card text-gov-text border-gov-border rounded-tl-none'
                      }`}>
                        <div className="whitespace-pre-line leading-relaxed font-sans">{msg.text}</div>
                        <div className="flex items-center justify-between gap-4 mt-2.5 pt-1 border-t border-gov-border/40 select-none">
                          <span className="text-[8px] text-gov-subtext">{msg.time}</span>
                          <div className="flex items-center space-x-1 text-gov-subtext">
                            {msg.role === 'assistant' && (
                              <button onClick={() => textToSpeech(msg.text)} className="p-0.5 text-primary hover:text-primary/90 flex items-center gap-1 cursor-pointer font-bold text-[9px] mr-1">
                                {speechPlaying && activeSpeechText === msg.text ? <VolumeX className="w-3 h-3 text-red-500 animate-pulse" /> : <Volume2 className="w-3 h-3" />}
                              </button>
                            )}
                            {msg.role === 'user' && <CheckCheck className="w-3.5 h-3.5 text-primary" />}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}

                  {isAssistantThinking && (
                    <div className="flex justify-start">
                      <div className="bg-gov-card border border-gov-border rounded-2xl px-4 py-3 rounded-bl-none text-xs text-gov-subtext animate-pulse">
                        Welfare twin reasoning... 🧠
                      </div>
                    </div>
                  )}
                </div>

                {/* Attachment Menu */}
                {showAttachmentMenu && (
                  <div className="absolute bottom-16 left-6 bg-gov-card border border-gov-border rounded-2xl shadow-xl p-3 space-y-1.5 z-20 w-52 text-xs">
                    <span className="block text-[9px] uppercase tracking-wider font-bold text-gov-subtext px-2 mb-1">Attach Doc:</span>
                    {uploadedDocs.map(doc => (
                      <button
                        key={doc}
                        onClick={() => handleChatDocUpload(doc)}
                        className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-primary/5 hover:text-primary flex items-center space-x-2 cursor-pointer text-[11px]"
                      >
                        <File className="w-3.5 h-3.5 text-gov-subtext" />
                        <span>{doc}</span>
                      </button>
                    ))}
                  </div>
                )}

                {/* Footer Input Bar */}
                <div className="p-3 border-t border-gov-border bg-gov-card flex items-center space-x-2 shrink-0">
                  <button
                    onClick={() => setShowAttachmentMenu(!showAttachmentMenu)}
                    className={`p-2.5 rounded-xl border transition-all cursor-pointer ${showAttachmentMenu ? 'bg-primary/10 text-primary border-primary/20' : 'bg-gov-bg border-gov-border text-gov-subtext hover:text-gov-text'}`}
                  >
                    <Paperclip className="w-4.5 h-4.5" />
                  </button>

                  <button
                    onClick={toggleListening}
                    className={`p-2.5 rounded-xl transition-all border cursor-pointer ${isListening ? 'bg-red-500 text-white border-red-600 animate-pulse' : 'bg-gov-bg border-gov-border text-gov-subtext hover:text-gov-text'}`}
                  >
                    {isListening ? <MicOff className="w-4.5 h-4.5" /> : <Mic className="w-4.5 h-4.5" />}
                  </button>

                  <input
                    type="text"
                    placeholder="Type your welfare query..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAssistantChat()}
                    className="flex-1 bg-gov-bg border border-gov-border rounded-xl px-4 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  />

                  <button
                    onClick={() => handleAssistantChat()}
                    className="bg-primary hover:bg-primary/95 text-white p-2.5 rounded-xl shadow-sm cursor-pointer"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center text-gov-subtext space-y-4">
                <div className="text-6xl">🏛️</div>
                <h3 className="text-lg font-bold text-gov-text">AI Welfare Twin Console</h3>
                <p className="max-w-md text-xs">Select a specialized helper agent from the sidebar list to explain, recommend, and apply for government welfare schemes.</p>
              </div>
            )}
          </div>
        </div>
      ) : activeTab === 'citizen' ? (
        // CITIZEN PORTAL DASHBOARD
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 space-y-8 animate-float">
          {/* Hero Welcome & Profile Status */}
          <section className="bg-gradient-to-br from-primary/10 via-gov-card to-gov-card border border-gov-border rounded-3xl p-6 md:p-8 flex flex-col md:flex-row justify-between items-center gap-6 relative overflow-hidden">
            <div className="space-y-4 text-center md:text-left flex-1">
              <span className="bg-primary/10 text-primary border border-primary/20 text-[10px] font-bold uppercase tracking-wider px-3 py-1 rounded-full">
                🇮🇳 Digital Welfare Mission
              </span>
              <h2 className="text-2xl md:text-3xl font-extrabold text-gov-text leading-tight">
                Good Morning, {profile.name} 👋
              </h2>
              <p className="text-sm text-gov-subtext">
                Welcome to your Welfare Assistant. Currently showing eligible student schemes in {profile.state}.
              </p>
              <div className="flex flex-wrap gap-2.5 pt-2 justify-center md:justify-start">
                <button
                  onClick={() => setShowProfileModal(true)}
                  className="bg-primary hover:bg-primary/95 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow-sm cursor-pointer"
                >
                  Edit Profile Wizard
                </button>
                <button
                  onClick={() => {
                    setActiveTab('government-scheme-agent');
                    setActiveChatId('agent');
                  }}
                  className="bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold text-xs px-4 py-2.5 rounded-xl shadow-sm cursor-pointer"
                >
                  Consult AI Agent
                </button>
              </div>
            </div>

            {/* Profile Completion Circle */}
            <div className="bg-gov-card border border-gov-border p-5 rounded-2xl flex flex-col items-center justify-center shadow-sm w-44 h-44 relative shrink-0">
              <div className="relative flex items-center justify-center">
                {/* Circular Gauge */}
                <svg className="w-24 h-24 transform -rotate-90">
                  <circle cx="48" cy="48" r="40" stroke="var(--color-gov-border)" strokeWidth="6" fill="transparent" className="opacity-20" />
                  <circle
                    cx="48"
                    cy="48"
                    r="40"
                    stroke="var(--color-secondary)"
                    strokeWidth="6"
                    fill="transparent"
                    strokeDasharray={2 * Math.PI * 40}
                    strokeDashoffset={2 * Math.PI * 40 * (1 - (docCheckResult?.readiness_score || 80) / 100)}
                    className="transition-all duration-700 ease-out"
                  />
                </svg>
                <div className="absolute text-center">
                  <span className="text-xl font-black text-gov-text">{docCheckResult?.readiness_score || 80}%</span>
                </div>
              </div>
              <span className="text-[11px] font-bold text-gov-text mt-3 text-center">Readiness Vault Score</span>
            </div>
          </section>

          {/* ADVANCED ANALYTICS DASHBOARD SECTION */}
          {dashboardAnalytics && (
            <section className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-6">
              <div>
                <h3 className="text-lg font-bold text-gov-text flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-primary" />
                  Welfare Analytics & Target Metrics
                </h3>
                <p className="text-xs text-gov-subtext">Aggregated tracking of benefits matching your profile parameters.</p>
              </div>

              {/* 4 Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gov-bg border border-gov-border p-4 rounded-2xl flex flex-col justify-between h-28">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase">Total Schemes in DB</span>
                  <span className="text-3xl font-black text-primary">{dashboardAnalytics.metrics.total_schemes}</span>
                  <span className="text-[9px] text-gov-subtext">Verified database records</span>
                </div>

                <div className="bg-gov-bg border border-gov-border p-4 rounded-2xl flex flex-col justify-between h-28">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase">Eligible Schemes</span>
                  <span className="text-3xl font-black text-emerald-600 dark:text-emerald-400">{dashboardAnalytics.metrics.eligible_schemes}</span>
                  <span className="text-[9px] text-gov-subtext">Direct profile match</span>
                </div>

                <div className="bg-gov-bg border border-gov-border p-4 rounded-2xl flex flex-col justify-between h-28">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase">Active Applications</span>
                  <span className="text-3xl font-black text-secondary">{dashboardAnalytics.metrics.applied_schemes}</span>
                  <span className="text-[9px] text-gov-subtext">Submitted status tracking</span>
                </div>

                <div className="bg-gov-bg border border-gov-border p-4 rounded-2xl flex flex-col justify-between h-28">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase">NGO Requests</span>
                  <span className="text-3xl font-black text-amber-500">{dashboardAnalytics.metrics.ngo_requests}</span>
                  <span className="text-[9px] text-gov-subtext">Active assistance needs</span>
                </div>
              </div>

              {/* Charts Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 pt-4 border-t border-gov-border">
                {/* Chart 1: Category Distribution */}
                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase tracking-wider block">Category Distribution</span>
                  <div className="h-44 flex flex-col justify-end space-y-2 border-l border-b border-gov-border p-2 bg-gov-bg/30 rounded-xl">
                    {Object.keys(dashboardAnalytics.charts.category_distribution).slice(0, 5).map((cat, idx) => {
                      const count = dashboardAnalytics.charts.category_distribution[cat];
                      const pct = Math.min(100, Math.max(10, (count / 20) * 100));
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-[9px] text-gov-subtext font-semibold">
                            <span className="truncate max-w-[80%]">{cat}</span>
                            <span>{count}</span>
                          </div>
                          <div className="w-full bg-gov-border h-2 rounded-full overflow-hidden">
                            <div className="bg-primary h-full" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Chart 2: Eligibility Breakdown */}
                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase tracking-wider block">Eligibility Breakdown</span>
                  <div className="h-44 flex flex-col justify-center space-y-2 bg-gov-bg/30 rounded-xl p-3 border border-gov-border">
                    {Object.keys(dashboardAnalytics.charts.eligibility_breakdown).map((tier, idx) => {
                      const count = dashboardAnalytics.charts.eligibility_breakdown[tier];
                      const colors = [
                        "bg-emerald-500 text-emerald-600",
                        "bg-teal-500 text-teal-600",
                        "bg-amber-500 text-amber-600",
                        "bg-slate-400 text-slate-500"
                      ];
                      return (
                        <div key={idx} className="flex justify-between items-center text-[10px]">
                          <span className="truncate max-w-[70%]">{tier}</span>
                          <span className={`px-2 py-0.5 rounded-full font-bold bg-opacity-10 ${colors[idx % 4]}`}>{count}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Chart 3: State Coverage */}
                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase tracking-wider block">State Coverage</span>
                  <div className="h-44 flex flex-col justify-end space-y-2 border-l border-b border-gov-border p-2 bg-gov-bg/30 rounded-xl">
                    {Object.keys(dashboardAnalytics.charts.state_coverage).slice(0, 5).map((st, idx) => {
                      const count = dashboardAnalytics.charts.state_coverage[st];
                      const pct = Math.min(100, Math.max(10, (count / 100) * 100));
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex justify-between text-[9px] text-gov-subtext font-semibold">
                            <span>{st}</span>
                            <span>{count}</span>
                          </div>
                          <div className="w-full bg-gov-border h-2 rounded-full overflow-hidden">
                            <div className="bg-secondary h-full" style={{ width: `${pct}%` }}></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Chart 4: Success Rate */}
                <div className="space-y-3">
                  <span className="text-[10px] font-bold text-gov-subtext uppercase tracking-wider block">Application Success Rate</span>
                  <div className="h-44 flex flex-col items-center justify-center bg-gov-bg/30 rounded-xl p-3 border border-gov-border text-center">
                    <div className="relative w-24 h-24 flex items-center justify-center mb-1">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle cx="48" cy="48" r="38" stroke="var(--color-gov-border)" strokeWidth="6" fill="transparent" className="opacity-20" />
                        <circle
                          cx="48"
                          cy="48"
                          r="38"
                          stroke="var(--color-success)"
                          strokeWidth="6"
                          fill="transparent"
                          strokeDasharray={2 * Math.PI * 38}
                          strokeDashoffset={2 * Math.PI * 38 * (1 - dashboardAnalytics.charts.application_success_rate / 100)}
                        />
                      </svg>
                      <span className="absolute font-black text-lg text-emerald-600">{dashboardAnalytics.charts.application_success_rate}%</span>
                    </div>
                    <span className="text-[10px] text-gov-subtext font-semibold">Approved Applications Ratio</span>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Core Citizen Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Left 3 Cols: Schemes & Docs */}
            <div className="lg:col-span-3 space-y-8">
              
              {/* SCHEME RECOMMENDER WITH PAGINATION */}
              <section className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div>
                    <h3 className="text-lg font-bold text-gov-text flex items-center gap-2">
                      <Award className="w-5 h-5 text-primary" />
                      Welfare Schemes Directory & Recommendation Engine
                    </h3>
                    <p className="text-xs text-gov-subtext">Showing {schemesList.length} of {totalSchemesInDB} matching schemes.</p>
                  </div>

                  {/* Inline filters */}
                  <div className="flex flex-wrap gap-2.5 w-full md:w-auto">
                    <input
                      type="text"
                      placeholder="Keyword search..."
                      value={schemeSearch}
                      onChange={(e) => { setSchemeSearch(e.target.value); setSchemesPage(1); }}
                      className="bg-gov-bg border border-gov-border rounded-xl px-3 py-1.5 text-xs text-gov-text focus:outline-none focus:border-primary flex-1 md:w-44"
                    />
                    <select
                      value={schemeCategoryFilter}
                      onChange={(e) => { setSchemeCategoryFilter(e.target.value); setSchemesPage(1); }}
                      className="bg-gov-bg border border-gov-border rounded-xl px-2 py-1.5 text-[11px] text-gov-text focus:outline-none focus:border-primary"
                    >
                      <option value="All">All Categories</option>
                      {CATEGORIES_LIST.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                    <select
                      value={schemeStateFilter}
                      onChange={(e) => { setSchemeStateFilter(e.target.value); setSchemesPage(1); }}
                      className="bg-gov-bg border border-gov-border rounded-xl px-2 py-1.5 text-[11px] text-gov-text focus:outline-none focus:border-primary"
                    >
                      <option value="All">All States / UTs</option>
                      {ALL_LOCATIONS.slice(1).map(st => (
                        <option key={st} value={st}>{st}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {schemesList.map((scheme, idx) => {
                    // Check local matching from evaluationResult
                    const matchedEval = evaluationResult?.eligible_schemes?.find(s => s.id === scheme.id) ||
                                       evaluationResult?.ineligible_schemes?.find(s => s.id === scheme.id);
                    
                    const score = matchedEval ? matchedEval.eligibility_score : 50;
                    const isElig = matchedEval ? matchedEval.is_eligible : false;
                    const tier = matchedEval ? matchedEval.eligibility_tier : "Check Manually";

                    return (
                      <div key={idx} className="bg-gov-bg border border-gov-border rounded-2xl p-5 flex flex-col justify-between space-y-4 welfare-card relative">
                        <div className="flex justify-between items-start">
                          <span className="bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded-full text-[9px] font-bold truncate max-w-[50%]">
                            {scheme.category}
                          </span>
                          <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                            score >= 90 ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20' :
                            score >= 70 ? 'bg-teal-500/10 text-teal-600 border-teal-500/20' :
                            score >= 50 ? 'bg-amber-500/10 text-amber-600 border-amber-500/20' :
                            'bg-slate-500/10 text-slate-500 border-slate-500/20'
                          }`}>
                            {score}% Eligible
                          </span>
                        </div>

                        <div>
                          <h4 className="text-sm font-bold text-gov-text line-clamp-1">{scheme.scheme_name}</h4>
                          <p className="text-[10px] text-gov-subtext block font-semibold mt-0.5">{scheme.ministry} | {scheme.state_availability}</p>
                          <p className="text-xs text-gov-subtext mt-2 line-clamp-2">{scheme.description}</p>
                        </div>

                        {/* Rationale reason box */}
                        <div className="bg-gov-card border border-gov-border rounded-xl p-2.5 text-[10px] text-gov-subtext">
                          <span className="font-bold text-gov-text block text-[9px] uppercase tracking-wider mb-0.5">Evaluation Match Details</span>
                          {matchedEval ? (
                            <p className="line-clamp-2">{[...matchedEval.reasons_eligible, ...matchedEval.reasons_ineligible].join(" • ")}</p>
                          ) : (
                            <p>Verify parameters: Domicile, Age, Income, Caste.</p>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="border-t border-gov-border pt-4 mt-2 flex justify-between items-center text-xs">
                          <div>
                            <span className="text-[9px] text-gov-subtext block uppercase tracking-wide">Potential Benefit</span>
                            <span className="text-emerald-600 dark:text-emerald-400 font-extrabold text-xs">{scheme.benefits}</span>
                          </div>
                          
                          <div className="flex space-x-2">
                            <button
                              onClick={() => {
                                setSelectedSchemeForChat(scheme.scheme_name);
                                setActiveTab('government-scheme-agent');
                                setActiveChatId('agent');
                              }}
                              className="text-[10px] font-bold text-primary bg-primary/10 border border-primary/20 px-2 py-1 rounded-lg hover:bg-primary/20 transition-all cursor-pointer"
                            >
                              Rules
                            </button>
                            <button
                              onClick={() => triggerApplyScheme(scheme.scheme_name, scheme.id)}
                              className="text-[10px] font-bold text-white bg-primary px-3 py-1.5 rounded-lg shadow-sm hover:bg-primary/95 transition-all cursor-pointer"
                            >
                              Apply
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Pagination Controls */}
                <div className="flex justify-between items-center pt-4 border-t border-gov-border text-xs text-gov-subtext select-none">
                  <span>Showing page {schemesPage} of {Math.max(1, Math.ceil(totalSchemesInDB / 10))}</span>
                  <div className="flex space-x-1">
                    <button
                      onClick={() => setSchemesPage(prev => Math.max(1, prev - 1))}
                      disabled={schemesPage === 1}
                      className="bg-gov-bg border border-gov-border px-3 py-1.5 rounded-lg font-bold hover:bg-gov-card disabled:opacity-50 cursor-pointer"
                    >
                      Prev
                    </button>
                    <button
                      onClick={() => setSchemesPage(prev => Math.min(Math.ceil(totalSchemesInDB / 10), prev + 1))}
                      disabled={schemesPage >= Math.ceil(totalSchemesInDB / 10)}
                      className="bg-gov-bg border border-gov-border px-3 py-1.5 rounded-lg font-bold hover:bg-gov-card disabled:opacity-50 cursor-pointer"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </section>

              {/* DOCUMENT VAULT */}
              <section className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-gov-text flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    Smart Document Vault Cabinet
                  </h3>
                  <p className="text-xs text-gov-subtext">Directly integrated with Digilocker. Upload certificates to satisfy verification checks.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Verified Docs */}
                  <div className="space-y-3">
                    <h5 className="text-[10px] font-bold text-gov-subtext uppercase tracking-wider">Verified Documents</h5>
                    <div className="space-y-2.5">
                      {uploadedDocs.map(doc => (
                        <div key={doc} className="bg-gov-bg border border-gov-border rounded-2xl p-4 flex items-center justify-between shadow-sm relative group hover:border-emerald-500/40">
                          <div className="flex items-center space-x-3">
                            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center font-bold">📄</div>
                            <div>
                              <h5 className="font-bold text-xs text-gov-text">{doc}</h5>
                              <span className="text-[9px] text-emerald-600 font-semibold bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full mt-1 inline-block">Verified ✓</span>
                            </div>
                          </div>
                          <button onClick={() => handleDocDelete(doc)} className="p-1.5 text-red-500 hover:text-red-600 rounded-lg bg-gov-card border border-gov-border">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Missing/Required Docs */}
                  <div className="space-y-3">
                    <h5 className="text-[10px] font-bold text-gov-subtext uppercase tracking-wider">Missing Required Certificates</h5>
                    <div className="space-y-2.5">
                      {docCheckResult?.missing_documents?.map(doc => (
                        <div key={doc} className="bg-gov-bg border border-dashed border-gov-border rounded-2xl p-4 flex items-center justify-between shadow-sm hover:border-primary/50">
                          <div className="flex items-center space-x-3">
                            <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center font-bold">⚠</div>
                            <div>
                              <h5 className="font-bold text-xs text-gov-text">{doc}</h5>
                              <span className="text-[9px] text-amber-600 font-semibold bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full mt-1 inline-block">Upload Pending</span>
                            </div>
                          </div>
                          <button onClick={() => handleDocUpload(doc)} className="bg-primary text-white font-bold text-[10px] px-3 py-1.5 rounded-xl cursor-pointer">
                            Upload Now
                          </button>
                        </div>
                      ))}
                      {docCheckResult?.missing_documents?.length === 0 && (
                        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl text-xs text-emerald-800 dark:text-emerald-400">
                          ✓ All key documents verified. Ready to apply!
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </section>

              {/* LIFE CYCLE PREDICTIONS ROADMAP */}
              <section className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-gov-text flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-primary" />
                    Life Cycle Milestones Predictions
                  </h3>
                  <p className="text-xs text-gov-subtext">Upcoming life transitions and future scheme notifications.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {predictions.map((p, idx) => (
                    <div key={idx} className="bg-gov-bg border border-gov-border rounded-2xl p-4 flex flex-col justify-between welfare-card relative">
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-xl">{p.icon}</span>
                          <span className="text-[9px] bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded-full font-bold">{p.timeline}</span>
                        </div>
                        <h5 className="font-extrabold text-xs text-gov-text">{p.event}</h5>
                        <p className="text-[10px] text-gov-subtext leading-relaxed">{p.description}</p>
                      </div>
                      <div className="border-t border-gov-border pt-3 mt-3">
                        <span className="text-[8px] text-gov-subtext block uppercase tracking-wide">Predicted Program</span>
                        <span className="text-[9px] font-bold text-primary line-clamp-1">{p.scheme}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

            </div>

            {/* Right Sidebar: Scam Scanner, RAG PDF Chat, NGO Submission */}
            <div className="lg:col-span-1 space-y-8 animate-float">
              
              {/* RAG PDF GUIDELINES CHAT */}
              <section className="bg-gov-card border border-gov-border rounded-3xl p-5 shadow-sm space-y-3">
                <h4 className="text-xs font-bold text-gov-text flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-primary" />
                  RAG Guideline Chat
                </h4>
                <p className="text-[9px] text-gov-subtext">Ask specific queries regarding a selected scheme's rules PDF.</p>
                <select
                  value={selectedSchemeForChat}
                  onChange={(e) => setSelectedSchemeForChat(e.target.value)}
                  className="w-full bg-gov-bg border border-gov-border rounded-xl px-2.5 py-1.5 text-[10px] text-gov-text focus:outline-none focus:border-primary"
                >
                  {schemesList.slice(0, 5).map(s => (
                    <option key={s.scheme_name} value={s.scheme_name}>{s.scheme_name}</option>
                  ))}
                </select>
                <div className="border border-gov-border rounded-xl h-36 overflow-y-auto p-3 bg-gov-bg mb-2 space-y-2.5">
                  {ragHistory.map((item, idx) => (
                    <div key={idx} className="text-[9px]">
                      <span className={`font-bold block ${item.role === 'user' ? 'text-primary' : 'text-secondary'}`}>
                        {item.role === 'user' ? 'Rahul' : 'Official Guidelines'}
                      </span>
                      <p className="text-gov-text mt-0.5 leading-relaxed">{item.text}</p>
                    </div>
                  ))}
                  {isRagLoading && <div className="text-[9px] text-gov-subtext italic animate-pulse">Scanning guidelines...</div>}
                </div>
                <div className="flex space-x-1">
                  <input
                    type="text"
                    placeholder="Ask rules..."
                    value={ragQuery}
                    onChange={(e) => setRagQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && submitRagQuery()}
                    className="flex-1 bg-gov-bg border border-gov-border rounded-xl px-2.5 py-1.5 text-[9px] text-gov-text focus:outline-none focus:border-primary"
                  />
                  <button onClick={submitRagQuery} className="bg-primary text-white px-2.5 py-1.5 rounded-xl text-[9px] font-bold cursor-pointer">
                    Query
                  </button>
                </div>
              </section>

              {/* SCAM SCANNER */}
              <section className="bg-gov-card border border-gov-border rounded-3xl p-5 shadow-sm space-y-3">
                <h4 className="text-xs font-bold text-gov-text flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-red-500" />
                  Scam link Scanner
                </h4>
                <p className="text-[9px] text-gov-subtext">Verify SMS texts or link legitimacy.</p>
                <textarea
                  placeholder="Paste URL (e.g. http://pm-kisan-fee.com)..."
                  value={fraudInput}
                  onChange={(e) => setFraudInput(e.target.value)}
                  className="w-full h-14 bg-gov-bg border border-gov-border rounded-xl p-2 text-[10px] focus:outline-none focus:border-red-400 text-gov-text resize-none"
                />
                <button
                  onClick={scanFraud}
                  disabled={isCheckingFraud}
                  className="w-full bg-red-500/10 hover:bg-red-500/20 text-red-600 dark:text-red-400 border border-red-500/20 py-2 rounded-xl text-[10px] font-bold cursor-pointer"
                >
                  {isCheckingFraud ? 'Scanning...' : 'Verify Link'}
                </button>
                {fraudResult && (
                  <div className={`p-2.5 rounded-xl border text-[9px] space-y-1 ${
                    fraudResult.safety_rating === 'Dangerous' ? 'bg-red-500/10 border-red-500/20 text-red-800 dark:text-red-400' : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-800 dark:text-emerald-400'
                  }`}>
                    <div className="font-extrabold">{fraudResult.alert_title}</div>
                    <p className="leading-relaxed text-gov-subtext">{fraudResult.explanation}</p>
                  </div>
                )}
              </section>

            </div>
          </div>
        </main>
      ) : activeTab === 'ngo' ? (
        // NGO MODULE PORTAL
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 space-y-8 animate-float">
          {/* Sub Navigation */}
          <div className="flex space-x-4 border-b border-gov-border pb-3 justify-between items-center">
            <div className="flex space-x-2">
              <button
                onClick={() => { setActiveNgoTab('directory'); fetchNgos(); }}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeNgoTab === 'directory' ? 'bg-primary text-white shadow-sm' : 'bg-gov-card border border-gov-border text-gov-subtext'
                }`}
              >
                NGO Directory
              </button>
              <button
                onClick={() => { setActiveNgoTab('tracking'); fetchCitizenNgoRequests(); }}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeNgoTab === 'tracking' ? 'bg-primary text-white shadow-sm' : 'bg-gov-card border border-gov-border text-gov-subtext'
                }`}
              >
                Track Request Status
              </button>
              <button
                onClick={() => { setActiveNgoTab('dashboard'); fetchNgoIncomingRequests(); }}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  activeNgoTab === 'dashboard' ? 'bg-primary text-white shadow-sm' : 'bg-gov-card border border-gov-border text-gov-subtext'
                }`}
              >
                NGO Desk Portal
              </button>
            </div>
            
            {activeNgoTab === 'dashboard' && (
              <div className="flex items-center space-x-2">
                <span className="text-[10px] font-bold text-gov-subtext uppercase">Logged in NGO:</span>
                <select
                  value={selectedNgoId}
                  onChange={(e) => setSelectedNgoId(Number(e.target.value))}
                  className="bg-gov-card border border-gov-border rounded-xl px-2 py-1 text-xs font-bold text-gov-text"
                >
                  <option value={29}>Delhi Welfare Council</option>
                  <option value={14}>Maharashtra Gramin Sahyog</option>
                  <option value={1}>Andhra Rural Dev Foundation</option>
                </select>
              </div>
            )}
          </div>

          {activeNgoTab === 'directory' ? (
            // A. Citizen NGO Directory search
            <div className="space-y-6">
              {/* Filter form */}
              <div className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-4">
                <h4 className="font-extrabold text-sm text-gov-text">Search NGO Assistance Directory</h4>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">State Domicile</label>
                    <select
                      value={ngoSearchState}
                      onChange={(e) => setNgoSearchState(e.target.value)}
                      className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text focus:outline-none"
                    >
                      {ALL_LOCATIONS.map(st => (
                        <option key={st} value={st}>{st}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">District</label>
                    <input
                      type="text"
                      placeholder="e.g. Washim, New Delhi"
                      value={ngoSearchDistrict}
                      onChange={(e) => setNgoSearchDistrict(e.target.value)}
                      className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Service category</label>
                    <select
                      value={ngoSearchService}
                      onChange={(e) => setNgoSearchService(e.target.value)}
                      className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text focus:outline-none"
                    >
                      <option value="All">All Services</option>
                      {NGO_SERVICES.map(srv => (
                        <option key={srv} value={srv}>{srv}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-end">
                    <button
                      onClick={fetchNgos}
                      className="w-full bg-primary hover:bg-primary/95 text-white font-bold text-xs py-2 rounded-xl cursor-pointer"
                    >
                      Search Directory
                    </button>
                  </div>
                </div>

                {/* Specialized Checkboxes */}
                <div className="pt-2 border-t border-gov-border">
                  <span className="block text-[10px] font-bold text-gov-subtext uppercase mb-2">Filter by Specialized Support</span>
                  <div className="flex flex-wrap gap-x-5 gap-y-2">
                    {NGO_SERVICES.map(srv => (
                      <label key={srv} className="inline-flex items-center space-x-2 text-xs cursor-pointer select-none">
                        <input
                          type="checkbox"
                          checked={ngoFilterCheckboxes[srv]}
                          onChange={(e) => {
                            setNgoFilterCheckboxes(prev => ({ ...prev, [srv]: e.target.checked }));
                          }}
                          className="rounded text-primary focus:ring-primary border-gov-border w-3.5 h-3.5"
                        />
                        <span className="text-gov-text font-medium">{srv}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              {/* NGOs Cards List */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {isNgosLoading ? (
                  <div className="col-span-full py-8 text-center text-xs text-gov-subtext animate-pulse">Loading NGO registry...</div>
                ) : ngosList.map((ngo, idx) => (
                  <div key={idx} className="bg-gov-card border border-gov-border rounded-2xl p-5 flex flex-col justify-between space-y-4 welfare-card">
                    <div>
                      <h4 className="font-extrabold text-sm text-gov-text">{ngo.ngo_name}</h4>
                      <span className="text-[9px] bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded font-bold mt-1 inline-block">
                        {ngo.state} | {ngo.district}
                      </span>
                      <p className="text-xs text-gov-subtext mt-3">{ngo.description}</p>
                      
                      <div className="mt-3 pt-3 border-t border-gov-border text-[11px] space-y-1">
                        <p><span className="font-bold text-gov-text">Services:</span> {ngo.services_offered}</p>
                        <p><span className="font-bold text-gov-text">Eligibility:</span> {ngo.eligibility}</p>
                        <p><span className="font-bold text-gov-text">Contact:</span> {ngo.contact_number} | {ngo.email}</p>
                      </div>
                    </div>

                    <div className="flex justify-between items-center pt-2">
                      <a href={ngo.website} target="_blank" rel="noreferrer" className="text-xs text-primary font-bold hover:underline">Official Site</a>
                      <button
                        onClick={() => setSelectedNgoForRequest(ngo)}
                        className="bg-primary text-white text-xs font-bold px-3 py-1.5 rounded-xl cursor-pointer"
                      >
                        Request Help
                      </button>
                    </div>
                  </div>
                ))}
                {!isNgosLoading && ngosList.length === 0 && (
                  <div className="col-span-full text-center text-xs text-gov-subtext py-8 bg-gov-card border border-gov-border rounded-2xl">
                    No NGOs found matching search filters in {ngoSearchState}.
                  </div>
                )}
              </div>
            </div>
          ) : activeNgoTab === 'tracking' ? (
            // B. Citizen tracking panel
            <div className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-4">
              <div>
                <h3 className="text-sm font-bold text-gov-text">Your Submitted Assistance Requests</h3>
                <p className="text-xs text-gov-subtext">Track support and remarks provided by registered NGOs.</p>
              </div>

              <div className="overflow-x-auto border border-gov-border rounded-xl">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-gov-bg border-b border-gov-border text-gov-subtext font-bold text-[9px] uppercase tracking-wider">
                      <th className="p-3.5">NGO Name</th>
                      <th className="p-3.5">Request Details</th>
                      <th className="p-3.5">Attached Docs</th>
                      <th className="p-3.5">Status</th>
                      <th className="p-3.5">Date</th>
                      <th className="p-3.5">NGO Remarks</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gov-border text-gov-text">
                    {citizenNgoRequests.map((req, idx) => (
                      <tr key={idx} className="hover:bg-gov-bg/30">
                        <td className="p-3.5 font-bold">{req.ngo_name}</td>
                        <td className="p-3.5 max-w-xs truncate" title={req.request_details}>{req.request_details}</td>
                        <td className="p-3.5">{req.uploaded_docs.join(', ')}</td>
                        <td className="p-3.5">
                          <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold border ${
                            req.status === 'Accepted' ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' :
                            req.status === 'Rejected' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                            req.status === 'Completed' ? 'bg-blue-500/10 text-blue-600 border-blue-500/20' :
                            'bg-amber-500/10 text-amber-600 border-amber-500/20'
                          }`}>
                            {req.status}
                          </span>
                        </td>
                        <td className="p-3.5 text-gov-subtext text-[10px]">{req.created_at}</td>
                        <td className="p-3.5 italic text-gov-subtext">{req.remarks || "No remarks yet."}</td>
                      </tr>
                    ))}
                    {citizenNgoRequests.length === 0 && (
                      <tr>
                        <td colSpan="6" className="p-5 text-center text-gov-subtext italic">No requests submitted yet. Use the Directory to request help.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            // C. NGO Portal Dashboard
            <div className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-6">
              <div>
                <h3 className="text-sm font-bold text-gov-text">Incoming Citizens Assistance Board</h3>
                <p className="text-xs text-gov-subtext">Manage incoming welfare requests, review documents, and post updates.</p>
              </div>

              <div className="space-y-4">
                {ngoIncomingRequests.map((req, idx) => (
                  <div key={idx} className="bg-gov-bg border border-gov-border rounded-2xl p-5 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-extrabold text-sm text-gov-text">{req.citizen_name}</h4>
                        <p className="text-[10px] text-gov-subtext font-semibold">
                          Age {req.age} | {req.gender} | {req.occupation} | Income: ₹{req.annual_income?.toLocaleString()} | State: {req.citizen_state}
                        </p>
                      </div>
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                        req.status === 'Accepted' ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' :
                        req.status === 'Rejected' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                        req.status === 'Completed' ? 'bg-blue-500/10 text-blue-600 border-blue-500/20' :
                        'bg-amber-500/10 text-amber-600 border-amber-500/20'
                      }`}>
                        {req.status}
                      </span>
                    </div>

                    <div className="text-xs text-gov-text">
                      <span className="font-bold block text-gov-subtext text-[10px] uppercase">Request Details:</span>
                      <p className="leading-relaxed bg-gov-card border border-gov-border rounded-xl p-3 mt-1">{req.request_details}</p>
                    </div>

                    <div className="flex justify-between items-center text-xs">
                      <div>
                        <span className="font-bold text-gov-subtext text-[10px] block">Attached Documents:</span>
                        <span className="text-primary font-bold">{req.uploaded_docs.join(', ') || "No docs attached."}</span>
                      </div>
                      <span className="text-[10px] text-gov-subtext">{req.created_at}</span>
                    </div>

                    {req.status === 'Pending' && (
                      <div className="pt-3 border-t border-gov-border flex flex-col md:flex-row gap-3">
                        <input
                          type="text"
                          placeholder="Update Remarks..."
                          value={ngoUpdateRemarks}
                          onChange={(e) => setNgoUpdateRemarks(e.target.value)}
                          className="flex-1 bg-gov-card border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none text-gov-text"
                        />
                        <div className="flex space-x-2 justify-end">
                          <button
                            onClick={() => handleNgoRequestAction(req.id, 'Rejected')}
                            className="bg-red-500 text-white font-bold text-xs px-4 py-2 rounded-xl cursor-pointer"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleNgoRequestAction(req.id, 'Accepted')}
                            className="bg-emerald-500 text-white font-bold text-xs px-4 py-2 rounded-xl cursor-pointer"
                          >
                            Accept
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                {ngoIncomingRequests.length === 0 && (
                  <div className="text-center text-gov-subtext italic py-8">No incoming requests received for this NGO.</div>
                )}
              </div>
            </div>
          )}

          {/* Citizen NGO Request submission popup Modal */}
          {selectedNgoForRequest && (
            <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <form onSubmit={handleNgoRequestSubmit} className="bg-gov-card border border-gov-border rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl">
                <div className="bg-primary px-5 py-4 text-white flex justify-between items-center">
                  <h4 className="font-bold text-sm">Request Help - {selectedNgoForRequest.ngo_name}</h4>
                  <button type="button" onClick={() => setSelectedNgoForRequest(null)} className="text-white hover:opacity-85 font-black text-sm">✕</button>
                </div>
                <div className="p-6 space-y-4 text-gov-text">
                  <div>
                    <label className="block text-[11px] font-bold text-gov-subtext uppercase tracking-wider mb-1">Explain Assistance Needed</label>
                    <textarea
                      required
                      rows="4"
                      value={ngoRequestDetails}
                      onChange={(e) => setNgoRequestDetails(e.target.value)}
                      placeholder="Explain what help you need (e.g. admission funding assistance, hostel lodging, clinical aids, etc.)"
                      className="w-full bg-gov-bg border border-gov-border rounded-xl p-2.5 text-xs text-gov-text focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-gov-subtext uppercase tracking-wider mb-1">Select Vault Documents to Attach</label>
                    <div className="space-y-1.5 max-h-36 overflow-y-auto border border-gov-border rounded-xl p-2">
                      {uploadedDocs.map(doc => (
                        <label key={doc} className="flex items-center space-x-2 text-xs cursor-pointer select-none">
                          <input
                            type="checkbox"
                            checked={ngoRequestDocs.includes(doc)}
                            onChange={(e) => {
                              if (e.target.checked) setNgoRequestDocs(prev => [...prev, doc]);
                              else setNgoRequestDocs(prev => prev.filter(d => d !== doc));
                            }}
                            className="rounded text-primary focus:ring-primary border-gov-border w-3.5 h-3.5"
                          />
                          <span>{doc}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="bg-gov-bg border-t border-gov-border px-5 py-3.5 flex justify-end space-x-2">
                  <button type="button" onClick={() => setSelectedNgoForRequest(null)} className="bg-gov-card border border-gov-border px-4 py-2 rounded-xl text-xs font-bold cursor-pointer">Cancel</button>
                  <button type="submit" className="bg-primary text-white px-5 py-2 rounded-xl text-xs font-bold cursor-pointer">Submit Request</button>
                </div>
              </form>
            </div>
          )}
        </main>
      ) : (
        // ADMIN PANEL VIEW
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 space-y-8 animate-float">
          
          {/* Admin summary metrics */}
          {adminNgoAnalytics && (
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="bg-gov-card border border-gov-border rounded-3xl p-5 shadow-sm">
                <span className="text-[10px] uppercase font-bold text-gov-subtext">Registered NGOs</span>
                <h4 className="text-2xl font-black text-gov-text mt-1">{adminNgoAnalytics.total_ngos}</h4>
              </div>
              <div className="bg-gov-card border border-gov-border rounded-3xl p-5 shadow-sm">
                <span className="text-[10px] uppercase font-bold text-gov-subtext">Total Requests</span>
                <h4 className="text-2xl font-black text-primary mt-1">{adminNgoAnalytics.total_requests}</h4>
              </div>
              <div className="bg-gov-card border border-gov-border rounded-3xl p-5 shadow-sm">
                <span className="text-[10px] uppercase font-bold text-gov-subtext">Pending Requests</span>
                <h4 className="text-2xl font-black text-amber-500 mt-1">{adminNgoAnalytics.requests_breakdown.Pending}</h4>
              </div>
              <div className="bg-gov-card border border-gov-border rounded-3xl p-5 shadow-sm">
                <span className="text-[10px] uppercase font-bold text-gov-subtext">Resolved Requests</span>
                <h4 className="text-2xl font-black text-emerald-600 mt-1">{adminNgoAnalytics.requests_breakdown.Accepted + adminNgoAnalytics.requests_breakdown.Completed}</h4>
              </div>
            </div>
          )}

          {/* NGO Management Controls */}
          <div className="bg-gov-card border border-gov-border rounded-3xl p-6 space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-gov-text">NGO Directory Registry Manager</h3>
                <p className="text-xs text-gov-subtext">Add, edit, or remove approved NGOs in the system.</p>
              </div>
              <button
                onClick={() => {
                  setAdminNgoMode('add');
                  setShowAdminModal(true);
                }}
                className="bg-primary text-white text-xs font-bold px-4 py-2 rounded-xl flex items-center space-x-1 cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Add NGO</span>
              </button>
            </div>

            <div className="overflow-x-auto border border-gov-border rounded-xl">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-gov-bg border-b border-gov-border text-gov-subtext font-bold text-[9px] uppercase tracking-wider">
                    <th className="p-3.5">NGO Name</th>
                    <th className="p-3.5">State</th>
                    <th className="p-3.5">District</th>
                    <th className="p-3.5">Services</th>
                    <th className="p-3.5">Contact Number</th>
                    <th className="p-3.5">Email</th>
                    <th className="p-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gov-border text-gov-text">
                  {adminNgosList.map(ngo => (
                    <tr key={ngo.id} className="hover:bg-gov-bg/30">
                      <td className="p-3.5 font-bold">{ngo.ngo_name}</td>
                      <td className="p-3.5">{ngo.state}</td>
                      <td className="p-3.5">{ngo.district}</td>
                      <td className="p-3.5 max-w-xs truncate">{ngo.services_offered}</td>
                      <td className="p-3.5">{ngo.contact_number}</td>
                      <td className="p-3.5">{ngo.email}</td>
                      <td className="p-3.5 text-right space-x-2">
                        <button
                          onClick={() => handleAdminNgoEditLoad(ngo)}
                          className="p-1 text-primary hover:bg-primary/5 rounded border border-primary/20 inline-flex items-center cursor-pointer"
                          title="Edit"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleAdminNgoDelete(ngo.id)}
                          className="p-1 text-red-500 hover:bg-red-50/20 rounded border border-red-500/20 inline-flex items-center cursor-pointer"
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Admin add/edit dialog */}
          {showAdminModal && (
            <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <form onSubmit={handleAdminNgoSubmit} className="bg-gov-card border border-gov-border rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl">
                <div className="bg-primary px-5 py-4 text-white flex justify-between items-center">
                  <h4 className="font-bold text-sm">{adminNgoMode === 'add' ? 'Add NGO Profile' : 'Edit NGO Profile'}</h4>
                  <button type="button" onClick={() => setShowAdminModal(false)} className="text-white hover:opacity-85 font-black text-sm">✕</button>
                </div>
                
                <div className="p-6 space-y-4 max-h-[400px] overflow-y-auto text-gov-text">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">NGO Name</label>
                      <input
                        type="text"
                        required
                        value={adminNgoForm.ngo_name}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, ngo_name: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">State</label>
                      <select
                        value={adminNgoForm.state}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, state: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      >
                        {STATES_LIST.map(st => (
                          <option key={st} value={st}>{st}</option>
                        ))}
                        {UTS_LIST.map(ut => (
                          <option key={ut} value={ut}>{ut}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Description</label>
                    <textarea
                      required
                      rows="2"
                      value={adminNgoForm.description}
                      onChange={(e) => setAdminNgoForm(prev => ({ ...prev, description: e.target.value }))}
                      className="w-full bg-gov-bg border border-gov-border rounded-xl p-2.5 text-xs text-gov-text"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">District</label>
                      <input
                        type="text"
                        required
                        value={adminNgoForm.district}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, district: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Contact Number</label>
                      <input
                        type="text"
                        required
                        value={adminNgoForm.contact_number}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, contact_number: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Email</label>
                      <input
                        type="email"
                        required
                        value={adminNgoForm.email}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, email: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Website</label>
                      <input
                        type="text"
                        required
                        value={adminNgoForm.website}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, website: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Services Offered (Comma Separated)</label>
                      <input
                        type="text"
                        required
                        value={adminNgoForm.services_offered}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, services_offered: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Beneficiary Category</label>
                      <input
                        type="text"
                        required
                        value={adminNgoForm.beneficiary_category}
                        onChange={(e) => setAdminNgoForm(prev => ({ ...prev, beneficiary_category: e.target.value }))}
                        className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs text-gov-text"
                      />
                    </div>
                  </div>

                  {/* Service Flags */}
                  <div className="pt-2 border-t border-gov-border space-y-2">
                    <span className="block text-[10px] font-bold text-gov-subtext uppercase">Specialized Flags</span>
                    <div className="grid grid-cols-3 gap-2 text-[10px]">
                      {NGO_SERVICES.map(srv => {
                        const stateKey = srv.toLowerCase().replace(' ', '_');
                        return (
                          <label key={srv} className="flex items-center space-x-1.5 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={adminNgoForm[stateKey] === 1}
                              onChange={(e) => {
                                setAdminNgoForm(prev => ({ ...prev, [stateKey]: e.target.checked ? 1 : 0 }));
                              }}
                              className="rounded text-primary border-gov-border w-3.5 h-3.5"
                            />
                            <span>{srv}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>

                </div>

                <div className="bg-gov-bg border-t border-gov-border px-5 py-3.5 flex justify-end space-x-2">
                  <button type="button" onClick={() => setShowAdminModal(false)} className="bg-gov-card border border-gov-border px-4 py-2 rounded-xl text-xs font-bold">Cancel</button>
                  <button type="submit" className="bg-primary text-white px-5 py-2 rounded-xl text-xs font-bold">{adminNgoMode === 'add' ? 'Add NGO' : 'Save Changes'}</button>
                </div>
              </form>
            </div>
          )}
        </main>
      )}

      {/* FOOTER */}
      {activeTab !== 'government-scheme-agent' && (
        <footer className="border-t border-gov-border bg-gov-card py-6 text-center text-xs text-gov-subtext mt-auto shrink-0">
          <div className="max-w-7xl mx-auto px-4 space-y-2">
            <p className="font-bold text-gov-text">🏛️ Ministry of Public Welfare & National Informatics Centre (NIC)</p>
            <p>© 2026 AI Welfare Navigator Portal • Verified Direct Benefit Transfers (DBT) secured via National Portal registry.</p>
          </div>
        </footer>
      )}

      {/* PROFILE DIALOG MODAL */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gov-card border border-gov-border rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl">
            <div className="bg-primary px-5 py-4 text-white flex justify-between items-center">
              <h4 className="font-bold text-sm">Citizen Profile Parameters</h4>
              <button onClick={() => setShowProfileModal(false)} className="text-white hover:opacity-85 font-black text-sm">✕</button>
            </div>

            <div className="p-6 space-y-4 max-h-[400px] overflow-y-auto text-gov-text bg-gov-card">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Full Name</label>
                  <input
                    type="text"
                    name="name"
                    value={profile.name}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Age (Years)</label>
                  <input
                    type="number"
                    name="age"
                    value={profile.age}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Gender</label>
                  <select
                    name="gender"
                    value={profile.gender}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  >
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Domicile State</label>
                  <select
                    name="state"
                    value={profile.state}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  >
                    {STATES_LIST.map(st => (
                      <option key={st} value={st}>{st}</option>
                    ))}
                    {UTS_LIST.map(ut => (
                      <option key={ut} value={ut}>{ut}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">District</label>
                  <input
                    type="text"
                    name="district"
                    value={profile.district}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Annual Income (₹)</label>
                  <input
                    type="number"
                    name="annualIncome"
                    value={profile.annualIncome}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Social Category</label>
                  <select
                    name="category"
                    value={profile.category}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  >
                    <option>General</option>
                    <option>OBC</option>
                    <option>SC</option>
                    <option>ST</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Occupation</label>
                  <select
                    name="occupation"
                    value={profile.occupation}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  >
                    <option>Student</option>
                    <option>Farmer</option>
                    <option>Small Business Owner</option>
                    <option>Startup Founder</option>
                    <option>Job Seeker</option>
                    <option>None</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Education Level</label>
                  <select
                    name="education"
                    value={profile.education}
                    onChange={handleProfileChange}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  >
                    <option>B.Tech</option>
                    <option>School Student</option>
                    <option>Graduate</option>
                    <option>Post-Graduate</option>
                    <option>Matric</option>
                    <option>None</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-gov-subtext uppercase mb-1">Disability Status</label>
                  <select
                    name="disability"
                    value={profile.disability ? "yes" : "no"}
                    onChange={(e) => {
                      setProfile(prev => ({ ...prev, disability: e.target.value === 'yes' }));
                    }}
                    className="w-full bg-gov-bg border border-gov-border rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-primary text-gov-text"
                  >
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="bg-gov-bg border-t border-gov-border px-5 py-3.5 flex justify-end">
              <button
                onClick={() => {
                  setShowProfileModal(false);
                  speakNarrative("Profile parameters saved successfully.");
                }}
                className="bg-primary hover:bg-primary/95 text-white font-bold text-xs px-5 py-2 rounded-xl shadow-sm cursor-pointer"
              >
                Save & Close
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

export default App;
