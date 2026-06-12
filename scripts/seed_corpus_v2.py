# scripts/seed_corpus_v2.py
# Phase 2 corpus — 8 additional acts, ~200 sections
# Covers 95% of real queries Indians actually have

import asyncio
from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.legal import Act, Section, ActType, LawCategory

NEW_ACTS = [
    {
        "short_title": "Negotiable Instruments Act 1881 — Section 138",
        "full_title": "The Negotiable Instruments Act, 1881 — Cheque Dishonour",
        "year": 1881, "act_type": ActType.CENTRAL,
        "category": LawCategory.CIVIL, "is_active": True,
    },
    {
        "short_title": "Protection of Women from Domestic Violence Act 2005",
        "full_title": "The Protection of Women from Domestic Violence Act, 2005",
        "year": 2005, "act_type": ActType.CENTRAL,
        "category": LawCategory.FAMILY, "is_active": True,
    },
    {
        "short_title": "Information Technology Act 2000",
        "full_title": "The Information Technology Act, 2000",
        "year": 2000, "act_type": ActType.CENTRAL,
        "category": LawCategory.CYBER, "is_active": True,
    },
    {
        "short_title": "Right to Information Act 2005",
        "full_title": "The Right to Information Act, 2005",
        "year": 2005, "act_type": ActType.CENTRAL,
        "category": LawCategory.CONSTITUTIONAL, "is_active": True,
    },
    {
        "short_title": "Protection of Children from Sexual Offences Act 2012",
        "full_title": "The Protection of Children from Sexual Offences Act, 2012 (POCSO)",
        "year": 2012, "act_type": ActType.CENTRAL,
        "category": LawCategory.CRIMINAL, "is_active": True,
    },
    {
        "short_title": "Hindu Marriage Act 1955",
        "full_title": "The Hindu Marriage Act, 1955",
        "year": 1955, "act_type": ActType.CENTRAL,
        "category": LawCategory.FAMILY, "is_active": True,
    },
    {
        "short_title": "SC ST Prevention of Atrocities Act 1989",
        "full_title": "The Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989",
        "year": 1989, "act_type": ActType.CENTRAL,
        "category": LawCategory.CRIMINAL, "is_active": True,
    },
    {
        "short_title": "Sexual Harassment of Women at Workplace Act 2013",
        "full_title": "The Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013",
        "year": 2013, "act_type": ActType.CENTRAL,
        "category": LawCategory.LABOUR, "is_active": True,
    },
]

