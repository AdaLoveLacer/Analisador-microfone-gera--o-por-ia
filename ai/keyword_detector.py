"""Keyword detection with fuzzy matching and variation support."""

import re
import logging
from typing import List, Dict, Tuple, Optional
from thefuzz import fuzz
from thefuzz import process as fuzzy_process

logger = logging.getLogger(__name__)


class KeywordDetector:
    """Detects keywords in text with fuzzy matching and variations."""

    def __init__(self, keywords: List[Dict], fuzzy_threshold: int = 80):
        """
        Initialize KeywordDetector.

        Args:
            keywords: List of keyword configurations
            fuzzy_threshold: Threshold for fuzzy matching (0-100)
        """
        self.keywords = keywords
        self.fuzzy_threshold = fuzzy_threshold
        self._build_index()

    def _build_index(self) -> None:
        """Build internal keyword index for faster matching."""
        self.keyword_map = {}
        for kw in self.keywords:
            if not kw.get("enabled", True):
                continue

            keyword_id = kw.get("id")
            self.keyword_map[keyword_id] = {
                "pattern": kw.get("pattern", "").lower(),
                "variations": [v.lower() for v in kw.get("variations", [])],
                "weight": kw.get("weight", 1.0),
                "name": kw.get("name"),
            }

    def detect(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect keywords in text.

        Args:
            text: Text to search for keywords
            variations: Include fuzzy matching

        Returns:
            Tuple of (keyword_id, confidence)
        """
        if not text or not isinstance(text, str):
            return None, 0.0

        text_lower = text.lower()
        best_match = None
        best_confidence = 0.0

        for keyword_id, kw_data in self.keyword_map.items():
            # Exact match
            pattern = kw_data["pattern"]
            if self._exact_match(text_lower, pattern):
                confidence = 1.0 * kw_data["weight"]
                if confidence > best_confidence:
                    best_match = keyword_id
                    best_confidence = confidence
                continue

            # Variations match
            variations = kw_data["variations"]
            for variation in variations:
                if self._exact_match(text_lower, variation):
                    confidence = 0.95 * kw_data["weight"]
                    if confidence > best_confidence:
                        best_match = keyword_id
                        best_confidence = confidence
                    continue

            # Fuzzy matching
            fuzzy_confidence = self._fuzzy_match(text_lower, pattern, variations)
            if fuzzy_confidence > 0:
                confidence = fuzzy_confidence * kw_data["weight"]
                if confidence > best_confidence:
                    best_match = keyword_id
                    best_confidence = confidence

        return best_match, best_confidence

    def detect_all(self, text: str) -> List[Tuple[str, float]]:
        """
        Detect all keywords in text.

        Args:
            text: Text to search for keywords

        Returns:
            List of tuples (keyword_id, confidence) sorted by confidence
        """
        if not text or not isinstance(text, str):
            return []

        text_lower = text.lower()
        matches = []

        for keyword_id, kw_data in self.keyword_map.items():
            # Exact match
            pattern = kw_data["pattern"]
            if self._exact_match(text_lower, pattern):
                confidence = 1.0 * kw_data["weight"]
                matches.append((keyword_id, confidence))
                continue

            # Variations match
            variations = kw_data["variations"]
            for variation in variations:
                if self._exact_match(text_lower, variation):
                    confidence = 0.95 * kw_data["weight"]
                    matches.append((keyword_id, confidence))
                    continue

            # Fuzzy matching
            fuzzy_confidence = self._fuzzy_match(text_lower, pattern, variations)
            if fuzzy_confidence > 0:
                confidence = fuzzy_confidence * kw_data["weight"]
                matches.append((keyword_id, confidence))

        # Sort by confidence descending
        return sorted(matches, key=lambda x: x[1], reverse=True)

    def _exact_match(self, text: str, pattern: str) -> bool:
        """
        Check for exact word match.

        Args:
            text: Text to search in
            pattern: Pattern to search for

        Returns:
            True if exact match found
        """
        # Word boundary match
        pattern_escaped = re.escape(pattern)
        regex = rf"\b{pattern_escaped}\b"
        return bool(re.search(regex, text))

    def _fuzzy_match(
        self, text: str, pattern: str, variations: List[str]
    ) -> float:
        """
        Fuzzy matching with confidence score.

        Args:
            text: Text to search in
            pattern: Main pattern
            variations: Variation patterns

        Returns:
            Confidence score (0-1)
        """
        all_patterns = [pattern] + variations
        best_score = 0

        for pat in all_patterns:
            # Ratio-based matching
            ratio = fuzz.partial_ratio(pat, text) / 100.0

            if ratio >= self.fuzzy_threshold / 100.0:
                best_score = max(best_score, ratio)

        # Normalize to 0-1 range and only return if above threshold
        if best_score >= self.fuzzy_threshold / 100.0:
            return best_score
        return 0.0

    def update_keywords(self, keywords: List[Dict]) -> None:
        """Update keyword list."""
        self.keywords = keywords
        self._build_index()

    def get_keyword_name(self, keyword_id: str) -> Optional[str]:
        """Get keyword name by ID."""
        if keyword_id in self.keyword_map:
            return self.keyword_map[keyword_id]["name"]
        return None
