from __future__ import annotations

KG_EDGES: list[tuple[str, str, str, float, str]] = [
    ("Indian Penal Code, 1860", "300", "Indian Penal Code, 1860", "302", "related_section", 0.95, "Murder definition → Murder punishment"),
    ("Indian Penal Code, 1860", "300", "Indian Penal Code, 1860", "304", "related_section", 0.85, "Murder vs CHNAM thresholds"),
    ("Indian Penal Code, 1860", "304B", "Indian Penal Code, 1860", "498A", "cited_in", 0.9, "Dowry death often preceded by 498A cruelty"),
    ("Indian Penal Code, 1860", "375", "Indian Penal Code, 1860", "376", "related_section", 0.97, "Rape definition → punishment"),
    ("Indian Penal Code, 1860", "378", "Indian Penal Code, 1860", "383", "related_section", 0.75, "Theft → Extortion distinction (consent element)"),
    ("Indian Penal Code, 1860", "383", "Indian Penal Code, 1860", "390", "related_section", 0.8, "Extortion escalated to Robbery by force"),
    ("Indian Penal Code, 1860", "405", "Indian Penal Code, 1860", "411", "related_section", 0.65, "CBT → Receiving stolen property chain"),
    ("Indian Penal Code, 1860", "415", "Indian Penal Code, 1860", "420", "related_section", 0.9, "Cheating → aggravated Cheating with property inducement"),
    ("Bharatiya Nyaya Sanhita, 2023", "107", "Bharatiya Nyaya Sanhita, 2023", "108", "related_section", 0.96, "Murder BNS definition → punishment"),
    ("Bharatiya Nyaya Sanhita, 2023", "65", "Bharatiya Nyaya Sanhita, 2023", "63", "related_section", 0.8, "Rape BNS → new Rape by Deceit BNS Sec 63"),
    ("Bharatiya Nyaya Sanhita, 2023", "126", "Bharatiya Nyaya Sanhita, 2023", "124", "cited_in", 0.9, "Dowry death BNS requires prior cruelty 124"),
    ("Bharatiya Nyaya Sanhita, 2023", "306", "Bharatiya Nyaya Sanhita, 2023", "323", "related_section", 0.8, "Theft BNS → Robbery BNS via immediate violence"),
    ("Information Technology Act, 2000", "66", "Prevention of Money Laundering Act, 2002", "3", "cited_in", 0.55, "Cyber-enabled laundering triggers both"),
    ("Protection of Women from Domestic Violence Act, 2005", "3", "Indian Penal Code, 1860", "498A", "related_section", 0.92, "Civil DVA definition mirrors criminal cruelty 498A"),
    ("Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989", "3", "Indian Penal Code, 1860", "376", "related_section", 0.72, "SCST Act Sec 3(2)(v) gang rape SC/ST woman elevates IPC 376"),
]
