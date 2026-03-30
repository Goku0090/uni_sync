import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class CollegeManager:
    """Utility for college lookup and validation using RapidAPI and fallback data."""

    FALLBACK_UNIVERSITIES = [
        'Harvard University', 'Massachusetts Institute of Technology (MIT)',
        'Stanford University', 'California Institute of Technology (Caltech)',
        'Princeton University', 'University of Oxford', 'University of Cambridge',
        'Imperial College London', 'University of California, Berkeley',
        'University of California, Los Angeles', 'IIT Bombay', 'IIT Delhi',
        'IIT Madras', 'IIT Kanpur', 'IIT Kharagpur', 'NIT Trichy', 'NIT Warangal',
        'BITS Pilani', 'IIIT Hyderabad', 'Delhi University', 'JNU',
        'University of Toronto', 'ETH Zurich', 'Australian National University',
        'National University of Singapore', 'Tsinghua University', 'Peking University'
    ]

    RAPIDAPI_URL = 'https://universities-list.p.rapidapi.com/search'

    @classmethod
    def search_colleges(cls, query, max_results=12):
        query = (query or '').strip()

        # Base results from local fallback list
        matching = [c for c in cls.FALLBACK_UNIVERSITIES if query.lower() in c.lower()] if query else cls.FALLBACK_UNIVERSITIES.copy()

        if len(matching) >= max_results:
            return matching[:max_results]

        # Use RapidAPI on top of fallback
        if not settings.RAPIDAPI_KEY:
            return matching[:max_results]

        try:
            headers = {
                'X-RapidAPI-Key': settings.RAPIDAPI_KEY,
                'X-RapidAPI-Host': settings.RAPIDAPI_HOST,
            }
            params = {'name': query or 'university'}

            response = requests.get(cls.RAPIDAPI_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            remote_colleges = response.json() or []

            for item in remote_colleges:
                if isinstance(item, dict):
                    name = item.get('name') or item.get('university')
                else:
                    name = str(item)

                if not name:
                    continue

                normalized = name.strip()
                if normalized and normalized not in matching:
                    matching.append(normalized)

                if len(matching) >= max_results:
                    break

        except Exception as exc:
            logger.warning('RapidAPI college lookup failed: %s', exc)

        return matching[:max_results]

    @classmethod
    def validate_college(cls, college_name):
        if not college_name:
            return False

        normalized = college_name.strip().lower()
        if not normalized:
            return False

        if any(m.lower() == normalized for m in cls.FALLBACK_UNIVERSITIES):
            return True

        # Try an API search for exact match
        try:
            candidates = cls.search_colleges(college_name, max_results=20)
            return any(c.lower() == normalized for c in candidates)
        except Exception:
            return False
