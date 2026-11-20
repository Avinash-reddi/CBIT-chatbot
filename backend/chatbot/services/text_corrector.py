"""
Spell correction and informal language normalization for college chatbot.

Uses edit distance for fuzzy matching against a known vocabulary,
plus a slang/abbreviation dictionary for common student shorthand.
"""

import re


# ── Common abbreviations & slang students use ──────────────────

SLANG_MAP = {
    # Shortened words
    "wen": "when",
    "whn": "when",
    "whn": "when",
    "wer": "where",
    "whr": "where",
    "wat": "what",
    "wht": "what",
    "hw": "how",
    "hwo": "how",
    "howw": "how",
    "plz": "please",
    "pls": "please",
    "plzz": "please",
    "thnx": "thanks",
    "thx": "thanks",
    "thnks": "thanks",
    "ty": "thank you",
    "u": "you",
    "ur": "your",
    "r": "are",
    "m": "am",
    "im": "i am",
    "dont": "do not",
    "cant": "can not",
    "wont": "will not",
    "doesnt": "does not",
    "isnt": "is not",
    "arent": "are not",
    "whts": "what is",
    "hws": "how is",
    "giv": "give",
    "gve": "give",
    "abt": "about",
    "bout": "about",
    "info": "information",
    "yr": "year",
    "yrs": "years",
    "sem": "semester",
    "dept": "department",
    "dept.": "department",
    "btech": "b.tech",
    "mtech": "m.tech",
    "mba": "mba",
    "cse": "computer science",
    "ece": "electronics",
    "eee": "electrical",
    "mech": "mechanical",
    "civ": "civil",

    # College-specific slang
    "addmission": "admission",
    "admision": "admission",
    "addmision": "admission",
    "admisn": "admission",
    "admsn": "admission",
    "admssion": "admission",
    "plcment": "placement",
    "placemnt": "placement",
    "plcement": "placement",
    "schlrship": "scholarship",
    "scholrship": "scholarship",
    "scholarshp": "scholarship",
    "schlorship": "scholarship",
    "hostle": "hostel",
    "hostl": "hostel",
    "hostell": "hostel",
    "dorm": "hostel",
    "dormitory": "hostel",
    "attndance": "attendance",
    "attendnce": "attendance",
    "attendence": "attendance",
    "atendance": "attendance",
    "examm": "exam",
    "exm": "exam",
    "exams": "exam",
    "xam": "exam",
    "xams": "exam",
    "timetbl": "timetable",
    "timetabel": "timetable",
    "schedl": "schedule",
    "schdule": "schedule",
    "shedule": "schedule",
    "shcedule": "schedule",
    "feez": "fees",
    "fess": "fees",
    "feees": "fees",
    "fe": "fees",
    "colege": "college",
    "collage": "college",
    "colg": "college",
    "clg": "college",
    "clge": "college",
    "librarey": "library",
    "libary": "library",
    "librry": "library",
    "labratory": "laboratory",
    "labrotary": "laboratory",
    "cantin": "canteen",
    "caneten": "canteen",
    "transprt": "transport",
    "transort": "transport",
    "certficate": "certificate",
    "certifikat": "certificate",
    "documnt": "document",
    "documnts": "documents",
    "requred": "required",
    "requird": "required",
    "reqrd": "required",
    "eligiblity": "eligibility",
    "elegibility": "eligibility",
    "eligibilty": "eligibility",
    "internl": "internal",
    "intrnl": "internal",
    "semster": "semester",
    "semstr": "semester",
    "structur": "structure",
    "strucure": "structure",
    "struture": "structure",
    "processs": "process",
    "procss": "process",
    "availble": "available",
    "availabe": "available",
    "avlbl": "available",
    "facillity": "facility",
    "facilty": "facility",
    "faclity": "facility",
    "facilites": "facilities",
    "facilitees": "facilities",
    "paymet": "payment",
    "paymnt": "payment",
    "sallary": "salary",
    "salry": "salary",
    "packge": "package",
    "pkg": "package",
    "compny": "company",
    "companys": "companies",
    "recruter": "recruiter",
    "recuriter": "recruiter",
    "intrship": "internship",
    "internshp": "internship",
    "intenship": "internship",
    "wfi": "wifi",
    "wi-fi": "wifi",
    "sportss": "sports",
    "sprt": "sports",
}

# ── College-domain vocabulary (correct words) ─────────────────

