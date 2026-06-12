export type Lang = "en" | "hi";

export type UiStrings = {
  nav: {
    references: string;
    browseLaws: string;
    askNyaya: string;
    live: string;
    tagline: string;
    brand: string;
  };
  home: {
    heroTitle: string;
    heroLead: string;
    heroDbNote: string;
    step1Label: string;
    step1Title: string;
    step1Body: string;
    step2Label: string;
    step2Title: string;
    step2Body: string;
    step3Label: string;
    step3Title: string;
    step3Body: string;
    trustPill1: string;
    trustPill2: string;
    trustPill3: string;
    composerHint: string;
    refLinkFull: string;
    disclaimer: string;
    assistantBadge: string;
    assistantTitle: string;
    assistantSubtitle: string;
    newChat: string;
    composerPlaceholderEmpty: string;
    composerPlaceholderFollowUp: string;
    composerHintEmpty: string;
    composerHintActive: string;
    loadingLine: string;
    floatingLabel: string;
    floatingSr: string;
  };
  chat: {
    sectionsFound: string;
    sectionsFoundOne: string;
  };
  categoryGrid: {
    title: string;
    subtitleHtml: string;
    insertCta: string;
    cats: Record<
      string,
      { label: string; desc: string; insert: string; example: string }
    >;
  };
  trustedPanel: {
    inlineTitle: string;
    chatToggle: string;
    booksLabel: string;
    footnote: string;
  };
  references: {
    back: string;
    badge: string;
    title: string;
    intro: string;
    officialHeading: string;
    academicHeading: string;
    academicIntro: string;
    booksHeading: string;
    booksIntro: string;
    techHeading: string;
    disclaimer: string;
    bookmarksHeading: string;
    bookmarksEmpty: string;
    bookmarkAdd: string;
    bookmarkRemove: string;
    techItems: Record<string, { title: string; detail: string }>;
  };
  lawyers: {
    title: string;
    subtitle: string;
    verified: string;
    exp: string;
    connect: string;
    modalTitle: string;
    modalSubtitle: string;
    formName: string;
    formPhone: string;
    formSummary: string;
    formSubmit: string;
    successTitle: string;
    successBody: string;
  };
  fir: {
    title: string;
    subtitle: string;
    formComplainant: string;
    formDate: string;
    formPlace: string;
    formAccused: string;
    formNarrative: string;
    formSubmit: string;
    disclaimer: string;
    preview: string;
    download: string;
  };
};

