"""Guided-tour content in 4 languages. STRUCTURE (which element each step points at) is shared; only words differ.

NEEDS NATIVE REVIEW: Tamil/Hindi/Telugu below are careful drafts. Keep every language at the same step count
(tests/test_shell.py enforces it) and keep texts short: they sit inside a speech bubble.
"""
from __future__ import annotations

LANGS = [("en", "English"), ("ta", "தமிழ்"), ("hi", "हिन्दी"), ("te", "తెలుగు")]

# id, page (nav key to be on), selectors tried in order ('@lang_radio' / '@nav_radio' are special), preferred side
STEP_DEFS = [
    ("welcome",  "nav_dashboard", [], "center"),
    ("language", "nav_dashboard", ["@lang_radio"], "right"),
    ("pages",    "nav_dashboard", ["@nav_radio"], "right"),
    ("demo",     "nav_dashboard", [".st-key-btn_load_demo", ".st-key-btn_reset"], "bottom"),
    ("method",   "nav_dashboard", [".st-key-tour_stepper"], "bottom"),
    ("next",     "nav_dashboard", [".st-key-tour_nba"], "bottom"),
    ("agents",   "nav_dashboard", [".st-key-tour_agents"], "top"),
    ("documents", "nav_documents", ['[data-testid="stFileUploader"]'], "bottom"),
    ("schemes",  "nav_schemes", ['[data-testid="stMetric"]', '[data-testid="stSelectbox"]'], "bottom"),
    ("copilot",  "nav_copilot", ['[data-testid="stChatInput"]'], "top"),
    ("controls", "nav_dashboard", ["#msme-cluster"], "left"),
    ("finish",   "nav_dashboard", [], "center"),
]

