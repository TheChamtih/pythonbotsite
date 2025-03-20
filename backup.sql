--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 16.5

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.admins (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    email character varying(120) NOT NULL,
    username character varying(120),
    first_name character varying(120),
    last_name character varying(120)
);


ALTER TABLE public.admins OWNER TO neondb_owner;

--
-- Name: admins_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.admins_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admins_id_seq OWNER TO neondb_owner;

--
-- Name: admins_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.admins_id_seq OWNED BY public.admins.id;


--
-- Name: course_reviews; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.course_reviews (
    id integer NOT NULL,
    course_id integer NOT NULL,
    user_id integer,
    rating double precision NOT NULL,
    comment text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    source character varying(20) DEFAULT 'website'::character varying,
    updated_at timestamp with time zone,
    CONSTRAINT rating_range_check CHECK (((rating >= (0.5)::double precision) AND (rating <= (5)::double precision)))
);


ALTER TABLE public.course_reviews OWNER TO neondb_owner;

--
-- Name: course_reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.course_reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_reviews_id_seq OWNER TO neondb_owner;

--
-- Name: course_reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.course_reviews_id_seq OWNED BY public.course_reviews.id;


--
-- Name: course_tags; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.course_tags (
    id integer NOT NULL,
    course_id integer,
    tag character varying(100)
);


ALTER TABLE public.course_tags OWNER TO neondb_owner;

--
-- Name: course_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.course_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.course_tags_id_seq OWNER TO neondb_owner;

--
-- Name: course_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.course_tags_id_seq OWNED BY public.course_tags.id;


--
-- Name: courses; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.courses (
    id integer NOT NULL,
    name text NOT NULL,
    description text,
    min_age integer NOT NULL,
    max_age integer NOT NULL,
    rating double precision DEFAULT 0.0,
    rating_count integer DEFAULT 0,
    duration character varying(50),
    schedule text,
    price character varying(50),
    skills text,
    requirements text
);


ALTER TABLE public.courses OWNER TO neondb_owner;

--
-- Name: courses_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.courses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.courses_id_seq OWNER TO neondb_owner;

--
-- Name: courses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.courses_id_seq OWNED BY public.courses.id;


--
-- Name: districts; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.districts (
    id integer NOT NULL,
    name text NOT NULL
);


ALTER TABLE public.districts OWNER TO neondb_owner;

--
-- Name: districts_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.districts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.districts_id_seq OWNER TO neondb_owner;

--
-- Name: districts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.districts_id_seq OWNED BY public.districts.id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    address text NOT NULL,
    district_id integer NOT NULL
);


ALTER TABLE public.locations OWNER TO neondb_owner;

--
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_id_seq OWNER TO neondb_owner;

--
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- Name: trial_lessons; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.trial_lessons (
    id integer NOT NULL,
    user_id integer NOT NULL,
    course_id integer NOT NULL,
    location_id integer NOT NULL,
    date timestamp without time zone NOT NULL,
    confirmed boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    telegram_id bigint
);


ALTER TABLE public.trial_lessons OWNER TO neondb_owner;

--
-- Name: trial_lessons_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.trial_lessons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trial_lessons_id_seq OWNER TO neondb_owner;

--
-- Name: trial_lessons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.trial_lessons_id_seq OWNED BY public.trial_lessons.id;


--
-- Name: user_activities; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.user_activities (
    id integer NOT NULL,
    user_id integer NOT NULL,
    activity_type character varying(50) NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    details json NOT NULL
);


ALTER TABLE public.user_activities OWNER TO neondb_owner;

--
-- Name: user_activities_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.user_activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_activities_id_seq OWNER TO neondb_owner;

--
-- Name: user_activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.user_activities_id_seq OWNED BY public.user_activities.id;


--
-- Name: user_session_stats; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.user_session_stats (
    id integer NOT NULL,
    user_id integer NOT NULL,
    session_start timestamp without time zone NOT NULL,
    session_end timestamp without time zone,
    platform character varying(50),
    device_info character varying(255)
);


ALTER TABLE public.user_session_stats OWNER TO neondb_owner;

