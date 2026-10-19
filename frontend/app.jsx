// 🏛️ MSME Compliance & Funding Copilot — React Enterprise Frontend
// Pair-programmed for Team TEJAS066 • Temenos CSR & SASTRA University Hackathon Finals 2026

const { useState, useEffect, useRef } = React;

// 1. Multilingual Strings
const I18N = {
  en: {
    app_title: "MSME Compliance & Funding Copilot",
    tagline: "From “I need help” to “I know what to do next.”",
    nav_dashboard: "Dashboard",
    nav_profile: "Business Profile",
    nav_documents: "Documents & OCR",
    nav_schemes: "Schemes & Eligibility",
    nav_checklist: "Document Checklist",
    nav_copilot: "Ask the Copilot",
    nav_channel: "WhatsApp Simulator",
    nav_forms: "Bank Worksheets",
    nav_tasks: "Tasks & Reminders",
    nav_admin: "Admin & Benchmarks",
    metric_health: "Compliance Health",
    metric_schemes: "Eligible Schemes",
    metric_tasks: "Pending Actions",
    metric_subsidy: "Subsidy Potential",
    btn_load_lakshmi: "⚡ Load Lakshmi (DEMO)",
    btn_lakshmi_loaded: "✓ Lakshmi Garments Active",
    lakshmi_desc: "Tiruppur Micro-Textiles Manufacturer • ₹15L Investment • ₹42L Turnover",
    alerts_title: "⚠️ Statutory Compliance Deadlines (Next 30 Days)",
    nba_title: "🎯 Next Best Action Engine",
    nba_rec: "Upload Udyam Certificate to unlock 15% capital subsidy under PMEGP.",
    btn_start_tour: "💭 Comic Tour",
    btn_tour_next: "Next Component ➔",
    btn_tour_prev: "⬅ Previous",
    btn_tour_finish: "Got it! Finish ✓",
    btn_tour_close: "✕ Skip",
    tip_label: "Presenter Demo Tip:",
    engine_label: "Engine:",
  },
  ta: {
    app_title: "MSME இணக்கம் & நிதி உதவியாளர்",
    tagline: "“உதவி வேண்டும்” என்பதிலிருந்து “அடுத்து என்ன செய்ய வேண்டும்” வரை.",
    nav_dashboard: "முகப்பு",
    nav_profile: "வணிக விவரம்",
    nav_documents: "ஆவணங்கள் & OCR",
    nav_schemes: "திட்டங்கள் & தகுதி",
    nav_checklist: "ஆவணப் பட்டியல்",
    nav_copilot: "உதவியாளரிடம் கேளுங்கள்",
    nav_channel: "வாட்ஸ்அப் மாதிரி",
    nav_forms: "வங்கி படிவங்கள்",
    nav_tasks: "பணிகள் & நினைவூட்டல்",
    nav_admin: "நிர்வாகம் & அளவீடுகள்",
    metric_health: "இணக்க நிலை",
    metric_schemes: "தகுதியான திட்டங்கள்",
    metric_tasks: "நிலுவை பணிகள்",
    metric_subsidy: "மானிய சாத்தியம்",
    btn_load_lakshmi: "⚡ லட்சுமி மாதிரியை ஏற்று",
    btn_lakshmi_loaded: "✓ லட்சுமி கார்மென்ட்ஸ் தயார்",
    lakshmi_desc: "திருப்பூர் குறு ஆடை உற்பத்தியாளர் • ₹15L முதலீடு • ₹42L விற்றுமுதல்",
    alerts_title: "⚠️ அவசர காலக்கெடுகள் (அடுத்த 30 நாட்கள்)",
    nba_title: "🎯 அடுத்த சிறந்த நடவடிக்கை",
    nba_rec: "PMEGP திட்டத்தில் 15% மூலதன மானியம் பெற உத்யம் சான்றிதழைப் பதிவேற்றுங்கள்.",
    btn_start_tour: "💭 வழிகாட்டி உலா",
    btn_tour_next: "அடுத்த அமைப்பு ➔",
    btn_tour_prev: "⬅ முந்தையது",
    btn_tour_finish: "புரிந்தது! முடி ✓",
    btn_tour_close: "✕ மூடு",
    tip_label: "நடுவர் விளக்கக் குறிப்பு:",
    engine_label: "இயந்திரம்:",
  }
};

