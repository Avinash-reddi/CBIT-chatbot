"""
Synonym groups for college chatbot intent matching.

Each group maps related words to a canonical form.
When matching user input against patterns, synonyms are expanded
so "cost", "fees", "payment", "charge" all map to the same concept.
"""

# Each key is the canonical word; values are its synonyms.
# During matching, all synonyms in a group are treated as equivalent.
SYNONYM_GROUPS = {
    # Money / Fees
    "fees": [
        "fee", "fees", "cost", "costs", "charge", "charges",
        "price", "payment", "amount", "money", "tuition", "expense",
    ],

    # Admission
    "admission": [
        "admission", "admissions", "apply", "application", "enroll",
        "enrollment", "enrolment", "register", "registration", "join",
        "joining", "entry", "seat", "seats",
    ],

    # Exam
    "exam": [
        "exam", "exams", "examination", "examinations", "test", "tests",
        "paper", "papers",
    ],

    # Schedule / Dates
    "schedule": [
        "schedule", "timetable", "dates", "date", "calendar", "timeline",
        "when", "deadline", "timing", "timings",
    ],

    # Placement
    "placement": [
        "placement", "placements", "placed", "recruit", "recruitment",
        "recruiting", "hiring", "hired", "job", "jobs", "career",
        "employment", "employ",
    ],

    # Salary / Package
    "salary": [
        "salary", "package", "packages", "ctc", "compensation", "pay",
        "income", "earning", "earnings", "lpa", "stipend", "offer",
    ],

    # Company
    "company": [
        "company", "companies", "firm", "firms", "recruiter", "recruiters",
        "employer", "employers", "organization", "mnc", "startup",
    ],

    # Scholarship
    "scholarship": [
        "scholarship", "scholarships", "financial aid", "fee concession",
        "concession", "grant", "grants", "waiver", "free seat",
    ],

    # Course / Branch
    "course": [
        "course", "courses", "branch", "branches", "program", "programs",
        "programme", "programmes", "stream", "streams", "department",
        "departments", "subject", "subjects", "specialization",
    ],

    # Hostel
    "hostel": [
        "hostel", "hostels", "accommodation", "dorm", "dormitory",
        "room", "rooms", "stay", "boarding", "residence", "pg",
    ],

    # Library
    "library": [
        "library", "books", "book", "reading", "study room",
        "e-library", "digital library", "journal", "journals",
    ],

    # Sports
    "sports": [
        "sports", "sport", "games", "game", "play", "playing",
        "playground", "ground", "court", "gym", "fitness",
        "cricket", "football", "basketball", "volleyball", "badminton",
    ],

    # Transport
    "transport": [
        "transport", "transportation", "bus", "buses", "shuttle",
        "vehicle", "commute", "travel", "route", "routes",
    ],

    # Canteen / Food
    "canteen": [
        "canteen", "cafeteria", "food", "mess", "eat", "eating",
        "lunch", "breakfast", "snacks", "restaurant", "dining",
    ],

    # Internship
    "internship": [
        "internship", "internships", "intern", "interns", "training",
        "apprentice", "apprenticeship", "industrial training",
    ],

    # Attendance
    "attendance": [
        "attendance", "absent", "absent", "leave", "leaves",
        "present", "bunking", "shortage", "minimum attendance",
    ],

    # Marks / Grades
    "marks": [
        "marks", "mark", "grade", "grades", "score", "scores",
        "result", "results", "gpa", "cgpa", "percentage", "internal",
    ],

    # Eligibility
    "eligibility": [
        "eligibility", "eligible", "criteria", "qualification",
        "qualified", "minimum", "requirement", "requirements",
        "needed", "necessary",
    ],

    # Documents
    "documents": [
        "documents", "document", "certificate", "certificates",
        "papers", "paperwork", "proof", "id", "records",
    ],

    # College / Institute
    "college": [
        "college", "institute", "institution", "university",
        "campus", "cbit",
    ],

    # Facilities
    "facilities": [
        "facilities", "facility", "infrastructure", "amenities",
        "resources", "services",
    ],

    # WiFi / Internet
    "wifi": [
        "wifi", "wi-fi", "internet", "network", "connectivity",
        "broadband", "lan",
    ],

    # Lab
    "lab": [
        "lab", "labs", "laboratory", "laboratories", "practical",
        "practicals", "workshop",
    ],

    # Information
    "information": [
        "information", "info", "details", "detail", "about",
        "regarding", "tell", "explain", "describe",
    ],
}


def build_synonym_lookup():
    """
    Build a reverse lookup: word -> canonical form.
    E.g., "cost" -> "fees", "recruit" -> "placement"
    """
    lookup = {}
    for canonical, synonyms in SYNONYM_GROUPS.items():
        for syn in synonyms:
            lookup[syn.lower()] = canonical
    return lookup


# Pre-built lookup for fast access
SYNONYM_LOOKUP = build_synonym_lookup()


def expand_with_synonyms(tokens):
    """
    Given a list of tokens, return a set that includes both
    the original tokens and their canonical synonym forms.
    """
    expanded = set(tokens)
    for token in tokens:
        if token in SYNONYM_LOOKUP:
            canonical = SYNONYM_LOOKUP[token]
            expanded.add(canonical)
            # Also add all synonyms in that group for broader matching
            for syn in SYNONYM_GROUPS.get(canonical, []):
                expanded.add(syn)
    return expanded


def get_canonical(word):
    """Return the canonical form of a word, or the word itself."""
    return SYNONYM_LOOKUP.get(word.lower(), word.lower())