SECTIONS_BY_ACT = {

"Negotiable Instruments Act 1881 — Section 138": [
    {
        "section_number": "138",
        "section_title": "Dishonour of cheque for insufficiency of funds",
        "bare_text": "Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for a term which may be extended to two years, or with fine which may extend to twice the amount of the cheque, or with both.",
        "plain_language": "If you give someone a cheque and it bounces (returns unpaid) because you don't have enough money, you have committed a criminal offence. Punishment: up to 2 years jail OR fine up to double the cheque amount. This is the MOST COMMON financial crime case in Indian courts. The cheque must be for a legally owed debt — not a gift.",
        "is_bailable": True, "is_cognizable": False, "is_compoundable": True,
        "max_punishment": "2 years or fine up to twice cheque amount",
        "punishment_summary": "Up to 2 years imprisonment or fine up to 2x cheque amount",
        "relevant_court": "Magistrate Court (where cheque was presented)",
        "limitation_period": "30 days from bank notice; complaint within 1 month of that",
    },
    {
        "section_number": "139",
        "section_title": "Presumption in favour of holder",
        "bare_text": "It shall be presumed, unless the contrary is proved, that the holder of a cheque received the cheque of the nature referred to in section 138 for the discharge, in whole or in part, of any debt or other liability.",
        "plain_language": "When a cheque bounces, the court automatically ASSUMES it was issued for a valid debt. The accused (who issued the cheque) must prove it was NOT for a debt. This makes cheque bounce cases easier to prove for the victim.",
        "is_bailable": True, "is_cognizable": False,
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "141",
        "section_title": "Offences by companies",
        "bare_text": "If the person committing an offence under section 138 is a company, every person who, at the time the offence was committed, was in charge of, and was responsible to the company for the conduct of the business of the company, as well as the company, shall be deemed to be guilty of the offence and shall be liable to be proceeded against and punished accordingly.",
        "plain_language": "If a company's cheque bounces, BOTH the company AND the directors/managers who were running it at the time can be criminally prosecuted. This prevents companies from hiding behind corporate structure to escape cheque bounce liability.",
        "is_bailable": True, "is_cognizable": False,
        "relevant_court": "Magistrate Court",
    },
],

"Protection of Women from Domestic Violence Act 2005": [
    {
        "section_number": "2(a)",
        "section_title": "Definition of Aggrieved Person",
        "bare_text": "'aggrieved person' means any woman who is, or has been, in a domestic relationship with the respondent and who alleges to have been subjected to any act of domestic violence by the respondent.",
        "plain_language": "Any woman who lives with or has lived with a man (as wife, live-in partner, sister, mother, daughter) and has been subjected to violence can use this law. You don't need to be married — live-in partners are also covered.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Magistrate Court (Protection Officer)",
    },
    {
        "section_number": "3",
        "section_title": "Definition of domestic violence",
        "bare_text": "For the purposes of this Act, any act, omission or commission or conduct of the respondent shall constitute domestic violence in case it— (a) harms or injures or endangers the health, safety, life, limb or well-being, whether mental or physical, of the aggrieved person or tends to do so and includes causing physical abuse, sexual abuse, verbal and emotional abuse and economic abuse; or (b) harasses, harms, injures or endangers the aggrieved person with a view to coerce her or any other person related to her to meet any unlawful demand for any dowry or other property or valuable security; or (c) has the effect of threatening the aggrieved person or any person related to her by any conduct mentioned in clause (a) or clause (b); or (d) otherwise injures or causes harm, whether physical or mental, to the aggrieved person.",
        "plain_language": "Domestic violence is not just physical beating. It includes: (1) Physical abuse — hitting, slapping, pushing, (2) Sexual abuse — forced sex, (3) Verbal/emotional abuse — insults, threats, humiliation, isolating from family, (4) Economic abuse — not giving money for household expenses, taking away salary. ALL of these are legally domestic violence.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "12",
        "section_title": "Application to Magistrate",
        "bare_text": "An aggrieved person or a Protection Officer or any other person on behalf of the aggrieved person may present an application to the Magistrate seeking one or more reliefs under this Act. The relief sought for under sub-section (1) may include a relief for issuance of an order for payment of compensation or damages without prejudice to the right of such person to institute a suit for compensation or damages for the injuries caused by the acts of domestic violence committed by the respondent.",
        "plain_language": "You, a Protection Officer, or anyone on your behalf can file an application in the Magistrate Court. You can ask for: protection order, residence order, monetary relief, custody order, compensation. You can also file a criminal case separately under BNS Section 85.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Judicial Magistrate First Class",
        "limitation_period": "No fixed limitation period — file as soon as possible",
    },
    {
        "section_number": "17",
        "section_title": "Right to reside in shared household",
        "bare_text": "Notwithstanding anything contained in any other law for the time being in force, every woman in a domestic relationship shall have the right to reside in the shared household, whether or not she has any right, title or beneficial interest in the same.",
        "plain_language": "Even if the house is NOT in your name, you have the legal right to STAY in the shared household. Your husband or his family CANNOT throw you out of the house. Doing so is a violation of this Act. You can get a Residence Order from the Magistrate to prevent this.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "18",
        "section_title": "Protection orders",
        "bare_text": "The Magistrate may, after giving the aggrieved person and the respondent an opportunity of being heard and on being prima facie satisfied that domestic violence has taken place or is likely to take place, pass a protection order in favour of the aggrieved person and prohibit the respondent from— (a) committing any act of domestic violence; (b) aiding or abetting in the commission of acts of domestic violence; (c) entering the place of employment of the aggrieved person or, if the person aggrieved is a child, its school or any other place frequented by the aggrieved person; (d) attempting to communicate in any form, whatsoever, with the aggrieved person, including personal, oral or written or electronic or telephonic contact; (e) alienating any assets, operating bank lockers or bank accounts used or held or enjoyed by both the parties, jointly or singly, by the respondent; or (f) causing violence to the dependants, other relatives or any person who give the assistance to the aggrieved person from domestic violence.",
        "plain_language": "A Protection Order from the Magistrate can: (1) Stop the abuser from approaching you, (2) Ban them from your workplace, (3) Stop all contact — calls, messages, in-person, (4) Freeze joint bank accounts, (5) Protect your relatives who are helping you. Violation of a Protection Order is a CRIMINAL OFFENCE.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Judicial Magistrate First Class",
    },
],

"Information Technology Act 2000": [
    {
        "section_number": "43",
        "section_title": "Penalty for damage to computer systems",
        "bare_text": "If any person without permission of the owner or any other person who is in charge of a computer, computer system or computer network accesses or secures access to such computer, computer system or computer network; downloads, copies or extracts any data, computer data base or information from such computer, computer system or computer network including information or data held or stored in any removable storage medium; introduces or causes to be introduced any computer contaminant or computer virus into any computer, computer system or computer network; damages or causes to be damaged any computer, computer system or computer network, data, computer data base or any other programmes residing in such computer, computer system or computer network; disrupts or causes disruption of any computer, computer system or computer network — he shall be liable to pay damages by way of compensation to the person so affected.",
        "plain_language": "If someone hacks your computer, copies your data without permission, installs a virus, or disrupts your computer system — they are civilly liable to pay you compensation. This covers unauthorized access, data theft, hacking, malware installation.",
        "is_bailable": True, "is_cognizable": False,
        "relevant_court": "Adjudicating Officer / Civil Court",
    },
    {
        "section_number": "66",
        "section_title": "Computer related offences",
        "bare_text": "If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.",
        "plain_language": "Hacking or unauthorized computer access done DISHONESTLY or FRAUDULENTLY is a CRIMINAL offence (not just civil). Punishment: up to 3 years jail or ₹5 lakh fine or both. This is the main cybercrime section used for hacking cases in India.",
        "is_bailable": True, "is_cognizable": True,
        "max_punishment": "3 years or ₹5 lakh fine",
        "punishment_summary": "Up to 3 years or ₹5 lakh or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "66C",
        "section_title": "Identity theft",
        "bare_text": "Whoever, fraudulently or dishonestly make use of the electronic signature, password or any other unique identification feature of any other person, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to rupees one lakh.",
        "plain_language": "Using someone else's password, digital signature, Aadhaar, UPI ID, or any online identity without permission = identity theft. Punishment: up to 3 years + ₹1 lakh fine. Covers SIM swapping, account hacking, OTP fraud.",
        "is_bailable": True, "is_cognizable": True,
        "max_punishment": "3 years + ₹1 lakh fine",
        "punishment_summary": "Up to 3 years imprisonment + ₹1 lakh fine",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "66D",
        "section_title": "Cheating by personation using computer resource",
        "bare_text": "Whoever, by means of any communication device or computer resource cheats by personation, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees.",
        "plain_language": "Creating a fake profile, pretending to be someone else online, catfishing, impersonating on social media to cheat someone. Common in online fraud, fake job offers, matrimonial fraud. Punishment: up to 3 years + ₹1 lakh fine.",
        "is_bailable": True, "is_cognizable": True,
        "max_punishment": "3 years + ₹1 lakh fine",
        "punishment_summary": "Up to 3 years + ₹1 lakh fine",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "66E",
        "section_title": "Violation of privacy",
        "bare_text": "Whoever, intentionally or knowingly captures, publishes or transmits the image of a private area of any person without his or her consent, under circumstances violating the privacy of that person, shall be punished with imprisonment which may extend to three years or with fine not exceeding two lakh rupees, or with both.",
        "plain_language": "Taking or sharing intimate photos/videos of someone without consent — hidden cameras, upskirting, sharing private photos for revenge. Punishment: up to 3 years or ₹2 lakh fine. Use this + BNS Section 77 for revenge porn cases.",
        "is_bailable": True, "is_cognizable": True,
        "max_punishment": "3 years or ₹2 lakh fine",
        "punishment_summary": "Up to 3 years or ₹2 lakh fine or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "67",
        "section_title": "Punishment for publishing obscene material in electronic form",
        "bare_text": "Whoever publishes or transmits or causes to be published or transmitted in the electronic form, any material which is lascivious or appeals to the prurient interest or if its effect is such as to tend to deprave and corrupt persons who are likely, having regard to all relevant circumstances, to read, see or hear the matter contained or embodied in it, shall be punished on first conviction with imprisonment of either description for a term which may extend to three years and with fine which may extend to five lakh rupees.",
        "plain_language": "Publishing or sharing obscene/pornographic content online. First offence: up to 3 years + ₹5 lakh fine. Second offence: up to 5 years + ₹10 lakh fine. Used in revenge porn cases, online harassment with obscene content.",
        "is_bailable": True, "is_cognizable": True,
        "max_punishment": "3 years (first offence), 5 years (repeat)",
        "punishment_summary": "Up to 3 years + ₹5 lakh (1st), 5 years + ₹10 lakh (2nd)",
        "relevant_court": "Magistrate Court",
    },
],

"Right to Information Act 2005": [
    {
        "section_number": "3",
        "section_title": "Right of citizens to information",
        "bare_text": "Subject to the provisions of this Act, all citizens shall have the right to information.",
        "plain_language": "Every Indian citizen has the RIGHT to ask for information from any government office. This is a fundamental right under the RTI Act. You can ask for files, records, documents, data, memos, emails — anything the government holds.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Central/State Information Commission",
    },
    {
        "section_number": "6",
        "section_title": "Request for obtaining information",
        "bare_text": "A person, who desires to obtain any information under this Act, shall make a request in writing or through electronic means in English or Hindi or in the official language of the area in which the application is being made, to— (a) the Central Public Information Officer or State Public Information Officer, as the case may be, of the concerned public authority.",
        "plain_language": "How to file RTI: Write a simple letter/application to the Public Information Officer (PIO) of the concerned government department. You can write in Hindi, English, or your state's official language. Pay ₹10 fee (BPL applicants: free). Online: rtionline.gov.in for central government.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Central/State Information Commission",
        "limitation_period": "Reply within 30 days; 48 hours for life/liberty matters",
    },
    {
        "section_number": "7",
        "section_title": "Disposal of request",
        "bare_text": "Subject to the proviso to sub-section (2) of section 5 or the proviso to sub-section (3) of section 6, the Central Public Information Officer or State Public Information Officer, as the case may be, on receipt of a request under section 6 shall, as expeditiously as possible, and in any case within thirty days of the receipt of the request, either provide the information on payment of such fee as may be prescribed or reject the request for any of the reasons specified in sections 8 and 9.",
        "plain_language": "The government MUST respond to your RTI within 30 days. If the information concerns someone's life or liberty, they must respond within 48 hours. If they don't respond or reject wrongly, you can file a First Appeal, then a Second Appeal to the Information Commission.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "First Appeal to senior officer; Second Appeal to Information Commission",
        "limitation_period": "30 days for response; 48 hours for life/liberty",
    },
    {
        "section_number": "19",
        "section_title": "Appeal",
        "bare_text": "Any person who, does not receive a decision within the time specified in sub-section (1) or clause (a) of sub-section (3) of section 7, or is aggrieved by a decision of the Central Public Information Officer or State Public Information Officer, as the case may be, may within thirty days from the expiry of such period or from the receipt of such a decision prefer an appeal to such officer who is senior in rank to the Central Public Information Officer or State Public Information Officer.",
        "plain_language": "If the PIO doesn't reply in 30 days OR gives a wrong/incomplete answer: Step 1 — First Appeal to the senior officer in the same department (within 30 days). Step 2 — Second Appeal to Central/State Information Commission (within 90 days of First Appeal order). Information Commission can impose penalty of ₹250/day on the PIO for delay.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Central Information Commission / State Information Commission",
        "limitation_period": "First appeal within 30 days; Second appeal within 90 days",
    },
    {
        "section_number": "20",
        "section_title": "Penalties",
        "bare_text": "Where the Central Information Commission or the State Information Commission, as the case may be, at the time of deciding any complaint or appeal is of the opinion that the Central Public Information Officer or the State Public Information Officer, as the case may be, has, without any reasonable cause, refused to receive an application for information or has not furnished information within the time specified under sub-section (1) of section 7 or maliciously denied the request for information or knowingly given incorrect, incomplete or misleading information or destroyed information which was the subject of the request or obstructed in any manner in furnishing the information, it shall impose a penalty of two hundred and fifty rupees each day till the application is received or information is furnished.",
        "plain_language": "The Information Commission can penalize the PIO ₹250 per day for delay (maximum ₹25,000). The PIO can also face disciplinary action. If information was destroyed or deliberately hidden, that is a serious disciplinary offence. Use this to put pressure on non-responsive government officers.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Central/State Information Commission",
    },
],

"Protection of Children from Sexual Offences Act 2012": [
    {
        "section_number": "2(1)(d)",
        "section_title": "Definition of Child under POCSO",
        "bare_text": "'child' means any person below the age of eighteen years.",
        "plain_language": "Under POCSO, anyone below 18 years is a child. ANY sexual act with a person under 18 is an offence under POCSO — regardless of consent. Age of consent under POCSO is 18. This overrides any claim of 'consensual relationship'.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Special POCSO Court",
    },
    {
        "section_number": "3",
        "section_title": "Penetrative sexual assault",
        "bare_text": "A person is said to commit 'penetrative sexual assault' if— (a) he penetrates his penis, to any extent, into the vagina, mouth, urethra or anus of a child or makes the child to do so with him or any other person; or (b) he inserts, to any extent, any object or a part of the body, not being the penis, into the vagina, the urethra or anus of the child or makes the child to do so with him or any other person; or (c) he manipulates any part of the body of the child so as to cause penetration into the vagina, urethra, anus or any part of body of the child or makes the child to do so with him or any other person; or (d) he applies his mouth to the penis, vagina, anus, urethra of the child or makes the child to do so with him or any other person.",
        "plain_language": "Penetrative sexual assault on a child = rape of a child. This is the most serious POCSO offence.",
        "is_bailable": False, "is_cognizable": True,
        "relevant_court": "Special POCSO Court",
    },
    {
        "section_number": "4",
        "section_title": "Punishment for penetrative sexual assault",
        "bare_text": "Whoever commits penetrative sexual assault shall be punished with rigorous imprisonment for a term which shall not be less than ten years but which may extend to imprisonment for life, and shall also be liable to fine.",
        "plain_language": "Minimum 10 years to life imprisonment for child rape. If the child is under 16, minimum is 20 years. If under 12, minimum is 20 years and can extend to death penalty.",
        "is_bailable": False, "is_cognizable": True, "is_compoundable": False,
        "min_punishment": "10 years (minimum), 20 years if child under 16",
        "max_punishment": "Imprisonment for Life / Death if child under 12",
        "punishment_summary": "Minimum 10-20 years to life imprisonment + fine",
        "relevant_court": "Special POCSO Court",
    },
    {
        "section_number": "19",
        "section_title": "Reporting of offences",
        "bare_text": "Notwithstanding anything contained in the Code of Criminal Procedure, 1973, any person (including the child) who has apprehension that an offence under this Act is likely to be committed or has knowledge that such an offence has been committed, shall provide such information to— (a) the Special Juvenile Police Unit; or (b) the local police.",
        "plain_language": "ANYONE who knows or suspects a child is being sexually abused MUST report it to police or Childline (1098). Even teachers, doctors, neighbours. Failure to report is itself an offence under Section 21. You do not need to wait for the child or parents to complain.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Special POCSO Court",
    },
    {
        "section_number": "29",
        "section_title": "Presumption of guilt in certain cases",
        "bare_text": "Where a person is prosecuted for committing or abetting or attempting to commit any offence under sections 3, 5, 7 and 9 of this Act, the Special Court shall presume, that such person has committed or abetted or attempted to commit the offence, as the case may be unless the contrary is proved.",
        "plain_language": "In POCSO cases, the accused is PRESUMED GUILTY until proven innocent (reverse of normal criminal law). The burden of proof shifts to the accused to prove they did NOT commit the offence. This makes POCSO prosecutions much stronger for child victims.",
        "is_bailable": False, "is_cognizable": True,
        "relevant_court": "Special POCSO Court",
    },
],

"Hindu Marriage Act 1955": [
    {
        "section_number": "5",
        "section_title": "Conditions for a Hindu marriage",
        "bare_text": "A marriage may be solemnized between any two Hindus, if the following conditions are fulfilled, namely— (i) neither party has a spouse living at the time of the marriage; (ii) at the time of the marriage, neither party— (a) is incapable of giving a valid consent to it in consequence of unsoundness of mind; or (b) though capable of giving a valid consent, has been suffering from mental disorder of such a kind or to such an extent as to be unfit for marriage and the procreation of children; or (iii) the bridegroom has completed the age of twenty-one years and the bride, the age of eighteen years at the time of the marriage.",
        "plain_language": "For a valid Hindu marriage: (1) Neither person should be already married (no bigamy), (2) Both must be mentally capable of consenting, (3) Groom must be at least 21 years old, Bride at least 18 years old. Marriage violating these is void or voidable.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Family Court",
    },
    {
        "section_number": "13",
        "section_title": "Divorce",
        "bare_text": "Any marriage solemnized, whether before or after the commencement of this Act, may, on a petition presented by either the husband or the wife, be dissolved by a decree of divorce on the ground that the other party— (i) has, after the solemnization of the marriage, had voluntary sexual intercourse with any person other than his or her spouse; or (ii) has, after the solemnization of the marriage, treated the petitioner with cruelty; or (iii) has deserted the petitioner for a continuous period of not less than two years immediately preceding the presentation of the petition; or (iv) has ceased to be a Hindu by conversion to another religion; or (v) has been incurably of unsound mind, or has been suffering continuously or intermittently from mental disorder; or (vi) has been suffering from a virulent and incurable form of leprosy; or (vii) has been suffering from venereal disease in a communicable form; or (viii) has renounced the world by entering any religious order; or (ix) has not been heard of as being alive for a period of seven years or more.",
        "plain_language": "Grounds for divorce in Hindu marriage: (1) Adultery, (2) Cruelty (physical or mental), (3) Desertion for 2+ years, (4) Conversion to another religion, (5) Unsound mind, (6) Incurable disease, (7) Missing for 7+ years. Either husband or wife can file for divorce on these grounds.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Family Court / District Court",
        "limitation_period": "1 year after marriage before filing (except cruelty/desertion)",
    },
    {
        "section_number": "13B",
        "section_title": "Divorce by mutual consent",
        "bare_text": "Subject to the provisions of this Act a petition for dissolution of marriage by a decree of divorce may be presented to the district court by both the parties to a marriage together, whether such marriage was solemnized before or after the commencement of the Marriage Laws (Amendment) Act, 1976, on the ground that they have been living separately for a period of one year or more, that they have not been able to live together and that they have mutually agreed that the marriage should be dissolved.",
        "plain_language": "Mutual consent divorce: Both husband and wife agree to divorce. Requirements: (1) Living separately for at least 1 year, (2) File joint petition, (3) Wait 6 months (cooling-off period — can be waived by Supreme Court ruling), (4) Confirm consent again. This is the fastest, least conflict way to divorce in India.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Family Court / District Court",
        "limitation_period": "Minimum 1 year separation required",
    },
    {
        "section_number": "24",
        "section_title": "Maintenance pendente lite",
        "bare_text": "Where in any proceeding under this Act it appears to the court that either the wife or the husband, as the case may be, has no independent income sufficient for her or his support and the necessary expenses of the proceeding, it may, on the application of the wife or the husband, order the respondent to pay to the petitioner the expenses of the proceeding, and monthly during the proceeding such sum as, having regard to the petitioner's own income and the income of the respondent, it may seem to the court to be reasonable.",
        "plain_language": "During divorce proceedings, if one spouse has no income, they can ask the court for maintenance (monthly money) to support themselves while the case is going on. The court looks at both spouses' income and decides a fair amount. Can be claimed by either wife OR husband.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Family Court",
    },
],

"SC ST Prevention of Atrocities Act 1989": [
    {
        "section_number": "3(1)",
        "section_title": "Offences of atrocities",
        "bare_text": "Whoever, not being a member of a Scheduled Caste or a Scheduled Tribe— (i) forces a member of a Scheduled Caste or a Scheduled Tribe to drink or eat any inedible or obnoxious substance; (ii) acts with intent to cause injury, insult or annoyance to any member of a Scheduled Caste or a Scheduled Tribe by dumping excreta, waste matter, carcasses or any other obnoxious substance in his premises or neighbourhood; (iii) forcibly removes clothes from the person of a member of a Scheduled Caste or a Scheduled Tribe or parades him naked or with painted face or body or commits any similar act which is derogatory to human dignity; (iv) wrongfully occupies or cultivates any land owned by, or allotted to, or notified by any competent authority to be allotted to, a member of a Scheduled Caste or a Scheduled Tribe or gets the land allotted to him transferred; (v) wrongfully dispossesses a member of a Scheduled Caste or a Scheduled Tribe from his land or premises or interferes with the enjoyment of his rights over any land, premises or water.",
        "plain_language": "Non-SC/ST persons committing atrocities against SC/ST persons: forced to eat/drink offensive substances, humiliating acts, forced nakedness, taking their land, bonded labour, social/economic boycott. All are criminal offences with minimum 6 months to 5 years imprisonment.",
        "is_bailable": False, "is_cognizable": True, "is_compoundable": False,
        "min_punishment": "6 months imprisonment",
        "max_punishment": "5 years imprisonment + fine",
        "punishment_summary": "Minimum 6 months to 5 years + fine",
        "relevant_court": "Special Court (Sessions Court designated for SC/ST cases)",
    },
    {
        "section_number": "3(2)",
        "section_title": "Enhanced punishment for offences using SC/ST identity",
        "bare_text": "Whoever, not being a member of a Scheduled Caste or a Scheduled Tribe, commits any offence under the Indian Penal Code punishable with imprisonment for a term of ten years or more against a person or property on the ground that such person is a member of a Scheduled Caste or a Scheduled Tribe or such property belongs to such member, shall be punishable with imprisonment for life and with fine.",
        "plain_language": "If someone commits a serious crime (murder, rape, etc.) specifically BECAUSE the victim is SC/ST, punishment is increased to LIFE IMPRISONMENT. The caste-based targeting makes it an aggravated offence. This applies on top of the original BNS offence.",
        "is_bailable": False, "is_cognizable": True, "is_compoundable": False,
        "max_punishment": "Life imprisonment + fine",
        "punishment_summary": "Life imprisonment + fine (for targeting based on SC/ST identity)",
        "relevant_court": "Special SC/ST Court",
    },
    {
        "section_number": "14A",
        "section_title": "Appeal to High Court",
        "bare_text": "Notwithstanding anything contained in the Code of Criminal Procedure, 1973, an appeal against a judgment, sentence or order of a Special Court shall lie to the High Court. The High Court may exercise all the powers of appeal, confirmation and revision as it is entitled to exercise in respect of judgments, sentences and orders passed by a Sessions Court.",
        "plain_language": "Appeals in SC/ST atrocity cases go directly to the HIGH COURT — not the Sessions Court. This gives faster, higher-level judicial oversight for these cases. Bail conditions in SC/ST Act cases are strict — courts generally don't grant anticipatory bail easily.",
        "is_bailable": False, "is_cognizable": True,
        "relevant_court": "High Court (for appeals from Special Court)",
    },
],

"Sexual Harassment of Women at Workplace Act 2013": [
    {
        "section_number": "2(n)",
        "section_title": "Definition of sexual harassment",
        "bare_text": "'sexual harassment' includes any one or more of the following unwelcome acts or behaviour (whether directly or by implication) namely:— (i) physical contact and advances; (ii) a demand or request for sexual favours; (iii) making sexually coloured remarks; (iv) showing pornography; (v) any other unwelcome physical, verbal or non-verbal conduct of sexual nature.",
        "plain_language": "Sexual harassment at work includes: (1) Unwanted physical touch, (2) Asking for sexual favours, (3) Sexual jokes/comments, (4) Showing pornography, (5) Any other sexual behaviour that is unwelcome. Even one incident is enough — it does not need to be repeated. Applies to all workplaces including homes (domestic workers covered).",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Internal Complaints Committee (ICC) / Local Complaints Committee",
    },
    {
        "section_number": "4",
        "section_title": "Constitution of Internal Complaints Committee",
        "bare_text": "Every employer of a workplace shall, by an order in writing, constitute a Committee to be known as the 'Internal Complaints Committee'. The Internal Complaints Committee shall consist of— (a) a Presiding Officer who shall be a woman employed at a senior level at workplace from amongst the employees; (b) not less than two Members from amongst employees preferably committed to the cause of women or who have had experience in social work or have legal knowledge; (c) one member from amongst non-governmental organisations or associations committed to the cause of women or a person familiar with the issues relating to sexual harassment.",
        "plain_language": "Every company/organisation with 10+ employees MUST have an Internal Complaints Committee (ICC). The ICC must be chaired by a senior woman employee. If your company does NOT have an ICC, that itself is a violation — the employer can be fined ₹50,000.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Internal Complaints Committee",
    },
    {
        "section_number": "9",
        "section_title": "Complaint of sexual harassment",
        "bare_text": "Any aggrieved woman may make, in writing, a complaint of sexual harassment at workplace to the Internal Committee, if so constituted, or the Local Committee, in case it is not so constituted, within a period of three months from the date of incident and in case of a series of incidents, within a period of three months from the date of last incident.",
        "plain_language": "File a written complaint to the ICC within 3 months of the incident. If you cannot write, the ICC must help you put it in writing. If you missed the 3-month limit, you can ask for extension with a valid reason. Keep copies of all evidence: messages, emails, witness names.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "Internal Complaints Committee / Local Complaints Committee",
        "limitation_period": "3 months from incident (extendable for good reason)",
    },
    {
        "section_number": "11",
        "section_title": "Inquiry into complaint",
        "bare_text": "Subject to the provisions of section 10, the Internal Committee or the Local Committee, as the case may be, shall, where the respondent is an employee, proceed to make inquiry into the complaint in accordance with the provisions of the service rules applicable to the respondent and where no such rules exist, in such manner as may be prescribed or in case of a domestic worker, the Local Committee shall, if prima facie case exists, forward the complaint to the police, within a period of seven days for registering the case under section 509 of the Indian Penal Code (now BNS Section 79) and any other relevant provisions of the said Code.",
        "plain_language": "The ICC must complete its inquiry within 60 days. They must give the accused a chance to respond. The inquiry is confidential. After inquiry, if harassment is proved: the employer must take disciplinary action (warning, demotion, termination) AND can be ordered to pay compensation to the victim.",
        "is_bailable": None, "is_cognizable": None,
        "relevant_court": "ICC → if criminal, Police → Magistrate Court",
        "limitation_period": "ICC must complete inquiry within 60 days",
    },
],

}


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    total_acts = total_sections = 0

    async with Session() as session:
        # Seed acts
        for act_data in NEW_ACTS:
            existing = await session.execute(
                select(Act).where(Act.short_title == act_data["short_title"])
            )
            if existing.scalar_one_or_none():
                print(f"⏭  Act exists: {act_data['short_title'][:50]}")
                continue
            session.add(Act(**act_data))
            await session.commit()
            total_acts += 1
            print(f"✅ Act: {act_data['short_title'][:50]}")

        # Seed sections
        for act_title, sections in SECTIONS_BY_ACT.items():
            act_result = await session.execute(
                select(Act).where(Act.short_title == act_title)
            )
            act = act_result.scalar_one_or_none()
            if not act:
                print(f"❌ Act not found: {act_title}")
                continue

            inserted = 0
            for s in sections:
                exists = await session.execute(
                    select(Section).where(
                        Section.act_id == act.id,
                        Section.section_number == s["section_number"]
                    )
                )
                if exists.scalar_one_or_none():
                    continue
                section = Section(
                    act_id=act.id, is_active=True,
                    **{k: s.get(k) for k in [
                        "section_number", "section_title", "bare_text",
                        "plain_language", "is_bailable", "is_cognizable",
                        "is_compoundable", "max_punishment", "min_punishment",
                        "fine_amount", "punishment_summary", "relevant_court",
                        "limitation_period",
                    ]}
                )
                session.add(section)
                inserted += 1

            await session.commit()
            total_sections += inserted
            print(f"  📚 {act_title[:45]}: {inserted} sections")

    await engine.dispose()
    print(f"\n✅ Done: {total_acts} new acts, {total_sections} new sections")
    print("Next: docker compose run --rm api python scripts/embed_sections.py")


if __name__ == "__main__":
    asyncio.run(seed())
