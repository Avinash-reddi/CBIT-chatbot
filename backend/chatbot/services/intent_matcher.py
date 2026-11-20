"""
Enhanced intent matcher with spell correction, synonym expansion,
fuzzy token matching, and n-gram similarity.

Handles:
- Spelling mistakes ("wen is exam" -> "when is exam")
- Informal language ("wat r the feez" -> "what are the fees")
- Synonyms ("cost", "payment", "charge" all match "fees")
- Partial matches with confidence scoring
- Follow-up suggestions for low-confidence matches
"""

import re
from chatbot.models import Intent
from .text_corrector import normalize_input, _edit_distance
from .synonym_map import expand_with_synonyms, get_canonical, SYNONYM_LOOKUP


class TextPreprocessor:
    """Tokenize and normalize text for intent matching."""

    STOPWORDS = {
        "i", "me", "my", "we", "our", "you", "your", "he", "she", "it",
        "they", "them", "this", "that", "is", "am", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "can", "may", "might",
        "a", "an", "the", "and", "but", "or", "for", "of", "to", "in",
        "on", "at", "by", "with", "from", "up", "about", "into",
        "what", "which", "who", "whom", "where", "when", "why", "how",
        "not", "no", "nor", "so", "too", "very",
        "just", "if", "then", "than", "also", "more",
        "please", "tell", "know", "want", "need", "like",
    }

    STEM_RULES = [
        (r"ies$", "y"),
        (r"ves$", "f"),
        (r"ses$", "s"),
        (r"tion$", "t"),
        (r"sion$", "s"),
        (r"ment$", ""),
        (r"ness$", ""),
        (r"ence$", ""),
        (r"ance$", ""),
        (r"able$", ""),
        (r"ible$", ""),
        (r"ing$", ""),
        (r"ed$", ""),
        (r"ly$", ""),
        (r"er$", ""),
        (r"est$", ""),
        (r"s$", ""),
    ]

    @classmethod
    def preprocess(cls, text, remove_stopwords=True):
        """Tokenize, lowercase, optionally remove stopwords, and stem."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", " ", text)
        tokens = text.split()
        if remove_stopwords:
            tokens = [t for t in tokens if t not in cls.STOPWORDS and len(t) > 1]
        else:
            tokens = [t for t in tokens if len(t) > 1]
        return [cls._stem(t) for t in tokens]

    @classmethod
    def _stem(cls, word):
        for pattern, replacement in cls.STEM_RULES:
            if re.search(pattern, word) and len(word) > 4:
                return re.sub(pattern, replacement, word)
        return word


def _ngrams(tokens, n=2):
    """Generate character n-grams from a list of tokens."""
    text = " ".join(tokens)
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def _ngram_similarity(tokens_a, tokens_b, n=2):
    """Compute n-gram (character-level) similarity between two token lists."""
    grams_a = _ngrams(tokens_a, n)
    grams_b = _ngrams(tokens_b, n)
    if not grams_a or not grams_b:
        return 0.0
    intersection = grams_a & grams_b
    union = grams_a | grams_b
    return len(intersection) / len(union)


def _fuzzy_token_match(token, candidates, max_dist=1):
    """Check if token fuzzy-matches any candidate within edit distance."""
    for candidate in candidates:
        if abs(len(token) - len(candidate)) > max_dist:
            continue
        if _edit_distance(token, candidate) <= max_dist:
            return True
    return False


class IntentMatcher:
    """
    Enhanced intent matcher with multi-signal scoring:
    1. Spell-correct the user input first
    2. Expand tokens with synonyms
    3. Score using keyword overlap + fuzzy matching + n-gram similarity
    4. Return match with confidence, or suggest clarification

    Uses a class-level cache of intents that refreshes every 60 seconds
    to avoid re-querying the database on every message.
    """

    CONFIDENCE_THRESHOLD = 0.35
    LOW_CONFIDENCE_THRESHOLD = 0.20  # For "did you mean?" suggestions

    _intent_cache = None
    _cache_time = 0
    CACHE_TTL = 60  # seconds

    @classmethod
    def _get_intents(cls):
        """Return cached intents, refreshing if stale."""
        import time
        now = time.time()
        if cls._intent_cache is None or (now - cls._cache_time) > cls.CACHE_TTL:
            cls._intent_cache = list(
                Intent.objects.filter(is_active=True)
                .prefetch_related("patterns", "responses")
                .select_related("category")
            )
            cls._cache_time = now
        return cls._intent_cache

    @classmethod
    def clear_cache(cls):
        """Force cache refresh (call after intent CRUD operations)."""
        cls._intent_cache = None

    def match(self, user_input):
        """
        Match user input to the best intent.

        Returns dict with:
        - intent: matched Intent object or None
        - confidence: float score
        - corrected_input: spell-corrected version of input
        - is_clarification: True if confidence is low but we have candidates
        - suggestions: list of possible intent tags for follow-up
        """
        # Step 1: Normalize and spell-correct
        corrected = normalize_input(user_input)
        user_input_lower = corrected.lower().strip()

        # Step 2: Tokenize (both with and without stopword removal)
        user_tokens = TextPreprocessor.preprocess(corrected)
        user_tokens_full = TextPreprocessor.preprocess(corrected, remove_stopwords=False)

        # Step 3: Expand with synonyms
        user_expanded = expand_with_synonyms(user_tokens)
        # Also get canonical forms of user tokens
        user_canonical = {get_canonical(t) for t in user_tokens}

        # Handle empty input (greetings, single words)
        if not user_tokens:
            greeting_result = self._check_greeting(user_input.lower().strip())
            greeting_result["corrected_input"] = corrected
            greeting_result["is_clarification"] = False
            greeting_result["suggestions"] = []
            return greeting_result

        # Step 4: Score all active intents (cached)
        intents = self._get_intents()

        scored = []

        for intent in intents:
            intent_score = 0.0

            for pattern in intent.patterns.all():
                if pattern.is_regex:
                    try:
                        if re.search(pattern.text, user_input_lower, re.IGNORECASE):
                            return {
                                "intent": intent,
                                "confidence": 0.98,
                                "corrected_input": corrected,
                                "is_clarification": False,
                                "suggestions": [],
                            }
                    except re.error:
                        continue
                else:
                    score = self._compute_enhanced_score(
                        user_input_lower, user_tokens, user_expanded,
                        user_canonical, pattern.text
                    )
                    intent_score = max(intent_score, score)

            final_score = intent_score + (intent.priority * 0.001)
            scored.append((intent, final_score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        if not scored:
            return {
                "intent": None,
                "confidence": 0.0,
                "corrected_input": corrected,
                "is_clarification": False,
                "suggestions": [],
            }

        best_intent, best_score = scored[0]

        # High confidence match
        if best_score >= self.CONFIDENCE_THRESHOLD:
            return {
                "intent": best_intent,
                "confidence": round(best_score, 3),
                "corrected_input": corrected,
                "is_clarification": False,
                "suggestions": [],
            }

        # Low confidence - offer clarification if we have candidates
        if best_score >= self.LOW_CONFIDENCE_THRESHOLD:
            top_candidates = [
                intent.tag for intent, score in scored[:3]
                if score >= self.LOW_CONFIDENCE_THRESHOLD
            ]
            return {
                "intent": None,
                "confidence": round(best_score, 3),
                "corrected_input": corrected,
                "is_clarification": True,
                "suggestions": top_candidates,
            }

        # No match at all
        return {
            "intent": None,
            "confidence": round(best_score, 3),
            "corrected_input": corrected,
            "is_clarification": False,
            "suggestions": [],
        }

    def _compute_enhanced_score(self, user_input_lower, user_tokens,
                                 user_expanded, user_canonical, pattern_text):
        """
        Multi-signal scoring combining:
        1. Exact keyword overlap (base score)
        2. Synonym-expanded overlap
        3. Fuzzy token matching (edit distance)
        4. N-gram character similarity
        5. Substring matching bonuses
        """
        pattern_lower = pattern_text.lower().strip()
        pattern_tokens = TextPreprocessor.preprocess(pattern_text)

        if not pattern_tokens:
            return 0.0

        pattern_expanded = expand_with_synonyms(pattern_tokens)
        pattern_canonical = {get_canonical(t) for t in pattern_tokens}

        # ── Signal 1: Exact keyword overlap (weight: 0.30) ──
        exact_matched = set(user_tokens) & set(pattern_tokens)
        exact_score = len(exact_matched) / len(pattern_tokens) if pattern_tokens else 0

        # ── Signal 2: Synonym-expanded overlap (weight: 0.25) ──
        # Check if user's expanded set overlaps with pattern's expanded set
        canonical_overlap = user_canonical & pattern_canonical
        syn_score = len(canonical_overlap) / len(pattern_canonical) if pattern_canonical else 0

        # ── Signal 3: Fuzzy token matching (weight: 0.20) ──
        fuzzy_matches = 0
        for p_token in pattern_tokens:
            if p_token in user_tokens:
                fuzzy_matches += 1
            elif _fuzzy_token_match(p_token, user_tokens, max_dist=1):
                fuzzy_matches += 0.7  # Partial credit for fuzzy match
            elif _fuzzy_token_match(p_token, list(user_expanded), max_dist=1):
                fuzzy_matches += 0.5
        fuzzy_score = fuzzy_matches / len(pattern_tokens) if pattern_tokens else 0

        # ── Signal 4: N-gram similarity (weight: 0.15) ──
        ngram_score = _ngram_similarity(user_tokens, pattern_tokens)

        # ── Signal 5: Bonus signals (weight: 0.10) ──
        bonus = 0.0

        # Substring match bonus
        if pattern_lower in user_input_lower:
            bonus += 0.25

        # All pattern tokens present (exact or expanded)
        if set(pattern_tokens).issubset(user_expanded):
            bonus += 0.15

        # Consecutive token match
        if self._has_consecutive_match(pattern_tokens, user_tokens):
            bonus += 0.10

        # Combine weighted signals
        combined = (
            exact_score * 0.30 +
            syn_score * 0.25 +
            fuzzy_score * 0.20 +
            ngram_score * 0.15 +
            bonus * 0.10
        )

        # Normalize: if any single signal is very high, boost overall
        max_signal = max(exact_score, syn_score, fuzzy_score)
        if max_signal > 0.8:
            combined = max(combined, max_signal * 0.85)

        return min(combined, 1.0)

    def _has_consecutive_match(self, pattern_tokens, user_tokens):
        """Check if pattern tokens appear consecutively in user tokens."""
        if len(pattern_tokens) < 2:
            return False
        pat_str = " ".join(pattern_tokens)
        usr_str = " ".join(user_tokens)
        return pat_str in usr_str

    def _check_greeting(self, user_input_lower):
        """Handle greeting inputs that get stripped by stopword removal."""
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon",
            "good evening", "howdy", "greetings", "hii", "helo",
            "hllo", "helloo", "heyy", "heya", "yo", "sup",
        ]
        for g in greetings:
            if g in user_input_lower:
                try:
                    greeting_intent = Intent.objects.get(tag="greeting", is_active=True)
                    return {"intent": greeting_intent, "confidence": 0.95}
                except Intent.DoesNotExist:
                    pass
        return {"intent": None, "confidence": 0.0}
