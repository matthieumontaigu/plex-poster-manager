# Mapping between country codes and TMDB language codes

LANGUAGE_CODES = {
    "fr": "fr",
    "us": "en",
    "gb": "en",
    "au": "en",
    "nz": "en",
    "ca": "fr",
    "be": "fr",
    "lu": "fr",
    "ch": "fr",
    "de": "de",
    "it": "it",
    "es": "es",
}

LOCALES = {
    "fr": "fr-FR",
}


def get_language_code(country: str) -> str:
    """Resolve a language code for a given country code."""
    if country not in LANGUAGE_CODES:
        raise ValueError(f"Unsupported country code: {country}")

    return LANGUAGE_CODES[country]


def get_locale_code(country: str) -> str:
    """Resolve a locale code for a given country code."""
    language = get_language_code(country)
    if language not in LOCALES:
        return language

    return LOCALES[language]