const en: UiStrings = {
  nav: {
    references: "References",
    browseLaws: "Browse Laws",
    askNyaya: "Ask Nyaya",
    live: "Live",
    tagline: "Your facts · eligible Acts · next steps",
    brand: "Nyaya",
  },
  home: {
    heroTitle: "Legal clarity for every Indian household",
    heroLead:
      "Type what happened in your own words. Nyaya searches our database for matching Acts and sections, explains them plainly, and outlines practical next steps. Nothing is sent until you press Send.",
    heroDbNote:
      "Indexed today: BNS 2023 · Constitution (Part III) · Consumer Protection Act 2019",
    step1Label: "Step 1",
    step1Title: "Your narrative",
    step1Body:
      "Who, what, when, and what outcome you need (eviction, refund, FIR, etc.).",
    step2Label: "Step 2",
    step2Title: "Eligible provisions",
    step2Body:
      "Matched sections with plain-language notes and badges (bailable, cognizable, court).",
    step3Label: "Step 3",
    step3Title: "Process map",
    step3Body:
      "High-level forums and steps — always confirm with a qualified advocate.",
    trustPill1: "Database-grounded",
    trustPill2: "Citizens & lawyers",
    trustPill3: "Official links in answers",
    composerHint:
      "Type below — or tap an example to paste text you can edit before sending.",
    refLinkFull:
      "Full list: courts, Law Commission, debates, books & roadmap →",
    disclaimer:
      "Nyaya shares legal information, not legal advice. Consult a qualified advocate for your situation.",
    assistantBadge: "Nyaya Assistant",
    assistantTitle: "Ask in plain language",
    assistantSubtitle:
      "Hindi or English · multiline · Enter to send · Shift+Enter for new line",
    newChat: "New conversation",
    composerPlaceholderEmpty:
      "Describe your situation… Who did what, when, and what you want to know.",
    composerPlaceholderFollowUp:
      "Follow-up or more detail… (Enter to send, Shift+Enter for new line)",
    composerHintEmpty:
      "Enter sends · Shift+Enter new line · Examples are drafts until you edit & send",
    composerHintActive:
      "Enter sends · Shift+Enter new line · Verify facts on official portals",
    loadingLine: "Searching the legal database…",
    floatingLabel: "Ask Nyaya",
    floatingSr: "Open legal assistant chat",
  },
  chat: {
    sectionsFound: "relevant sections found",
    sectionsFoundOne: "relevant section found",
  },
  categoryGrid: {
    title: "Example starters (not auto-sent)",
    subtitleHtml:
      'Tap one to <strong>insert text below</strong> — edit to match <em>your</em> facts, then press <span class="font-semibold text-amber-900">Send</span>. Nothing is sent until you choose.',
    insertCta: "Insert example →",
    cats: {
      criminal: {
        label: "Criminal Law",
        desc: "Murder, theft, assault, fraud, rape",
        insert: "Insert example →",
        example:
          "Someone stole my phone at the market yesterday. What offence is this and can I file an FIR?",
      },
      constitutional: {
        label: "Constitutional Rights",
        desc: "Fundamental rights, arrest, detention",
        insert: "Insert example →",
        example:
          "Police arrested me without telling me why. What are my constitutional rights?",
      },
      consumer: {
        label: "Consumer Rights",
        desc: "Defective goods, refunds, complaints",
        insert: "Insert example →",
        example:
          "I bought a defective phone and the shop refuses a refund. What can I do under consumer law?",
      },
      family: {
        label: "Family & Marriage",
        desc: "Divorce, dowry, domestic violence",
        insert: "Insert example →",
        example: "My husband beats me daily. What legal protection can I get?",
      },
      property: {
        label: "Property Law",
        desc: "Land disputes, tenants, eviction",
        insert: "Insert example →",
        example:
          "My landlord is trying to evict me without notice. What are my rights as a tenant?",
      },
      labour: {
        label: "Labour & Employment",
        desc: "Termination, unpaid wages",
        insert: "Insert example →",
        example:
          "My company terminated me without notice and has not paid my last salary. What can I do?",
      },
      cyber: {
        label: "Cyber Crime",
        desc: "Online fraud, harassment, extortion",
        insert: "Insert example →",
        example:
          "Someone is blackmailing me with edited photos on WhatsApp. Which cyber laws apply?",
      },
      other: {
        label: "Other Laws",
        desc: "RTI, environment, tax, IPR",
        insert: "Insert example →",
        example:
          "I want information from a government office about road construction funds. How do I file RTI?",
      },
    },
  },
  trustedPanel: {
    inlineTitle: "Official & academic sources",
    chatToggle: "Verify on trusted sources (Constitution, Bare Acts, courts…)",
    booksLabel: "Suggested commentaries (purchase / library)",
    footnote:
      "Nyaya does not host copyrighted treatises. Use official portals for Bare Acts; borrow standard books for depth.",
  },
  references: {
    back: "Back to Nyaya",
    badge: "References",
    title: "Trusted legal references",
    intro:
      "Use these alongside Nyaya. The assistant only cites sections present in our database; for judgments, journals, and full Bare Acts, use the original publisher or official portal.",
    officialHeading: "Official & court sources",
    academicHeading: "Research papers, syllabi & journals",
    academicIntro:
      "University syllabi and NLU reading lists change yearly — always use the official PDF from your faculty. For papers and theses, prefer institutional repositories.",
    booksHeading: "Suggested reference books",
    booksIntro:
      "Standard Indian commentaries — obtain through publishers or your college library.",
    techHeading: "Platform roadmap (technical)",
    disclaimer:
      "Nyaya provides legal information, not legal advice. Third-party links are for convenience; we do not control those sites.",
    bookmarksHeading: "Saved links",
    bookmarksEmpty: "Star any link below to save it on this device.",
    bookmarkAdd: "Save link",
    bookmarkRemove: "Remove",
    techItems: {
      "Responsive UI": {
        title: "Responsive UI",
        detail: "Mobile-first layouts for chat, acts browser, and reference hub.",
      },
      "Fast document indexing & search": {
        title: "Fast document indexing & search",
        detail: "Server-side indexing of Bare Acts and notes as the corpus grows.",
      },
      "PDF upload & text extraction": {
        title: "PDF upload & text extraction",
        detail: "Secure pipeline for syllabi/judgments with OCR where needed.",
      },
      "AI-generated summaries": {
        title: "AI-generated summaries",
        detail: "Grounded summaries only from uploaded or licensed corpora.",
      },
      "Secure authentication & cloud progress": {
        title: "Secure authentication & cloud progress",
        detail: "Accounts for bookmarks, annotations, and revision streaks.",
      },
      "API integration for legal databases": {
        title: "API integration for legal databases",
        detail: "Optional connectors to licensed providers under institutional keys.",
      },
      "Offline reading": {
        title: "Offline reading",
        detail: "Cached articles and PWA-style reading lists for low connectivity.",
      },
    },
  },
  lawyers: {
    title: "Verified Lawyer Directory",
    subtitle: "Connect with specialized advocates for consultation and representation.",
    verified: "VERIFIED",
    exp: "Years Experience",
    connect: "Connect with Advocate",
    modalTitle: "Consult with Expert",
    modalSubtitle: "Briefly share your situation to get a call back.",
    formName: "Your Name",
    formPhone: "Phone Number",
    formSummary: "Query Summary",
    formSubmit: "Submit Inquiry",
    successTitle: "Request Sent!",
    successBody: "The advocate has received your inquiry and will contact you shortly.",
  },
  fir: {
    title: "FIR Draft Generator",
    subtitle: "Fill in the details to generate a formal FIR draft for police filing.",
    formComplainant: "Complainant Name",
    formDate: "Date of Incident",
    formPlace: "Place of Incident",
    formAccused: "Accused Details (if known)",
    formNarrative: "Incident Narrative (Describe what happened)",
    formSubmit: "Generate Formal Draft",
    disclaimer: "Disclaimer: This tool uses AI to structure your information. It is NOT a substitute for legal advice.",
    preview: "Draft Preview",
    download: "Download .txt",
  },
};

