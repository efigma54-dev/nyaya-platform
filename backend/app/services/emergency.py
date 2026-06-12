# backend/app/services/emergency.py
# Detects legal emergencies and returns immediate action cards.
# These are shown BEFORE the AI response — speed matters.

CRISIS_KEYWORDS = {
    "arrest": [
        "arrested", "arrest kar", "pakad liya", "police ne pakda",
        "being arrested", "just arrested", "abhi arrest",
        "detained", "custody mein", "lock up",
    ],
    "violence": [
        "being beaten", "maar raha hai", "hitting me", "beating me",
        "physical attack", "assault ho raha", "threat to kill",
        "jaan se maarne ki dhamki", "knife", "gun", "pistol",
    ],
    "domestic_violence": [
        "husband beating", "pati maar raha", "domestic violence",
        "ghar mein maar", "sasural mein maar", "in-laws beating",
        "husband beats", "beats me", "hitting me daily",
        "my husband beats", "husband is beating", "wife beating",
        "beating me daily", "physically abuse", "mujhe maarta hai",
        "beat me", "pati maarta",
    ],
    "eviction": [
        "being thrown out right now", "abhi nikal rahe hain",
        "ghar se nikal", "evicting me today", "locks changed",
        "taala laga diya",
    ],
    "rape": [
        "just raped", "abhi rape", "sexual assault abhi",
        "being raped", "rape ho raha",
    ],
    "child_danger": [
        "child missing", "bachcha gaya", "kidnapped my child",
        "bachche ko le gaya", "child abuse",
    ],
}

EMERGENCY_RESPONSES = {
    "arrest": {
        "title": "You Are Being Arrested — Your Rights RIGHT NOW",
        "color": "red",
        "rights": [
            "DEMAND to know why you are being arrested (Article 22 — Constitution)",
            "You have the RIGHT to call a lawyer immediately",
            "Police MUST produce you before a Magistrate within 24 hours",
            "Do NOT sign anything without a lawyer present",
            "You can REFUSE to answer questions beyond basic identity",
        ],
        "contacts": [
            {"label": "NALSA Legal Aid (Free)", "number": "15100"},
            {"label": "National Human Rights Commission", "number": "14433"},
            {"label": "Police Complaint (emergency)", "number": "100"},
        ],
        "sections": ["Article 22 (Constitution)", "Section 47 BNSS (grounds of arrest)"],
    },
    "violence": {
        "title": "You Are in Danger — Act NOW",
        "color": "red",
        "rights": [
            "Call 100 (Police) or 112 (Emergency) IMMEDIATELY",
            "Get to a safe location if possible",
            "Your attacker can be arrested without warrant (cognizable offence)",
            "Take photos of injuries as evidence",
            "File FIR — police MUST register it under BNS Sections 115/117",
        ],
        "contacts": [
            {"label": "Police Emergency", "number": "100"},
            {"label": "National Emergency", "number": "112"},
            {"label": "NALSA Legal Aid", "number": "15100"},
        ],
        "sections": ["BNS Section 115 (hurt)", "BNS Section 117 (grievous hurt)"],
    },
    "domestic_violence": {
        "title": "Domestic Violence — Immediate Help",
        "color": "red",
        "rights": [
            "Call 181 (Women Helpline) immediately",
            "You have RIGHT to stay in the shared household (PWDVA 2005)",
            "Protection Officer can get you an emergency Protection Order same day",
            "You cannot be thrown out of your home",
            "Children stay with you — court order needed to separate them",
        ],
        "contacts": [
            {"label": "Women Helpline", "number": "181"},
            {"label": "Police Emergency", "number": "100"},
            {"label": "NCW Helpline", "number": "7827170170"},
            {"label": "NALSA Legal Aid", "number": "15100"},
        ],
        "sections": ["PWDVA 2005", "BNS Section 85 (dowry cruelty)"],
    },
    "eviction": {
        "title": "Being Forcibly Evicted — Your Rights",
        "color": "orange",
        "rights": [
            "Landlord CANNOT evict you without a court order",
            "Changing locks without court order = criminal offence (BNS 329/330)",
            "Call police — this is a cognizable offence",
            "You can apply for immediate injunction in Civil Court",
            "Tenant Protection: Rent Control Act protects you",
        ],
        "contacts": [
            {"label": "Police Emergency", "number": "100"},
            {"label": "NALSA Legal Aid", "number": "15100"},
            {"label": "District Legal Services Authority", "number": "15100"},
        ],
        "sections": ["BNS Section 329 (criminal trespass)", "Transfer of Property Act"],
    },
    "rape": {
        "title": "Sexual Assault — Immediate Support",
        "color": "red",
        "rights": [
            "Call 1091 (Women Helpline) or 112 immediately",
            "Go to nearest government hospital — free medical examination",
            "Do NOT shower before medical examination (preserves evidence)",
            "FIR can be filed at any police station — not just where it happened",
            "You can record statement at hospital (Section 164 BNSS)",
            "Your identity CANNOT be disclosed publicly",
        ],
        "contacts": [
            {"label": "Women Distress Helpline", "number": "1091"},
            {"label": "National Emergency", "number": "112"},
            {"label": "iCall (trauma support)", "number": "9152987821"},
        ],
        "sections": ["BNS Section 63 (rape)", "BNS Section 64 (punishment)"],
    },
    "child_danger": {
        "title": "Child in Danger — Act Immediately",
        "color": "red",
        "rights": [
            "Call 1098 (Childline) IMMEDIATELY — 24/7 free service",
            "Call 100 — child missing/abduction is a cognizable offence",
            "File FIR immediately — police must act without delay",
            "POCSO Act provides special protection for children under 18",
        ],
        "contacts": [
            {"label": "Childline India", "number": "1098"},
            {"label": "Police Emergency", "number": "100"},
            {"label": "National Commission for Protection of Child Rights", "number": "1800-11-1616"},
        ],
        "sections": ["POCSO Act 2012", "BNS Section 137 (kidnapping)"],
    },
}


def detect_emergency(query: str) -> dict | None:
    """
    Returns emergency response dict if crisis detected, else None.
    Checks all crisis categories and returns the most critical one.
    Priority: rape > violence > arrest > domestic_violence > child > eviction
    """
    query_lower = query.lower()
    priority_order = [
        "rape", "violence", "arrest",
        "domestic_violence", "child_danger", "eviction"
    ]

    for crisis_type in priority_order:
        keywords = CRISIS_KEYWORDS.get(crisis_type, [])
        if any(kw in query_lower for kw in keywords):
            return {
                "type": crisis_type,
                **EMERGENCY_RESPONSES[crisis_type],
            }

    return None