TEXT = {
    "en": {
        "welcome": ("Welcome to MSME Copilot 👋", "From “I need help” to “I know what to do next.” In one minute, see how Lakshmi — a garment maker in Tiruppur — goes from confusion to a clear plan. Press Next."),
        "language": ("Pick your language", "English, தமிழ், हिन्दी or తెలుగు. The whole app — and this tour — switches instantly. Try it now: this bubble will change too."),
        "pages": ("Your workspaces", "Profile → Documents → Schemes → Checklist → Copilot → Tasks. Follow them top to bottom, or jump anywhere."),
        "demo": ("Start with Lakshmi", "One click loads a clearly-labelled DEMO business (synthetic data) so you can explore straight away. “Reset my data” clears it."),
        "method": ("Understand → Profile → Match → Prepare → Track", "Our 5-stage method, always visible. It lights up the stage you are in."),
        "next": ("Your next best action", "Chosen by rules: the one missing fact that settles the most open eligibility questions. No guessing."),
        "agents": ("Six specialised agents", "Document, Retrieval, Eligibility, Form, Deadline and Monitoring — each a separate, tested module. Rules decide; AI explains; you act."),
        "documents": ("Upload → read → confirm", "Three separate states. Nothing reaches your profile until you confirm each value, and mismatches are flagged, never overwritten."),
        "schemes": ("Rules decide", "Every scheme is checked criterion by criterion, with sources. Scroll to the what-if explorer to see exactly where a verdict flips."),
        "copilot": ("Ask in your language", "Grounded answers with sources and a module trace. Out-of-scope questions get an honest “I can’t find this”, not a guess."),
        "controls": ("Light / dark & help", "Switch the theme here. The ⓘ button reopens this tour or explains the page you are on."),
        "finish": ("You’re ready 🎉", "Try it: Load demo → Documents (sample Udyam) → Schemes → Ask the Copilot. Nothing is ever submitted for you."),
    },
    "ta": {
        "welcome": ("MSME உதவியாளருக்கு வரவேற்கிறோம் 👋", "“உதவி வேண்டும்” என்பதிலிருந்து “அடுத்து என்ன செய்வது” என்று தெரியும் வரை. திருப்பூர் ஆடைத் தொழிலாளர் லட்சுமி எப்படி தெளிவான திட்டத்தை அடைகிறார் என்பதை ஒரு நிமிடத்தில் பாருங்கள். ‘அடுத்து’ அழுத்துங்கள்."),
        "language": ("உங்கள் மொழியைத் தேர்வு செய்யுங்கள்", "English, தமிழ், हिन्दी, తెలుగు. முழு செயலியும், இந்த வழிகாட்டியும் உடனே மாறும். இப்போதே முயற்சி செய்யுங்கள்."),
        "pages": ("உங்கள் பணிப் பகுதிகள்", "விவரம் → ஆவணங்கள் → திட்டங்கள் → பட்டியல் → உதவியாளர் → பணிகள். மேலிருந்து கீழாகப் பின்பற்றலாம்; எங்கு வேண்டுமானாலும் செல்லலாம்."),
        "demo": ("லட்சுமியுடன் தொடங்குங்கள்", "ஒரே கிளிக்கில் தெளிவாக ‘டெமோ’ எனக் குறிக்கப்பட்ட மாதிரி தொழில் ஏற்றப்படும் (செயற்கைத் தரவு). ‘என் தரவை அழி’ அதை நீக்கும்."),
        "method": ("புரிந்துகொள் → விவரம் → பொருத்து → தயாரி → கண்காணி", "எங்கள் 5 படி முறை எப்போதும் தெரியும்; நீங்கள் இருக்கும் படி ஒளிரும்."),
        "next": ("உங்கள் அடுத்த சிறந்த செயல்", "விதிகளால் தேர்வு செய்யப்படுகிறது: அதிகத் தகுதிக் கேள்விகளைத் தீர்க்கும் ஒரே விடுபட்ட தகவல். ஊகம் இல்லை."),
        "agents": ("ஆறு சிறப்புத் தொகுதிகள்", "ஆவணம், தேடல், தகுதி, படிவம், காலக்கெடு, கண்காணிப்பு — ஒவ்வொன்றும் தனியாகச் சோதிக்கப்பட்டது. விதிகள் முடிவு செய்யும்; AI விளக்கும்; நீங்கள் செயல்படுவீர்கள்."),
        "documents": ("பதிவேற்று → படி → உறுதி செய்", "மூன்று தனி நிலைகள். நீங்கள் உறுதி செய்யும் வரை எதுவும் உங்கள் விவரத்தில் சேராது; முரண்பாடுகள் குறிக்கப்படும், மேலெழுதப்படாது."),
        "schemes": ("விதிகளே முடிவு செய்கின்றன", "ஒவ்வொரு திட்டமும் நிபந்தனை வாரியாக, ஆதாரங்களுடன் சோதிக்கப்படுகிறது. 'என்ன ஆகும்' பகுதியில் முடிவு எங்கு மாறுகிறது எனப் பாருங்கள்."),
        "copilot": ("உங்கள் மொழியில் கேளுங்கள்", "ஆதாரங்களுடனும் தொகுதி தடத்துடனும் பதில்கள். எல்லைக்கு வெளியே கேள்விக்கு ஊகம் அல்ல, ‘இது கிடைக்கவில்லை’ என நேர்மையான பதில்."),
        "controls": ("ஒளி / இருள் & உதவி", "தீமை இங்கே மாற்றலாம். ⓘ பொத்தான் இந்த வழிகாட்டியை மீண்டும் திறக்கும் அல்லது தற்போதைய பக்கத்தை விளக்கும்."),
        "finish": ("நீங்கள் தயார் 🎉", "முயற்சி செய்யுங்கள்: டெமோ ஏற்று → ஆவணங்கள் → திட்டங்கள் → உதவியாளரிடம் கேளுங்கள். உங்கள் சார்பில் எதுவும் சமர்ப்பிக்கப்படாது."),
    },
    "hi": {
        "welcome": ("MSME कोपायलट में स्वागत है 👋", "“मुझे मदद चाहिए” से “अब आगे क्या करना है” तक। एक मिनट में देखें कि तिरुप्पुर की गारमेंट निर्माता लक्ष्मी कैसे उलझन से साफ़ योजना तक पहुँचती हैं। ‘आगे’ दबाएँ।"),
        "language": ("अपनी भाषा चुनें", "English, தமிழ், हिन्दी या తెలుగు। पूरा ऐप और यह टूर तुरंत बदल जाता है। अभी आज़माएँ।"),
        "pages": ("आपके कार्य-क्षेत्र", "प्रोफ़ाइल → दस्तावेज़ → योजनाएँ → चेकलिस्ट → कोपायलट → कार्य। ऊपर से नीचे चलें या कहीं भी जाएँ।"),
        "demo": ("लक्ष्मी से शुरू करें", "एक क्लिक में साफ़ ‘डेमो’ चिह्नित नमूना व्यवसाय (कृत्रिम डेटा) लोड होता है। ‘मेरा डेटा रीसेट करें’ इसे हटा देता है।"),
        "method": ("समझें → प्रोफ़ाइल → मिलान → तैयारी → ट्रैक", "हमारी 5-चरण पद्धति हमेशा दिखती है; आप जिस चरण में हैं वह चमकता है।"),
        "next": ("आपका अगला सर्वोत्तम कदम", "नियमों से चुना गया: वह एक छूटी जानकारी जो सबसे ज़्यादा पात्रता-प्रश्न सुलझाती है। कोई अनुमान नहीं।"),
        "agents": ("छह विशेष एजेंट", "दस्तावेज़, खोज, पात्रता, फ़ॉर्म, समय-सीमा और निगरानी — हर एक अलग, परीक्षित मॉड्यूल। नियम तय करते हैं; AI समझाता है; आप कार्रवाई करते हैं।"),
        "documents": ("अपलोड → पढ़ें → पुष्टि करें", "तीन अलग अवस्थाएँ। आपकी पुष्टि के बिना कुछ भी प्रोफ़ाइल में नहीं जुड़ता; असंगति चिह्नित होती है, अधिलेखित नहीं।"),
        "schemes": ("नियम तय करते हैं", "हर योजना मानदंड-दर-मानदंड, स्रोतों के साथ जाँची जाती है। ‘क्या होगा अगर’ में देखें कि निर्णय कहाँ बदलता है।"),
        "copilot": ("अपनी भाषा में पूछें", "स्रोतों और मॉड्यूल-ट्रेस के साथ उत्तर। दायरे से बाहर के प्रश्न पर अनुमान नहीं, ईमानदार “यह नहीं मिला”।"),
        "controls": ("लाइट / डार्क और मदद", "थीम यहाँ बदलें। ⓘ बटन यह टूर फिर खोलता है या मौजूदा पेज समझाता है।"),
        "finish": ("आप तैयार हैं 🎉", "आज़माएँ: डेमो लोड → दस्तावेज़ → योजनाएँ → कोपायलट से पूछें। आपकी ओर से कुछ भी जमा नहीं किया जाता।"),
    },
    "te": {
        "welcome": ("MSME కోపైలట్‌కు స్వాగతం 👋", "“సహాయం కావాలి” నుండి “తర్వాత ఏమి చేయాలో తెలుసు” వరకు. తిరుప్పూర్ గార్మెంట్ తయారీదారు లక్ష్మి గందరగోళం నుండి స్పష్టమైన ప్రణాళికకు ఎలా చేరుతుందో ఒక నిమిషంలో చూడండి. ‘తదుపరి’ నొక్కండి."),
        "language": ("మీ భాషను ఎంచుకోండి", "English, தமிழ், हिन्दी లేదా తెలుగు. మొత్తం యాప్, ఈ టూర్ వెంటనే మారతాయి. ఇప్పుడే ప్రయత్నించండి."),
        "pages": ("మీ పని విభాగాలు", "ప్రొఫైల్ → పత్రాలు → పథకాలు → చెక్‌లిస్ట్ → కోపైలట్ → పనులు. పై నుండి కిందికి వెళ్లండి లేదా ఎక్కడికైనా వెళ్లండి."),
        "demo": ("లక్ష్మితో ప్రారంభించండి", "ఒక్క క్లిక్‌తో స్పష్టంగా ‘డెమో’ అని గుర్తించిన నమూనా వ్యాపారం (కృత్రిమ డేటా) లోడ్ అవుతుంది. ‘నా డేటాను రీసెట్ చేయి’ దానిని తొలగిస్తుంది."),
        "method": ("అర్థం చేసుకో → ప్రొఫైల్ → సరిపోల్చు → సిద్ధం → ట్రాక్", "మా 5 దశల పద్ధతి ఎప్పుడూ కనిపిస్తుంది; మీరు ఉన్న దశ వెలుగుతుంది."),
        "next": ("మీ తదుపరి ఉత్తమ చర్య", "నియమాల ద్వారా ఎంపిక: ఎక్కువ అర్హత ప్రశ్నలను పరిష్కరించే ఒక్క లోపించిన సమాచారం. ఊహ లేదు."),
        "agents": ("ఆరు ప్రత్యేక ఏజెంట్లు", "పత్రం, శోధన, అర్హత, ఫారం, గడువు, పర్యవేక్షణ — ప్రతిదీ వేరుగా పరీక్షించిన మాడ్యూల్. నియమాలు నిర్ణయిస్తాయి; AI వివరిస్తుంది; మీరు చర్య తీసుకుంటారు."),
        "documents": ("అప్‌లోడ్ → చదువు → నిర్ధారించు", "మూడు వేర్వేరు దశలు. మీరు నిర్ధారించే వరకు ఏదీ ప్రొఫైల్‌లో చేరదు; తేడాలు గుర్తించబడతాయి, ఓవర్‌రైట్ కావు."),
        "schemes": ("నియమాలే నిర్ణయిస్తాయి", "ప్రతి పథకం ప్రమాణం వారీగా, ఆధారాలతో తనిఖీ అవుతుంది. ‘ఏమైతే’ విభాగంలో నిర్ణయం ఎక్కడ మారుతుందో చూడండి."),
        "copilot": ("మీ భాషలో అడగండి", "ఆధారాలు, మాడ్యూల్ ట్రేస్‌తో సమాధానాలు. పరిధి వెలుపల ప్రశ్నకు ఊహ కాదు, నిజాయితీగా “ఇది దొరకలేదు”."),
        "controls": ("లైట్ / డార్క్ & సహాయం", "థీమ్‌ను ఇక్కడ మార్చండి. ⓘ బటన్ ఈ టూర్‌ను మళ్లీ తెరుస్తుంది లేదా ప్రస్తుత పేజీని వివరిస్తుంది."),
        "finish": ("మీరు సిద్ధం 🎉", "ప్రయత్నించండి: డెమో లోడ్ → పత్రాలు → పథకాలు → కోపైలట్‌ను అడగండి. మీ తరఫున ఏదీ సమర్పించబడదు."),
    },
}