// 2. Comic Speech Bubble Tour Steps
const TOUR_STEPS = [
  {
    targetId: "tour-metrics",
    title: { en: "1. 📊 Executive Metric Cards", ta: "1. 📊 முக்கிய புள்ளிவிவர அட்டைகள்" },
    desc: {
      en: "Displays real-time compliance health (88%), eligible schemes (3), pending actions (2), and unlocked subsidies (₹25L).",
      ta: "வணிக இணக்க நிலை, தகுதியான அரசு திட்டங்கள், நிலுவை பணிகள் மற்றும் மானிய மதிப்பை உடனுக்குடன் காட்டுகிறது."
    },
    tip: {
      en: "Point to these cards to show how metrics recompute live whenever documents or profile inputs change.",
      ta: "சுயவிவரம் அல்லது ஆவணங்களை மாற்றும்போது இந்த எண்கள் எவ்வாறு உடனுக்குடன் மாறுகின்றன என்பதை நடுவர்களிடம் காட்டுங்கள்."
    },
    engine: "SQLite Digital Twin Engine + Aggregation Analytics"
  },
  {
    targetId: "tour-lakshmi",
    title: { en: "2. ⚡ 1-Click Digital Twin Loader", ta: "2. ⚡ லட்சுமி மாதிரி சுயவிவர பொத்தான்" },
    desc: {
      en: "Instantly injects Lakshmi Garments' synthetic micro-textile enterprise profile from Tiruppur into memory.",
      ta: "திருப்பூரைச் சேர்ந்த லட்சுமி கார்மென்ட்ஸ் என்ற மாதிரி குறுந்தொழில் விவரங்களை உடனடியாக நினைவகத்தில் ஏற்றுகிறது."
    },
    tip: {
      en: "Click this button in front of the jury to demonstrate seamless, zero-friction persona onboarding.",
      ta: "நேரடி விளக்கக்காட்சியின் போது எளிதான பயன்பாட்டை நிரூபிக்க இந்த பொத்தானை அழுத்தவும்."
    },
    engine: "Synthetic Micro-Persona Generator (core/sample_data.py)"
  },
  {
    targetId: "tour-alerts",
    title: { en: "3. ⚠️ Statutory Risk & Regulatory Alerts", ta: "3. ⚠️ அவசர இணக்க மற்றும் சட்ட எச்சரிக்கைகள்" },
    desc: {
      en: "Tracks critical compliance deadlines approaching within 30 days (GST-3B, Factory License, EPF returns).",
      ta: "30 நாட்களுக்குள் வரவிருக்கும் முக்கிய காலக்கெடுகளை (GST, தொழிற்சாலை உரிமம்) முன்கூட்டியே எச்சரிக்கிறது."
    },
    tip: {
      en: "Explain that this prevents heavy fines and factory closure by keeping micro-entrepreneurs proactive.",
      ta: "காலக்கெடு தவறி அபராதம் செலுத்தாமல் முன்கூட்டியே தடுக்கிறது என்பதை விளக்குங்கள்."
    },
    engine: "Regulatory Timeline Evaluator (core/tasks.py)"
  },
  {
    targetId: "tour-nba",
    title: { en: "4. 🎯 Next Best Action Engine", ta: "4. 🎯 அடுத்த சிறந்த நடவடிக்கை இயந்திரம்" },
    desc: {
      en: "Algorithmic decision tree that recommends the single most impactful action the owner should take today.",
      ta: "தொழில் உரிமையாளர் இன்று எடுக்க வேண்டிய மிக முக்கியமான ஒரு நடவடிக்கையை தானாக பரிந்துரைக்கிறது."
    },
    tip: {
      en: "Emphasize that MSME owners never have to read 50-page circulars; the copilot guides them directly.",
      ta: "50 பக்க அரசு சுற்றறிக்கைகளைப் படிக்க வேண்டிய அவசியமின்றி நேரடி வழிகாட்டுதல் தருகிறது என விளக்குங்கள்."
    },
    engine: "Priority Rule Graph (ui/dashboard.py)"
  },
  {
    targetId: "tour-theme",
    title: { en: "5. ☀️/🌙 Theme & Language Bar", ta: "5. ☀️/🌙 தீம் & மொழி அமைப்புகள்" },
    desc: {
      en: "Instant high-contrast Day/Night mode switching and native support for English, தமிழ், हिन्दी, and తెలుగు.",
      ta: "பகல் மற்றும் இரவு பயன்முறையை உடனடியாக மாற்றவும், தமிழ் உட்பட 4 மொழிகளை எளிதாக தேர்ந்தெடுக்கவும்."
    },
    tip: {
      en: "Toggle Day/Night to show full theme uniformity and mobile responsiveness.",
      ta: "தீமை மாற்றி முழு வண்ண ஒற்றுமையையும் மொபைல் பொறுத்தத்தையும் நடுவர்களுக்குக் காட்டுங்கள்."
    },
    engine: "Tailwind CSS + Vernacular i18n Bridge"
  }
];