--
-- Name: user_session_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.user_session_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_session_stats_id_seq OWNER TO neondb_owner;

--
-- Name: user_session_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.user_session_stats_id_seq OWNED BY public.user_session_stats.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    parent_name text,
    phone text,
    child_name text NOT NULL,
    child_age integer NOT NULL,
    child_interests text,
    username character varying(120),
    first_name character varying(120),
    last_name character varying(120)
);


ALTER TABLE public.users OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: admins id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admins ALTER COLUMN id SET DEFAULT nextval('public.admins_id_seq'::regclass);


--
-- Name: course_reviews id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course_reviews ALTER COLUMN id SET DEFAULT nextval('public.course_reviews_id_seq'::regclass);


--
-- Name: course_tags id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course_tags ALTER COLUMN id SET DEFAULT nextval('public.course_tags_id_seq'::regclass);


--
-- Name: courses id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.courses ALTER COLUMN id SET DEFAULT nextval('public.courses_id_seq'::regclass);


--
-- Name: districts id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.districts ALTER COLUMN id SET DEFAULT nextval('public.districts_id_seq'::regclass);


--
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- Name: trial_lessons id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.trial_lessons ALTER COLUMN id SET DEFAULT nextval('public.trial_lessons_id_seq'::regclass);


--
-- Name: user_activities id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_activities ALTER COLUMN id SET DEFAULT nextval('public.user_activities_id_seq'::regclass);


