import pycountry
from movieRatingSystem.logging_config import get_logger

logger = get_logger()

# Common language names that might differ from pycountry
LANGUAGE_OVERRIDES = {
    'cn': 'Chinese',
    'ze': 'Chinese',
    'zh': 'Chinese',
    'nb': 'Norwegian',
    'no': 'Norwegian',
    'xx': 'No Language',
    'none': 'No Language',
    '': 'Unknown'
}

def get_language_name(iso_code):
    """Convert ISO 639-1 language code to plain English name."""
    if not iso_code:
        return 'Unknown'
    
    # Check overrides first
    iso_code = iso_code.lower()
    if iso_code in LANGUAGE_OVERRIDES:
        return LANGUAGE_OVERRIDES[iso_code]
    
    try:
        # Try to find the language in pycountry
        language = pycountry.languages.get(alpha_2=iso_code)
        if language:
            return language.name
        
        # Try looking up by name (some codes might be full names)
        language = pycountry.languages.get(name=iso_code.title())
        if language:
            return language.name
        
        # If all lookups fail, capitalize the code
        return iso_code.upper()
    except (AttributeError, KeyError):
        # If lookup fails, return the original code in uppercase
        return iso_code.upper()

def create_language_options(iso_codes):
    """Create a list of language options with both code and name."""
    languages = []
    seen_names = set()
    
    for code in iso_codes:
        if not code:  # Skip empty codes
            continue
            
        name = get_language_name(code)
        if name not in seen_names:
            languages.append({
                'value': code,  # Keep original ISO code as value
                'label': f"{name} ({code})"  # Show both name and code in label
            })
            seen_names.add(name)
    
    # Sort by language name
    languages.sort(key=lambda x: x['label'])
    logger.info(f"Created {len(languages)} language options")
    return languages 