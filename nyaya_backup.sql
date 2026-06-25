--
-- PostgreSQL database dump
--

\restrict VCzWqReohJtDoosmh47V5oFP8y077EkckDFINOcnngjkC9fCLbDATqe8DcaEaGK

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: acttype; Type: TYPE; Schema: public; Owner: nyaya_user
--

CREATE TYPE public.acttype AS ENUM (
    'CENTRAL',
    'STATE',
    'CONSTITUTIONAL',
    'REGULATION'
);


ALTER TYPE public.acttype OWNER TO nyaya_user;

--
-- Name: lawcategory; Type: TYPE; Schema: public; Owner: nyaya_user
--

CREATE TYPE public.lawcategory AS ENUM (
    'CRIMINAL',
    'CIVIL',
    'FAMILY',
    'PROPERTY',
    'LABOUR',
    'CONSTITUTIONAL',
    'CORPORATE',
    'CONSUMER',
    'CYBER',
    'ENVIRONMENTAL',
    'TAX',
    'IPR',
    'NARCOTICS',
    'OTHER'
);


ALTER TYPE public.lawcategory OWNER TO nyaya_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: acts; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.acts (
    id integer NOT NULL,
    short_title character varying(300) NOT NULL,
    full_title character varying(500) NOT NULL,
    act_number character varying(50),
    year integer,
    act_type public.acttype NOT NULL,
    category public.lawcategory NOT NULL,
    state character varying(100),
    is_active boolean NOT NULL,
    replaces_act_id integer,
    source_url character varying(500),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.acts OWNER TO nyaya_user;

--
-- Name: acts_id_seq; Type: SEQUENCE; Schema: public; Owner: nyaya_user
--

CREATE SEQUENCE public.acts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.acts_id_seq OWNER TO nyaya_user;

--
-- Name: acts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nyaya_user
--

ALTER SEQUENCE public.acts_id_seq OWNED BY public.acts.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO nyaya_user;

--
-- Name: amendments; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.amendments (
    id integer NOT NULL,
    section_id integer NOT NULL,
    effective_date character varying(50),
    old_text text,
    new_text text NOT NULL,
    amendment_act character varying(300),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.amendments OWNER TO nyaya_user;

--
-- Name: amendments_id_seq; Type: SEQUENCE; Schema: public; Owner: nyaya_user
--

CREATE SEQUENCE public.amendments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.amendments_id_seq OWNER TO nyaya_user;

--
-- Name: amendments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nyaya_user
--

ALTER SEQUENCE public.amendments_id_seq OWNED BY public.amendments.id;


--
-- Name: lawyer_inquiries; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.lawyer_inquiries (
    id integer NOT NULL,
    lawyer_id integer NOT NULL,
    user_name character varying(200) NOT NULL,
    user_phone character varying(20) NOT NULL,
    query_summary text,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.lawyer_inquiries OWNER TO nyaya_user;

--
-- Name: lawyer_inquiries_id_seq; Type: SEQUENCE; Schema: public; Owner: nyaya_user
--

CREATE SEQUENCE public.lawyer_inquiries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lawyer_inquiries_id_seq OWNER TO nyaya_user;

--
-- Name: lawyer_inquiries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nyaya_user
--

ALTER SEQUENCE public.lawyer_inquiries_id_seq OWNED BY public.lawyer_inquiries.id;


--
-- Name: lawyers; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.lawyers (
    id integer NOT NULL,
    full_name character varying(200) NOT NULL,
    specialization character varying(200) NOT NULL,
    location character varying(200) NOT NULL,
    experience_years integer,
    bio text,
    phone character varying(20),
    email character varying(100),
    is_verified boolean DEFAULT false NOT NULL,
    profile_image_url character varying(500),
    rating integer DEFAULT 5 NOT NULL
);


ALTER TABLE public.lawyers OWNER TO nyaya_user;

--
-- Name: lawyers_id_seq; Type: SEQUENCE; Schema: public; Owner: nyaya_user
--

CREATE SEQUENCE public.lawyers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lawyers_id_seq OWNER TO nyaya_user;

--
-- Name: lawyers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nyaya_user
--

ALTER SEQUENCE public.lawyers_id_seq OWNED BY public.lawyers.id;


--
-- Name: query_logs; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.query_logs (
    id integer NOT NULL,
    query_text text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    response_text text,
    category character varying(100),
    state character varying(100),
    provider character varying(50),
    confidence_score double precision,
    lang character varying(10),
    response_time_ms integer
);


ALTER TABLE public.query_logs OWNER TO nyaya_user;

--
-- Name: query_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: nyaya_user
--

CREATE SEQUENCE public.query_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.query_logs_id_seq OWNER TO nyaya_user;

--
-- Name: query_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nyaya_user
--

ALTER SEQUENCE public.query_logs_id_seq OWNED BY public.query_logs.id;


--
-- Name: sections; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.sections (
    id integer NOT NULL,
    act_id integer NOT NULL,
    section_number character varying(50) NOT NULL,
    section_title character varying(500),
    bare_text text NOT NULL,
    plain_language text,
    is_bailable boolean,
    is_cognizable boolean,
    is_compoundable boolean,
    punishment_summary character varying(500),
    min_punishment character varying(200),
    max_punishment character varying(200),
    fine_amount character varying(200),
    relevant_court character varying(200),
    limitation_period character varying(200),
    qdrant_id character varying(100),
    embedding_model character varying(100),
    is_active boolean NOT NULL,
    is_amended boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.sections OWNER TO nyaya_user;

--
-- Name: sections_id_seq; Type: SEQUENCE; Schema: public; Owner: nyaya_user
--

CREATE SEQUENCE public.sections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sections_id_seq OWNER TO nyaya_user;

--
-- Name: sections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nyaya_user
--

ALTER SEQUENCE public.sections_id_seq OWNED BY public.sections.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: nyaya_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    supabase_id character varying(100),
    phone character varying(20),
    email character varying(255),
    is_lawyer boolean NOT NULL,
    preferred_language character varying(10) NOT NULL,
    state character varying(100),
    daily_query_count integer NOT NULL,
    daily_reset_at timestamp with time zone,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO nyaya_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: nyaya_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO nyaya_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nyaya_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: acts id; Type: DEFAULT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.acts ALTER COLUMN id SET DEFAULT nextval('public.acts_id_seq'::regclass);


--
-- Name: amendments id; Type: DEFAULT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.amendments ALTER COLUMN id SET DEFAULT nextval('public.amendments_id_seq'::regclass);


--
-- Name: lawyer_inquiries id; Type: DEFAULT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.lawyer_inquiries ALTER COLUMN id SET DEFAULT nextval('public.lawyer_inquiries_id_seq'::regclass);


--
-- Name: lawyers id; Type: DEFAULT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.lawyers ALTER COLUMN id SET DEFAULT nextval('public.lawyers_id_seq'::regclass);


--
-- Name: query_logs id; Type: DEFAULT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.query_logs ALTER COLUMN id SET DEFAULT nextval('public.query_logs_id_seq'::regclass);


--
-- Name: sections id; Type: DEFAULT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.sections ALTER COLUMN id SET DEFAULT nextval('public.sections_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: acts; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.acts (id, short_title, full_title, act_number, year, act_type, category, state, is_active, replaces_act_id, source_url, created_at, updated_at) FROM stdin;
1	Bharatiya Nyaya Sanhita, 2023	The Bharatiya Nyaya Sanhita, 2023	\N	2023	CENTRAL	CRIMINAL	\N	t	\N	\N	2026-05-30 08:36:10.745046+00	2026-05-30 08:36:10.745046+00
2	Bharatiya Nyaya Sanhita 2023	The Bharatiya Nyaya Sanhita, 2023	\N	2023	CENTRAL	CRIMINAL	\N	t	\N	\N	2026-06-01 09:56:39.581876+00	2026-06-01 09:56:39.581876+00
3	Negotiable Instruments Act 1881 — Section 138	The Negotiable Instruments Act, 1881 — Cheque Dishonour	\N	1881	CENTRAL	CIVIL	\N	t	\N	\N	2026-06-01 11:07:20.742842+00	2026-06-01 11:07:20.742842+00
4	Protection of Women from Domestic Violence Act 2005	The Protection of Women from Domestic Violence Act, 2005	\N	2005	CENTRAL	FAMILY	\N	t	\N	\N	2026-06-01 11:07:20.969189+00	2026-06-01 11:07:20.969189+00
5	Information Technology Act 2000	The Information Technology Act, 2000	\N	2000	CENTRAL	CYBER	\N	t	\N	\N	2026-06-01 11:07:20.977169+00	2026-06-01 11:07:20.977169+00
6	Right to Information Act 2005	The Right to Information Act, 2005	\N	2005	CENTRAL	CONSTITUTIONAL	\N	t	\N	\N	2026-06-01 11:07:20.98279+00	2026-06-01 11:07:20.98279+00
7	Protection of Children from Sexual Offences Act 2012	The Protection of Children from Sexual Offences Act, 2012 (POCSO)	\N	2012	CENTRAL	CRIMINAL	\N	t	\N	\N	2026-06-01 11:07:20.988496+00	2026-06-01 11:07:20.988496+00
8	Hindu Marriage Act 1955	The Hindu Marriage Act, 1955	\N	1955	CENTRAL	FAMILY	\N	t	\N	\N	2026-06-01 11:07:20.995458+00	2026-06-01 11:07:20.995458+00
9	SC ST Prevention of Atrocities Act 1989	The Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989	\N	1989	CENTRAL	CRIMINAL	\N	t	\N	\N	2026-06-01 11:07:21.003025+00	2026-06-01 11:07:21.003025+00
10	Sexual Harassment of Women at Workplace Act 2013	The Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013	\N	2013	CENTRAL	LABOUR	\N	t	\N	\N	2026-06-01 11:07:21.009183+00	2026-06-01 11:07:21.009183+00
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.alembic_version (version_num) FROM stdin;
update_query_logs
\.


--
-- Data for Name: amendments; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.amendments (id, section_id, effective_date, old_text, new_text, amendment_act, notes, created_at) FROM stdin;
\.


--
-- Data for Name: lawyer_inquiries; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.lawyer_inquiries (id, lawyer_id, user_name, user_phone, query_summary, status, created_at) FROM stdin;
\.


--
-- Data for Name: lawyers; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.lawyers (id, full_name, specialization, location, experience_years, bio, phone, email, is_verified, profile_image_url, rating) FROM stdin;
\.


--
-- Data for Name: query_logs; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.query_logs (id, query_text, created_at, response_text, category, state, provider, confidence_score, lang, response_time_ms) FROM stdin;
1	what is section 103 BNS	2026-06-01 10:30:32.354427+00	**Section 103 BNS prescribes the punishment for murder, which can be either death or imprisonment for life, along with a fine.**\n\n**Applicable Laws:**\n- BNS Section 103: Punishment for murder | Punishment: Death or imprisonment for life and fine | Non-Bailable\n\n**What You Should Do:**\n1. If you are a victim or witness of murder, immediately report to the police.\n2. Cooperate with the investigation and provide any relevant information.\n3. If you are accused of murder, consult a qualified advocate to understand your rights and options.\n\n**Important:** Murder is a serious offense with severe punishments, and it's crucial to seek legal advice if you are involved in such a case.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	5922
2	murder punishment India	2026-06-01 10:40:57.141626+00	**Direct Answer:** In India, the punishment for murder can be life imprisonment or the death penalty. \n\n**Applicable Laws:**\n- None § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you or someone you know is accused of murder, immediately contact a qualified advocate.\n2. Gather all relevant evidence and witness statements to build a strong defense.\n3. Cooperate with the authorities during the investigation.\n\n**Important:** The punishment for murder is severe, and the legal process can be complex. It's crucial to seek professional legal advice to navigate the situation effectively.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	3363
3	murder punishment India	2026-06-01 10:49:14.154799+00	**Direct Answer:** The punishment for murder in India can be life imprisonment or the death penalty. \n\n**Applicable Laws:**\n- None § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you or someone you know is accused of murder, immediately contact a qualified advocate.\n2. Gather all relevant evidence and witness statements to build a strong defense.\n3. Cooperate with the investigation and court proceedings.\n\n**Important:** The death penalty is awarded in the rarest of rare cases, and the punishment is decided based on the severity of the crime and the circumstances surrounding it.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	\N
4	my husband beats me daily	2026-06-01 11:33:23.795168+00		criminal	\N	rag-only	\N	en	\N
5	my husband beats me daily	2026-06-01 11:34:36.493426+00	**Direct Answer:** You can file a complaint under the domestic violence laws, and the police are bound to take action. \n\n**Applicable Laws:**\n- Unfortunately, I don't have this specific law in my database yet.\n\n**What You Should Do:**\n1. Contact the National Commission for Women (NCW) helpline at 011-26942369 or 011-26944754 for immediate assistance.\n2. Reach out to local NGOs or women's organizations that provide support and shelter to victims of domestic violence.\n3. Consider filing a complaint with the police, and they will guide you through the process.\n\n**Important:** Please prioritize your safety, and if you feel threatened, try to reach a safe place as soon as possible.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	7035
6	cheque bounced what to do	2026-06-01 11:37:39.178046+00	**Direct Answer:** If a cheque has bounced, the payee (the person to whom the cheque was given) can file a complaint under Section 138 of the Negotiable Instruments Act 1881. The drawer (the person who issued the cheque) can be liable for up to 2 years imprisonment or a fine up to double the cheque amount.\n\n**Applicable Laws:**\n- Negotiable Instruments Act 1881 Section 138: Dishonour of cheque for insufficiency of funds | Punishment: Up to 2 years imprisonment or fine up to 2x cheque amount | Bailable\n\n**What You Should Do:**\n1. Send a notice to the drawer within 30 days of the cheque bounce, demanding payment.\n2. If the drawer does not pay within 15 days of receiving the notice, file a complaint in the Magistrate Court where the cheque was presented.\n3. Provide all necessary documents, including the bounced cheque, notice, and proof of sending the notice.\n\n**Important:** The complaint must be filed within 1 month of the expiry of the 15-day notice period. It is recommended to consult a qualified advocate for assistance with the process.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	23474
7	my husband beats me daily	2026-06-01 11:53:31.674598+00	**Direct Answer:** You can file a complaint under the domestic violence laws and seek protection from the court. \n\n**Applicable Laws:**\n- Unfortunately, I don't have this specific law in my database yet.\n\n**What You Should Do:**\n1. Contact the National Commission for Women (NCW) helpline 181 for immediate assistance and guidance.\n2. Reach out to a local women's organization or a domestic violence shelter for support.\n3. Consider filing a complaint with the police and seeking a protection order from the court.\n\n**Important:** Please prioritize your safety and well-being. If you are in immediate danger, call the emergency services or reach out to a trusted friend or family member for help.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	1424
8	cheque bounced what to do	2026-06-01 11:53:35.278912+00	**Direct Answer:** If a cheque has bounced, the payee (the person to whom the cheque was issued) can take legal action against the drawer (the person who issued the cheque) under Section 138 of the Negotiable Instruments Act, 1881. \n\n**Applicable Laws:**\n- Negotiable Instruments Act 1881 Section 138: Deals with the dishonour of a cheque for insufficiency of funds. Punishment: Up to 2 years imprisonment or fine up to 2x cheque amount. Bailable.\n- Negotiable Instruments Act 1881 Section 139: Presumption in favour of the holder of the cheque that it was received for the discharge of a debt or liability.\n- Negotiable Instruments Act 1881 Section 141: Offences by companies, where the company and its directors/managers can be held liable for a bounced cheque.\n\n**What You Should Do:**\n1. **Send a notice**: Within 30 days of the cheque bounce, send a notice to the drawer demanding payment of the cheque amount along with the bank charges.\n2. **Wait for 15 days**: Wait for 15 days from the date of sending the notice for the drawer to make the payment.\n3. **File a complaint**: If the payment is not made within 15 days, file a complaint under Section 138 of the Negotiable Instruments Act, 1881, in the Magistrate Court where the cheque was presented.\n\n**Important:** The complaint must be filed within one month from the date of the expiry of the notice period (15 days). The court may order the drawer to pay the cheque amount along with a fine, which can be up to twice the cheque amount.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	3541
9	my husband beats me daily	2026-06-01 11:54:07.570497+00	**Direct Answer:** You can file a complaint under the domestic violence laws and seek protection from your husband's abuse. \n\n**Applicable Laws:**\n- Unfortunately, I don't have the specific domestic violence laws in my database yet.\n\n**What You Should Do:**\n1. Contact the National Commission for Women (NCW) helpline 181 for immediate support and guidance.\n2. Reach out to a local women's shelter or a non-governmental organization (NGO) that provides support to victims of domestic violence.\n3. Consider filing a complaint with the police and seeking a protection order from the court.\n\n**Important:** Please prioritize your safety and well-being. If you are in immediate danger, call the police or emergency services.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	\N
10	cheque bounced what to do	2026-06-01 11:54:58.774822+00	**Direct Answer:** If a cheque has bounced, you can send a notice to the drawer (the person who issued the cheque) demanding payment within 15 days, and if the payment is not made, you can file a complaint under Section 138 of the Negotiable Instruments Act, 1881.\n\n**Applicable Laws:**\n- Negotiable Instruments Act, 1881 - Section 138: Dishonour of cheque for insufficiency of funds | Punishment: Up to 2 years imprisonment or fine up to 2x cheque amount | Bailable\n- Negotiable Instruments Act, 1881 - Section 139: Presumption in favour of holder | Bailable\n- Negotiable Instruments Act, 1881 - Section 141: Offences by companies | Bailable\n\n**What You Should Do:**\n1. Send a notice to the drawer demanding payment within 15 days, as per Section 138 of the Negotiable Instruments Act, 1881.\n2. If the payment is not made, file a complaint with the Magistrate Court within 30 days of the expiry of the notice period.\n3. Provide all necessary documents, including the bounced cheque, the notice sent to the drawer, and any other relevant evidence.\n\n**Important:** The complaint must be filed within the prescribed time limit, and it is essential to follow the proper procedure to ensure a successful prosecution.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	\N
11	my husband beats me daily	2026-06-01 12:00:16.946706+00	**Direct Answer:** You can file a complaint under the Protection of Women from Domestic Violence Act, 2005, and seek protection from your husband's abuse.\n\n**Applicable Laws:**\n- Unfortunately, I don't have the specific domestic violence laws in my database yet, but I can tell you that the Protection of Women from Domestic Violence Act, 2005, provides protection to women from domestic violence.\n\n**What You Should Do:**\n1. Contact the National Commission for Women (NCW) helpline 181 for immediate support and guidance.\n2. Reach out to a local women's shelter or a non-governmental organization (NGO) that provides support to victims of domestic violence.\n3. Consider filing a complaint with the police and seeking a protection order from the court.\n\n**Important:** Please prioritize your safety and well-being. If you are in immediate danger, call the police or emergency services.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	\N
12	my husband beats me daily	2026-06-01 12:17:35.584194+00	**Direct Answer:** Domestic violence is a serious offense in India, and you have the right to protection and support. \n\n**Applicable Laws:**\n- None: I don't have this specific law in my database yet. However, the Protection of Women from Domestic Violence Act, 2005, and Section 498-A of the Bharatiya Nyaya Sanhita (replacing IPC 498-A) generally deal with domestic violence and cruelty against women.\n\n**What You Should Do:**\n1. Reach out to a trusted friend, family member, or a women's helpline (such as the National Commission for Women helpline 1091) for immediate support.\n2. Document all incidents of abuse, including dates, times, and details of what happened.\n3. Consider filing a complaint with the police or a court under the Protection of Women from Domestic Violence Act, 2005.\n\n**Important:** Your safety is paramount. If you're in immediate danger, call the police or a crisis helpline. You have the right to live a life free from violence and abuse.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	4498
13	my husband beats me daily	2026-06-01 12:18:17.771278+00	**Direct Answer:** You can file a complaint under the domestic violence laws and seek protection from your husband's daily beatings. \n\n**Applicable Laws:**\n- Unfortunately, I don't have this specific law in my database yet.\n\n**What You Should Do:**\n1. Contact the National Commission for Women (NCW) helpline at 011-26942369 or 011-26944754 for immediate assistance.\n2. Reach out to local NGOs or women's organizations that provide support and shelter to victims of domestic violence.\n3. Consider filing a complaint with the police and seeking a protection order from the court.\n\n**Important:** Please prioritize your safety and well-being. If you are in immediate danger, call the emergency services or reach out to a trusted friend or family member for help.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	\N
14	Police arrested me without telling me why. What are my constitutional rights?	2026-06-01 12:49:10.728733+00	**Direct Answer:** You have the right to know the grounds of your arrest and the right to be produced before a magistrate within 24 hours. \n\n**Applicable Laws:**\n- Unfortunately, I don't have the specific law in my database yet, but generally, the Code of Criminal Procedure and the Constitution of India provide protections for individuals arrested by the police.\n\n**What You Should Do:**\n1. Ask the police to inform you of the reasons for your arrest.\n2. Request to contact a family member, friend, or lawyer to inform them of your situation.\n3. Ensure you are produced before a magistrate within 24 hours of your arrest.\n\n**Important:** It is crucial to remember that you have the right to remain silent and the right to legal counsel. Do not hesitate to ask for these rights to be respected.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	\N
15	what is section 300	2026-06-10 06:37:37.512839+00	**Section 300 of the Bharatiya Nyaya Sanhita 2023 defines murder as culpable homicide with the intention of causing death or with the knowledge that the act is so imminently dangerous that it must in all probability cause death.** This section essentially outlines the conditions under which an act of culpable homicide would be considered as murder.\n\n**Applicable Laws:**\n- Bharatiya Nyaya Sanhita 2023 § 300: Defines murder as culpable homicide by causing death with the intention of causing death, or with the knowledge that the act is so imminently dangerous that it must in all probability cause death | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you or someone you know is involved in a situation that could lead to or has led to a charge under Section 300, it is crucial to seek legal counsel immediately.\n2. Understanding the specifics of the case, including the circumstances and intentions involved, is key to navigating the legal process.\n3. Consult with a qualified advocate who can provide guidance based on the details of the case and the applicable laws.\n\n**Important:** The punishment for murder under Section 300 of the Bharatiya Nyaya Sanhita 2023 can be severe, including life imprisonment or the death penalty, making it essential to approach such cases with the utmost seriousness and legal expertise.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	34669
16	Police arrested me without telling me why. What are my constitutional rights?	2026-06-10 06:45:40.432419+00	**Direct Answer:** You have the right to be informed of the grounds of your arrest as soon as possible, as per Article 22 of the Constitution of India. \n\n**Applicable Laws:**\n- Article 22 of the Constitution of India: Protection against arrest and detention in certain cases, stating that no person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest.\n\n**What You Should Do:**\n1. Demand to know the reasons for your arrest immediately.\n2. If not informed, request to contact a lawyer or a family member to inform them about your arrest.\n3. File a complaint with the concerned authorities if your rights are violated.\n\n**Important:** The constitutional mandate of informing the arrestee the grounds of arrest is mandatory in all offences under all statutes, including offences under special laws, as supported by legal judgments such as Zamkhankap S/O Thangzachin vs The State Of Maharashtra.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	51612
17	test murder section	2026-06-10 06:49:25.962328+00	**Direct Answer:** Murder is defined as culpable homicide with the intention of causing death or knowledge that the act is imminently dangerous and must cause death. The punishment for murder is life imprisonment or the death penalty.\n\n**Applicable Laws:**\n- Bharatiya Nyaya Sanhita, 2023 § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death. | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you or someone you know is accused of murder, immediately contact a qualified advocate.\n2. Gather all relevant evidence and witness statements to build a strong defense.\n3. Cooperate fully with the investigation and court proceedings.\n\n**Important:** Murder is a non-bailable offense, and the punishment can be severe, including life imprisonment or the death penalty. It is crucial to seek professional legal advice as soon as possible.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	70585
18	Police arrested me without telling me why. What are my constitutional rights?	2026-06-10 06:52:09.753466+00	**Direct Answer:** As per Article 22 of the Constitution of India, you have the right to be informed of the grounds of your arrest as soon as possible, and the police are obligated to inform you about the reasons for your arrest.\n\n**Applicable Laws:**\n- Article 22 of the Constitution of India: Protection against arrest and detention in certain cases, stating that no person who is arrested shall be detained in custody without being informed, as soon as may be, of the grounds for such arrest.\n\n**What You Should Do:**\n1. Demand to know the reasons for your arrest immediately, citing your constitutional right under Article 22.\n2. If not informed, request to contact a lawyer or a family member to inform them about your arrest.\n3. File a complaint with the concerned authorities if your rights are violated, as supported by legal judgments such as Bail Appln./624/2025, which emphasizes the importance of informing the arrestee about the grounds of arrest.\n\n**Important:** The Supreme Court has consistently held that the right to be informed of the grounds of arrest is a fundamental right, and any violation of this right can lead to the arrest being deemed unlawful. As stated in Article 22, this right is essential to ensure that the arrestee's personal liberty is protected.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	\N
19	murder punishment India	2026-06-10 07:52:54.534042+00	**Direct Answer:** In India, the punishment for murder is life imprisonment or the death penalty, as per Bharatiya Nyaya Sanhita, 2023 § 300. \n\n**Applicable Laws:**\n- Bharatiya Nyaya Sanhita, 2023 § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death. | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you or someone you know is accused of murder, immediately contact a qualified advocate.\n2. Gather all relevant evidence and witness statements to build a strong defense.\n3. Cooperate with the investigation and court proceedings.\n\n**Important:** The punishment for murder can be enhanced to life imprisonment with fine if the offence is committed against a member of a Scheduled Caste or a Scheduled Tribe, as per SC ST Prevention of Atrocities Act 1989 § 3(2).\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	15197
20	murder punishment India	2026-06-10 07:52:56.943864+00	**Direct Answer:** In India, the punishment for murder is life imprisonment or the death penalty, as per Bharatiya Nyaya Sanhita, 2023 § 300. \n\n**Applicable Laws:**\n- Bharatiya Nyaya Sanhita, 2023 § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death. | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you or someone you know is accused of murder, immediately contact a qualified advocate.\n2. Gather all relevant evidence and witness statements to build a strong defense.\n3. Cooperate with the investigation and court proceedings.\n\n**Important:** The punishment for murder can be enhanced to life imprisonment with fine if the offence is committed against a member of a Scheduled Caste or a Scheduled Tribe, as per SC ST Prevention of Atrocities Act 1989 § 3(2).\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	1942
21	section 300 murder	2026-06-10 07:56:26.624175+00	**Direct Answer:** Section 300 of the Bharatiya Nyaya Sanhita 2023 defines murder as culpable homicide by causing death with the intention of causing death, or with the knowledge that the act is so imminently dangerous that it must in all probability cause death. The punishment for murder under this section is life imprisonment or death penalty.\n\n**Applicable Laws:**\n- Bharatiya Nyaya Sanhita 2023 § 300: Defines murder as culpable homicide by causing death with the intention of causing death, or with the knowledge that the act is so imminently dangerous that it must in all probability cause death. | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you are accused of murder under Section 300, immediately contact a qualified advocate to understand your rights and the legal process.\n2. Gather all relevant evidence and witness statements to support your case.\n3. Cooperate with the investigation and court proceedings to ensure a fair trial.\n\n**Important:** Murder is a serious offence with severe punishments, and it is essential to take immediate legal action to protect your rights. As stated in various legal judgments, including those found on Indian Kanoon, Section 300 of the Bharatiya Nyaya Sanhita 2023 defines murder with reference to culpable homicide, and the requirements given in this section must be met for a conviction.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	17334
22	murder	2026-06-17 08:48:42.446182+00	**Direct Answer:** Murder is defined as culpable homicide with the intention of causing death or with the knowledge that the act is so imminently dangerous that it must in all probability cause death, punishable with life imprisonment or death penalty.\n\n**Applicable Laws:**\n- None § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death | Punishment: Life imprisonment or death penalty | Non-Bailable\n- None § 3(2): If someone commits a serious crime (murder, etc.) specifically because the victim is SC/ST, punishment is increased to LIFE IMPRISONMENT | Punishment: Life imprisonment + fine (for targeting based on SC/ST identity) | Non-Bailable\n\n**What You Should Do:**\n1. Report the incident to the police immediately.\n2. Cooperate with the investigation and provide any relevant information.\n3. If you are a witness or have any information about the case, you may be required to testify in court.\n\n**Important:** Murder is a serious offense with severe punishments, and it's essential to take immediate action if you are involved in or witness such a crime.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	45651
23	murder	2026-06-17 08:50:30.205683+00	**Direct Answer:** Murder is defined as culpable homicide with the intention of causing death or with the knowledge that the act is so imminently dangerous that it must in all probability cause death. \nThe punishment for murder can be life imprisonment or the death penalty.\n\n**Applicable Laws:**\n- None § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death. | Punishment: Life imprisonment or death penalty | Non-Bailable\n\n**What You Should Do:**\n1. If you are a victim or witness of a murder, immediately contact the local police and report the incident.\n2. If you are accused of murder, it is crucial to seek legal counsel from a qualified advocate.\n3. Cooperate with the investigation and provide any relevant information to the authorities.\n\n**Important:** Murder is a serious and non-bailable offence, and it is essential to take immediate action if you are involved in such a case.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	2317
24	murder	2026-06-17 08:51:40.019769+00	**Direct Answer:** Murder is defined as culpable homicide with the intention of causing death or with the knowledge that the act is so imminently dangerous that it must in all probability cause death, punishable with life imprisonment or death penalty.\n\n**Applicable Laws:**\n- None § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death. | Punishment: Life imprisonment or death penalty | Non-Bailable\n- None § 3(2): If someone commits a serious crime (murder, rape, etc.) specifically because the victim is SC/ST, punishment is increased to LIFE IMPRISONMENT. | Punishment: Life imprisonment + fine (for targeting based on SC/ST identity) | Non-Bailable\n\n**What You Should Do:**\n1. Report the incident to the police immediately.\n2. Cooperate with the investigation and provide any relevant information.\n3. Seek legal counsel if you are a suspect or have any concerns about the investigation.\n\n**Important:** Murder is a serious offense with severe consequences, and it's essential to take immediate action if you are involved in such a situation.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	2337
25	What is section 300?	2026-06-17 19:02:18.574134+00	**Direct Answer:** I don't have this specific law in my database yet.\n\n**Applicable Laws:** None available for Section 300.\n\n**What You Should Do:**\n1. Check the latest version of the Bharatiya Nyaya Sanhita (BNS) or the Indian Penal Code (IPC) for the relevant section.\n2. Consult a legal expert or advocate for guidance on the specific section.\n3. Visit the official government website for the most up-to-date information on laws and sections.\n\n**Important:** It is crucial to consult a reliable source for legal information to ensure accuracy and relevance.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	21669
26	What is Section 300 BNS?	2026-06-20 16:04:24.454652+00	**Direct Answer:** Section 300 of the Bharatiya Nyaya Sanhita (BNS) deals with the offense of disturbing a religious assembly. \n\n**Applicable Laws:**\n- Bharatiya Nyaya Sanhita (BNS) Section 300: Whoever voluntarily causes disturbance to any assembly lawfully engaged in the performance of religious worship, or religious ceremonies, shall be punished | Punishment: As per the BNS, though specific punishment details are not provided in the given context.\n\n**What You Should Do:**\n1. Avoid engaging in any activity that disturbs religious assemblies or ceremonies.\n2. Be respectful of all religious gatherings and ceremonies.\n3. If you witness any disturbance, report it to the authorities immediately.\n\n**Important:** It is crucial to respect and maintain peace during religious assemblies to avoid legal consequences.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	4328
27	murder	2026-06-20 16:04:42.634048+00	**Direct Answer:** Murder is defined as culpable homicide with the intention of causing death or with the knowledge that the act is so imminently dangerous that it must in all probability cause death, punishable with life imprisonment or death penalty.\n\n**Applicable Laws:**\n- Bharatiya Nyaya Sanhita, 2023 § 300: Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death. | Punishment: Life imprisonment or death penalty | Non-Bailable\n- SC ST Prevention of Atrocities Act 1989 § 3(2): If someone commits a serious crime (like murder) specifically because the victim is SC/ST, punishment is increased to life imprisonment. | Punishment: Life imprisonment + fine (for targeting based on SC/ST identity) | Non-Bailable\n\n**What You Should Do:**\n1. Report the incident to the police immediately.\n2. Cooperate with the investigation and provide any relevant information.\n3. If you are a victim or a witness, you may be eligible for protection under the law.\n\n**Important:** Murder is a serious offence with severe punishments, including life imprisonment or death penalty. If you or someone you know is involved in a murder case, it is crucial to seek legal counsel from a qualified advocate.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	13510
28	cybercrime hacking	2026-06-20 16:04:53.223999+00	**Direct Answer:** Cybercrime hacking is a serious offense in India, punishable under the Information Technology Act 2000, with imprisonment up to 3 years and/or a fine of up to ₹5 lakh. \n\n**Applicable Laws:**\n- Information Technology Act 2000 § 66: Hacking or unauthorized computer access done dishonestly or fraudulently is a criminal offense, punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both. | Punishment: Up to 3 years or ₹5 lakh or both | Bailable\n- Information Technology Act 2000 § 43: If someone hacks your computer, copies your data without permission, installs a virus, or disrupts your computer system — they are civilly liable to pay you compensation. | Punishment: None | Bailable\n\n**What You Should Do:**\n1. Immediately report the incident to the cybercrime cell or the local police station.\n2. Gather evidence, such as logs and screenshots, to support your complaint.\n3. Consult a cyber lawyer to understand your rights and options.\n\n**Important:** Cybercrime hacking can lead to serious consequences, including financial loss, identity theft, and reputational damage. It is essential to take prompt action and seek professional help to mitigate the effects.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	\N	\N	groq/llama-3.3-70b-versatile	\N	en	4017
29	domestic violence protection order	2026-06-20 16:04:58.534294+00	**Direct Answer:** A domestic violence protection order is a legal order issued by a Magistrate under the Protection of Women from Domestic Violence Act 2005, which prohibits the respondent from committing any act of domestic violence against the aggrieved person.\n\n**Applicable Laws:**\n- Protection of Women from Domestic Violence Act 2005 § 18: The Magistrate may pass a protection order in favour of the aggrieved person and prohibit the respondent from committing any act of domestic violence, aiding or abetting in the commission of acts of domestic violence, and other related actions. | Punishment: None | Non-Bailable\n- Protection of Women from Domestic Violence Act 2005 § 31: A breach of protection order, or of an interim protection order, by the respondent shall be an offence under this Act and shall be punishable with imprisonment.\n\n**What You Should Do:**\n1. File an application under Section 12 of the Protection of Women from Domestic Violence Act 2005 to the Magistrate seeking a protection order.\n2. Provide evidence of domestic violence, such as medical records, witness statements, and other relevant documents.\n3. Attend the court hearing and present your case to the Magistrate.\n\n**Important:** A breach of a protection order is a criminal offence punishable with imprisonment. If you are a victim of domestic violence, it is essential to seek help and file an application for a protection order to ensure your safety.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	family	\N	groq/llama-3.3-70b-versatile	\N	en	5237
30	domestic violence section	2026-06-20 16:16:13.276088+00	**Direct Answer:** Domestic violence is defined under Section 3 of the Protection of Women from Domestic Violence Act 2005, which includes physical, sexual, verbal, emotional, and economic abuse.\n\n**Applicable Laws:**\n- Protection of Women from Domestic Violence Act 2005 § 3: Defines domestic violence as any act, omission, or commission that harms or injures the health, safety, life, limb, or well-being of the aggrieved person, including physical abuse, sexual abuse, verbal and emotional abuse, and economic abuse. | Punishment: None | Non-Bailable\n\n**What You Should Do:**\n1. If you are a victim of domestic violence, immediately contact the National Domestic Violence Helpline (181) or the local police for assistance.\n2. File a complaint under Section 12 of the Domestic Violence Act, which will initiate the process for obtaining a protection order, residence order, or other relief.\n3. Seek support from a lawyer or a non-governmental organization that specializes in domestic violence cases to guide you through the legal process.\n\n**Important:** Remember that domestic violence is not just physical abuse; it also includes emotional, verbal, and economic abuse. You have the right to seek protection and relief under the law.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	family	\N	groq/llama-3.3-70b-versatile	\N	en	5412
31	Someone stole my phone at the market yesterday. What offence is this and can I file an FIR?	2026-06-20 16:27:41.698819+00	**Direct Answer:** The theft of your phone at the market is an offence under the Indian Penal Code (IPC), and you can file a First Information Report (FIR) with the police. \n\n**Applicable Laws:**\n- Information Technology Act 2000 § 43: This section deals with unauthorized access to computer systems, but since your phone is a computer system, this section might be relevant in case of data theft or unauthorized access. | Punishment: None (civil liability) | Bailable\n\n**What You Should Do:**\n1. Immediately report the incident to the nearest police station and provide as much detail as possible about the incident, including the time, location, and description of the person who stole your phone.\n2. File a First Information Report (FIR) with the police, which will help initiate an investigation into the theft.\n3. Provide any relevant evidence, such as witness statements or CCTV footage, to support your complaint.\n\n**Important:** You should report the incident to the police as soon as possible, as delay in reporting can affect the investigation. You can also refer to legal judgments such as State vs Amir Qureshi, State vs Nijam Sheik, and State vs Nizam Khan, which demonstrate the process of filing an FIR for mobile phone theft.\n\n⚠️ This is legal information only, not legal advice. Consult a qualified advocate for your specific situation. Free legal aid: NALSA helpline 15100.	criminal	\N	groq/llama-3.3-70b-versatile	\N	en	\N
\.


--
-- Data for Name: sections; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.sections (id, act_id, section_number, section_title, bare_text, plain_language, is_bailable, is_cognizable, is_compoundable, punishment_summary, min_punishment, max_punishment, fine_amount, relevant_court, limitation_period, qdrant_id, embedding_model, is_active, is_amended, created_at) FROM stdin;
1	1	103	Definitions	In this Sanhita, unless the context otherwise requires, the following definitions apply...	This section defines key legal terms used throughout the BNS 2023 including concepts like 'act', 'voluntarily', 'person', and other fundamental legal definitions.	t	f	\N	\N	\N	\N	\N	\N	\N	1	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
15	2	300	Definition of murder	Except in the cases hereinafter excepted, culpable homicide by causing death with the intention of causing death, or with the knowledge that the act is so imminently dangerous that it must in all probability cause death, shall amount to the offence of murder.	Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death.	f	t	\N	Life imprisonment or death penalty	\N	\N	\N	\N	\N	15	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
16	2	301	Culpable homicide not amounting to murder	Whoever causes death by doing an act with the intention of causing death, or with knowledge that he is likely by such act to cause death, commits the offence of culpable homicide not amounting to murder, if the circumstances of the case do not amount to culpable homicide amounting to murder.	Causing death without the specific intention or knowledge required for murder, but with criminal negligence or recklessness.	f	t	\N	Imprisonment up to 10 years or fine up to ₹10,000	\N	\N	\N	\N	\N	16	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
36	7	2(1)(d)	Definition of Child under POCSO	'child' means any person below the age of eighteen years.	Under POCSO, anyone below 18 years is a child. ANY sexual act with a person under 18 is an offence under POCSO — regardless of consent. Age of consent under POCSO is 18. This overrides any claim of 'consensual relationship'.	\N	\N	\N	\N	\N	\N	\N	Special POCSO Court	\N	36	BAAI/bge-m3	t	f	2026-06-01 11:07:21.11573+00
14	2	116	Act of person bound by law	Whoever, being bound by law to take charge of any person in a state of unsoundness of mind, leaves that person in circumstances under which, if he were in a sound state of mind, he would be unable to save himself from death, is guilty of an offence.	A caregiver who abandons a mentally ill person in dangerous circumstances commits an offence.	f	t	\N	Imprisonment up to 6 months or fine up to ₹500	\N	\N	\N	\N	\N	14	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
2	1	104	General Exceptions	Nothing is an offence which is done by a person who, at the time of doing it, by reason of unsoundness of mind, is incapable of knowing the nature of the act, or that he is doing what is either wrong or contrary to law.	A person cannot be punished for an act done while suffering from mental illness if they couldn't understand their actions or their wrongfulness.	t	f	\N	\N	\N	\N	\N	\N	\N	2	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
3	1	105	Act of a person of unsound mind	No act is an offence by reason of any harm which it may cause to a person who, at the time when it is done, is incapable of knowing that the act is harm to him, or knowing it is so, has given his consent in circumstances which, though the circumstances invalidate the consent, in law do not make the act an offence by reason of the unsoundness of mind.	Acts done to persons mentally incapable of consenting are not offences if they cannot understand the harm.	t	f	\N	\N	\N	\N	\N	\N	\N	3	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
4	1	109	Act done by a person not knowing it is illegal	Nothing is an offence which is done by a person who, at the time of doing it, by reason of a mistake of fact and not by reason of a mistake of law in force in India, is incapable of knowing that the act is an offence, or that he is doing what is wrong or contrary to law.	If someone commits an act by honest mistake of fact (not law), they cannot be punished if they couldn't know it was wrong.	t	f	\N	\N	\N	\N	\N	\N	\N	4	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
5	1	115	Definitions of 'Voluntarily'	A person is said to cause an effect 'voluntarily' when he causes it by means whereby he intended to cause it, or by means which, at the time of employing them, he knew or had reason to believe to be likely to cause it.	An act is voluntary when a person intends to cause the effect or knows their actions are likely to cause it.	t	f	\N	\N	\N	\N	\N	\N	\N	5	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
6	1	116	Act of person bound by law	Whoever, being bound by law to take charge of any person in a state of unsoundness of mind, leaves that person in circumstances under which, if he were in a sound state of mind, he would be unable to save himself from death, is guilty of an offence.	A caregiver who abandons a mentally ill person in dangerous circumstances commits an offence.	f	t	\N	Imprisonment up to 6 months or fine up to ₹500	\N	\N	\N	\N	\N	6	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
7	1	300	Definition of murder	Except in the cases hereinafter excepted, culpable homicide by causing death with the intention of causing death, or with the knowledge that the act is so imminently dangerous that it must in all probability cause death, shall amount to the offence of murder.	Murder is when a person kills another with intent to kill or knowing the act will almost certainly cause death.	f	t	\N	Life imprisonment or death penalty	\N	\N	\N	\N	\N	7	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
8	1	301	Culpable homicide not amounting to murder	Whoever causes death by doing an act with the intention of causing death, or with knowledge that he is likely by such act to cause death, commits the offence of culpable homicide not amounting to murder, if the circumstances of the case do not amount to culpable homicide amounting to murder.	Causing death without the specific intention or knowledge required for murder, but with criminal negligence or recklessness.	f	t	\N	Imprisonment up to 10 years or fine up to ₹10,000	\N	\N	\N	\N	\N	8	BAAI/bge-m3	t	f	2026-05-30 08:36:10.745046+00
9	2	103	Definitions	In this Sanhita, unless the context otherwise requires, the following definitions apply...	This section defines key legal terms used throughout the BNS 2023 including concepts like 'act', 'voluntarily', 'person', and other fundamental legal definitions.	t	f	\N	\N	\N	\N	\N	\N	\N	9	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
10	2	104	General Exceptions	Nothing is an offence which is done by a person who, at the time of doing it, by reason of unsoundness of mind, is incapable of knowing the nature of the act, or that he is doing what is either wrong or contrary to law.	A person cannot be punished for an act done while suffering from mental illness if they couldn't understand their actions or their wrongfulness.	t	f	\N	\N	\N	\N	\N	\N	\N	10	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
11	2	105	Act of a person of unsound mind	No act is an offence by reason of any harm which it may cause to a person who, at the time when it is done, is incapable of knowing that the act is harm to him, or knowing it is so, has given his consent in circumstances which, though the circumstances invalidate the consent, in law do not make the act an offence by reason of the unsoundness of mind.	Acts done to persons mentally incapable of consenting are not offences if they cannot understand the harm.	t	f	\N	\N	\N	\N	\N	\N	\N	11	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
12	2	109	Act done by a person not knowing it is illegal	Nothing is an offence which is done by a person who, at the time of doing it, by reason of a mistake of fact and not by reason of a mistake of law in force in India, is incapable of knowing that the act is an offence, or that he is doing what is wrong or contrary to law.	If someone commits an act by honest mistake of fact (not law), they cannot be punished if they couldn't know it was wrong.	t	f	\N	\N	\N	\N	\N	\N	\N	12	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
13	2	115	Definitions of 'Voluntarily'	A person is said to cause an effect 'voluntarily' when he causes it by means whereby he intended to cause it, or by means which, at the time of employing them, he knew or had reason to believe to be likely to cause it.	An act is voluntary when a person intends to cause the effect or knows their actions are likely to cause it.	t	f	\N	\N	\N	\N	\N	\N	\N	13	BAAI/bge-m3	t	f	2026-06-01 09:56:39.581876+00
17	3	138	Dishonour of cheque for insufficiency of funds	Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provision of this Act, be punished with imprisonment for a term which may be extended to two years, or with fine which may extend to twice the amount of the cheque, or with both.	If you give someone a cheque and it bounces (returns unpaid) because you don't have enough money, you have committed a criminal offence. Punishment: up to 2 years jail OR fine up to double the cheque amount. This is the MOST COMMON financial crime case in Indian courts. The cheque must be for a legally owed debt — not a gift.	t	f	t	Up to 2 years imprisonment or fine up to 2x cheque amount	\N	2 years or fine up to twice cheque amount	\N	Magistrate Court (where cheque was presented)	30 days from bank notice; complaint within 1 month of that	17	BAAI/bge-m3	t	f	2026-06-01 11:07:21.016153+00
18	3	139	Presumption in favour of holder	It shall be presumed, unless the contrary is proved, that the holder of a cheque received the cheque of the nature referred to in section 138 for the discharge, in whole or in part, of any debt or other liability.	When a cheque bounces, the court automatically ASSUMES it was issued for a valid debt. The accused (who issued the cheque) must prove it was NOT for a debt. This makes cheque bounce cases easier to prove for the victim.	t	f	\N	\N	\N	\N	\N	Magistrate Court	\N	18	BAAI/bge-m3	t	f	2026-06-01 11:07:21.016153+00
19	3	141	Offences by companies	If the person committing an offence under section 138 is a company, every person who, at the time the offence was committed, was in charge of, and was responsible to the company for the conduct of the business of the company, as well as the company, shall be deemed to be guilty of the offence and shall be liable to be proceeded against and punished accordingly.	If a company's cheque bounces, BOTH the company AND the directors/managers who were running it at the time can be criminally prosecuted. This prevents companies from hiding behind corporate structure to escape cheque bounce liability.	t	f	\N	\N	\N	\N	\N	Magistrate Court	\N	19	BAAI/bge-m3	t	f	2026-06-01 11:07:21.016153+00
20	4	2(a)	Definition of Aggrieved Person	'aggrieved person' means any woman who is, or has been, in a domestic relationship with the respondent and who alleges to have been subjected to any act of domestic violence by the respondent.	Any woman who lives with or has lived with a man (as wife, live-in partner, sister, mother, daughter) and has been subjected to violence can use this law. You don't need to be married — live-in partners are also covered.	\N	\N	\N	\N	\N	\N	\N	Magistrate Court (Protection Officer)	\N	20	BAAI/bge-m3	t	f	2026-06-01 11:07:21.050362+00
21	4	3	Definition of domestic violence	For the purposes of this Act, any act, omission or commission or conduct of the respondent shall constitute domestic violence in case it— (a) harms or injures or endangers the health, safety, life, limb or well-being, whether mental or physical, of the aggrieved person or tends to do so and includes causing physical abuse, sexual abuse, verbal and emotional abuse and economic abuse; or (b) harasses, harms, injures or endangers the aggrieved person with a view to coerce her or any other person related to her to meet any unlawful demand for any dowry or other property or valuable security; or (c) has the effect of threatening the aggrieved person or any person related to her by any conduct mentioned in clause (a) or clause (b); or (d) otherwise injures or causes harm, whether physical or mental, to the aggrieved person.	Domestic violence is not just physical beating. It includes: (1) Physical abuse — hitting, slapping, pushing, (2) Sexual abuse — forced sex, (3) Verbal/emotional abuse — insults, threats, humiliation, isolating from family, (4) Economic abuse — not giving money for household expenses, taking away salary. ALL of these are legally domestic violence.	\N	\N	\N	\N	\N	\N	\N	Magistrate Court	\N	21	BAAI/bge-m3	t	f	2026-06-01 11:07:21.050362+00
22	4	12	Application to Magistrate	An aggrieved person or a Protection Officer or any other person on behalf of the aggrieved person may present an application to the Magistrate seeking one or more reliefs under this Act. The relief sought for under sub-section (1) may include a relief for issuance of an order for payment of compensation or damages without prejudice to the right of such person to institute a suit for compensation or damages for the injuries caused by the acts of domestic violence committed by the respondent.	You, a Protection Officer, or anyone on your behalf can file an application in the Magistrate Court. You can ask for: protection order, residence order, monetary relief, custody order, compensation. You can also file a criminal case separately under BNS Section 85.	\N	\N	\N	\N	\N	\N	\N	Judicial Magistrate First Class	No fixed limitation period — file as soon as possible	22	BAAI/bge-m3	t	f	2026-06-01 11:07:21.050362+00
23	4	17	Right to reside in shared household	Notwithstanding anything contained in any other law for the time being in force, every woman in a domestic relationship shall have the right to reside in the shared household, whether or not she has any right, title or beneficial interest in the same.	Even if the house is NOT in your name, you have the legal right to STAY in the shared household. Your husband or his family CANNOT throw you out of the house. Doing so is a violation of this Act. You can get a Residence Order from the Magistrate to prevent this.	\N	\N	\N	\N	\N	\N	\N	Magistrate Court	\N	23	BAAI/bge-m3	t	f	2026-06-01 11:07:21.050362+00
24	4	18	Protection orders	The Magistrate may, after giving the aggrieved person and the respondent an opportunity of being heard and on being prima facie satisfied that domestic violence has taken place or is likely to take place, pass a protection order in favour of the aggrieved person and prohibit the respondent from— (a) committing any act of domestic violence; (b) aiding or abetting in the commission of acts of domestic violence; (c) entering the place of employment of the aggrieved person or, if the person aggrieved is a child, its school or any other place frequented by the aggrieved person; (d) attempting to communicate in any form, whatsoever, with the aggrieved person, including personal, oral or written or electronic or telephonic contact; (e) alienating any assets, operating bank lockers or bank accounts used or held or enjoyed by both the parties, jointly or singly, by the respondent; or (f) causing violence to the dependants, other relatives or any person who give the assistance to the aggrieved person from domestic violence.	A Protection Order from the Magistrate can: (1) Stop the abuser from approaching you, (2) Ban them from your workplace, (3) Stop all contact — calls, messages, in-person, (4) Freeze joint bank accounts, (5) Protect your relatives who are helping you. Violation of a Protection Order is a CRIMINAL OFFENCE.	\N	\N	\N	\N	\N	\N	\N	Judicial Magistrate First Class	\N	24	BAAI/bge-m3	t	f	2026-06-01 11:07:21.050362+00
25	5	43	Penalty for damage to computer systems	If any person without permission of the owner or any other person who is in charge of a computer, computer system or computer network accesses or secures access to such computer, computer system or computer network; downloads, copies or extracts any data, computer data base or information from such computer, computer system or computer network including information or data held or stored in any removable storage medium; introduces or causes to be introduced any computer contaminant or computer virus into any computer, computer system or computer network; damages or causes to be damaged any computer, computer system or computer network, data, computer data base or any other programmes residing in such computer, computer system or computer network; disrupts or causes disruption of any computer, computer system or computer network — he shall be liable to pay damages by way of compensation to the person so affected.	If someone hacks your computer, copies your data without permission, installs a virus, or disrupts your computer system — they are civilly liable to pay you compensation. This covers unauthorized access, data theft, hacking, malware installation.	t	f	\N	\N	\N	\N	\N	Adjudicating Officer / Civil Court	\N	25	BAAI/bge-m3	t	f	2026-06-01 11:07:21.070441+00
26	5	66	Computer related offences	If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment for a term which may extend to three years or with fine which may extend to five lakh rupees or with both.	Hacking or unauthorized computer access done DISHONESTLY or FRAUDULENTLY is a CRIMINAL offence (not just civil). Punishment: up to 3 years jail or ₹5 lakh fine or both. This is the main cybercrime section used for hacking cases in India.	t	t	\N	Up to 3 years or ₹5 lakh or both	\N	3 years or ₹5 lakh fine	\N	Magistrate Court	\N	26	BAAI/bge-m3	t	f	2026-06-01 11:07:21.070441+00
27	5	66C	Identity theft	Whoever, fraudulently or dishonestly make use of the electronic signature, password or any other unique identification feature of any other person, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to rupees one lakh.	Using someone else's password, digital signature, Aadhaar, UPI ID, or any online identity without permission = identity theft. Punishment: up to 3 years + ₹1 lakh fine. Covers SIM swapping, account hacking, OTP fraud.	t	t	\N	Up to 3 years imprisonment + ₹1 lakh fine	\N	3 years + ₹1 lakh fine	\N	Magistrate Court	\N	27	BAAI/bge-m3	t	f	2026-06-01 11:07:21.070441+00
28	5	66D	Cheating by personation using computer resource	Whoever, by means of any communication device or computer resource cheats by personation, shall be punished with imprisonment of either description for a term which may extend to three years and shall also be liable to fine which may extend to one lakh rupees.	Creating a fake profile, pretending to be someone else online, catfishing, impersonating on social media to cheat someone. Common in online fraud, fake job offers, matrimonial fraud. Punishment: up to 3 years + ₹1 lakh fine.	t	t	\N	Up to 3 years + ₹1 lakh fine	\N	3 years + ₹1 lakh fine	\N	Magistrate Court	\N	28	BAAI/bge-m3	t	f	2026-06-01 11:07:21.070441+00
29	5	66E	Violation of privacy	Whoever, intentionally or knowingly captures, publishes or transmits the image of a private area of any person without his or her consent, under circumstances violating the privacy of that person, shall be punished with imprisonment which may extend to three years or with fine not exceeding two lakh rupees, or with both.	Taking or sharing intimate photos/videos of someone without consent — hidden cameras, upskirting, sharing private photos for revenge. Punishment: up to 3 years or ₹2 lakh fine. Use this + BNS Section 77 for revenge porn cases.	t	t	\N	Up to 3 years or ₹2 lakh fine or both	\N	3 years or ₹2 lakh fine	\N	Magistrate Court	\N	29	BAAI/bge-m3	t	f	2026-06-01 11:07:21.070441+00
30	5	67	Punishment for publishing obscene material in electronic form	Whoever publishes or transmits or causes to be published or transmitted in the electronic form, any material which is lascivious or appeals to the prurient interest or if its effect is such as to tend to deprave and corrupt persons who are likely, having regard to all relevant circumstances, to read, see or hear the matter contained or embodied in it, shall be punished on first conviction with imprisonment of either description for a term which may extend to three years and with fine which may extend to five lakh rupees.	Publishing or sharing obscene/pornographic content online. First offence: up to 3 years + ₹5 lakh fine. Second offence: up to 5 years + ₹10 lakh fine. Used in revenge porn cases, online harassment with obscene content.	t	t	\N	Up to 3 years + ₹5 lakh (1st), 5 years + ₹10 lakh (2nd)	\N	3 years (first offence), 5 years (repeat)	\N	Magistrate Court	\N	30	BAAI/bge-m3	t	f	2026-06-01 11:07:21.070441+00
31	6	3	Right of citizens to information	Subject to the provisions of this Act, all citizens shall have the right to information.	Every Indian citizen has the RIGHT to ask for information from any government office. This is a fundamental right under the RTI Act. You can ask for files, records, documents, data, memos, emails — anything the government holds.	\N	\N	\N	\N	\N	\N	\N	Central/State Information Commission	\N	31	BAAI/bge-m3	t	f	2026-06-01 11:07:21.095652+00
32	6	6	Request for obtaining information	A person, who desires to obtain any information under this Act, shall make a request in writing or through electronic means in English or Hindi or in the official language of the area in which the application is being made, to— (a) the Central Public Information Officer or State Public Information Officer, as the case may be, of the concerned public authority.	How to file RTI: Write a simple letter/application to the Public Information Officer (PIO) of the concerned government department. You can write in Hindi, English, or your state's official language. Pay ₹10 fee (BPL applicants: free). Online: rtionline.gov.in for central government.	\N	\N	\N	\N	\N	\N	\N	Central/State Information Commission	Reply within 30 days; 48 hours for life/liberty matters	32	BAAI/bge-m3	t	f	2026-06-01 11:07:21.095652+00
33	6	7	Disposal of request	Subject to the proviso to sub-section (2) of section 5 or the proviso to sub-section (3) of section 6, the Central Public Information Officer or State Public Information Officer, as the case may be, on receipt of a request under section 6 shall, as expeditiously as possible, and in any case within thirty days of the receipt of the request, either provide the information on payment of such fee as may be prescribed or reject the request for any of the reasons specified in sections 8 and 9.	The government MUST respond to your RTI within 30 days. If the information concerns someone's life or liberty, they must respond within 48 hours. If they don't respond or reject wrongly, you can file a First Appeal, then a Second Appeal to the Information Commission.	\N	\N	\N	\N	\N	\N	\N	First Appeal to senior officer; Second Appeal to Information Commission	30 days for response; 48 hours for life/liberty	33	BAAI/bge-m3	t	f	2026-06-01 11:07:21.095652+00
34	6	19	Appeal	Any person who, does not receive a decision within the time specified in sub-section (1) or clause (a) of sub-section (3) of section 7, or is aggrieved by a decision of the Central Public Information Officer or State Public Information Officer, as the case may be, may within thirty days from the expiry of such period or from the receipt of such a decision prefer an appeal to such officer who is senior in rank to the Central Public Information Officer or State Public Information Officer.	If the PIO doesn't reply in 30 days OR gives a wrong/incomplete answer: Step 1 — First Appeal to the senior officer in the same department (within 30 days). Step 2 — Second Appeal to Central/State Information Commission (within 90 days of First Appeal order). Information Commission can impose penalty of ₹250/day on the PIO for delay.	\N	\N	\N	\N	\N	\N	\N	Central Information Commission / State Information Commission	First appeal within 30 days; Second appeal within 90 days	34	BAAI/bge-m3	t	f	2026-06-01 11:07:21.095652+00
35	6	20	Penalties	Where the Central Information Commission or the State Information Commission, as the case may be, at the time of deciding any complaint or appeal is of the opinion that the Central Public Information Officer or the State Public Information Officer, as the case may be, has, without any reasonable cause, refused to receive an application for information or has not furnished information within the time specified under sub-section (1) of section 7 or maliciously denied the request for information or knowingly given incorrect, incomplete or misleading information or destroyed information which was the subject of the request or obstructed in any manner in furnishing the information, it shall impose a penalty of two hundred and fifty rupees each day till the application is received or information is furnished.	The Information Commission can penalize the PIO ₹250 per day for delay (maximum ₹25,000). The PIO can also face disciplinary action. If information was destroyed or deliberately hidden, that is a serious disciplinary offence. Use this to put pressure on non-responsive government officers.	\N	\N	\N	\N	\N	\N	\N	Central/State Information Commission	\N	35	BAAI/bge-m3	t	f	2026-06-01 11:07:21.095652+00
37	7	3	Penetrative sexual assault	A person is said to commit 'penetrative sexual assault' if— (a) he penetrates his penis, to any extent, into the vagina, mouth, urethra or anus of a child or makes the child to do so with him or any other person; or (b) he inserts, to any extent, any object or a part of the body, not being the penis, into the vagina, the urethra or anus of the child or makes the child to do so with him or any other person; or (c) he manipulates any part of the body of the child so as to cause penetration into the vagina, urethra, anus or any part of body of the child or makes the child to do so with him or any other person; or (d) he applies his mouth to the penis, vagina, anus, urethra of the child or makes the child to do so with him or any other person.	Penetrative sexual assault on a child = rape of a child. This is the most serious POCSO offence.	f	t	\N	\N	\N	\N	\N	Special POCSO Court	\N	37	BAAI/bge-m3	t	f	2026-06-01 11:07:21.11573+00
38	7	4	Punishment for penetrative sexual assault	Whoever commits penetrative sexual assault shall be punished with rigorous imprisonment for a term which shall not be less than ten years but which may extend to imprisonment for life, and shall also be liable to fine.	Minimum 10 years to life imprisonment for child rape. If the child is under 16, minimum is 20 years. If under 12, minimum is 20 years and can extend to death penalty.	f	t	f	Minimum 10-20 years to life imprisonment + fine	10 years (minimum), 20 years if child under 16	Imprisonment for Life / Death if child under 12	\N	Special POCSO Court	\N	38	BAAI/bge-m3	t	f	2026-06-01 11:07:21.11573+00
39	7	19	Reporting of offences	Notwithstanding anything contained in the Code of Criminal Procedure, 1973, any person (including the child) who has apprehension that an offence under this Act is likely to be committed or has knowledge that such an offence has been committed, shall provide such information to— (a) the Special Juvenile Police Unit; or (b) the local police.	ANYONE who knows or suspects a child is being sexually abused MUST report it to police or Childline (1098). Even teachers, doctors, neighbours. Failure to report is itself an offence under Section 21. You do not need to wait for the child or parents to complain.	\N	\N	\N	\N	\N	\N	\N	Special POCSO Court	\N	39	BAAI/bge-m3	t	f	2026-06-01 11:07:21.11573+00
40	7	29	Presumption of guilt in certain cases	Where a person is prosecuted for committing or abetting or attempting to commit any offence under sections 3, 5, 7 and 9 of this Act, the Special Court shall presume, that such person has committed or abetted or attempted to commit the offence, as the case may be unless the contrary is proved.	In POCSO cases, the accused is PRESUMED GUILTY until proven innocent (reverse of normal criminal law). The burden of proof shifts to the accused to prove they did NOT commit the offence. This makes POCSO prosecutions much stronger for child victims.	f	t	\N	\N	\N	\N	\N	Special POCSO Court	\N	40	BAAI/bge-m3	t	f	2026-06-01 11:07:21.11573+00
41	8	5	Conditions for a Hindu marriage	A marriage may be solemnized between any two Hindus, if the following conditions are fulfilled, namely— (i) neither party has a spouse living at the time of the marriage; (ii) at the time of the marriage, neither party— (a) is incapable of giving a valid consent to it in consequence of unsoundness of mind; or (b) though capable of giving a valid consent, has been suffering from mental disorder of such a kind or to such an extent as to be unfit for marriage and the procreation of children; or (iii) the bridegroom has completed the age of twenty-one years and the bride, the age of eighteen years at the time of the marriage.	For a valid Hindu marriage: (1) Neither person should be already married (no bigamy), (2) Both must be mentally capable of consenting, (3) Groom must be at least 21 years old, Bride at least 18 years old. Marriage violating these is void or voidable.	\N	\N	\N	\N	\N	\N	\N	Family Court	\N	41	BAAI/bge-m3	t	f	2026-06-01 11:07:21.131846+00
42	8	13	Divorce	Any marriage solemnized, whether before or after the commencement of this Act, may, on a petition presented by either the husband or the wife, be dissolved by a decree of divorce on the ground that the other party— (i) has, after the solemnization of the marriage, had voluntary sexual intercourse with any person other than his or her spouse; or (ii) has, after the solemnization of the marriage, treated the petitioner with cruelty; or (iii) has deserted the petitioner for a continuous period of not less than two years immediately preceding the presentation of the petition; or (iv) has ceased to be a Hindu by conversion to another religion; or (v) has been incurably of unsound mind, or has been suffering continuously or intermittently from mental disorder; or (vi) has been suffering from a virulent and incurable form of leprosy; or (vii) has been suffering from venereal disease in a communicable form; or (viii) has renounced the world by entering any religious order; or (ix) has not been heard of as being alive for a period of seven years or more.	Grounds for divorce in Hindu marriage: (1) Adultery, (2) Cruelty (physical or mental), (3) Desertion for 2+ years, (4) Conversion to another religion, (5) Unsound mind, (6) Incurable disease, (7) Missing for 7+ years. Either husband or wife can file for divorce on these grounds.	\N	\N	\N	\N	\N	\N	\N	Family Court / District Court	1 year after marriage before filing (except cruelty/desertion)	42	BAAI/bge-m3	t	f	2026-06-01 11:07:21.131846+00
43	8	13B	Divorce by mutual consent	Subject to the provisions of this Act a petition for dissolution of marriage by a decree of divorce may be presented to the district court by both the parties to a marriage together, whether such marriage was solemnized before or after the commencement of the Marriage Laws (Amendment) Act, 1976, on the ground that they have been living separately for a period of one year or more, that they have not been able to live together and that they have mutually agreed that the marriage should be dissolved.	Mutual consent divorce: Both husband and wife agree to divorce. Requirements: (1) Living separately for at least 1 year, (2) File joint petition, (3) Wait 6 months (cooling-off period — can be waived by Supreme Court ruling), (4) Confirm consent again. This is the fastest, least conflict way to divorce in India.	\N	\N	\N	\N	\N	\N	\N	Family Court / District Court	Minimum 1 year separation required	43	BAAI/bge-m3	t	f	2026-06-01 11:07:21.131846+00
44	8	24	Maintenance pendente lite	Where in any proceeding under this Act it appears to the court that either the wife or the husband, as the case may be, has no independent income sufficient for her or his support and the necessary expenses of the proceeding, it may, on the application of the wife or the husband, order the respondent to pay to the petitioner the expenses of the proceeding, and monthly during the proceeding such sum as, having regard to the petitioner's own income and the income of the respondent, it may seem to the court to be reasonable.	During divorce proceedings, if one spouse has no income, they can ask the court for maintenance (monthly money) to support themselves while the case is going on. The court looks at both spouses' income and decides a fair amount. Can be claimed by either wife OR husband.	\N	\N	\N	\N	\N	\N	\N	Family Court	\N	44	BAAI/bge-m3	t	f	2026-06-01 11:07:21.131846+00
45	9	3(1)	Offences of atrocities	Whoever, not being a member of a Scheduled Caste or a Scheduled Tribe— (i) forces a member of a Scheduled Caste or a Scheduled Tribe to drink or eat any inedible or obnoxious substance; (ii) acts with intent to cause injury, insult or annoyance to any member of a Scheduled Caste or a Scheduled Tribe by dumping excreta, waste matter, carcasses or any other obnoxious substance in his premises or neighbourhood; (iii) forcibly removes clothes from the person of a member of a Scheduled Caste or a Scheduled Tribe or parades him naked or with painted face or body or commits any similar act which is derogatory to human dignity; (iv) wrongfully occupies or cultivates any land owned by, or allotted to, or notified by any competent authority to be allotted to, a member of a Scheduled Caste or a Scheduled Tribe or gets the land allotted to him transferred; (v) wrongfully dispossesses a member of a Scheduled Caste or a Scheduled Tribe from his land or premises or interferes with the enjoyment of his rights over any land, premises or water.	Non-SC/ST persons committing atrocities against SC/ST persons: forced to eat/drink offensive substances, humiliating acts, forced nakedness, taking their land, bonded labour, social/economic boycott. All are criminal offences with minimum 6 months to 5 years imprisonment.	f	t	f	Minimum 6 months to 5 years + fine	6 months imprisonment	5 years imprisonment + fine	\N	Special Court (Sessions Court designated for SC/ST cases)	\N	45	BAAI/bge-m3	t	f	2026-06-01 11:07:21.145971+00
46	9	3(2)	Enhanced punishment for offences using SC/ST identity	Whoever, not being a member of a Scheduled Caste or a Scheduled Tribe, commits any offence under the Indian Penal Code punishable with imprisonment for a term of ten years or more against a person or property on the ground that such person is a member of a Scheduled Caste or a Scheduled Tribe or such property belongs to such member, shall be punishable with imprisonment for life and with fine.	If someone commits a serious crime (murder, rape, etc.) specifically BECAUSE the victim is SC/ST, punishment is increased to LIFE IMPRISONMENT. The caste-based targeting makes it an aggravated offence. This applies on top of the original BNS offence.	f	t	f	Life imprisonment + fine (for targeting based on SC/ST identity)	\N	Life imprisonment + fine	\N	Special SC/ST Court	\N	46	BAAI/bge-m3	t	f	2026-06-01 11:07:21.145971+00
47	9	14A	Appeal to High Court	Notwithstanding anything contained in the Code of Criminal Procedure, 1973, an appeal against a judgment, sentence or order of a Special Court shall lie to the High Court. The High Court may exercise all the powers of appeal, confirmation and revision as it is entitled to exercise in respect of judgments, sentences and orders passed by a Sessions Court.	Appeals in SC/ST atrocity cases go directly to the HIGH COURT — not the Sessions Court. This gives faster, higher-level judicial oversight for these cases. Bail conditions in SC/ST Act cases are strict — courts generally don't grant anticipatory bail easily.	f	t	\N	\N	\N	\N	\N	High Court (for appeals from Special Court)	\N	47	BAAI/bge-m3	t	f	2026-06-01 11:07:21.145971+00
48	10	2(n)	Definition of sexual harassment	'sexual harassment' includes any one or more of the following unwelcome acts or behaviour (whether directly or by implication) namely:— (i) physical contact and advances; (ii) a demand or request for sexual favours; (iii) making sexually coloured remarks; (iv) showing pornography; (v) any other unwelcome physical, verbal or non-verbal conduct of sexual nature.	Sexual harassment at work includes: (1) Unwanted physical touch, (2) Asking for sexual favours, (3) Sexual jokes/comments, (4) Showing pornography, (5) Any other sexual behaviour that is unwelcome. Even one incident is enough — it does not need to be repeated. Applies to all workplaces including homes (domestic workers covered).	\N	\N	\N	\N	\N	\N	\N	Internal Complaints Committee (ICC) / Local Complaints Committee	\N	48	BAAI/bge-m3	t	f	2026-06-01 11:07:21.157255+00
49	10	4	Constitution of Internal Complaints Committee	Every employer of a workplace shall, by an order in writing, constitute a Committee to be known as the 'Internal Complaints Committee'. The Internal Complaints Committee shall consist of— (a) a Presiding Officer who shall be a woman employed at a senior level at workplace from amongst the employees; (b) not less than two Members from amongst employees preferably committed to the cause of women or who have had experience in social work or have legal knowledge; (c) one member from amongst non-governmental organisations or associations committed to the cause of women or a person familiar with the issues relating to sexual harassment.	Every company/organisation with 10+ employees MUST have an Internal Complaints Committee (ICC). The ICC must be chaired by a senior woman employee. If your company does NOT have an ICC, that itself is a violation — the employer can be fined ₹50,000.	\N	\N	\N	\N	\N	\N	\N	Internal Complaints Committee	\N	49	BAAI/bge-m3	t	f	2026-06-01 11:07:21.157255+00
50	10	9	Complaint of sexual harassment	Any aggrieved woman may make, in writing, a complaint of sexual harassment at workplace to the Internal Committee, if so constituted, or the Local Committee, in case it is not so constituted, within a period of three months from the date of incident and in case of a series of incidents, within a period of three months from the date of last incident.	File a written complaint to the ICC within 3 months of the incident. If you cannot write, the ICC must help you put it in writing. If you missed the 3-month limit, you can ask for extension with a valid reason. Keep copies of all evidence: messages, emails, witness names.	\N	\N	\N	\N	\N	\N	\N	Internal Complaints Committee / Local Complaints Committee	3 months from incident (extendable for good reason)	50	BAAI/bge-m3	t	f	2026-06-01 11:07:21.157255+00
51	10	11	Inquiry into complaint	Subject to the provisions of section 10, the Internal Committee or the Local Committee, as the case may be, shall, where the respondent is an employee, proceed to make inquiry into the complaint in accordance with the provisions of the service rules applicable to the respondent and where no such rules exist, in such manner as may be prescribed or in case of a domestic worker, the Local Committee shall, if prima facie case exists, forward the complaint to the police, within a period of seven days for registering the case under section 509 of the Indian Penal Code (now BNS Section 79) and any other relevant provisions of the said Code.	The ICC must complete its inquiry within 60 days. They must give the accused a chance to respond. The inquiry is confidential. After inquiry, if harassment is proved: the employer must take disciplinary action (warning, demotion, termination) AND can be ordered to pay compensation to the victim.	\N	\N	\N	\N	\N	\N	\N	ICC → if criminal, Police → Magistrate Court	ICC must complete inquiry within 60 days	51	BAAI/bge-m3	t	f	2026-06-01 11:07:21.157255+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: nyaya_user
--

COPY public.users (id, supabase_id, phone, email, is_lawyer, preferred_language, state, daily_query_count, daily_reset_at, is_active, created_at) FROM stdin;
\.


--
-- Name: acts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nyaya_user
--

SELECT pg_catalog.setval('public.acts_id_seq', 10, true);


--
-- Name: amendments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nyaya_user
--

SELECT pg_catalog.setval('public.amendments_id_seq', 1, false);


--
-- Name: lawyer_inquiries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nyaya_user
--

SELECT pg_catalog.setval('public.lawyer_inquiries_id_seq', 1, false);


--
-- Name: lawyers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nyaya_user
--

SELECT pg_catalog.setval('public.lawyers_id_seq', 1, false);


--
-- Name: query_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nyaya_user
--

SELECT pg_catalog.setval('public.query_logs_id_seq', 31, true);


--
-- Name: sections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nyaya_user
--

SELECT pg_catalog.setval('public.sections_id_seq', 51, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nyaya_user
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: acts acts_pkey; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT acts_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: amendments amendments_pkey; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.amendments
    ADD CONSTRAINT amendments_pkey PRIMARY KEY (id);


--
-- Name: lawyer_inquiries lawyer_inquiries_pkey; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.lawyer_inquiries
    ADD CONSTRAINT lawyer_inquiries_pkey PRIMARY KEY (id);


--
-- Name: lawyers lawyers_pkey; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.lawyers
    ADD CONSTRAINT lawyers_pkey PRIMARY KEY (id);


--
-- Name: query_logs query_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.query_logs
    ADD CONSTRAINT query_logs_pkey PRIMARY KEY (id);


--
-- Name: sections sections_pkey; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_pkey PRIMARY KEY (id);


--
-- Name: sections sections_qdrant_id_key; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_qdrant_id_key UNIQUE (qdrant_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_acts_short_title; Type: INDEX; Schema: public; Owner: nyaya_user
--

CREATE INDEX ix_acts_short_title ON public.acts USING btree (short_title);


--
-- Name: ix_sections_act_number; Type: INDEX; Schema: public; Owner: nyaya_user
--

CREATE INDEX ix_sections_act_number ON public.sections USING btree (act_id, section_number);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: nyaya_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_phone; Type: INDEX; Schema: public; Owner: nyaya_user
--

CREATE UNIQUE INDEX ix_users_phone ON public.users USING btree (phone);


--
-- Name: ix_users_supabase_id; Type: INDEX; Schema: public; Owner: nyaya_user
--

CREATE UNIQUE INDEX ix_users_supabase_id ON public.users USING btree (supabase_id);


--
-- Name: acts acts_replaces_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.acts
    ADD CONSTRAINT acts_replaces_act_id_fkey FOREIGN KEY (replaces_act_id) REFERENCES public.acts(id);


--
-- Name: amendments amendments_section_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.amendments
    ADD CONSTRAINT amendments_section_id_fkey FOREIGN KEY (section_id) REFERENCES public.sections(id);


--
-- Name: lawyer_inquiries lawyer_inquiries_lawyer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.lawyer_inquiries
    ADD CONSTRAINT lawyer_inquiries_lawyer_id_fkey FOREIGN KEY (lawyer_id) REFERENCES public.lawyers(id);


--
-- Name: sections sections_act_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nyaya_user
--

ALTER TABLE ONLY public.sections
    ADD CONSTRAINT sections_act_id_fkey FOREIGN KEY (act_id) REFERENCES public.acts(id);


--
-- PostgreSQL database dump complete
--

\unrestrict VCzWqReohJtDoosmh47V5oFP8y077EkckDFINOcnngjkC9fCLbDATqe8DcaEaGK