VOCABULARY = {
    # Common English
    "when", "where", "what", "which", "who", "how", "why",
    "the", "is", "are", "was", "were", "will", "can", "could",
    "should", "would", "has", "have", "had", "does", "do", "did",
    "not", "and", "but", "for", "with", "from", "about", "into",
    "this", "that", "these", "those", "there", "here", "some",
    "any", "all", "each", "every", "much", "many", "more", "most",
    "give", "get", "tell", "know", "want", "need", "like",
    "please", "help", "thanks", "thank", "hello", "hi", "hey",
    "good", "morning", "afternoon", "evening", "bye", "goodbye",
    "yes", "no", "okay", "ok",

    # College domain words
    "admission", "admissions", "course", "courses", "branch", "branches",
    "department", "departments", "college", "university", "institute",
    "fees", "fee", "tuition", "cost", "payment", "scholarship",
    "scholarships", "financial", "aid", "concession",
    "exam", "exams", "examination", "examinations", "test", "tests",
    "schedule", "timetable", "calendar", "dates", "deadline",
    "semester", "year", "annual", "monthly",
    "placement", "placements", "campus", "recruitment", "recruiter",
    "recruiters", "company", "companies", "salary", "package",
    "internship", "internships", "training", "job", "career",
    "hostel", "accommodation", "room", "mess", "food",
    "library", "books", "digital", "resources",
    "sports", "games", "facilities", "facility", "infrastructure",
    "laboratory", "laboratories", "labs", "lab", "computer",
    "transport", "transportation", "bus", "canteen", "cafeteria",
    "wifi", "internet", "campus",
    "attendance", "marks", "internal", "external", "grade", "grades",
    "result", "results", "pass", "fail",
    "certificate", "certificates", "document", "documents", "required",
    "eligibility", "criteria", "minimum", "maximum",
    "apply", "application", "process", "procedure", "steps",
    "available", "offered", "details", "information", "structure",
    "lateral", "entry", "diploma",
    "average", "highest", "lowest",
    "boys", "girls", "students", "faculty", "professor",
    "engineering", "technology", "science", "management",
    "computer", "electronics", "electrical", "mechanical", "civil",
    "b.tech", "m.tech", "mba", "btech", "mtech",
}


def _edit_distance(word1, word2):
    """Compute Levenshtein edit distance between two words."""
    m, n = len(word1), len(word2)
    if abs(m - n) > 2:
        return max(m, n)

    prev = list(range(n + 1))
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev, curr = curr, prev

    return prev[n]


def _best_vocab_match(word, max_distance=2):
    """Find the closest vocabulary word within the allowed edit distance."""
    if word in VOCABULARY:
        return word

    best_word = None
    best_dist = max_distance + 1

    for vocab_word in VOCABULARY:
        if abs(len(word) - len(vocab_word)) > max_distance:
            continue
        dist = _edit_distance(word, vocab_word)
        if dist < best_dist:
            best_dist = dist
            best_word = vocab_word

    if best_dist <= max_distance:
        return best_word
    return None


def correct_text(text):
    """
    Correct spelling mistakes and normalize informal language.

    Steps:
    1. Normalize whitespace and lowercase
    2. Replace known slang/abbreviations
    3. Fuzzy-match remaining unknown words against vocabulary

    Returns the corrected text string.
    """
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)

    # Split into words, preserving order
    words = text.split()
    corrected = []

    for word in words:
        # Strip punctuation for matching, preserve for output
        clean = re.sub(r"[^\w]", "", word)

        if not clean:
            continue

        # Step 1: Check slang map (exact match)
        if clean in SLANG_MAP:
            corrected.append(SLANG_MAP[clean])
            continue

        # Step 2: Check if already a known word
        if clean in VOCABULARY:
            corrected.append(clean)
            continue

        # Step 3: Fuzzy match against vocabulary
        # Only attempt for words 3+ chars (short words are likely intentional)
        if len(clean) >= 3:
            match = _best_vocab_match(clean)
            if match:
                corrected.append(match)
                continue

        # Step 4: Keep the original word (might be a name, number, etc.)
        corrected.append(clean)

    return " ".join(corrected)


def normalize_input(text):
    """
    Full normalization pipeline:
    1. Correct spelling
    2. Expand abbreviations
    3. Return cleaned text ready for intent matching
    """
    corrected = correct_text(text)

    # Handle repeated characters (e.g., "helllo" -> "hello", "feees" -> "fees")
    corrected = re.sub(r"(.)\1{2,}", r"\1\1", corrected)

    # Re-check slang after dedup (e.g., "feees" -> "fees" after dedup might match)
    words = corrected.split()
    final = []
    for w in words:
        if w in SLANG_MAP:
            final.append(SLANG_MAP[w])
        else:
            final.append(w)

    return " ".join(final)
