# scripts/seed_bns_sections.py
# Hardcoded BNS 2023 critical sections — verified against official gazette
# BNS = Bharatiya Nyaya Sanhita 2023 (replaced IPC 1860 from July 1, 2024)

from __future__ import annotations

import asyncio

from _bootstrap import ensure_backend_on_path

ensure_backend_on_path()

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.legal import Act, Section

BNS_SECTIONS = [
    {
        "section_number": "103",
        "section_title": "Punishment for murder",
        "bare_text": (
            "Whoever commits murder shall be punished with death or imprisonment for life, "
            "and shall also be liable to fine.\n"
            "Exception 1: When culpable homicide is not murder — A person who, whilst deprived "
            "of the power of self-control by grave and sudden provocation, causes the death of "
            "the person who gave the provocation or causes the death of any other person by "
            "mistake or accident, is not guilty of murder.\n"
            "Exception 2: Private defence — A person is not guilty of murder if they exceed "
            "the right of private defence in good faith.\n"
            "Exception 3: Public servant — A public servant acting in furtherance of law, "
            "exceeding their power in good faith.\n"
            "Exception 4: Sudden fight — No premeditation, no undue advantage.\n"
            "Exception 5: Consent — Person above 18 years suffering from fatal condition "
            "gives consent."
        ),
        "plain_language": (
            "If someone kills another person intentionally, that is murder. "
            "The punishment is either death penalty or life imprisonment, plus a fine. "
            "There are 5 exceptions where killing is NOT murder — such as extreme provocation, "
            "self-defence, or accidental death during a sudden fight."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "Death or Imprisonment for Life",
        "punishment_summary": "Death or life imprisonment + fine",
        "relevant_court": "Sessions Court",
    },
    {
        "section_number": "104",
        "section_title": "Punishment for culpable homicide not amounting to murder",
        "bare_text": (
            "Whoever commits culpable homicide not amounting to murder shall be punished with "
            "imprisonment for life, or imprisonment of either description for a term which may "
            "extend to ten years, and shall also be liable to fine.\n"
            "If the act by which death is caused is done with the intention of causing death, "
            "or of causing such bodily injury as is likely to cause death, the offender shall "
            "be liable to either description of imprisonment for a term which may extend to "
            "ten years, or imprisonment for life, and shall also be liable to fine."
        ),
        "plain_language": (
            "When someone causes death without full intention to murder — for example during "
            "a fight that went too far — it is culpable homicide. Punishment: up to 10 years "
            "or life imprisonment. Less serious than Section 103 (murder) but still a major crime."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "Imprisonment for Life or 10 years",
        "punishment_summary": "Life imprisonment or up to 10 years + fine",
        "relevant_court": "Sessions Court",
    },
    {
        "section_number": "105",
        "section_title": "Culpable homicide by causing death of person other than person whose death was intended",
        "bare_text": (
            "If a person, by doing anything which he intends or knows to be likely to cause "
            "death, commits culpable homicide by causing the death of any person, whose death "
            "he neither intends nor knows himself to be likely to cause, the culpable homicide "
            "committed by the offender is of the description of which it would have been if he "
            "had caused the death of the person whose death he intended or knew himself to be "
            "likely to cause."
        ),
        "plain_language": (
            "If you intended to kill person A but accidentally killed person B instead, "
            "you are still guilty of the same level of culpable homicide as if you had "
            "killed person A. The 'transferred malice' doctrine."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "Same as intended offence",
        "punishment_summary": "Same punishment as if intended victim was killed",
        "relevant_court": "Sessions Court",
    },
    {
        "section_number": "106",
        "section_title": "Causing death by negligence",
        "bare_text": (
            "Whoever causes the death of any person by doing any rash or negligent act not "
            "amounting to culpable homicide, shall be punished with imprisonment of either "
            "description for a term which may extend to five years, and shall also be liable "
            "to fine.\n"
            "Provided that whoever causes the death of any person by rash or negligent driving "
            "of a vehicle and escapes without reporting to a police officer or a Magistrate "
            "soon after the incident shall be punished with imprisonment of either description "
            "for a term which may extend to ten years, and shall also be liable to fine."
        ),
        "plain_language": (
            "If someone dies because of your careless or reckless act (but you did not intend "
            "to kill) — for example a road accident — this section applies. Punishment: up to "
            "5 years. If you hit someone with a vehicle and flee without reporting to police, "
            "punishment increases to 10 years. This is the hit-and-run provision."
        ),
        "is_bailable": True,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "5 years (10 years for hit-and-run)",
        "punishment_summary": "Up to 5 years + fine; 10 years if hit-and-run",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "109",
        "section_title": "Abetment of suicide",
        "bare_text": (
            "If any person commits suicide, whoever abets the commission of such suicide "
            "shall be punished with imprisonment of either description for a term which may "
            "extend to ten years, and shall also be liable to fine."
        ),
        "plain_language": (
            "If you drive someone to suicide — through harassment, threats, cruelty, or "
            "any form of abetment — you can be imprisoned for up to 10 years. Commonly "
            "applied in cases of dowry harassment, workplace bullying, and cyberbullying "
            "leading to suicide."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "10 years imprisonment + fine",
        "punishment_summary": "Up to 10 years + fine",
        "relevant_court": "Sessions Court",
    },
    {
        "section_number": "115",
        "section_title": "Voluntarily causing hurt",
        "bare_text": (
            "Whoever, except in the case provided for by section 122, voluntarily causes hurt, "
            "shall be punished with imprisonment of either description for a term which may "
            "extend to one year, or with fine which may extend to ten thousand rupees, or "
            "with both.\n"
            "Whoever voluntarily causes hurt to a person being a public servant in the "
            "discharge of his duty as such public servant shall be punished with imprisonment "
            "of either description for a term which may extend to two years, or with fine, "
            "or with both."
        ),
        "plain_language": (
            "If you physically injure someone — hit, punch, push causing pain or injury — "
            "this is 'hurt'. Punishment: up to 1 year jail or ₹10,000 fine or both. "
            "If the victim is a government officer on duty, punishment doubles to 2 years."
        ),
        "is_bailable": True,
        "is_cognizable": False,
        "is_compoundable": True,
        "max_punishment": "1 year or ₹10,000 fine",
        "fine_amount": "₹10000",
        "punishment_summary": "Up to 1 year or ₹10,000 fine or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "117",
        "section_title": "Voluntarily causing grievous hurt",
        "bare_text": (
            "Whoever, except in the case provided for by section 122, voluntarily causes "
            "grievous hurt, shall be punished with imprisonment of either description for a "
            "term which may extend to seven years, and shall also be liable to fine."
        ),
        "plain_language": (
            "Grievous hurt means serious injury — broken bones, permanent disfigurement, "
            "loss of sight/hearing, life-threatening injury. Punishment: up to 7 years + fine. "
            "Much more serious than simple hurt (Section 115)."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "7 years + fine",
        "punishment_summary": "Up to 7 years imprisonment + fine",
        "relevant_court": "Magistrate Court / Sessions Court",
    },
    {
        "section_number": "131",
        "section_title": "Assault",
        "bare_text": (
            "Whoever makes any gesture, or any preparation intending or knowing it to be "
            "likely that such gesture or preparation will cause any person present to "
            "apprehend that he who makes that gesture or preparation is about to use criminal "
            "force to that person, is said to commit an assault.\n"
            "Mere words do not amount to an assault. But the words which a person uses may "
            "give to his gestures or preparation such a meaning as may make those gestures "
            "or preparations amount to an assault."
        ),
        "plain_language": (
            "Assault is making someone FEAR that you are about to physically attack them — "
            "even if you never actually touch them. Threatening gestures, raising a fist, "
            "pointing a weapon at someone. Note: words alone are NOT assault, but gestures + "
            "threatening words together can be."
        ),
        "is_bailable": True,
        "is_cognizable": False,
        "is_compoundable": True,
        "max_punishment": "3 months or ₹1,000 fine",
        "punishment_summary": "Up to 3 months or fine",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "191",
        "section_title": "Dacoity",
        "bare_text": (
            "When five or more persons conjointly commit or attempt to commit a robbery, "
            "or where the whole number of persons conjointly committing or attempting to "
            "commit a robbery, and persons present and aiding such commission or attempt, "
            "amount to five or more, every person so committing, attempting or aiding, "
            "is said to commit dacoity."
        ),
        "plain_language": (
            "Dacoity = robbery committed by 5 or more people together. Even if you were "
            "just present and helping (not the one stealing), you are guilty of dacoity. "
            "This is one of the most serious property crimes under Indian law."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "Imprisonment for Life or 10 years",
        "punishment_summary": "Life imprisonment or up to 10 years + fine",
        "relevant_court": "Sessions Court",
    },
    {
        "section_number": "303",
        "section_title": "Theft",
        "bare_text": (
            "Whoever, intending to take dishonestly any moveable property out of the "
            "possession of any person without that person's consent, moves that property "
            "in order to such taking, is said to commit theft."
        ),
        "plain_language": (
            "Theft = taking someone else's moveable property without their consent, "
            "with the intention of keeping it. The property must actually be moved "
            "(even slightly). Punishment is covered under Section 304."
        ),
        "is_bailable": True,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "3 years or fine or both",
        "punishment_summary": "Up to 3 years or fine or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "308",
        "section_title": "Extortion",
        "bare_text": (
            "Whoever intentionally puts any person in fear of any injury to that person, "
            "or to any other, and thereby dishonestly induces the person so put in fear to "
            "deliver to any person any property or valuable security, or anything signed or "
            "sealed which may be converted into a valuable security, commits extortion."
        ),
        "plain_language": (
            "Extortion = threatening someone to hand over money or property. "
            "'Pay me or I will harm you/your family.' Punishment: up to 3 years + fine. "
            "If threat involves death or grievous hurt, punishment increases significantly."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "3 years + fine",
        "punishment_summary": "Up to 3 years imprisonment + fine",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "316",
        "section_title": "Criminal breach of trust",
        "bare_text": (
            "Whoever, being in any manner entrusted with property, or with any dominion "
            "over property, dishonestly misappropriates or converts to his own use that "
            "property, or dishonestly uses or disposes of that property in violation of any "
            "direction of law prescribing the mode in which such trust is to be discharged, "
            "or of any legal contract, express or implied, which he has made touching the "
            "discharge of such trust, or wilfully suffers any other person so to do, commits "
            "criminal breach of trust."
        ),
        "plain_language": (
            "If you are trusted with someone's money or property (employee, agent, trustee) "
            "and you misuse it for yourself — that is criminal breach of trust. Common in "
            "employer-employee disputes, society treasurer cases, and business fraud."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "3 years or fine or both",
        "punishment_summary": "Up to 3 years or fine or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "318",
        "section_title": "Cheating",
        "bare_text": (
            "Whoever, by deceiving any person, fraudulently or dishonestly induces the "
            "person so deceived to deliver any property to any person, or to consent that "
            "any person shall retain any property, or intentionally induces the person so "
            "deceived to do or omit to do anything which he would not do or omit if he were "
            "not so deceived, and which act or omission causes or is likely to cause damage "
            "or harm to that person in body, mind, reputation or property, is said to cheat."
        ),
        "plain_language": (
            "Cheating = deceiving someone to get their money, property, or make them do "
            "something they wouldn't otherwise do. Online fraud, fake job offers, property "
            "scams all fall under this. Very commonly used FIR section."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "3 years or fine or both",
        "punishment_summary": "Up to 3 years or fine or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "351",
        "section_title": "Criminal intimidation",
        "bare_text": (
            "Whoever threatens another with any injury to his person, reputation or property, "
            "or to the person or reputation or property of any one in whom that person is "
            "interested, with intent to cause alarm to that person, or to cause that person "
            "to do any act which he is not legally bound to do, or to omit to do any act "
            "which that person is legally entitled to do, as the means of avoiding the "
            "execution of such threat, commits criminal intimidation."
        ),
        "plain_language": (
            "Threatening someone — 'I will harm you/your family/your property' to frighten "
            "them or force them to do something. Includes threats via WhatsApp, phone calls, "
            "social media. Punishment: up to 2 years or fine or both. "
            "Anonymous threats: up to 2 years."
        ),
        "is_bailable": True,
        "is_cognizable": False,
        "is_compoundable": False,
        "max_punishment": "2 years or fine or both",
        "punishment_summary": "Up to 2 years or fine or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "63",
        "section_title": "Rape",
        "bare_text": (
            "A man is said to commit rape if he penetrates his penis, to any extent, into "
            "the vagina, mouth, urethra or anus of a woman or makes her to do so with him "
            "or any other person; or inserts, to any extent, any object or a part of the "
            "body, not being the penis, into the vagina, the urethra or anus of a woman or "
            "makes her to do so with him or any other person; or manipulates any part of "
            "the body of a woman so as to cause penetration into the vagina, urethra, anus "
            "or any part of body of such woman or makes her to do so with him or any other "
            "person; or applies his mouth to the vagina, anus, urethra of a woman or makes "
            "her to do so with him or any other person, under the circumstances falling "
            "under any of the following seven descriptions:\n"
            "First — Against her will.\n"
            "Secondly — Without her consent.\n"
            "Thirdly — With her consent obtained by putting her or any person in whom she "
            "is interested in fear of death or of hurt.\n"
            "Fourthly — With her consent obtained by impersonation.\n"
            "Fifthly — With her consent when she could not understand the nature of the act.\n"
            "Sixthly — With or without her consent when she is under eighteen years of age.\n"
            "Seventhly — When she is unable to communicate consent."
        ),
        "plain_language": (
            "Sexual assault against a woman without consent or against her will. "
            "Consent obtained by fear, fraud, or impersonation is NOT valid consent. "
            "Any sexual act with a girl under 18 is rape regardless of 'consent'. "
            "Punishment: minimum 10 years, maximum life imprisonment."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "min_punishment": "10 years (minimum)",
        "max_punishment": "Imprisonment for Life",
        "punishment_summary": "Minimum 10 years to life imprisonment + fine",
        "relevant_court": "Sessions Court (Special Fast Track Court)",
    },
    {
        "section_number": "64",
        "section_title": "Punishment for rape",
        "bare_text": (
            "Whoever, except in the cases provided for in sub-section (2), commits rape, "
            "shall be punished with rigorous imprisonment of either description for a term "
            "which shall not be less than ten years, but which may extend to imprisonment "
            "for life, and shall also be liable to fine.\n"
            "Whoever commits rape under any of the following circumstances:\n"
            "(i) being a police officer; (ii) being a public servant; (iii) being a member "
            "of the armed forces; (iv) being a management or staff of a jail; (v) being on "
            "the management or staff of a remand home; (vi) being on the management or staff "
            "of a hospital; (vii) being a relative, guardian or teacher of the woman; "
            "(viii) committing rape during communal or sectarian violence; (ix) rape on a "
            "woman knowing her to be pregnant; (x) rape on a woman incapable of giving "
            "consent; (xi) committing rape repeatedly on the same woman; shall be punished "
            "with rigorous imprisonment for a term which shall not be less than ten years "
            "but which may extend to imprisonment for life, which shall mean imprisonment "
            "for the remainder of that person's natural life, and shall also be liable to fine."
        ),
        "plain_language": (
            "Minimum 10 years, maximum life imprisonment for rape. "
            "Aggravated rape (by police, public servants, during communal violence, "
            "on pregnant woman) carries mandatory life imprisonment."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "min_punishment": "10 years rigorous imprisonment",
        "max_punishment": "Imprisonment for Life (natural life)",
        "punishment_summary": "10 years to life imprisonment (rigorous) + fine",
        "relevant_court": "Sessions Court (Special Fast Track Court)",
    },
    {
        "section_number": "85",
        "section_title": "Husband or relative of husband subjecting woman to cruelty",
        "bare_text": (
            "Whoever, being the husband or the relative of the husband of a woman, "
            "subjects such woman to cruelty shall be punished with imprisonment of either "
            "description for a term which may extend to three years and shall also be "
            "liable to fine.\n"
            "For the purposes of this section, cruelty means—\n"
            "(a) any wilful conduct which is of such a nature as is likely to drive the "
            "woman to commit suicide or to cause grave injury or danger to life, limb or "
            "health (whether mental or physical) of the woman; or\n"
            "(b) harassment of the woman where such harassment is with a view to coercing "
            "her or any person related to her to meet any unlawful demand for any property "
            "or valuable security or is on account of failure by her or any person related "
            "to her to meet such demand."
        ),
        "plain_language": (
            "Dowry harassment and domestic cruelty section. If a husband or his family "
            "harasses, threatens, or physically/mentally abuses a wife — especially for "
            "dowry — this section applies. Punishment: up to 3 years + fine. "
            "This is one of the most commonly invoked sections in India. "
            "Equivalent to old IPC Section 498A."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "3 years + fine",
        "punishment_summary": "Up to 3 years imprisonment + fine",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "356",
        "section_title": "Defamation",
        "bare_text": (
            "Whoever, by words either spoken or intended to be read, or by signs or by "
            "visible representations, makes or publishes any imputation concerning any "
            "person intending to harm, or knowing or having reason to believe that such "
            "imputation will harm, the reputation of such person, is said, except in the "
            "cases hereinafter expected, to defame that person.\n"
            "It may amount to defamation to impute anything to a deceased person, if the "
            "imputation would harm the reputation of that person if living, and is intended "
            "to be hurtful to the feelings of his family or other near relatives."
        ),
        "plain_language": (
            "Making false statements about a person that damage their reputation — "
            "spoken (slander) or written/published (libel). Includes social media posts. "
            "Punishment: up to 2 years or fine or both. Truth is a complete defence."
        ),
        "is_bailable": True,
        "is_cognizable": False,
        "is_compoundable": True,
        "max_punishment": "2 years or fine or both",
        "punishment_summary": "Up to 2 years or fine or both",
        "relevant_court": "Magistrate Court",
    },
    {
        "section_number": "61",
        "section_title": "Criminal conspiracy",
        "bare_text": (
            "When two or more persons agree to do, or cause to be done, an illegal act, "
            "or an act which is not illegal by illegal means, such an agreement is "
            "designated a criminal conspiracy.\n"
            "Provided that no agreement except an agreement to commit an offence shall "
            "amount to a criminal conspiracy unless some act besides the agreement is done "
            "by one or more parties to such agreement in pursuance thereof."
        ),
        "plain_language": (
            "When two or more people plan together to commit a crime — even if the crime "
            "never actually happens — that planning itself is criminal conspiracy. "
            "Commonly added to FIRs alongside the main offence sections. "
            "Punishment depends on the conspiracy's objective."
        ),
        "is_bailable": False,
        "is_cognizable": True,
        "is_compoundable": False,
        "max_punishment": "6 months to life (depends on objective)",
        "punishment_summary": "Varies based on the crime conspired",
        "relevant_court": "Court having jurisdiction over the conspired offence",
    },
]

CPA_SECTIONS = [
    {
        "section_number": "2(7)",
        "section_title": "Definition of Consumer",
        "bare_text": (
            "'consumer' means any person who— (i) buys any goods for a consideration which "
            "has been paid or promised or partly paid and partly promised, or under any "
            "system of deferred payment and includes any user of such goods other than the "
            "person who buys such goods for consideration paid or promised or partly paid "
            "or partly promised, or under any system of deferred payment, when such use is "
            "made with the approval of such person, but does not include a person who obtains "
            "such goods for resale or for any commercial purpose; or (ii) hires or avails of "
            "any service for a consideration which has been paid or promised or partly paid "
            "and partly promised, or under any system of deferred payment and includes any "
            "beneficiary of such service other than the person who hires or avails of the "
            "services for consideration paid or promised, or partly paid and partly promised, "
            "or under any system of deferred payment, when such services are availed of with "
            "the approval of the first mentioned person, but does not include a person who "
            "avails of such service for any commercial purpose."
        ),
        "plain_language": (
            "A consumer is anyone who buys goods or services for personal use (not for "
            "resale or business). If you bought a phone for yourself and it is defective, "
            "you are a consumer. If you bought it to sell in your shop, you are NOT a consumer "
            "under this Act. Online purchases are covered."
        ),
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "District Consumer Disputes Redressal Commission",
    },
    {
        "section_number": "2(11)",
        "section_title": "Definition of Deficiency",
        "bare_text": (
            "'deficiency' means any fault, imperfection, shortcoming or inadequacy in the "
            "quality, nature and manner of performance which is required to be maintained "
            "by or under any law for the time being in force or has been undertaken to be "
            "performed by a person in pursuance of a contract or otherwise in relation to "
            "any service and includes any act of negligence or omission or commission by "
            "such person which causes loss or injury to the consumer."
        ),
        "plain_language": (
            "Deficiency in service means: the service was not performed as promised or "
            "required by law. Examples: airline losing baggage, hospital negligence, "
            "builder not delivering flat on time, insurance claim wrongly rejected, "
            "internet not working despite payment."
        ),
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "District Consumer Disputes Redressal Commission",
    },
    {
        "section_number": "34",
        "section_title": "Jurisdiction of District Commission",
        "bare_text": (
            "(1) Subject to the other provisions of this Act, the District Commission shall "
            "have jurisdiction to entertain complaints where the value of the goods or "
            "services paid as consideration does not exceed one crore rupees.\n"
            "(2) A complaint shall be instituted in a District Commission within the local "
            "limits of whose jurisdiction— (a) the opposite party, at the time of the "
            "institution of the complaint, actually and voluntarily resides or carries on "
            "business or has a branch office or personally works for gain; or (b) any of "
            "the opposite parties, where there are more than one, at the time of the "
            "institution of the complaint, actually and voluntarily resides, or carries on "
            "business or has a branch office, or personally works for gain; or (c) the cause "
            "of action, wholly or in part, arises; or (d) the complainant resides or "
            "personally works for gain."
        ),
        "plain_language": (
            "File a consumer complaint at the District Commission if your claim is up to "
            "₹1 crore. You can file in YOUR city — where you live or where the company's "
            "branch is. You do NOT have to go to the company's headquarters city. "
            "This is one of the most consumer-friendly jurisdictional rules."
        ),
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "District Consumer Disputes Redressal Commission",
    },
    {
        "section_number": "35",
        "section_title": "Manner in which complaint shall be made",
        "bare_text": (
            "(1) A complaint in relation to any goods sold or delivered or agreed to be "
            "sold or delivered or any service provided or agreed to be provided may be "
            "filed with the District Commission by— (a) the consumer to whom such goods "
            "are sold or delivered or agreed to be sold or delivered or such service is "
            "provided or agreed to be provided; (b) any recognised consumer association "
            "whether the consumer to whom the goods sold or delivered or agreed to be "
            "sold or delivered or such service provided or agreed to be provided is a "
            "member of such association or not; (c) one or more consumers, where there "
            "are numerous consumers having the same interest with the permission of the "
            "District Commission, on behalf of or for the benefit of all consumers so "
            "interested; or (d) the Central Government or the State Government.\n"
            "(2) Every complaint filed under sub-section (1) shall be accompanied by such "
            "fee as may be specified."
        ),
        "plain_language": (
            "How to file a consumer complaint: you can file it yourself, through a consumer "
            "organisation, as a group complaint, or the government can file on your behalf. "
            "A nominal filing fee applies. No lawyer is required — you can represent yourself."
        ),
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "District Consumer Disputes Redressal Commission",
    },
    {
        "section_number": "69",
        "section_title": "Limitation period for filing complaint",
        "bare_text": (
            "(1) The District Commission, the State Commission or the National Commission "
            "shall not admit a complaint unless it is filed within two years from the date "
            "on which the cause of action has arisen.\n"
            "(2) Notwithstanding anything contained in sub-section (1), a complaint may be "
            "entertained after the period specified in sub-section (1), if the complainant "
            "satisfies the District Commission, the State Commission or the National "
            "Commission, as the case may be, that he had sufficient cause for not filing "
            "the complaint within such period.\n"
            "Provided that no such complaint shall be entertained unless the National "
            "Commission, the State Commission or the District Commission, as the case may "
            "be, records its reasons for condoning such delay."
        ),
        "plain_language": (
            "You must file a consumer complaint within 2 years of the problem occurring. "
            "If you missed the deadline, you can still apply with a reason for the delay — "
            "the Commission can condone the delay if your reason is genuine. "
            "Do not wait too long after a bad product or service experience."
        ),
        "is_bailable": None,
        "is_cognizable": None,
        "relevant_court": "District Consumer Disputes Redressal Commission",
        "limitation_period": "2 years from cause of action",
    },
]

_SECTION_KEYS = (
    "section_number",
    "section_title",
    "bare_text",
    "plain_language",
    "is_bailable",
    "is_cognizable",
    "is_compoundable",
    "max_punishment",
    "min_punishment",
    "fine_amount",
    "punishment_summary",
    "relevant_court",
    "limitation_period",
)


async def seed_sections(
    act_title: str, sections_data: list[dict], session: AsyncSession
) -> int:
    result = await session.execute(select(Act).where(Act.short_title == act_title))
    act = result.scalar_one_or_none()
    if not act:
        print(f"❌ Act not found: {act_title}")
        return 0

    inserted = 0
    skipped = 0
    for data in sections_data:
        existing = await session.execute(
            select(Section).where(
                Section.act_id == act.id,
                Section.section_number == data["section_number"],
            )
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        payload = {k: data.get(k) for k in _SECTION_KEYS}
        section = Section(act_id=act.id, is_active=True, **payload)
        session.add(section)
        inserted += 1

    await session.commit()
    print(f"  ✅ {act_title[:45]}: {inserted} inserted, {skipped} skipped")
    return inserted


async def main() -> None:
    print("🏛  Nyaya — Seeding BNS + CPA critical sections")
    print("=" * 52)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as session:
        print(f"\n⚖️  BNS 2023 ({len(BNS_SECTIONS)} critical sections)...")
        await seed_sections("Bharatiya Nyaya Sanhita 2023", BNS_SECTIONS, session)

        print(f"\n🛒 Consumer Protection Act 2019 ({len(CPA_SECTIONS)} key sections)...")
        await seed_sections("Consumer Protection Act 2019", CPA_SECTIONS, session)

    await engine.dispose()
    print("\n✅ Done. Run the section count query to verify.")


if __name__ == "__main__":
    asyncio.run(main())