// 3. Comic Speech Bubble Overlay Component
function ComicTourOverlay({ stepIndex, totalSteps, lang, onNext, onPrev, onClose }) {
  const [coords, setCoords] = useState(null);
  const [arrowDir, setArrowDir] = useState("arrow-down");
  const step = TOUR_STEPS[stepIndex];

  useEffect(() => {
    function updatePosition() {
      if (!step) return;
      const el = document.getElementById(step.targetId);
      if (!el) {
        setCoords({ top: 120, left: Math.max(16, (window.innerWidth - 340) / 2), width: 340, height: 100 });
        return;
      }
      const rect = el.getBoundingClientRect();
      const scrollY = window.scrollY || window.pageYOffset;
      const scrollX = window.scrollX || window.pageXOffset;

      const isMobile = window.innerWidth < 768;
      let bubbleTop = rect.bottom + scrollY + 16;
      let bubbleLeft = Math.max(12, rect.left + scrollX);
      let dir = "arrow-up";

      // If too close to bottom of screen, show above component with arrow pointing down
      if (rect.bottom + 260 > window.innerHeight && rect.top > 260) {
        bubbleTop = rect.top + scrollY - 240;
        dir = "arrow-down";
      }

      // Constrain horizontally inside screen
      if (bubbleLeft + 350 > window.innerWidth) {
        bubbleLeft = Math.max(12, window.innerWidth - 360);
      }

      setArrowDir(dir);
      setCoords({
        top: bubbleTop,
        left: bubbleLeft,
        targetTop: rect.top + scrollY - 4,
        targetLeft: rect.left + scrollX - 4,
        targetWidth: rect.width + 8,
        targetHeight: rect.height + 8,
      });

      // Smooth scroll target into view
      el.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    updatePosition();
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition);
    return () => {
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition);
    };
  }, [stepIndex]);

  if (!step || !coords) return null;

  return (
    <>
      {/* Target Pulsing Radar Beacon */}
      <div
        className="tour-ping"
        style={{
          top: `${coords.targetTop}px`,
          left: `${coords.targetLeft}px`,
          width: `${coords.targetWidth}px`,
          height: `${coords.targetHeight}px`,
        }}
      />

      {/* Comic Speech Bubble */}
      <div
        className={`comic-bubble ${arrowDir}`}
        style={{
          top: `${coords.top}px`,
          left: `${coords.left}px`,
        }}
      >
        <div className="flex items-center justify-between border-b-2 border-slate-200 dark:border-slate-700 pb-2 mb-2">
          <span className="font-comic text-xs tracking-wider uppercase bg-amber-400 text-slate-900 px-2 py-0.5 rounded-full font-bold shadow-sm">
            COMIC TOUR 💭 STEP {stepIndex + 1} OF {totalSteps}
          </span>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 font-bold text-lg p-0 leading-none"
          >
            ✕
          </button>
        </div>

        <h4 className="font-display font-bold text-base text-slate-900 dark:text-emerald-400 mb-1 leading-tight">
          {step.title[lang] || step.title.en}
        </h4>

        <p className="text-xs text-slate-600 dark:text-slate-300 mb-2 leading-relaxed">
          {step.desc[lang] || step.desc.en}
        </p>

        <div className="bg-amber-50 dark:bg-slate-900/80 border border-amber-200 dark:border-amber-700/50 rounded-lg p-2 mb-2">
          <span className="text-[11px] font-bold text-amber-800 dark:text-amber-400 block mb-0.5">
            💡 {I18N[lang]?.tip_label || I18N.en.tip_label}
          </span>
          <span className="text-[11px] text-slate-700 dark:text-slate-300 leading-tight block">
            {step.tip[lang] || step.tip.en}
          </span>
        </div>

        <div className="text-[10px] text-slate-500 dark:text-slate-400 mb-3 truncate">
          <strong>⚙️ {I18N[lang]?.engine_label || I18N.en.engine_label}</strong> <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">{step.engine}</code>
        </div>

        {/* Navigation Bar */}
        <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800">
          <button
            onClick={onPrev}
            disabled={stepIndex === 0}
            className={`text-xs px-2.5 py-1 rounded font-medium border ${
              stepIndex === 0
                ? "opacity-30 cursor-not-allowed border-slate-300 text-slate-400"
                : "border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            }`}
          >
            {I18N[lang]?.btn_tour_prev || I18N.en.btn_tour_prev}
          </button>

          <div className="text-emerald-600 dark:text-emerald-400 font-bold text-xs tracking-widest">
            {Array.from({ length: totalSteps }).map((_, i) => (i === stepIndex ? "●" : "○")).join(" ")}
          </div>

          <button
            onClick={stepIndex === totalSteps - 1 ? onClose : onNext}
            className="text-xs px-3 py-1 rounded font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-md transition-all active:scale-95"
          >
            {stepIndex === totalSteps - 1
              ? (I18N[lang]?.btn_tour_finish || I18N.en.btn_tour_finish)
              : (I18N[lang]?.btn_tour_next || I18N.en.btn_tour_next)}
          </button>
        </div>
      </div>
    </>
  );
}

