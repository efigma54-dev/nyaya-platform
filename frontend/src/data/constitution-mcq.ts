export interface McqItem {
  id: string;
  questionEn: string;
  questionHi: string;
  optionsEn: string[];
  optionsHi: string[];
  correctIndex: number;
  explainEn: string;
  explainHi: string;
}

export const CONSTITUTION_MCQ: McqItem[] = [
  {
    id: "fr-basic",
    questionEn: "Part III of the Constitution of India primarily deals with:",
    questionHi: "भारत के संविधान का भाग III मुख्यतः किससे संबंधित है?",
    optionsEn: [
      "Directive Principles of State Policy",
      "Fundamental Rights",
      "Fundamental Duties",
      "Union–State relations",
    ],
    optionsHi: [
      "राज्य के नीति निर्देशक तत्व",
      "मूल अधिकार",
      "मूल कर्तव्य",
      "केंद्र–राज्य संबंध",
    ],
    correctIndex: 1,
    explainEn: "Articles 12–35 cover fundamental rights enforceable by courts (subject to reasonable restrictions).",
    explainHi: "अनुच्छेद 12–35 मूल अधिकारों को कवर करते हैं जिन्हें न्यायालय लागू कर सकता है।",
  },
  {
    id: "writ-32",
    questionEn: "The right to move the Supreme Court for enforcement of Fundamental Rights is guaranteed under:",
    questionHi: "मूल अधिकारों के प्रवर्तन हेतु सर्वोच्च न्यायालय जाने का अधिकार कहाँ गारंटीकृत है?",
    optionsEn: ["Article 14", "Article 19", "Article 32", "Article 226"],
    optionsHi: ["अनुच्छेद 14", "अनुच्छेद 19", "अनुच्छेद 32", "अनुच्छेद 226"],
    correctIndex: 2,
    explainEn: "Article 32 is the ‘heart and soul’ (Dr. Ambedkar) — SC jurisdiction to issue writs.",
    explainHi: "अनुच्छेद 32 रिट जारी करने हेतु सर्वोच्च न्यायालय का क्षेत्राधिकार।",
  },
  {
    id: "basic-structure",
    questionEn: "The ‘basic structure’ doctrine limits Parliament’s power to amend the Constitution under Article 368. It was developed in:",
    questionHi: "‘मूल ढांचा’ सिद्धांत अनुच्छेद 368 के अंतर्गत संसद की शक्ति सीमित करता है। यह विकसित हुआ:",
    optionsEn: [
      "Golak Nath case",
      "Kesavananda Bharati case",
      "Minerva Mills case",
      "Indira Nehru Gandhi case",
    ],
    optionsHi: [
      "गोलक नाथ मामला",
      "केसवानंद भारती मामला",
      "मिनर्वा मिल्स मामला",
      "इंदिरा नेहरू गांधी मामला",
    ],
    correctIndex: 1,
    explainEn: "Kesavananda Bharati (1973) held that while Parliament can amend, it cannot destroy the Constitution’s basic structure.",
    explainHi: "केसवानंद भारती (1973): संसद संशोधन कर सकती है पर संविधान के मूल ढांचे को नष्ट नहीं कर सकती।",
  },
  {
    id: "equality-14",
    questionEn: "Article 14 guarantees equality before law and equal protection of laws. It permits:",
    questionHi: "अनुच्छेद 14 कानून के समक्ष समानता व कानूनों की समान सुरक्षा। यह अनुमति देता है:",
    optionsEn: [
      "Only identical treatment in all cases",
      "Reasonable classification with intelligible differentia",
      "Discrimination on any ground",
      "Exemption of government from all laws",
    ],
    optionsHi: [
      "सभी मामलों में केवल समान व्यवहार",
      "सुगम भेदभाव सहित उचित वर्गीकरण",
      "किसी भी आधार पर भेदभाव",
      "सरकार को सभी कानूनों से मुक्ति",
    ],
    correctIndex: 1,
    explainEn: "Reasonable classification (intelligible differentia + rational nexus) is consistent with Article 14.",
    explainHi: "उचित वर्गीकरण (स्पष्ट भेद + तर्कसंगत संबंध) अनुच्छेद 14 के अनुरूप है।",
  },
  {
    id: "directive-38",
    questionEn: "Directive Principles of State Policy are found in:",
    questionHi: "राज्य के नीति निर्देशक तत्व कहाँ हैं?",
    optionsEn: ["Part II", "Part IV", "Part V", "Part VI"],
    optionsHi: ["भाग II", "भाग IV", "भाग V", "भाग VI"],
    correctIndex: 1,
    explainEn: "Part IV (Articles 36–51) — guiding principles; not enforceable by courts but fundamental in governance.",
    explainHi: "भाग IV (36–51) — मार्गदर्शक सिद्धांत; न्यायालय द्वारा प्रवर्तनीय नहीं पर शासन में मौलिक।",
  },
  {
    id: "amend-368",
    questionEn: "A Constitution Amendment Bill must be passed by:",
    questionHi: "संविधान संशोधन विधेयक पारित होना चाहिए:",
    optionsEn: [
      "Simple majority in Lok Sabha only",
      "Special majority in both Houses + in some cases ratification by half the States",
      "President’s ordinance",
      "2/3 of state legislatures only",
    ],
    optionsHi: [
      "केवल लोकसभा में साधारण बहुमत",
      "दोनों सदनों में विशेष बहुमत + कुछ मामलों में आधे राज्यों की अनुमोदन",
      "राष्ट्रपति अध्यादेश",
      "केवल 2/3 राज्य विधानमंडल",
    ],
    correctIndex: 1,
    explainEn: "Article 368 procedure: special majority; federal provisions also need state ratification.",
    explainHi: "अनुच्छेद 368: विशेष बहुमत; संघीय प्रावधानों हेतु राज्य अनुमोदन भी।",
  },
  {
    id: "judicial-review",
    questionEn: "Judicial review in India is a power of courts to:",
    questionHi: "भारत में न्यायिक समीक्षा न्यायालयों की शक्ति है:",
    optionsEn: [
      "Make new laws",
      "Examine constitutionality of laws and executive actions",
      "Appoint judges",
      "Dissolve Parliament",
    ],
    optionsHi: [
      "नए कानून बनाना",
      "कानूनों व कार्यकारी क्रियाओं की संवैधानिकता जाँचना",
      "न्यायाधीश नियुक्त करना",
      "संसद भंग करना",
    ],
    correctIndex: 1,
    explainEn: "Courts can strike down legislation/executive action that violates the Constitution.",
    explainHi: "न्यायालय संविधान के विरुद्ध विधायी/कार्यकारी कार्य को अमान्य कर सकते हैं।",
  },
  {
    id: "secular",
    questionEn: "The word ‘secular’ was inserted into the Preamble by which amendment?",
    questionHi: "‘धर्मनिरपेक्ष’ शब्द प्रस्तावना में किस संशोधन से जोड़ा गया?",
    optionsEn: [
      "42nd Amendment",
      "44th Amendment",
      "73rd Amendment",
      "86th Amendment",
    ],
    optionsHi: [
      "42वाँ संशोधन",
      "44वाँ संशोधन",
      "73वाँ संशोधन",
      "86वाँ संशोधन",
    ],
    correctIndex: 0,
    explainEn: "42nd Amendment (1976) also added ‘socialist’ and ‘integrity’ to the Preamble.",
    explainHi: "42वें संशोधन (1976) में ‘समाजवादी’ व ‘अखंडता’ भी जोड़े गए।",
  },
];
