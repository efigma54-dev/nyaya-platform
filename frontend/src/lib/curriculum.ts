/**
 * Indian law curriculum metadata for the Study hub.
 * Full notes / bare-act text / papers are not bundled; links point to official portals where applicable.
 */

export type StudyModuleId =
  | "chapter-notes"
  | "bare-act"
  | "case-summaries"
  | "landmarks"
  | "articles-amendments"
  | "pyqs"
  | "mcq"
  | "flashcards"
  | "dictionary"
  | "ai-doubt";

export interface StudyModule {
  id: StudyModuleId;
  /** Implementation status in this codebase */
  status: "live" | "partial" | "planned";
  href?: string;
}

export interface LawSubject {
  slug: string;
  titleEn: string;
  titleHi: string;
  shortEn: string;
  shortHi: string;
  /** Maps to CategoryGrid / API category when applicable */
  apiCategory?: string;
  /** Substring match against Act.short_title from API (client-side) */
  actTitleHint?: string;
  modules: StudyModule[];
}

export const STUDY_MODULES_META: Record<
  StudyModuleId,
  { labelEn: string; labelHi: string }
> = {
  "chapter-notes": {
    labelEn: "Chapter-wise notes",
    labelHi: "अध्यायवार नोट्स",
  },
  "bare-act": { labelEn: "Bare Act", labelHi: "मूल कानून (बेयर एक्ट)" },
  "case-summaries": {
    labelEn: "Case law summaries",
    labelHi: "केस लॉ सारांश",
  },
  landmarks: {
    labelEn: "Landmark judgments",
    labelHi: "महत्वपूर्ण निर्णय",
  },
  "articles-amendments": {
    labelEn: "Articles & amendments",
    labelHi: "अनुच्छेद व संशोधन",
  },
  pyqs: {
    labelEn: "Previous year papers",
    labelHi: "पिछले वर्ष के प्रश्नपत्र",
  },
  mcq: { labelEn: "MCQs & quizzes", labelHi: "बहुविकल्पीय प्रश्न" },
  flashcards: { labelEn: "Flashcards", labelHi: "फ्लैशकार्ड" },
  dictionary: { labelEn: "Legal dictionary", labelHi: "कानूनी शब्दकोश" },
  "ai-doubt": {
    labelEn: "AI doubt solving",
    labelHi: "AI से संदेह निवारण",
  },
};

