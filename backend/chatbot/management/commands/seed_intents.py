from django.core.management.base import BaseCommand
from chatbot.models import Category, Intent, Pattern, Response


SEED_DATA = {
    "categories": [
        {"name": "General", "slug": "general", "icon": "FaInfoCircle", "color": "#6366F1", "description": "General greetings and bot info"},
        {"name": "Admissions & Courses", "slug": "admissions-courses", "icon": "FaGraduationCap", "color": "#3B82F6", "description": "Admission process and course information"},
        {"name": "Fees & Scholarships", "slug": "fees-scholarships", "icon": "FaMoneyBillWave", "color": "#10B981", "description": "Fee structure and scholarship details"},
        {"name": "Exams & Schedules", "slug": "exams-schedules", "icon": "FaCalendarAlt", "color": "#F59E0B", "description": "Examination and academic schedule info"},
        {"name": "Placements", "slug": "placements", "icon": "FaBriefcase", "color": "#8B5CF6", "description": "Placement statistics and career info"},
        {"name": "Campus & Facilities", "slug": "campus-facilities", "icon": "FaBuilding", "color": "#EF4444", "description": "Campus infrastructure and facilities"},
        {"name": "Events & Activities", "slug": "events-activities", "icon": "FaCalendarCheck", "color": "#E91E63", "description": "College events, fests, and cultural activities"},
        {"name": "Faculty & Departments", "slug": "faculty-departments", "icon": "FaUserTie", "color": "#607D8B", "description": "Faculty information and department details"},
    ],
    "intents": [
        # ── General ─────────────────────────────
        {
            "tag": "greeting",
            "category": "general",
            "priority": 10,
            "patterns": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"],
            "responses": [
                "Hello! Welcome to CBIT Assistant. I can help you with information about admissions, courses, fees, placements, and campus facilities. What would you like to know?",
                "Hi there! I'm the CBIT Smart Chatbot. How can I help you today? Feel free to ask about admissions, courses, fees, or anything about our college!",
            ],
        },
        {
            "tag": "goodbye",
            "category": "general",
            "priority": 10,
            "patterns": ["bye", "goodbye", "see you", "see you later", "take care"],
            "responses": [
                "Goodbye! Feel free to come back anytime you have questions. Have a great day!",
                "See you later! Don't hesitate to reach out if you need more information.",
            ],
        },
        {
            "tag": "thanks",
            "category": "general",
            "priority": 10,
            "patterns": ["thanks", "thank you", "that's helpful", "thanks a lot"],
            "responses": [
                "You're welcome! Is there anything else I can help you with?",
                "Happy to help! Let me know if you have more questions.",
            ],
        },
        {
            "tag": "bot_name",
            "category": "general",
            "priority": 5,
            "patterns": ["what is your name", "who are you", "what are you"],
            "responses": [
                "I'm the CBIT Smart Assistant, an AI-powered chatbot designed to help you find information about Chaitanya Bharathi Institute of Technology.",
            ],
        },
        {
            "tag": "college_info",
            "category": "general",
            "priority": 5,
            "patterns": ["tell me about cbit", "about the college", "college information", "what is cbit"],
            "responses": [
                "Chaitanya Bharathi Institute of Technology (CBIT) is located in Kadapa, Andhra Pradesh. It is affiliated to JNTUA, approved by AICTE, accredited by NAAC with 'A' Grade, and accredited by NBA. The college offers various undergraduate and postgraduate programs in engineering and technology.",
            ],
        },
        {
            "tag": "contact_info",
            "category": "general",
            "priority": 5,
            "patterns": ["contact number", "phone number", "how to contact", "email address", "contact details"],
            "responses": [
                "You can reach CBIT at:\nPhone: +91-8562-XXXXXX\nEmail: info@cbit.ac.in\nAddress: Chaitanya Bharathi Institute of Technology, Proddatur Road, Kadapa, Andhra Pradesh - 516003",
            ],
        },
        {
            "tag": "college_address",
            "category": "general",
            "priority": 5,
            "patterns": ["where is cbit", "college address", "location", "how to reach cbit"],
            "responses": [
                "CBIT is located at Proddatur Road, Kadapa, Andhra Pradesh - 516003. The college is well connected by road and the nearest railway station is Kadapa Junction.",
            ],
        },
        {
            "tag": "college_timings",
            "category": "general",
            "priority": 3,
            "patterns": ["college timings", "working hours", "what time does college start"],
            "responses": [
                "College timings are from 9:00 AM to 4:30 PM, Monday to Saturday. The administrative office is open from 9:00 AM to 5:00 PM.",
            ],
        },

        # ── Admissions & Courses ────────────────
        {
            "tag": "admission_process",
            "category": "admissions-courses",
            "priority": 8,
            "patterns": ["how to apply", "admission process", "how do i get admitted", "steps for admission", "application procedure"],
            "responses": [
                "The admission process at CBIT involves:\n1. Qualify in TS EAMCET / AP EAMCET\n2. Participate in the counseling process\n3. Document verification at the college\n4. Fee payment and seat confirmation\n\nYou can also apply for management quota seats directly through the college. Visit the admissions office for more details.",
                "To get admission at CBIT:\n- For B.Tech: Through EAMCET counseling or management quota\n- For M.Tech: Through GATE/PGECET counseling\n\nContact the admissions office at admissions@cbit.ac.in for detailed guidance.",
            ],
        },
        {
            "tag": "courses_offered",
            "category": "admissions-courses",
            "priority": 8,
            "patterns": ["what courses are available", "courses offered", "branches available", "departments", "list of courses", "what programs do you offer"],
            "responses": [
                "CBIT offers the following B.Tech programs:\n- Computer Science & Engineering (CSE)\n- Electronics & Communication Engineering (ECE)\n- Electrical & Electronics Engineering (EEE)\n- Mechanical Engineering (ME)\n- Civil Engineering (CE)\n- Information Technology (IT)\n\nPostgraduate programs:\n- M.Tech in various specializations\n- MBA",
            ],
        },
        {
            "tag": "eligibility_criteria",
            "category": "admissions-courses",
            "priority": 7,
            "patterns": ["eligibility criteria", "minimum marks required", "who can apply", "qualification needed", "eligibility for btech"],
            "responses": [
                "Eligibility for B.Tech admission:\n- Must have passed 10+2 (Intermediate) with Mathematics, Physics, and Chemistry\n- Minimum 45% aggregate marks (40% for reserved categories)\n- Valid EAMCET rank\n\nFor M.Tech:\n- B.Tech/B.E. degree with minimum 50% marks\n- Valid GATE/PGECET score",
            ],
        },
        {
            "tag": "btech_cse",
            "category": "admissions-courses",
            "priority": 6,
            "patterns": ["cse course", "computer science", "about cse department", "cse branch details", "computer science engineering"],
            "responses": [
                "The CSE Department at CBIT offers:\n- B.Tech in Computer Science & Engineering\n- Intake: 120 seats\n- Well-equipped labs with latest software\n- Focus areas: AI/ML, Data Science, Web Development, Cloud Computing\n- Experienced faculty with PhDs from reputed institutions",
            ],
        },
        {
            "tag": "admission_dates",
            "category": "admissions-courses",
            "priority": 7,
            "patterns": ["admission deadline", "when do admissions start", "last date to apply", "admission dates"],
            "responses": [
                "Admission dates depend on the EAMCET counseling schedule:\n- EAMCET counseling: Usually June-August\n- Management quota admissions: July-September\n- Late admissions (if seats available): September-October\n\nPlease check the official website or contact the admissions office for exact dates.",
            ],
        },
        {
            "tag": "documents_required",
            "category": "admissions-courses",
            "priority": 6,
            "patterns": ["documents required", "what documents needed", "documents for admission", "required certificates"],
            "responses": [
                "Documents required for admission:\n1. EAMCET Rank Card\n2. Intermediate Marks Memo\n3. SSC Marks Memo\n4. Transfer Certificate (TC)\n5. Migration Certificate\n6. Caste Certificate (if applicable)\n7. Income Certificate\n8. Aadhaar Card\n9. Passport-size photographs (6 copies)\n10. Allotment Order",
            ],
        },
        {
            "tag": "lateral_entry",
            "category": "admissions-courses",
            "priority": 5,
            "patterns": ["lateral entry", "direct second year", "diploma to btech", "ecet admission"],
            "responses": [
                "Lateral entry admission to 2nd year B.Tech is available through ECET (Engineering Common Entrance Test).\n- Eligible: Diploma holders and B.Sc. degree holders\n- Admission through ECET counseling\n- Available in most branches\n\nContact the admissions office for more details.",
            ],
        },

        # ── Fees & Scholarships ─────────────────
        {
            "tag": "fee_structure",
            "category": "fees-scholarships",
            "priority": 8,
            "patterns": ["fee structure", "how much is the fee", "tuition fee", "total fees", "fees for btech", "annual fee"],
            "responses": [
                "Approximate fee structure for B.Tech (per year):\n- Tuition Fee: Rs. 1,00,000 - 1,50,000\n- Development Fee: Rs. 15,000\n- Exam Fee: Rs. 5,000\n- Total: Approximately Rs. 1,20,000 - 1,70,000 per year\n\nNote: Fees may vary by category and year. Contact the fee counter for exact current figures.",
            ],
        },
        {
            "tag": "hostel_fees",
            "category": "fees-scholarships",
            "priority": 6,
            "patterns": ["hostel fee", "hostel charges", "accommodation cost", "hostel fee structure"],
            "responses": [
                "Hostel fee details (per year):\n- Room Rent: Rs. 30,000 - 50,000\n- Mess Charges: Rs. 40,000 - 50,000\n- Caution Deposit: Rs. 5,000 (refundable)\n\nBoth boys and girls hostels are available. Contact the hostel office for availability.",
            ],
        },
        {
            "tag": "scholarship_info",
            "category": "fees-scholarships",
            "priority": 7,
            "patterns": ["scholarships available", "how to get scholarship", "financial aid", "fee concession", "scholarship"],
            "responses": [
                "Scholarships available at CBIT:\n1. Government Scholarships (SC/ST/BC/EBC/Minority)\n2. Merit-based scholarships for toppers\n3. Jagananna Vidya Deevena (for AP students)\n4. Central Sector Scholarship\n5. College-level fee concessions for economically weaker students\n\nApply through the respective scholarship portals. Contact the scholarship cell for assistance.",
            ],
        },
        {
            "tag": "payment_methods",
            "category": "fees-scholarships",
            "priority": 5,
            "patterns": ["how to pay fees", "payment methods", "online fee payment", "fee payment mode"],
            "responses": [
                "Fee payment methods:\n1. Online payment through the college portal\n2. Demand Draft (DD) in favor of CBIT\n3. NEFT/RTGS bank transfer\n4. At the college fee counter\n\nVisit the college website for the online payment portal link.",
            ],
        },

        # ── Exams & Schedules ───────────────────
        {
            "tag": "exam_schedule",
            "category": "exams-schedules",
            "priority": 8,
            "patterns": ["exam schedule", "when are exams", "examination dates", "exam timetable", "upcoming exams"],
            "responses": [
                "Examination schedule:\n- Mid-term exams: Usually in October (odd semester) and March (even semester)\n- End semester exams: December-January (odd) and May-June (even)\n- Supplementary exams: August-September\n\nDetailed timetables are published on the college notice board and website 2 weeks before exams.",
            ],
        },
        {
            "tag": "academic_calendar",
            "category": "exams-schedules",
            "priority": 7,
            "patterns": ["academic calendar", "semester dates", "when does semester start", "academic year schedule"],
            "responses": [
                "Academic Calendar (Typical):\n- Odd Semester: July to December\n- Even Semester: January to June\n- Summer vacation: May-June\n- Dussehra break: October\n- Sankranti break: January\n\nThe detailed academic calendar is available on the college website and notice boards.",
            ],
        },
        {
            "tag": "internal_marks",
            "category": "exams-schedules",
            "priority": 5,
            "patterns": ["internal marks", "internal assessment", "how are internals calculated", "mid marks"],
            "responses": [
                "Internal assessment structure:\n- Mid-term exams: 25 marks (2 mid-terms, best of 2)\n- Assignments: 5 marks\n- Attendance: 5 marks (minimum 75% required)\n- Total internal marks: 35 out of 100\n- External (semester exam): 65 marks",
            ],
        },
        {
            "tag": "attendance_rules",
            "category": "exams-schedules",
            "priority": 6,
            "patterns": ["attendance requirement", "minimum attendance", "attendance rules", "how much attendance needed"],
            "responses": [
                "Attendance requirements:\n- Minimum 75% attendance is mandatory in each subject\n- Students with less than 65% may be detained\n- Condonation may be granted for 65-75% with a fee\n- Medical leave requires a medical certificate submitted within one week",
            ],
        },

        # ── Placements ──────────────────────────
        {
            "tag": "placement_stats",
            "category": "placements",
            "priority": 8,
            "patterns": ["placement statistics", "placement record", "how are placements", "placement percentage"],
            "responses": [
                "CBIT Placement Highlights:\n- Overall placement rate: 80-85%\n- CSE/IT placement rate: 90%+\n- 100+ companies visit campus annually\n- Students placed in top MNCs and startups\n\nThe Training & Placement Cell actively works to ensure maximum placements for students.",
            ],
        },
        {
            "tag": "top_recruiters",
            "category": "placements",
            "priority": 7,
            "patterns": ["top recruiters", "which companies visit", "recruiting companies", "companies that hire from cbit"],
            "responses": [
                "Top recruiting companies at CBIT include:\n- TCS, Infosys, Wipro, HCL\n- Accenture, Cognizant, Tech Mahindra\n- Amazon, Microsoft (for top performers)\n- Capgemini, Deloitte\n- And many more IT & core companies\n\nThe placement cell regularly updates the list on the college website.",
            ],
        },
        {
            "tag": "average_package",
            "category": "placements",
            "priority": 7,
            "patterns": ["average salary", "average package", "highest package", "salary offered", "ctc offered"],
            "responses": [
                "Salary packages at CBIT:\n- Highest Package: Rs. 12-15 LPA\n- Average Package: Rs. 4-6 LPA\n- Minimum Package: Rs. 2.5-3 LPA\n\nPackages vary by branch and year. CSE and IT typically get higher packages.",
            ],
        },
        {
            "tag": "placement_process",
            "category": "placements",
            "priority": 6,
            "patterns": ["placement process", "how does placement work", "campus recruitment process", "placement drive"],
            "responses": [
                "Campus placement process:\n1. Company pre-placement talk\n2. Online aptitude test\n3. Group discussion (some companies)\n4. Technical interview\n5. HR interview\n6. Offer letter\n\nThe Training & Placement Cell conducts regular aptitude training and mock interviews to prepare students.",
            ],
        },
        {
            "tag": "internships",
            "category": "placements",
            "priority": 6,
            "patterns": ["internship opportunities", "summer internship", "how to get internship", "internship"],
            "responses": [
                "Internship opportunities at CBIT:\n- Summer internships through the placement cell\n- Industry collaboration internships\n- AICTE-sponsored internships\n- Company-specific internship drives on campus\n\n3rd year students are encouraged to do summer internships. The placement cell assists in finding suitable opportunities.",
            ],
        },

        # ── Campus & Facilities ─────────────────
        {
            "tag": "campus_facilities",
            "category": "campus-facilities",
            "priority": 7,
            "patterns": ["campus facilities", "what facilities are available", "infrastructure", "college facilities"],
            "responses": [
                "CBIT Campus Facilities:\n- Smart classrooms with projectors\n- Well-equipped laboratories\n- Central library with digital resources\n- Boys and Girls hostels\n- Sports complex (cricket, basketball, volleyball, badminton)\n- Canteen and cafeteria\n- Wi-Fi enabled campus\n- Seminar halls and auditorium\n- Medical facility\n- Transportation service",
            ],
        },
        {
            "tag": "library",
            "category": "campus-facilities",
            "priority": 6,
            "patterns": ["library", "library facilities", "library timings", "digital library", "books available"],
            "responses": [
                "CBIT Library:\n- Over 50,000 books and reference materials\n- Digital library with e-journals and e-books\n- NPTEL video resources\n- Reading room open 8 AM to 8 PM\n- Separate section for competitive exam preparation\n- Book bank facility for economically weaker students",
            ],
        },
        {
            "tag": "hostel",
            "category": "campus-facilities",
            "priority": 6,
            "patterns": ["hostel facility", "hostel details", "accommodation", "boys hostel", "girls hostel"],
            "responses": [
                "CBIT Hostel Facilities:\n- Separate hostels for boys and girls\n- Furnished rooms (2-3 sharing)\n- 24/7 Wi-Fi connectivity\n- Mess with quality food (veg & non-veg)\n- Common room with TV\n- Laundry service\n- 24/7 security\n- Warden on campus\n\nContact the hostel office for availability and booking.",
            ],
        },
        {
            "tag": "sports",
            "category": "campus-facilities",
            "priority": 5,
            "patterns": ["sports facilities", "sports", "games", "playground", "sports events"],
            "responses": [
                "Sports facilities at CBIT:\n- Cricket ground\n- Basketball and volleyball courts\n- Badminton courts\n- Table tennis\n- Indoor games room\n- Annual sports day\n- Inter-college sports competitions\n\nThe Physical Education department encourages students to participate in sports activities.",
            ],
        },
        {
            "tag": "labs",
            "category": "campus-facilities",
            "priority": 6,
            "patterns": ["computer labs", "laboratories", "lab facilities", "lab equipment"],
            "responses": [
                "Laboratory facilities at CBIT:\n- Advanced computer labs with latest hardware\n- Department-specific labs (Electronics, Mechanical, Civil, etc.)\n- Research labs for faculty and PG students\n- Language lab\n- All labs equipped with necessary software and equipment\n- Regular maintenance and upgrades",
            ],
        },
        {
            "tag": "transportation",
            "category": "campus-facilities",
            "priority": 4,
            "patterns": ["transport facility", "college bus", "bus routes", "transportation"],
            "responses": [
                "CBIT Transportation:\n- College bus service available from various parts of the city\n- Multiple routes covering Kadapa and surrounding areas\n- Bus pass facility available\n- Contact the transport office for route details and fees",
            ],
        },
        {
            "tag": "canteen",
            "category": "campus-facilities",
            "priority": 4,
            "patterns": ["canteen", "food court", "cafeteria", "food facilities"],
            "responses": [
                "CBIT has a well-maintained canteen and cafeteria:\n- Serves breakfast, lunch, and snacks\n- Hygienic food at affordable prices\n- Both vegetarian and non-vegetarian options\n- Separate juice and snack counters\n- Open during college hours",
            ],
        },
        {
            "tag": "wifi",
            "category": "campus-facilities",
            "priority": 4,
            "patterns": ["wifi", "internet facility", "wi-fi", "internet access"],
            "responses": [
                "CBIT provides Wi-Fi facility across the campus:\n- High-speed internet connectivity\n- Available in classrooms, labs, library, and hostels\n- Students can connect using their college credentials\n- Leased line internet connection for uninterrupted access",
            ],
        },

        # ── Events & Activities ─────────────────
        {
            "tag": "college_fest",
            "category": "events-activities",
            "priority": 7,
            "patterns": ["college fest", "annual fest", "cultural fest", "technical fest", "fest details", "college events"],
            "responses": [
                "CBIT organizes several major events each year:\n- Annual Technical Fest (usually in February/March)\n- Cultural Fest with music, dance, and drama\n- Hackathons and coding competitions\n- Workshop series and guest lectures\n\nFollow the college website and notice boards for event dates and registration details.",
            ],
        },
        {
            "tag": "sankranti_event",
            "category": "events-activities",
            "priority": 6,
            "patterns": ["sankranti sambaralu", "sankranti celebration", "sankranti event", "pongal celebration"],
            "responses": [
                "CBIT celebrates Sankranti Sambaralu every January with:\n- Traditional rangoli competitions\n- Kite flying events\n- Cultural programs showcasing Telugu traditions\n- Special food stalls with traditional delicacies\n- Prizes for best performances\n\nIt's one of the most enjoyed cultural events on campus!",
            ],
        },
        {
            "tag": "sports_events",
            "category": "events-activities",
            "priority": 5,
            "patterns": ["sports day", "sports events", "annual sports", "inter college sports", "sports meet"],
            "responses": [
                "CBIT Sports Events:\n- Annual Sports Day (usually in December/January)\n- Inter-departmental tournaments throughout the year\n- Inter-college sports competitions\n- Events: Cricket, Football, Basketball, Volleyball, Athletics\n- Kabaddi, Badminton, Table Tennis tournaments\n\nContact the Physical Education department for participation details.",
            ],
        },
        {
            "tag": "workshops",
            "category": "events-activities",
            "priority": 5,
            "patterns": ["workshops", "seminars", "guest lectures", "technical workshops", "training programs"],
            "responses": [
                "CBIT regularly conducts:\n- Technical workshops on AI/ML, Web Development, Cloud Computing\n- Industry expert guest lectures\n- Soft skills and aptitude training\n- NPTEL awareness programs\n- Research methodology workshops\n\nDepartment notice boards and the college website list upcoming events.",
            ],
        },
        {
            "tag": "clubs_activities",
            "category": "events-activities",
            "priority": 5,
            "patterns": ["clubs", "student clubs", "extracurricular activities", "student activities", "coding club"],
            "responses": [
                "Student Clubs at CBIT:\n- Coding Club - programming contests and hackathons\n- Robotics Club - robotics projects and competitions\n- Literary Club - debates, quizzes, and creative writing\n- NSS (National Service Scheme) - community service\n- NCC (National Cadet Corps)\n- Photography Club\n- Music and Dance clubs\n\nJoin clubs during the orientation week or contact the student affairs office.",
            ],
        },

        # ── Faculty & Departments ──────────────
        {
            "tag": "faculty_info",
            "category": "faculty-departments",
            "priority": 7,
            "patterns": ["faculty details", "professors", "teachers", "who are the professors", "faculty list", "teaching staff"],
            "responses": [
                "CBIT has experienced faculty across all departments:\n- Most faculty members hold PhDs from reputed institutions\n- Faculty-student ratio: approximately 1:15\n- Regular faculty development programs\n- Active in research and publications\n\nFor specific department faculty details, visit the college website or contact the respective HOD.",
            ],
        },
        {
            "tag": "hod_info",
            "category": "faculty-departments",
            "priority": 6,
            "patterns": ["hod details", "head of department", "who is the hod", "department head", "hod contact"],
            "responses": [
                "Each department at CBIT has a Head of Department (HOD) who oversees:\n- Academic activities and curriculum\n- Faculty coordination\n- Student grievances and mentoring\n- Industry collaboration\n\nFor specific HOD contact details, please visit the college website or the respective department office.",
            ],
        },
        {
            "tag": "department_details",
            "category": "faculty-departments",
            "priority": 6,
            "patterns": ["department details", "department information", "about departments", "list departments", "department offices"],
            "responses": [
                "CBIT Departments:\n- Computer Science & Engineering (CSE)\n- Electronics & Communication Engineering (ECE)\n- Electrical & Electronics Engineering (EEE)\n- Mechanical Engineering (ME)\n- Civil Engineering (CE)\n- Information Technology (IT)\n- Basic Sciences & Humanities (BS&H)\n- MBA Department\n\nEach department has dedicated labs, faculty rooms, and HOD offices.",
            ],
        },
        {
            "tag": "exam_results",
            "category": "exams-schedules",
            "priority": 7,
            "patterns": ["exam results", "results", "when are results", "result date", "how to check results", "semester results"],
            "responses": [
                "Exam Results:\n- Results are typically published 3-4 weeks after end-semester exams\n- Check results on the JNTUA website (jntua.ac.in)\n- College notice boards also display results\n- Internal marks are available through the college portal\n- For revaluation, apply within 2 weeks of result announcement\n\nContact the Exam Cell for any result-related queries.",
            ],
        },
        {
            "tag": "principal_info",
            "category": "faculty-departments",
            "priority": 5,
            "patterns": ["principal", "who is the principal", "principal details", "principal office", "college principal"],
            "responses": [
                "The Principal of CBIT oversees all academic and administrative activities.\n- Office located in the main administrative building\n- Available during office hours (10 AM - 4 PM)\n- Appointments can be scheduled through the office\n\nFor urgent matters, contact the principal's office directly.",
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Seed the database with initial college chatbot data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Create categories
        categories = {}
        for cat_data in SEED_DATA["categories"]:
            cat, created = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults=cat_data,
            )
            categories[cat_data["slug"]] = cat
            status_msg = "Created" if created else "Exists"
            self.stdout.write(f"  {status_msg}: Category '{cat.name}'")

        # Create intents with patterns and responses
        for intent_data in SEED_DATA["intents"]:
            cat_slug = intent_data.pop("category")
            patterns = intent_data.pop("patterns")
            responses = intent_data.pop("responses")

            intent, created = Intent.objects.get_or_create(
                tag=intent_data["tag"],
                defaults={
                    "category": categories[cat_slug],
                    "priority": intent_data.get("priority", 0),
                    "description": intent_data.get("description", ""),
                },
            )

            if created:
                for p_text in patterns:
                    Pattern.objects.create(intent=intent, text=p_text)
                for r_text in responses:
                    Response.objects.create(intent=intent, text=r_text)
                self.stdout.write(f"  Created: Intent '{intent.tag}' with {len(patterns)} patterns, {len(responses)} responses")
            else:
                self.stdout.write(f"  Exists: Intent '{intent.tag}'")

            # Restore popped keys for safety
            intent_data["category"] = cat_slug
            intent_data["patterns"] = patterns
            intent_data["responses"] = responses

        self.stdout.write(self.style.SUCCESS("\nDatabase seeding complete!"))
        self.stdout.write(f"  Categories: {Category.objects.count()}")
        self.stdout.write(f"  Intents: {Intent.objects.count()}")
        self.stdout.write(f"  Patterns: {Pattern.objects.count()}")
        self.stdout.write(f"  Responses: {Response.objects.count()}")