UI = {
    "en": {"next": "Next", "back": "Back", "skip": "Skip tour", "finish": "Finish", "step": "Step {n} of {total}", "tour": "Guided tour",
           "about": "About this page", "theme_dark": "Switch to dark theme", "theme_light": "Switch to light theme", "info": "Help & tour",
           "waiting": "Opening the page…", "close": "Close", "no_info": "Open a page to see what it does."},
    "ta": {"next": "அடுத்து", "back": "பின்", "skip": "வழிகாட்டியைத் தவிர்", "finish": "முடி", "step": "படி {n} / {total}", "tour": "வழிகாட்டி",
           "about": "இந்தப் பக்கம் பற்றி", "theme_dark": "இருள் தீமுக்கு மாறு", "theme_light": "ஒளி தீமுக்கு மாறு", "info": "உதவி & வழிகாட்டி",
           "waiting": "பக்கம் திறக்கிறது…", "close": "மூடு", "no_info": "பக்கத்தைத் திறந்தால் விளக்கம் தெரியும்."},
    "hi": {"next": "आगे", "back": "पीछे", "skip": "टूर छोड़ें", "finish": "समाप्त", "step": "चरण {n} / {total}", "tour": "गाइडेड टूर",
           "about": "इस पेज के बारे में", "theme_dark": "डार्क थीम पर जाएँ", "theme_light": "लाइट थीम पर जाएँ", "info": "मदद और टूर",
           "waiting": "पेज खुल रहा है…", "close": "बंद करें", "no_info": "विवरण देखने के लिए कोई पेज खोलें।"},
    "te": {"next": "తదుపరి", "back": "వెనుకకు", "skip": "టూర్ దాటవేయి", "finish": "ముగించు", "step": "దశ {n} / {total}", "tour": "గైడెడ్ టూర్",
           "about": "ఈ పేజీ గురించి", "theme_dark": "డార్క్ థీమ్‌కు మారండి", "theme_light": "లైట్ థీమ్‌కు మారండి", "info": "సహాయం & టూర్",
           "waiting": "పేజీ తెరుచుకుంటోంది…", "close": "మూసివేయి", "no_info": "వివరణ చూడటానికి ఒక పేజీ తెరవండి."},
}


def steps_for(lang: str) -> list[dict]:
    """Localised step list for the JS engine (falls back to English per step)."""
    text = TEXT.get(lang) or TEXT["en"]
    out = []
    for sid, page, sel, place in STEP_DEFS:
        title, body = text.get(sid) or TEXT["en"][sid]
        out.append({"id": sid, "page": page, "sel": sel, "place": place, "title": title, "text": body})
    return out