export const LAW_SUBJECTS: LawSubject[] = [
  {
    slug: "constitution",
    titleEn: "Indian Constitution",
    titleHi: "भारतीय संविधान",
    shortEn: "Preamble, structure, fundamental rights, duties, and amendments.",
    shortHi: "प्रस्तावना, संरचना, मूल अधिकार, कर्तव्य व संशोधन।",
    apiCategory: "constitutional",
    actTitleHint: "Constitution",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "bare-act", status: "partial", href: "https://legislative.gov.in/constitution-of-india" },
      { id: "case-summaries", status: "planned" },
      { id: "landmarks", status: "partial", href: "/learn/references#landmarks" },
      { id: "articles-amendments", status: "planned" },
      { id: "pyqs", status: "planned" },
      { id: "mcq", status: "live", href: "/learn/quiz/constitution" },
      { id: "flashcards", status: "live", href: "/learn/subjects/constitution#flashcards" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "constitutional-law",
    titleEn: "Constitutional Law",
    titleHi: "संवैधानिक विधि",
    shortEn: "Basic structure, separation of powers, judicial review.",
    shortHi: "मूल ढांचा, शक्तियों का पृथक्करण, न्यायिक समीक्षा।",
    apiCategory: "constitutional",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "bare-act", status: "partial", href: "https://legislative.gov.in/constitution-of-india" },
      { id: "landmarks", status: "partial", href: "/learn/references#landmarks" },
      { id: "mcq", status: "live", href: "/learn/quiz/constitution" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "bns",
    titleEn: "Bharatiya Nyaya Sanhita (BNS)",
    titleHi: "भारतीय न्याय संहिता",
    shortEn: "Substantive criminal law replacing the IPC (selected sections in Nyaya DB).",
    shortHi: "IPC के स्थान पर दंड संहिता (न्याय डेटाबेस में चयनित धाराएँ)।",
    apiCategory: "criminal",
    actTitleHint: "Bharatiya Nyaya",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "bare-act", status: "live", href: "/sections" },
      { id: "mcq", status: "planned" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "bnss",
    titleEn: "CrPC / Bharatiya Nagarik Suraksha Sanhita (BNSS)",
    titleHi: "दंड प्रक्रिया संहिता / भा. ना. सु. संहिता",
    shortEn: "Criminal procedure: FIR, bail, trial — align with latest BNSS study edition.",
    shortHi: "FIR, जमानत, मुकदमा — नवीनतम BNSS के अनुसार पढ़ें।",
    apiCategory: "criminal",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "bare-act", status: "partial", href: "https://legislative.gov.in/" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "bsa",
    titleEn: "Indian Evidence Act / Bharatiya Sakshya Adhiniyam (BSA)",
    titleHi: "साक्ष्य अधिनियम / भारतीय साक्ष्य अधिनियम",
    shortEn: "Relevance, admissibility, electronic evidence, burden of proof.",
    shortHi: "प्रासंगिकता, ग्राह्यता, इलेक्ट्रॉनिक साक्ष्य, साक्ष्य का भार।",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "bare-act", status: "partial", href: "https://legislative.gov.in/" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "contract",
    titleEn: "Contract Law",
    titleHi: "संविदा विधि",
    shortEn: "Offer, acceptance, consideration, breach, and remedies.",
    shortHi: "प्रस्ताव, स्वीकृति, प्रतिफल, उल्लंघन व उपचार।",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "bare-act", status: "partial", href: "https://legislative.gov.in/" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "family-law",
    titleEn: "Family Law",
    titleHi: "पारिवारिक विधि",
    shortEn: "Marriage, divorce, maintenance, and personal laws overview.",
    shortHi: "विवाह, तलाक, भरण-पोषण व व्यक्तिगत कानूनों का परिचय।",
    apiCategory: "family",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "administrative-law",
    titleEn: "Administrative Law",
    titleHi: "प्रशासनिक विधि",
    shortEn: "Delegated legislation, tribunals, natural justice, writ jurisdiction.",
    shortHi: "प्रत्यायोजित विधान, न्यायाधिकरण, प्राकृतिक न्याय, रिट क्षेत्राधिकार।",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "landmarks", status: "partial", href: "/learn/references#landmarks" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "jurisprudence",
    titleEn: "Jurisprudence",
    titleHi: "न्यायशास्त्र",
    shortEn: "Schools of thought, rights, justice, and critical legal theory basics.",
    shortHi: "विचारधाराएँ, अधिकार, न्याय व आलोचनात्मक सिद्धांत।",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "company-law",
    titleEn: "Company Law",
    titleHi: "कंपनी विधि",
    shortEn: "Incorporation, directors, meetings, oppression & mismanagement.",
    shortHi: "निगमन, निदेशक, बैठकें, उत्पीड़न व दुरप्रबंधन।",
    apiCategory: "corporate",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "bare-act", status: "partial", href: "https://legislative.gov.in/" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "cyber-law",
    titleEn: "Cyber Law",
    titleHi: "साइबर विधि",
    shortEn: "IT Act, digital evidence, intermediary liability, offences.",
    shortHi: "आईटी अधिनियम, डिजिटल साक्ष्य, मध्यस्थ दायित्व, अपराध।",
    apiCategory: "cyber",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "environmental-law",
    titleEn: "Environmental Law",
    titleHi: "पर्यावरण विधि",
    shortEn: "Pollution control, EIA, forest & wildlife statutes.",
    shortHi: "प्रदूषण नियंत्रण, पर्यावरण प्रभाव, वन व वन्यजीव कानून।",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
  {
    slug: "human-rights",
    titleEn: "Human Rights Law",
    titleHi: "मानव अधिकार विधि",
    shortEn: "UDHR, Indian charter, NHRC, and international instruments overview.",
    shortHi: "वैश्विक घोषणापत्र, भारतीय चार्टर, मा. अ. आयोग का परिचय।",
    modules: [
      { id: "chapter-notes", status: "planned" },
      { id: "dictionary", status: "live", href: "/learn/dictionary" },
      { id: "ai-doubt", status: "partial", href: "/" },
    ],
  },
];

export interface ExamTrack {
  slug: string;
  titleEn: string;
  titleHi: string;
  focusEn: string;
  focusHi: string;
  checklistEn: string[];
  checklistHi: string[];
}

export const EXAM_TRACKS: ExamTrack[] = [
  {
    slug: "clat",
    titleEn: "CLAT & law entrance",
    titleHi: "CLAT व विधि प्रवेश",
    focusEn: "Legal reasoning, constitution basics, current legal awareness.",
    focusHi: "कानूनी तर्क, संविधान, समसामयिक कानूनी जागरूकता।",
    checklistEn: [
      "Revise fundamental rights with leading cases",
      "Practice passage-based legal reasoning daily",
      "Maintain a one-page glossary of maxims",
    ],
    checklistHi: [
      "प्रमुख मामलों सहित मूल अधिकार दोहराएँ",
      "पैसेज आधारित तर्क का दैनिक अभ्यास",
      "कानूनी सूक्तियों की शब्दावली बनाए रखें",
    ],
  },
  {
    slug: "judiciary",
    titleEn: "Judiciary exams",
    titleHi: "न्यायिक सेवा परीक्षा",
    focusEn: "Bare acts, procedural codes, judgment writing, translations.",
    focusHi: "बेयर एक्ट, प्रक्रिया संहिताएँ, निर्णय लेखन, अनुवाद।",
    checklistEn: [
      "Read BNSS/BNS/BSA with section-wise notes",
      "Answer writing: issue–rule–application–conclusion",
      "Solve past papers under timed conditions",
    ],
    checklistHi: [
      "BNSS/BNS/BSA धारावार नोट्स बनाएँ",
      "लेखन: मुद्दा–नियम–प्रयोग–निष्कर्ष",
      "समयबद्ध पुराने प्रश्नपत्र हल करें",
    ],
  },
  {
    slug: "upsc-polity",
    titleEn: "UPSC Polity",
    titleHi: "UPSC राजव्यवस्था",
    focusEn: "Constitutional bodies, federalism, schemes linked to Parts of Constitution.",
    focusHi: "संवैधानिक निकाय, संघवाद, योजनाएँ व संविधान के भाग।",
    checklistEn: [
      "Laxmikanth-style outline + Nyaya Constitution MCQs",
      "Link articles to landmark judgments",
      "Map amendments to current debates",
    ],
    checklistHi: [
      "रूपरेखा + संविधान MCQ",
      "अनुच्छेदों को मील के पत्थर जोड़ें",
      "संशोधनों को चर्चा से जोड़ें",
    ],
  },
  {
    slug: "university",
    titleEn: "University semester exams",
    titleHi: "विश्वविद्यालय सेमेस्टर",
    focusEn: "Syllabus mapping, answer banks, moot & research skills.",
    focusHi: "पाठ्यक्रम मैपिंग, उत्तर बैंक, मूट व शोध कौशल।",
    checklistEn: [
      "Align modules with your faculty syllabus PDF",
      "Use flashcards for definitions and maxims",
      "Peer-review answers using the citation tool",
    ],
    checklistHi: [
      "संकाय पाठ्यक्रम से जोड़ें",
      "परिभाषाओं हेतु फ्लैशकार्ड",
      "उत्तरों का सहकर्मी समीक्षण व उद्धरण टूल",
    ],
  },
];

export interface SuggestedBook {
  author: string;
  title: string;
  areaEn: string;
}

export const SUGGESTED_BOOKS: SuggestedBook[] = [
  { author: "M.P. Jain", title: "Indian Constitutional Law", areaEn: "Constitution" },
  { author: "V.N. Shukla", title: "Constitution of India", areaEn: "Constitution" },
  { author: "D.D. Basu", title: "Introduction to the Constitution of India", areaEn: "Constitution" },
  { author: "Ratanlal & Dhirajlal", title: "Indian Penal Code / Criminal law series", areaEn: "Criminal" },
  { author: "Avtar Singh", title: "Law of Contract", areaEn: "Contract" },
  { author: "P.S.A. Pillai", title: "Criminal Law", areaEn: "Criminal" },
  { author: "Batuk Lal", title: "Criminal Procedure Code / BNSS", areaEn: "Procedure" },
  { author: "Sarkar", title: "Law of Evidence", areaEn: "Evidence" },
  { author: "H.M. Seervai", title: "Constitutional Law of India", areaEn: "Constitution" },
];

export interface TrustedReference {
  nameEn: string;
  nameHi: string;
  url: string;
  noteEn: string;
  noteHi?: string;
}

export const TRUSTED_REFERENCES: TrustedReference[] = [
  {
    nameEn: "Constitution of India (Legislative Department)",
    nameHi: "भारत का संविधान (विधायी विभाग)",
    url: "https://legislative.gov.in/constitution-of-india",
    noteEn: "Authoritative English text; use alongside Hindi version if offered on portal.",
    noteHi: "आधिकारिक अंग्रेज़ी पाठ; हिंदी संस्करण से तुलना करें।",
  },
  {
    nameEn: "India Code — Central Acts",
    nameHi: "India Code — केंद्रीय अधिनियम",
    url: "https://www.indiacode.nic.in/",
    noteEn: "Bare Acts and subordinate legislation from official sources.",
    noteHi: "आधिकारिक स्रोतों से बेयर एक्ट।",
  },
  {
    nameEn: "Supreme Court of India — Judgments",
    nameHi: "भारत का सर्वोच्च न्यायालय — निर्णय",
    url: "https://main.sci.gov.in/judgments",
    noteEn: "Official repository links; cite neutral citations when available.",
    noteHi: "आधिकारिक भंडार; neutral citation उपयोग करें।",
  },
  {
    nameEn: "Indian Kanoon — free search",
    nameHi: "Indian Kanoon — खोज",
    url: "https://indiankanoon.org/",
    noteEn: "Use for research; always verify against official reports for submissions.",
    noteHi: "शोध हेतु; प्रस्तुति से पहले आधिकारिक रिपोर्ट सत्यापित करें।",
  },
  {
    nameEn: "Law Commission of India",
    nameHi: "भारत विधि आयोग",
    url: "https://lawcommissionofindia.nic.in/",
    noteEn: "Reports and reform proposals for depth reading.",
    noteHi: "गहन अध्ययन हेतु रिपोर्ट व सुधार प्रस्ताव।",
  },
  {
    nameEn: "Parliament Digital Library / debates",
    nameHi: "संसदीय वाद-विवाद संसाधन",
    url: "https://eparlib.nic.in/",
    noteEn: "Legislative intent and speech context for interpretation courses.",
    noteHi: "व्याख्या पाठ्यक्रमों हेतु विधायी उद्देश्य।",
  },
];

export function getSubjectBySlug(slug: string): LawSubject | undefined {
  return LAW_SUBJECTS.find((s) => s.slug === slug);
}

export function getExamBySlug(slug: string): ExamTrack | undefined {
  return EXAM_TRACKS.find((e) => e.slug === slug);
}