--
-- Name: user_session_stats id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_session_stats ALTER COLUMN id SET DEFAULT nextval('public.user_session_stats_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.admins (id, telegram_id, email, username, first_name, last_name) FROM stdin;
6	963048430	admin@example.com	markys196	\N	\N
\.


--
-- Data for Name: course_reviews; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.course_reviews (id, course_id, user_id, rating, comment, created_at, source, updated_at) FROM stdin;
68	9	27	1	kkkk	2025-02-26 08:35:31.981812	website	\N
69	10	27	5	\N	2025-02-26 08:38:18.227425	telegram	\N
\.


--
-- Data for Name: course_tags; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.course_tags (id, course_id, tag) FROM stdin;
1	1	программирование
2	1	код
3	1	логика
4	1	вычисления
5	1	начинающий
6	12	огэ
7	12	математика
8	12	экзамены
9	12	егэ
10	12	подготовка
11	12	экзамен
12	11	бизнес
13	11	стартапы
14	11	управление
15	11	маркетинг
16	11	финансы
17	11	идеи
18	8	фронтенд
19	8	html
20	8	css
21	8	javascript
22	8	веб-дизайн
23	8	пользовательский
24	8	интерфейс
25	5	программирование
26	5	drag-and-drop
27	5	интерфейсы
28	5	визуализация
29	5	кодинг
30	3	веб-разработка
31	3	html
32	3	css
33	3	javascript
34	3	design
35	3	сайт
36	2	компьютеры
37	2	офисные
38	2	программы
39	2	базовые
40	2	навыки
41	2	работа
42	2	с
43	2	файлами
44	2	интернет
45	4	creative
46	4	дизайн
47	4	art
48	4	photoshop
49	4	графика
50	6	python
51	6	coding
52	6	разработка
53	6	алгоритмы
54	6	программирование
55	7	контент
56	7	youtube
57	7	медиа
58	7	соцсети
59	7	блогинг
60	9	creative
61	9	дизайн
62	9	art
63	9	photoshop
64	9	графика
65	10	числа
66	10	логика
67	10	алгебра
68	10	математика
69	10	геометрия
\.


--
-- Data for Name: courses; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.courses (id, name, description, min_age, max_age, rating, rating_count, duration, schedule, price, skills, requirements) FROM stdin;
9	Геймдизайн	🎮 Создание игр и игровых миров. Развиваем воображение и технические навыки!	10	11	1	1	\N	\N	\N	\N	\N
10	Математика	🧮 Углубленное изучение математики для школьников. Подготовка к олимпиадам и экзаменам!	6	13	5	1	\N	\N	\N	\N	\N
7	Видеоблогинг	🎥 Как создавать и продвигать видеоконтент. Стань звездой YouTube!	9	11	0	0	\N	\N	\N	\N	\N
2	Компьютерная грамотность	💻 Освойте основы работы с компьютером. Навыки, которые пригодятся каждому!	7	9	0	0	\N	\N	\N	\N	\N
3	Создание веб-сайтов	🌐 Научим создавать современные веб-сайты с нуля. От HTML до CSS и JavaScript!	11	13	0	0	\N	\N	\N	\N	\N
5	Визуальное программирование	🖥️ Программирование через визуальные блоки. Идеально для детей!	9	10	0	0	\N	\N	\N	\N	\N
8	Фронтенд-разработка	🖥️ Курс по созданию интерфейсов для веб-сайтов. Освой HTML, CSS и JavaScript!	15	18	0	0	\N	\N	\N	\N	\N
11	Предпринимательство	💼 Основы бизнеса и предпринимательства для детей. Как превратить идею в успешный проект!	13	16	0	0	\N	\N	\N	\N	\N
6	Python	🐍 Изучение языка программирования Python. От основ до создания реальных проектов!	12	17	0	0	\N	\N	\N	\N	\N
1	Основы логики и программирования	🧠 Развиваем логическое мышление и изучаем основы программирования. Идеально для начинающих!	6	7	0	0	\N	\N	\N	\N	\N
12	Подготовка к ЕГЭ	📚 Подготовка к ЕГЭ по математике и информатике. Максимальные баллы гарантированы!	17	18	0	0	\N	\N	\N	\N	\N
4	Графический дизайн	🎨 Курс по созданию графики и дизайну. Развиваем креативность и художественный вкус!	9	14	5	1	\N	\N	\N	\N	\N
\.


--
-- Data for Name: districts; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.districts (id, name) FROM stdin;
1	Вогонка
2	ГГМ
4	Центр
3	Выя
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.locations (id, address, district_id) FROM stdin;
1	ул. Черных, д. 23	3
3	ул. Захарова, д. 10А	2
2	просп. Мира, д. 49 (этаж 3)	4
4	ул. Володарского, д. 1	1
\.


--
-- Data for Name: trial_lessons; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.trial_lessons (id, user_id, course_id, location_id, date, confirmed, created_at, telegram_id) FROM stdin;
25	27	10	3	2025-02-26 08:34:59.487669	t	2025-02-26 08:34:59.487669	\N
26	27	1	2	2025-02-26 08:43:20.451089	t	2025-02-26 08:43:20.451089	\N
27	27	6	3	2025-02-26 08:47:09.67699	t	2025-02-26 08:47:09.67699	\N
\.


--
-- Data for Name: user_activities; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.user_activities (id, user_id, activity_type, "timestamp", details) FROM stdin;
116	27	view_dashboard	2025-02-26 08:35:05.104401	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/user/dashboard", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
117	27	view_dashboard	2025-02-26 08:35:18.898123	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/user/dashboard", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
118	27	view_home	2025-02-26 08:35:21.371481	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
119	27	view_course	2025-02-26 08:35:27.653802	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
120	27	review_create	2025-02-26 08:35:31.981812	{"review_id": null, "course_id": 9, "rating": 1.0, "action": "create"}
121	27	view_course	2025-02-26 08:35:32.609261	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
122	27	view_home	2025-02-26 08:36:20.901402	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
123	27	view_dashboard	2025-02-26 08:36:35.304551	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/user/dashboard", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
124	27	view_dashboard	2025-02-26 08:37:46.388391	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/user/dashboard", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
125	27	view_home	2025-02-26 08:37:51.434544	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
126	27	view_home	2025-02-26 08:37:54.281869	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
127	27	view_home	2025-02-26 08:38:25.920756	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
128	27	view_course	2025-02-26 08:38:31.088006	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/10", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
129	27	view_home	2025-02-26 08:39:06.195127	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
130	27	view_home	2025-02-26 08:42:38.617164	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
131	27	view_home	2025-02-26 08:46:11.501175	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
132	27	review_create	2025-02-26 08:47:26.804837	{"review_id": 71, "course_id": 6, "rating": 5.0, "action": "create", "platform": "telegram"}
133	27	view_home	2025-02-26 08:47:42.192552	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
134	27	view_course	2025-02-26 08:47:50.709192	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
135	27	view_home	2025-02-26 08:48:29.327938	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
136	27	view_home	2025-02-26 08:53:45.409514	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
137	27	view_home	2025-02-26 08:54:58.010919	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
138	27	view_course	2025-02-26 08:55:04.109853	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
139	27	view_course	2025-02-26 08:55:11.382932	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
140	27	view_course	2025-02-26 08:55:25.889371	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
141	27	view_home	2025-02-26 08:56:24.944818	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
142	27	view_home	2025-02-26 08:58:12.794213	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
143	27	view_dashboard	2025-02-26 09:01:49.328292	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/user/dashboard", "method": "GET", "user_agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"}
144	27	view_home	2025-02-26 09:02:07.217585	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"}
145	27	view_course	2025-02-26 09:02:24.008476	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
146	27	view_home	2025-02-26 09:03:05.723464	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
147	27	view_course	2025-02-26 09:04:00.068206	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
148	27	view_dashboard	2025-02-26 09:05:08.315688	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/user/dashboard", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
149	27	view_dashboard	2025-02-26 09:05:16.304631	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/user/dashboard", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
150	27	view_home	2025-02-26 09:05:24.232199	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
151	27	view_home	2025-02-26 09:07:18.724833	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
152	27	view_course	2025-02-26 09:07:24.883804	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
153	27	view_course	2025-02-26 09:07:32.50294	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
154	27	view_course	2025-02-26 09:07:37.320495	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
155	27	view_home	2025-02-26 09:08:47.668123	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
156	27	view_course	2025-02-26 09:09:05.375951	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
157	27	view_home	2025-02-26 09:10:07.224916	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
158	27	view_course	2025-02-26 09:10:15.639707	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/10", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
159	27	view_course	2025-02-26 09:13:02.766572	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/6", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
160	27	view_home	2025-02-26 09:13:34.648663	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
161	27	view_home	2025-02-26 09:13:37.844611	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
162	27	view_course	2025-02-26 09:13:41.763292	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
163	27	view_home	2025-02-26 09:17:51.237	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
164	27	view_course	2025-02-26 09:17:54.229949	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
165	27	view_home	2025-02-26 09:19:00.876705	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
166	27	view_home	2025-02-26 09:19:08.348911	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
167	27	view_course	2025-02-26 09:19:25.376071	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
168	27	view_course	2025-02-26 09:19:47.991981	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
169	27	view_home	2025-02-26 09:19:51.332433	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
170	27	view_home	2025-02-26 09:22:38.753456	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
171	27	view_course	2025-02-26 09:23:06.666088	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
172	27	view_home	2025-02-26 09:24:36.150854	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
173	27	view_course	2025-02-26 09:24:40.424415	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
174	27	view_home	2025-02-26 09:25:40.213014	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
175	27	view_course	2025-02-26 09:25:41.560096	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
176	27	view_course	2025-02-26 09:26:13.110161	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
177	27	view_course	2025-02-26 09:29:43.721619	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
178	27	view_home	2025-02-26 09:29:52.503525	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
179	27	view_course	2025-02-26 09:31:18.175968	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
180	27	view_home	2025-02-26 09:31:18.496278	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
181	27	view_course	2025-02-26 09:31:30.213875	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
182	27	view_course	2025-02-26 09:31:34.891756	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
183	27	view_course	2025-02-26 09:32:04.896408	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
184	27	view_course	2025-02-26 09:32:21.894803	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
185	27	view_course	2025-02-26 09:34:11.523181	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
186	27	view_course	2025-02-26 09:34:14.661394	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
187	27	view_home	2025-02-26 09:34:20.98812	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
188	27	view_home	2025-02-26 09:34:26.259753	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
189	27	view_home	2025-02-26 09:36:23.037407	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
190	27	view_home	2025-02-26 09:37:04.450588	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
191	27	view_course	2025-02-26 09:37:18.931632	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/10", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
192	27	view_home	2025-02-26 09:37:23.060633	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
193	27	view_home	2025-02-26 09:38:57.017667	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
194	27	view_home	2025-02-26 09:39:40.664984	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
195	27	view_course	2025-02-26 09:39:49.639848	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
196	27	view_home	2025-02-26 09:39:53.444743	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
197	27	view_home	2025-02-26 09:40:43.814191	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
198	27	view_home	2025-02-26 09:44:24.92195	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
199	27	view_home	2025-02-26 09:45:14.648281	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
200	27	view_home	2025-02-26 09:46:47.700049	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
201	27	view_course	2025-02-26 09:46:54.470829	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/course/9", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
202	27	view_home	2025-02-26 09:50:42.386056	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
203	27	view_home	2025-02-26 09:54:35.128275	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
204	27	view_home	2025-02-26 09:56:17.82856	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
205	27	view_home	2025-02-26 09:58:43.331402	{"platform": "web", "url": "http://466d63ff-58c6-4aeb-a5fc-4af62b390c98-00-1sy4vgnln8q1p.picard.replit.dev/", "method": "GET", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36"}
\.


--
-- Data for Name: user_session_stats; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.user_session_stats (id, user_id, session_start, session_end, platform, device_info) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.users (id, telegram_id, parent_name, phone, child_name, child_age, child_interests, username, first_name, last_name) FROM stdin;
27	963048430	Дитя	89827176525	Марк	12	дизайн	markys196	ماركوس	\N
\.


--
-- Name: admins_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.admins_id_seq', 6, true);


--
-- Name: course_reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.course_reviews_id_seq', 71, true);


--
-- Name: course_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.course_tags_id_seq', 73, true);


--
-- Name: courses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.courses_id_seq', 14, true);


--
-- Name: districts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.districts_id_seq', 6, true);


--
-- Name: locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.locations_id_seq', 8, true);


--
-- Name: trial_lessons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.trial_lessons_id_seq', 27, true);


--
-- Name: user_activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.user_activities_id_seq', 205, true);


--
-- Name: user_session_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.user_session_stats_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.users_id_seq', 27, true);


--
-- Name: admins admins_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_email_key UNIQUE (email);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- Name: admins admins_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_telegram_id_key UNIQUE (telegram_id);


--
-- Name: course_reviews course_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_pkey PRIMARY KEY (id);


--
-- Name: course_tags course_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course_tags
    ADD CONSTRAINT course_tags_pkey PRIMARY KEY (id);


--
-- Name: courses courses_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (id);


--
-- Name: districts districts_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.districts
    ADD CONSTRAINT districts_pkey PRIMARY KEY (id);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: trial_lessons trial_lessons_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.trial_lessons
    ADD CONSTRAINT trial_lessons_pkey PRIMARY KEY (id);


--
-- Name: user_activities user_activities_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_pkey PRIMARY KEY (id);


--
-- Name: user_session_stats user_session_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_session_stats
    ADD CONSTRAINT user_session_stats_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: course_reviews course_reviews_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: course_reviews course_reviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course_reviews
    ADD CONSTRAINT course_reviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: course_tags course_tags_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.course_tags
    ADD CONSTRAINT course_tags_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id);


--
-- Name: locations locations_district_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_district_id_fkey FOREIGN KEY (district_id) REFERENCES public.districts(id);


--
-- Name: trial_lessons trial_lessons_course_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.trial_lessons
    ADD CONSTRAINT trial_lessons_course_id_fkey FOREIGN KEY (course_id) REFERENCES public.courses(id) ON DELETE CASCADE;


--
-- Name: trial_lessons trial_lessons_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.trial_lessons
    ADD CONSTRAINT trial_lessons_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.locations(id) ON DELETE CASCADE;


--
-- Name: trial_lessons trial_lessons_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.trial_lessons
    ADD CONSTRAINT trial_lessons_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_activities user_activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_session_stats user_session_stats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_session_stats
    ADD CONSTRAINT user_session_stats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

