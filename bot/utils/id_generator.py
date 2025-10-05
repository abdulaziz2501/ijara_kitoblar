def format_library_id(number):
    """Kutubxona ID formatini yaratish"""
    return f"ID{number:04d}"

def validate_phone_number(phone):
    """Telefon raqam validatsiyasi"""
    # +998 XX XXX XX XX formatini tekshirish
    import re
    pattern = r'^\+998\d{9}$'
    return bool(re.match(pattern, phone))