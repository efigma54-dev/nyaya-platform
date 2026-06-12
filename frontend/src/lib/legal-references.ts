/**
 * Curated trusted and academic pointers (URLs only; no reproduced text).
 * Shown on /references and in chat footers to strengthen research hygiene.
 */

export interface OfficialSource {
  id: string;
  title: string;
  description: string;
  href: string;
  titleHi?: string;
  descriptionHi?: string;
}

export const OFFICIAL_LEGAL_SOURCES: OfficialSource[] = [
  {
    id: "constitution",
    title: "Constitution of India (official text)",
    description:
      "Authoritative Constitution as published by the Legislative Department.",
    titleHi: "भारत का संविधान (आधिकारिक पाठ)",
    descriptionHi: "विधायी विभाग द्वारा प्रकाशित प्रामाणिक संविधान पाठ।",
    href: "https://legislative.gov.in/constitution-of-india",
  },
  {
    id: "india-code",
    title: "India Code — central Bare Acts",
    description: "Consolidated central Acts and subordinate legislation from official sources.",
    titleHi: "India Code — केंद्रीय बेयर एक्ट",
    descriptionHi: "आधिकारिक स्रोतों से केंद्रीय अधिनियम व अधीनस्थ विधान।",
    href: "https://www.indiacode.nic.in/",
  },
  {
    id: "sci-judgments",
    title: "Supreme Court of India — judgments",
    description: "Official judgment portal; prefer neutral citations where listed.",
    titleHi: "भारत का सर्वोच्च न्यायालय — निर्णय",
    descriptionHi: "आधिकारिक निर्णय पोर्टल; neutral citation प्राथमिकता दें।",
    href: "https://main.sci.gov.in/judgments",
  },
  {
    id: "ecourts",
    title: "eCourts / High Court portals",
    description: "Case status and cause lists; use your state High Court’s official site for judgments.",
    titleHi: "eCourts / उच्च न्यायालय पोर्टल",
    descriptionHi: "मुकदमा स्थिति व कारण सूची; निर्णय हेतु अपने राज्य के उच्च न्यायालय की आधिकारिक साइट।",
    href: "https://ecourts.gov.in/",
  },
  {
    id: "law-commission",
    title: "Law Commission of India — reports",
    description: "Reform proposals and in-depth law commission reports for essays and exams.",
    titleHi: "भारत विधि आयोग — रिपोर्ट",
    descriptionHi: "सुधार प्रस्ताव व गहन विधि आयोग रिपोर्ट — निबंध व परीक्षा हेतु।",
    href: "https://lawcommissionofindia.nic.in/",
  },
  {
    id: "eparlib",
    title: "Parliament Digital Library — debates",
    description: "Hansard-style material for legislative intent and polity answers.",
    titleHi: "संसद डिजिटल पुस्तकालय — बहस",
    descriptionHi: "विधायी उद्देश्य व राजव्यवस्था उत्तरों हेतु हैन्सर्ड शैली सामग्री।",
    href: "https://eparlib.nic.in/",
  },
  {
    id: "indiankanoon",
    title: "Indian Kanoon — search",
    description: "Free full-text search; cross-check holdings against official reports before filing.",
    titleHi: "Indian Kanoon — खोज",
    descriptionHi: "मुफ्त पूर्ण पाठ खोज; दाखिल करने से पहले आधिकारिक रिपोर्ट से क्रॉस-चेक करें।",
    href: "https://indiankanoon.org/",
  },
];

/** Pointers for papers, syllabi, journals — not full content. */
export const ACADEMIC_RESEARCH_POINTERS: OfficialSource[] = [
  {
    id: "shodhganga",
    title: "Shodhganga — PhD theses (INFLIBNET)",
    description: "Indian doctoral theses; useful for literature review and footnotes.",
    titleHi: "शोधगंगा — पीएचडी प्रबंधधारा (INFLIBNET)",
    descriptionHi: "भारतीय डॉक्टरेट प्रबंधधारा; साहित्य समीक्षा व फुटनोट हेतु उपयोगी।",
    href: "https://shodhganga.inflibnet.ac.in/",
  },
  {
    id: "ssc",
    title: "SCC Online / Eastern Book (commercial)",
    description: "Paid case law databases widely used in practice; use through library access where available.",
    titleHi: "SCC Online / Eastern Book (वाणिज्यिक)",
    descriptionHi: "व्यापक उपयोग वाले सशुल्क केस लॉ डेटाबेस; उपलब्ध हो तो पुस्तकालय पहुँच से।",
    href: "https://www.scconline.com/",
  },
  {
    id: "ili",
    title: "Indian Law Institute",
    description: "Research, training, and publications — check library and journal access.",
    titleHi: "भारतीय विधि संस्थान",
    descriptionHi: "अनुसंधान, प्रशिक्षण व प्रकाशन — पुस्तकालय व पत्रिका पहुँच देखें।",
    href: "https://www.ili.ac.in/",
  },
  {
    id: "ugc",
    title: "UGC — regulations & learning resources",
    description: "Policy context for higher education; pair with your university’s official syllabus PDF.",
    titleHi: "UGC — नियम व शिक्षण संसाधन",
    descriptionHi: "उच्च शिक्षा हेतु नीति संदर्भ; विश्वविद्यालय के आधिकारिक पाठ्यक्रम PDF के साथ।",
    href: "https://www.ugc.gov.in/",
  },
];

export interface ReferenceBook {
  author: string;
  title: string;
}

export const SUGGESTED_REFERENCE_BOOKS: ReferenceBook[] = [
  { author: "M.P. Jain", title: "Indian Constitutional Law" },
  { author: "V.N. Shukla", title: "Constitution of India" },
  { author: "D.D. Basu", title: "Introduction to the Constitution of India" },
  { author: "Ratanlal & Dhirajlal", title: "Law books series" },
  { author: "Avtar Singh", title: "Law of Contract" },
  { author: "P.S.A. Pillai", title: "Criminal Law" },
  { author: "Batuk Lal", title: "Criminal Procedure Code" },
  { author: "Sarkar", title: "Law of Evidence" },
  { author: "H.M. Seervai", title: "Constitutional Law of India" },
];

export const TECHNICAL_ROADMAP = [
  {
    title: "Responsive UI",
    detail: "Mobile-first layouts for chat, acts browser, and reference hub.",
  },
  {
    title: "Fast document indexing & search",
    detail: "Server-side indexing of Bare Acts and notes as the corpus grows.",
  },
  {
    title: "PDF upload & text extraction",
    detail: "Secure pipeline for syllabi/judgments with OCR where needed.",
  },
  {
    title: "AI-generated summaries",
    detail: "Grounded summaries only from uploaded or licensed corpora.",
  },
  {
    title: "Secure authentication & cloud progress",
    detail: "Accounts for bookmarks, annotations, and revision streaks.",
  },
  {
    title: "API integration for legal databases",
    detail: "Optional connectors to licensed providers under institutional keys.",
  },
  {
    title: "Offline reading",
    detail: "Cached articles and PWA-style reading lists for low connectivity.",
  },
] as const;