const hi: UiStrings = {
  nav: {
    references: "संदर्भ",
    browseLaws: "कानून ब्राउज़ करें",
    askNyaya: "न्याय से पूछें",
    live: "लाइव",
    tagline: "आपके तथ्य · लागू अधिनियम · अगले कदम",
    brand: "न्याय",
  },
  home: {
    heroTitle: "हर भारतीय परिवार के लिए कानूनी स्पष्टता",
    heroLead:
      "जो हुआ उसे अपने शब्दों में लिखें। न्याय हमारे डेटाबेस से मेल खाते अधिनियम व धाराएँ ढूँढता है, सरल भाषा में समझाता है, और व्यावहारिक अगले कदम बताता है। तब तक कुछ नहीं भेजा जाता जब तक आप सेंड न दबाएँ।",
    heroDbNote:
      "आज अनुक्रमित: BNS 2023 · संविधान (भाग III) · उपभोक्ता संरक्षण अधिनियम 2019",
    step1Label: "चरण 1",
    step1Title: "आपकी कहानी",
    step1Body: "कौन, क्या, कब, और आपको क्या परिणाम चाहिए (बेदखली, रिफंड, FIR आदि)।",
    step2Label: "चरण 2",
    step2Title: "लागू प्रावधान",
    step2Body:
      "मिलान धाराएँ सरल नोट व बैज के साथ (जमानती, संज्ञेय, न्यायालय)।",
    step3Label: "चरण 3",
    step3Title: "प्रक्रिया मानचित्र",
    step3Body:
      "मंच व कदम — अंतिम राय हेतु योग्य वकील से अवश्य पुष्टि करें।",
    trustPill1: "डेटाबेस आधारित",
    trustPill2: "नागरिक व वकील",
    trustPill3: "उत्तरों में आधिकारिक लिंक",
    composerHint:
      "नीचे लिखें — या उदाहरण टैप कर पाठ चिपकाएँ, भेजने से पहले संपादित करें।",
    refLinkFull:
      "पूरी सूची: न्यायालय, विधि आयोग, बहस, पुस्तकें व रोडमैप →",
    disclaimer:
      "न्याय कानूनी जानकारी देता है, वकील की सलाह नहीं। अपने मामले हेतु योग्य वकील से संपर्क करें।",
    assistantBadge: "न्याय सहायक",
    assistantTitle: "सरल भाषा में पूछें",
    assistantSubtitle:
      "हिंदी या अंग्रेज़ी · कई पंक्तियाँ · भेजने हेतु Enter · नई पंक्ति हेतु Shift+Enter",
    newChat: "नई बातचीत",
    composerPlaceholderEmpty:
      "अपनी स्थिति लिखें… किसने क्या कब किया, और आप क्या जानना चाहते हैं।",
    composerPlaceholderFollowUp:
      "फॉलो-अप या विवरण… (Enter भेजने हेतु, Shift+Enter नई पंक्ति)",
    composerHintEmpty:
      "Enter भेजता है · Shift+Enter नई पंक्ति · उदाहरण संपादन के बाद ही भेजें",
    composerHintActive:
      "Enter भेजता है · Shift+Enter नई पंक्ति · आधिकारिक पोर्टल पर सत्यापित करें",
    loadingLine: "कानूनी डेटाबेस खोजा जा रहा है…",
    floatingLabel: "न्याय से पूछें",
    floatingSr: "कानूनी सहायक चैट खोलें",
  },
  chat: {
    sectionsFound: "प्रासंगिक धाराएँ मिलीं",
    sectionsFoundOne: "प्रासंगिक धारा मिली",
  },
  categoryGrid: {
    title: "उदाहरण प्रारंभ (स्वतः नहीं भेजे जाते)",
    subtitleHtml:
      'नीचे <strong>पाठ डालने</strong> के लिए एक टैप करें — <em>अपने</em> तथ्यों से मिलाएँ, फिर <span class="font-semibold text-amber-900">सेंड</span> दबाएँ। आपके चुनाव के बिना कुछ नहीं जाता।',
    insertCta: "उदाहरण डालें →",
    cats: {
      criminal: {
        label: "आपराधिक कानून",
        desc: "हत्या, चोरी, मारपीट, धोखाधड़ी, बलात्कार",
        insert: "उदाहरण डालें →",
        example:
          "कल बाज़ार में किसी ने मेरा फोन चुरा लिया। यह कौन सा अपराध है और क्या मैं FIR दर्ज करा सकती हूँ?",
      },
      constitutional: {
        label: "संवैधानिक अधिकार",
        desc: "मूल अधिकार, गिरफ्तारी, हिरासत",
        insert: "उदाहरण डालें →",
        example:
          "पुलिस ने मुझे बिना कारण बताए गिरफ्तार कर लिया। मेरे संवैधानिक अधिकार क्या हैं?",
      },
      consumer: {
        label: "उपभोक्ता अधिकार",
        desc: "खराब सामान, रिफंड, शिकायत",
        insert: "उदाहरण डालें →",
        example:
          "मैंने खराब फोन खरीदा और दुकान रिफंड नहीं दे रही। उपभोक्ता कानून में मेरे क्या विकल्प हैं?",
      },
      family: {
        label: "पारिवारिक कानून",
        desc: "तलाक, दहेज, घरेलू हिंसा",
        insert: "उदाहरण डालें →",
        example: "मेरा पति रोज़ मारता है। मुझे कानूनी सुरक्षा कैसे मिल सकती है?",
      },
      property: {
        label: "संपत्ति कानून",
        desc: "ज़मीन विवाद, किरायेदार, बेदखली",
        insert: "उदाहरण डालें →",
        example:
          "मकान मालिक बिना नोटिस के मुझे निकालना चाहता है। किरायेदार के रूप में मेरे अधिकार क्या हैं?",
      },
      labour: {
        label: "श्रम व रोज़गार",
        desc: "बर्खास्तगी, अवैतनिक मजदूरी",
        insert: "उदाहरण डालें →",
        example:
          "कंपनी ने बिना नोटिस नौकरी से निकाल दिया और अंतिम वेतन नहीं दिया। मैं क्या कर सकता हूँ?",
      },
      cyber: {
        label: "साइबर अपराध",
        desc: "ऑनलाइन धोखा, उत्पीड़न, ब्लैकमेल",
        insert: "उदाहरण डालें →",
        example:
          "कोई WhatsApp पर एडिट की हुई तस्वीरों से ब्लैकमेल कर रहा है। कौन से साइबर कानून लागू होते हैं?",
      },
      other: {
        label: "अन्य कानून",
        desc: "RTI, पर्यावरण, कर, IPR",
        insert: "उदाहरण डालें →",
        example:
          "सड़क निर्माण धन के बारे में सरकारी कार्यालय से जानकारी चाहिए। RTI कैसे दाखिल करूँ?",
      },
    },
  },
  trustedPanel: {
    inlineTitle: "आधिकारिक व शैक्षणिक स्रोत",
    chatToggle:
      "विश्वसनीय स्रोतों पर जाँच करें (संविधान, बेयर एक्ट, न्यायालय…)",
    booksLabel: "सुझाई गई टिप्पणियाँ (खरीदें / पुस्तकालय)",
    footnote:
      "न्याय कॉपीराइट ग्रंथ होस्ट नहीं करता। बेयर एक्ट हेतु आधिकारिक पोर्टल; गहराई हेतु पुस्तकें उधार लें।",
  },
  references: {
    back: "न्याय पर वापस",
    badge: "संदर्भ",
    title: "विश्वसनीय कानूनी संदर्भ",
    intro:
      "इन्हें न्याय के उत्तरों के साथ उपयोग करें। सहायक केवल हमारे डेटाबेस की धाराएँ उद्धृत करता है; निर्णयों, पत्रिकाओं व पूर्ण बेयर एक्ट हेतु मूल प्रकाशक या आधिकारिक पोर्टल देखें।",
    officialHeading: "आधिकारिक व न्यायालय स्रोत",
    academicHeading: "शोध पत्र, पाठ्यक्रम व पत्रिकाएँ",
    academicIntro:
      "विश्वविद्यालय व NLU की पठन सूची हर वर्ष बदलती है — हमेशा संकाय का आधिकारिक PDF उपयोग करें। प्रबंधधारा हेतु संस्थागत भंडार प्राथमिकता दें।",
    booksHeading: "सुझाई गई संदर्भ पुस्तकें",
    booksIntro:
      "मानक भारतीय टिप्पणियाँ — प्रकाशकों या कॉलेज पुस्तकालय से प्राप्त करें।",
    techHeading: "मंच रोडमैप (तकनीकी)",
    disclaimer:
      "न्याय कानूनी जानकारी देता है, वकील की सलाह नहीं। तृतीय-पक्ष लिंक सुविधा हेतु हैं; हम उन साइटों को नियंत्रित नहीं करते।",
    bookmarksHeading: "सहेजे गए लिंक (इस उपकरण पर)",
    bookmarksEmpty: "नीचे किसी लिंक पर तारा दबाकर इस उपकरण पर सहेजें।",
    bookmarkAdd: "लिंक सहेजें",
    bookmarkRemove: "हटाएँ",
    techItems: {
      "Responsive UI": {
        title: "उत्तरदायी UI",
        detail: "चैट, अधिनियम ब्राउज़र व संदर्भ केंद्र हेतु मोबाइल-प्रथम लेआउट।",
      },
      "Fast document indexing & search": {
        title: "द्रुत अनुक्रमण व खोज",
        detail: "कॉर्पस बढ़ने पर बेयर एक्ट व नोट्स का सर्वर-पक्ष अनुक्रमण।",
      },
      "PDF upload & text extraction": {
        title: "PDF अपलोड व पाठ निष्कर्षण",
        detail: "पाठ्यक्रम/निर्णय हेतु सुरक्षित पाइपलाइन; आवश्यकता पर OCR।",
      },
      "AI-generated summaries": {
        title: "AI सारांश",
        detail: "केवल अपलोड या लाइसेंस प्राप्त कॉर्पस से आधारित सारांश।",
      },
      "Secure authentication & cloud progress": {
        title: "सुरक्षित प्रमाणीकरण व क्लाउड प्रगति",
        detail: "बुकमार्क, टिप्पणी व संशोधन स्ट्रीक हेतु खाते।",
      },
      "API integration for legal databases": {
        title: "कानूनी डेटाबेस API एकीकरण",
        detail: "संस्थागत कुंजी के तहत लाइसेंस प्रदाता से वैकल्पिक कनेक्टर।",
      },
      "Offline reading": {
        title: "ऑफ़लाइन पढ़ना",
        detail: "कम कनेक्टिविटी हेतु कैश लेख व PWA शैली की पठन सूची।",
      },
    },
  },
  lawyers: {
    title: "सत्यापित वकील निर्देशिका",
    subtitle: "परामर्श और प्रतिनिधित्व के लिए विशेष अधिवक्ताओं से जुड़ें।",
    verified: "सत्यापित",
    exp: "वर्षों का अनुभव",
    connect: "अधिवक्ता से जुड़ें",
    modalTitle: "विशेषज्ञ से परामर्श करें",
    modalSubtitle: "कॉल बैक प्राप्त करने के लिए संक्षेप में अपनी स्थिति साझा करें।",
    formName: "आपका नाम",
    formPhone: "फ़ोन नंबर",
    formSummary: "प्रश्न का सारांश",
    formSubmit: "पूछताछ सबमिट करें",
    successTitle: "अनुरोध भेजा गया!",
    successBody: "अधिवक्ता को आपकी पूछताछ प्राप्त हो गई है और वे शीघ्र ही आपसे संपर्क करेंगे।",
  },
  fir: {
    title: "FIR ड्राफ्ट जनरेटर",
    subtitle: "पुलिस फाइलिंग के लिए औपचारिक FIR ड्राफ्ट तैयार करने के लिए विवरण भरें।",
    formComplainant: "शिकायतकर्ता का नाम",
    formDate: "घटना की तारीख",
    formPlace: "घटना का स्थान",
    formAccused: "आरोपी का विवरण (यदि ज्ञात हो)",
    formNarrative: "घटना का विवरण (क्या हुआ बताएं)",
    formSubmit: "औपचारिक ड्राफ्ट तैयार करें",
    disclaimer: "अस्वीकरण: यह टूल आपकी जानकारी को व्यवस्थित करने के लिए AI का उपयोग करता है। यह कानूनी सलाह का विकल्प नहीं है।",
    preview: "ड्राफ्ट पूर्वावलोकन",
    download: "डाउनलोड .txt",
  },
};

export function getStrings(lang: Lang): UiStrings {
  return lang === "hi" ? hi : en;
}