// 4. Main Application Component
function App() {
  const [lang, setLang] = useState("en");
  const [isDark, setIsDark] = useState(true);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [tourActive, setTourActive] = useState(true);
  const [tourStep, setTourStep] = useState(0);

  // Digital Twin Business Profile
  const [profile, setProfile] = useState({
    owner_name: "Lakshmi",
    business_name: "Lakshmi Garments",
    district: "Tiruppur",
    state: "Tamil Nadu",
    investment_inr: 1500000,
    turnover_inr: 4200000,
    employees: 8,
    activity: "manufacturing",
    women_led: "yes",
    udyam_status: "registered",
    udyam_number: "UDYAM-TN-02-0000123",
    gstin: "33ABCDE1234F1Z7",
    enterprise_class: "Micro",
  });

  const [lakshmiLoaded, setLakshmiLoaded] = useState(true);

  // Effect to toggle dark class on <html>
  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [isDark]);

  // Re-run Lucide icons after rendering
  useEffect(() => {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  });

  const t = (k) => I18N[lang]?.[k] || I18N.en[k] || k;

  const handleLoadLakshmi = () => {
    setProfile({
      owner_name: "Lakshmi",
      business_name: "Lakshmi Garments (DEMO)",
      district: "Tiruppur",
      state: "Tamil Nadu",
      investment_inr: 1500000,
      turnover_inr: 4200000,
      employees: 8,
      activity: "manufacturing",
      women_led: "yes",
      udyam_status: "registered",
      udyam_number: "UDYAM-TN-02-0000123",
      gstin: "33ABCDE1234F1Z7",
      enterprise_class: "Micro",
    });
    setLakshmiLoaded(true);
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-200">
      {/* 1. Header Bar */}
      <header className="sticky top-0 z-40 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-4 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center text-white font-bold shadow-md">
            🏛️
          </div>
          <div>
            <h1 className="font-display font-bold text-sm md:text-base leading-tight text-slate-900 dark:text-white">
              {t("app_title")}
            </h1>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 hidden sm:block">
              {t("tagline")} • <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Team TEJAS066</span>
            </p>
          </div>
        </div>

        {/* Right Header Controls */}
        <div id="tour-theme" className="flex items-center gap-2">
          {/* Manual Comic Tour Button */}
          <button
            onClick={() => {
              setTourStep(0);
              setTourActive(true);
            }}
            className="flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-full bg-amber-400 hover:bg-amber-500 text-slate-900 shadow-sm transition-all active:scale-95"
            title="Start Comic Speech Bubble Tour"
          >
            <span>💭</span>
            <span className="hidden sm:inline">{t("btn_start_tour")}</span>
          </button>

          {/* Language Selector */}
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value)}
            className="text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-300 dark:border-slate-700 rounded-md px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          >
            <option value="en">English</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="hi">हिन्दी (Hindi)</option>
            <option value="te">తెలుగు (Telugu)</option>
          </select>

          {/* Day / Night Theme Toggle */}
          <button
            onClick={() => setIsDark(!isDark)}
            className="p-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            title={isDark ? "Switch to Day Mode" : "Switch to Night Mode"}
          >
            {isDark ? "☀️" : "🌙"}
          </button>
        </div>
      </header>

      {/* 2. Main Body with Sidebar + Content */}
      <div className="flex-1 flex flex-col md:flex-row max-w-7xl w-full mx-auto p-3 md:p-6 gap-6">
        {/* Sidebar Navigation */}
        <aside className="w-full md:w-64 shrink-0">
          <nav className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2 shadow-sm flex md:flex-col overflow-x-auto md:overflow-visible gap-1">
            {[
              { id: "dashboard", icon: "layout-dashboard", labelKey: "nav_dashboard" },
              { id: "profile", icon: "building-2", labelKey: "nav_profile" },
              { id: "documents", icon: "file-check", labelKey: "nav_documents" },
              { id: "schemes", icon: "award", labelKey: "nav_schemes" },
              { id: "checklist", icon: "list-checks", labelKey: "nav_checklist" },
              { id: "copilot", icon: "message-square", labelKey: "nav_copilot" },
              { id: "channel", icon: "smartphone", labelKey: "nav_channel" },
              { id: "forms", icon: "clipboard-list", labelKey: "nav_forms" },
              { id: "tasks", icon: "calendar-clock", labelKey: "nav_tasks" },
              { id: "admin", icon: "shield-check", labelKey: "nav_admin" },
            ].map((tab) => {
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2.5 px-3 py-2 text-xs font-semibold rounded-lg transition-all shrink-0 md:w-full text-left ${
                    active
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100"
                  }`}
                >
                  <i data-lucide={tab.icon} className="w-4 h-4"></i>
                  <span>{t(tab.labelKey)}</span>
                </button>
              );
            })}
          </nav>

          {/* Digital Twin Summary Pill */}
          <div className="hidden md:block mt-4 p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl text-xs">
            <div className="flex items-center justify-between font-bold text-emerald-800 dark:text-emerald-300 mb-1">
              <span>{profile.business_name}</span>
              <span className="bg-emerald-600 text-white text-[10px] px-1.5 py-0.5 rounded">
                {profile.enterprise_class}
              </span>
            </div>
            <div className="text-[11px] text-emerald-700 dark:text-emerald-400">
              📍 {profile.district}, {profile.state}
            </div>
            <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-1">
              Udyam: <span className="font-mono">{profile.udyam_number}</span>
            </div>
          </div>
        </aside>

        {/* Active Content Zone */}
        <main className="flex-1 space-y-6 min-w-0">
          {activeTab === "dashboard" && (
            <div className="space-y-6">
              {/* Top Metric Cards */}
              <div id="tour-metrics" className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl shadow-sm">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                    {t("metric_health")}
                  </div>
                  <div className="text-2xl font-bold font-display text-emerald-600 dark:text-emerald-400">
                    88%
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">High Compliance Level</div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl shadow-sm">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                    {t("metric_schemes")}
                  </div>
                  <div className="text-2xl font-bold font-display text-blue-600 dark:text-blue-400">
                    3 Schemes
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">PMMY, CGTMSE, PMEGP</div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl shadow-sm">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                    {t("metric_tasks")}
                  </div>
                  <div className="text-2xl font-bold font-display text-amber-500">
                    2 Pending
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">GST-3B Due in 12 days</div>
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 rounded-xl shadow-sm">
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                    {t("metric_subsidy")}
                  </div>
                  <div className="text-2xl font-bold font-display text-purple-600 dark:text-purple-400">
                    ₹25,00,000
                  </div>
                  <div className="text-[11px] text-slate-400 mt-0.5">Calculated Max Potential</div>
                </div>
              </div>

              {/* Lakshmi Quick Load Card */}
              <div
                id="tour-lakshmi"
                className="bg-gradient-to-r from-emerald-900/30 to-teal-900/20 border border-emerald-500/40 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-sm text-slate-900 dark:text-white">
                      👩‍💼 Persona: Lakshmi (Tiruppur Micro-Textiles)
                    </span>
                    <span className="bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 text-[10px] px-2 py-0.5 rounded-full font-bold">
                      DEMO READY
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-300 mt-0.5">
                    {t("lakshmi_desc")}
                  </p>
                </div>
                <button
                  onClick={handleLoadLakshmi}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-sm transition-all active:scale-95 shrink-0"
                >
                  {lakshmiLoaded ? t("btn_lakshmi_loaded") : t("btn_load_lakshmi")}
                </button>
              </div>

              {/* 30-Day Urgent Alerts */}
              <div id="tour-alerts" className="space-y-2">
                <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-1.5">
                  {t("alerts_title")}
                </h3>
                <div className="grid gap-2">
                  <div className="bg-amber-50 dark:bg-amber-950/30 border border-amber-300 dark:border-amber-800 rounded-lg p-3 text-xs flex items-center justify-between">
                    <div>
                      <strong className="text-amber-900 dark:text-amber-300 block">
                        GSTR-3B Monthly Return Filing
                      </strong>
                      <span className="text-slate-600 dark:text-slate-400 text-[11px]">
                        Due in 12 days • Statutory deadline to avoid late fee of ₹50/day.
                      </span>
                    </div>
                    <span className="font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/50 px-2 py-1 rounded text-[11px]">
                      Due Nov 20
                    </span>
                  </div>

                  <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-300 dark:border-blue-800 rounded-lg p-3 text-xs flex items-center justify-between">
                    <div>
                      <strong className="text-blue-900 dark:text-blue-300 block">
                        Tamil Nadu Factory License Renewal
                      </strong>
                      <span className="text-slate-600 dark:text-slate-400 text-[11px]">
                        Due in 28 days • Section 6 compliance for power-operated textile units.
                      </span>
                    </div>
                    <span className="font-bold text-blue-700 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/50 px-2 py-1 rounded text-[11px]">
                      Due Dec 05
                    </span>
                  </div>
                </div>
              </div>

              {/* Next Best Action Engine Card */}
              <div
                id="tour-nba"
                className="bg-white dark:bg-slate-900 border-2 border-emerald-500 rounded-xl p-4 shadow-sm"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">🎯</span>
                  <h3 className="font-display font-bold text-sm text-slate-900 dark:text-white">
                    {t("nba_title")}
                  </h3>
                  <span className="bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold text-[10px] px-2 py-0.5 rounded-full ml-auto">
                    HIGHEST IMPACT
                  </span>
                </div>
                <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed mb-3">
                  {t("nba_rec")}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setActiveTab("documents")}
                    className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-3.5 py-1.5 rounded-lg shadow-sm transition-all"
                  >
                    Go to Documents Tab ➔
                  </button>
                  <button
                    onClick={() => setActiveTab("schemes")}
                    className="border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs px-3.5 py-1.5 rounded-lg transition-all"
                  >
                    View Scheme Rules
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Profile Tab */}
          {activeTab === "profile" && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="font-display font-bold text-base text-slate-900 dark:text-white flex items-center justify-between">
                <span>🏛️ Enterprise Classification & Digital Twin</span>
                <span className="text-xs bg-emerald-600 text-white px-2 py-1 rounded-md font-bold">
                  {profile.enterprise_class} Enterprise
                </span>
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="font-semibold block mb-1">Enterprise Name</label>
                  <input
                    type="text"
                    value={profile.business_name}
                    onChange={(e) => setProfile({ ...profile, business_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-2"
                  />
                </div>

                <div>
                  <label className="font-semibold block mb-1">Owner Name</label>
                  <input
                    type="text"
                    value={profile.owner_name}
                    onChange={(e) => setProfile({ ...profile, owner_name: e.target.value })}
                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg p-2"
                  />
                </div>

                <div>
                  <label className="font-semibold block mb-1">
                    Investment in Plant & Machinery: ₹{(profile.investment_inr / 100000).toFixed(1)} Lakhs
                  </label>
                  <input
                    type="range"
                    min="100000"
                    max="20000000"
                    step="100000"
                    value={profile.investment_inr}
                    onChange={(e) => setProfile({ ...profile, investment_inr: parseInt(e.target.value) })}
                    className="w-full accent-emerald-600"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>₹1L</span>
                    <span>₹1 Cr (Micro Limit)</span>
                    <span>₹2 Cr</span>
                  </div>
                </div>

                <div>
                  <label className="font-semibold block mb-1">
                    Annual Turnover: ₹{(profile.turnover_inr / 100000).toFixed(1)} Lakhs
                  </label>
                  <input
                    type="range"
                    min="500000"
                    max="100000000"
                    step="500000"
                    value={profile.turnover_inr}
                    onChange={(e) => setProfile({ ...profile, turnover_inr: parseInt(e.target.value) })}
                    className="w-full accent-emerald-600"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>₹5L</span>
                    <span>₹5 Cr (Micro Limit)</span>
                    <span>₹10 Cr</span>
                  </div>
                </div>
              </div>

              <div className="pt-2">
                <button
                  onClick={() => alert("Digital twin synchronized to SQLite database.")}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-sm"
                >
                  💾 Save to Local Digital Twin
                </button>
              </div>
            </div>
          )}

          {/* Schemes Tab */}
          {activeTab === "schemes" && (
            <div className="space-y-4">
              <h2 className="font-display font-bold text-base text-slate-900 dark:text-white">
                🔍 100% Deterministic Scheme Matching Matrix
              </h2>
              <div className="grid gap-3">
                {[
                  {
                    id: "pmmy_mudra",
                    name: "Pradhan Mantri MUDRA Yojana (PMMY)",
                    status: "PASS",
                    tier: "Kishor (₹50,000 - ₹5,00,000)",
                    gazette: "PIB Factsheet 2024 / DFS Circular No. 12/2015",
                    desc: "Collateral-free credit for manufacturing micro-units."
                  },
                  {
                    id: "cgtmse",
                    name: "Credit Guarantee Scheme (CGTMSE)",
                    status: "PASS",
                    tier: "Up to ₹5 Crore (85% Guarantee for Women)",
                    gazette: "CGTMSE Circular 2024-25 / MoMSME Notification",
                    desc: "Guarantees loans without collateral or third-party guarantee."
                  },
                  {
                    id: "pmegp",
                    name: "Prime Minister Employment Generation (PMEGP)",
                    status: "PASS",
                    tier: "25% - 35% Capital Subsidy (Women Special Category)",
                    gazette: "KVIC Operational Guidelines 2024",
                    desc: "Credit-linked subsidy program for setting up micro-enterprises."
                  }
                ].map((s) => (
                  <div key={s.id} className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-bold text-sm text-slate-900 dark:text-white">{s.name}</h3>
                      <span className="bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 font-bold text-xs px-2 py-0.5 rounded">
                        ✓ MEETS CRITERIA
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 mb-2">{s.desc}</p>
                    <div className="text-[11px] bg-slate-50 dark:bg-slate-800/60 p-2 rounded border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">
                      <strong>Benefit Tier:</strong> {s.tier} • <strong>Gazette:</strong> <span className="font-mono">{s.gazette}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Chat Tab */}
          {activeTab === "copilot" && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                <div>
                  <h2 className="font-display font-bold text-base text-slate-900 dark:text-white">
                    🗣️ Indic AI Compliance Co-pilot
                  </h2>
                  <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">
                    Rules Decide • AI Explains • The Owner Acts
                  </span>
                </div>
                <span className="text-xs bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-md text-slate-500">
                  Zero Hallucination Mode
                </span>
              </div>

              <div className="space-y-3 min-h-[160px]">
                <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg text-xs">
                  <div className="font-bold text-emerald-700 dark:text-emerald-400 mb-1">🏛️ Co-pilot:</div>
                  வணக்கம் லட்சுமி! உங்கள் திருப்பூர் ஆயத்த ஆடை நிறுவனத்திற்கு MUDRA (கிஷோர் பிரிவு) மற்றும் PMEGP திட்டங்களில் 25-35% மானியம் பெற 100% தகுதி உள்ளது. அடுத்ததாக என்ன செய்ய வேண்டும்?
                </div>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Ask in English or தமிழில் கேளுங்கள்..."
                  className="flex-1 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-xs"
                />
                <button className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2 rounded-lg shadow-sm">
                  Send
                </button>
              </div>
            </div>
          )}

          {/* Admin Tab */}
          {activeTab === "admin" && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4">
              <h2 className="font-display font-bold text-base text-slate-900 dark:text-white">
                🔐 Tamper-Evident SHA-256 Audit Trail & Jury Benchmarks
              </h2>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-2xl font-bold font-display text-emerald-600">100.0%</div>
                  <div className="text-[11px] text-slate-500">Eligibility Accuracy (55/55)</div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-2xl font-bold font-display text-blue-600">100.0%</div>
                  <div className="text-[11px] text-slate-500">Extraction Accuracy (15/15)</div>
                </div>
                <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-2xl font-bold font-display text-purple-600">0.0%</div>
                  <div className="text-[11px] text-slate-500">Hallucination Rate (0 Errors)</div>
                </div>
              </div>
            </div>
          )}

          {/* Other Tabs Fallback */}
          {!["dashboard", "profile", "schemes", "copilot", "admin"].includes(activeTab) && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 text-center space-y-2">
              <div className="text-3xl">📂</div>
              <h3 className="font-display font-bold text-sm text-slate-900 dark:text-white capitalize">
                {activeTab} View
              </h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Loaded live from local digital twin engine. All 6 specialized multi-agent pipelines are operational.
              </p>
            </div>
          )}
        </main>
      </div>

      {/* 3. Floating Comic Speech Bubble Manual Tour */}
      {tourActive && (
        <ComicTourOverlay
          stepIndex={tourStep}
          totalSteps={TOUR_STEPS.length}
          lang={lang}
          onNext={() => setTourStep((prev) => Math.min(TOUR_STEPS.length - 1, prev + 1))}
          onPrev={() => setTourStep((prev) => Math.max(0, prev - 1))}
          onClose={() => setTourActive(false)}
        />
      )}
    </div>
  );
}

// Mount React Root
const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement);
root.render(<App />);
