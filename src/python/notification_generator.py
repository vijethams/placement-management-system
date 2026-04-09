"""
Notification Generator Module
Generates WhatsApp messages, voice scripts, and phone call scripts
for placement notifications in student's mother tongue
Uses Twilio for phone calls only - does NOT affect WhatsApp messages
"""

import os
import json
from translator import translate_message, get_language_code, LANGUAGE_MAP


# ==================== API Key Detection ====================

def check_twilio_available():
    """
    Check if Twilio calling API is available
    
    Returns:
        bool: True if Twilio credentials are configured, False otherwise
    """
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    
    if twilio_sid and twilio_token and twilio_phone:
        print(f"[CALLING] [OK] Twilio configured - phone calls enabled")
        return True
    else:
        if not twilio_sid:
            print("[CALLING] [NOT FOUND] TWILIO_ACCOUNT_SID not set")
        if not twilio_token:
            print("[CALLING] [NOT FOUND] TWILIO_AUTH_TOKEN not set")
        if not twilio_phone:
            print("[CALLING] [NOT FOUND] TWILIO_PHONE_NUMBER not set")
        print("[CALLING] [NOT FOUND] Twilio not configured - phone calls disabled")
        return False


def check_calling_api_available():
    """
    Check if any calling API is available (currently uses Twilio only)
    
    Returns:
        bool: True if calling API available, False otherwise
    """
    return check_twilio_available()


# ==================== Simple Call Scripts ====================

# Pre-built call scripts for phone calls (simpler, conversational)
CALL_SCRIPTS = {
    'en': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        " We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'kn': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'ta': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'hi': (
        "प्रिय अभिभावकों, यह कॉल के प्लेसमेंट सेल की ओर से "
        "स्वचालित रूप से जनरेट किया गया है। आपको यह बताते हुए हमें खुशी हो रही है कि आपके "
        "बच्चे {name} को {company} कंपनी में {package} लाख रुपये वार्षिक पैकेज के साथ चयन मिला है। "
        "इस शानदार उपलब्धि पर हमारी हार्दिक शुभकामनाएँ। धन्यवाद, आपका दिन शुभ हो।"
    ),
    
    'te': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),

    'ml': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'gu': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'mr': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'pa': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'bn': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
    
    'or': (
        "Dear parents, this is an auto-generated call from the placement cell, "
        "We are pleased to inform you that your ward "
        "{name} has successfully been placed in {company} with an annual package of "
        "{package} lakhs per annum. We heartily congratulate you on this wonderful "
        "achievement. Thank you, have a good day."
    ),
}


def create_simple_kannada_message(student_name, company_name, package):
    """
    Create simple, clear Kannada messages for notifications
    
    Args:
        student_name (str): Student's full name
        company_name (str): Company name
        package (str): Salary package (e.g., "25 LPA")
    
    Returns:
        dict: Contains whatsapp_message, voice_script, call_script
    """
    
    # Simple Kannada WhatsApp message (conversational tone)
    whatsapp_message = f"ನಮಸ್ಕಾರ! ನಿಮ್ಮ ಮಗುವಾದ {student_name} ಅವರು {company_name} ಕಂಪನಿಯಲ್ಲಿ ಕೆಲಸಕ್ಕೆ ಆಯ್ಕೆಯಾಗಿದ್ದಾರೆ. ಸಂಪ್ರದಾಯ: {package} LPA. ನಿಮ್ಮ ಸಂಪೂರ್ಣ ಕುಟುಂಬಕ್ಕೆ ಅಭಿನಂದನೆಗಳು! 🎉"
    
    # Voice script (slightly more formal, for TTS reading)
    voice_script = f"ನಮಸ್ಕಾರ. ನಿಮ್ಮ ಮಗುವಾದ {student_name} ಅವರು {company_name} ಕಂಪನಿಯಲ್ಲಿ {package} ಲಕ್ಷ ರೂಪಾಯಿಗಳ ಸಂಪ್ರದಾಯದೊಂದಿಗೆ ಉದ್ಯೋಗಕ್ಕೆ ಆಯ್ಕೆಯಾಗಿದ್ದಾರೆ. ನಿಮ್ಮ ಸಂಪೂರ್ಣ ಕುಟುಂಬಕ್ಕೆ ಹಾರ್ದಿಕ ಅಭಿನಂದನೆಗಳು."
    
    # Phone call script (uses call script from CALL_SCRIPTS)
    call_script = CALL_SCRIPTS['kn'].format(name=student_name, company=company_name, package=package)
    
    return {
        'whatsapp_message': whatsapp_message,
        'voice_script': voice_script,
        'call_script': call_script
    }


# ==================== Translated Messages ====================

def create_translated_messages(student_name, company_name, package, mother_tongue):
    """
    Create translated messages (using translator module)
    
    Args:
        student_name (str): Student's full name
        company_name (str): Company name
        package (str): Salary package (e.g., "25 LPA")
        mother_tongue (str): Student's mother tongue
    
    Returns:
        dict: Contains whatsapp_message, voice_script, call_script
    """
    
    # Create English base message
    english_message = f"Congratulations! Your child {student_name} has been placed in {company_name} with a package of {package} LPA. Congratulations to the entire family!"
    
    # Translate to mother tongue
    translated_text, lang_code, lang_name = translate_message(english_message, mother_tongue)
    
    # Get call script from CALL_SCRIPTS dictionary (simpler, conversational version for calls)
    call_script = ''
    if lang_code in CALL_SCRIPTS:
        call_script = CALL_SCRIPTS[lang_code].format(name=student_name, company=company_name, package=package)
    else:
        call_script = CALL_SCRIPTS.get('en', '').format(name=student_name, company=company_name, package=package)
    
    # For non-Kannada languages, use translated text for WhatsApp and voice
    return {
        'whatsapp_message': translated_text,
        'voice_script': translated_text,
        'call_script': call_script,
        'language': lang_name,
        'language_code': lang_code
    }


# ==================== Main Notification Generator ====================

def generate_placement_notifications(student_name, company_name, package, mother_tongue='Kannada'):
    """
    Generate complete notification package for placement
    
    Args:
        student_name (str): Student's full name
        company_name (str): Company name
        package (str): Salary package (e.g., "25 LPA")
        mother_tongue (str): Student's mother tongue (default: 'Kannada')
    
    Returns:
        dict: JSON structure with all notification messages
        {
            "whatsapp_message": "...",
            "voice_note_script": "...",
            "call_enabled": true/false,
            "call_script": "",
            "language": "Kannada",
            "language_code": "kn"
        }
    """
    
    try:
        # Check if calling API is available
        call_enabled = check_calling_api_available()
        
        # Get language code
        lang_code = get_language_code(mother_tongue)
        lang_name = LANGUAGE_MAP.get(lang_code, {}).get('name', mother_tongue)
        
        # For Kannada, use simple conversational messages
        if lang_code == 'kn':
            messages = create_simple_kannada_message(student_name, company_name, package)
        else:
            # For other languages, use translator
            messages = create_translated_messages(student_name, company_name, package, mother_tongue)
        
        # Build final result
        result = {
            "whatsapp_message": messages['whatsapp_message'],
            "voice_note_script": messages['voice_script'],
            "call_enabled": call_enabled,
            "call_script": messages['call_script'] if call_enabled else "",
            "language": lang_name,
            "language_code": lang_code
        }
        
        print(f"\n[NOTIFICATION] [OK] Generated notifications for {lang_name}")
        print(f"[NOTIFICATION] [OK] Call enabled: {call_enabled}")
        
        return result
        
    except Exception as e:
        print(f"[NOTIFICATION] [ERROR] Error generating notifications: {str(e)}")
        
        # Return fallback English messages
        return {
            "whatsapp_message": f"Congratulations! Your child {student_name} has been placed in {company_name} with a package of {package} LPA.",
            "voice_note_script": f"Congratulations. Your child {student_name} has been placed in {company_name} with a package of {package} LPA.",
            "call_enabled": False,
            "call_script": "",
            "language": "English",
            "language_code": "en",
            "error": str(e)
        }


def generate_placement_notifications_json(student_name, company_name, package, mother_tongue='Kannada'):
    """
    Generate notifications and return as JSON string
    
    Args:
        student_name (str): Student's full name
        company_name (str): Company name
        package (str): Salary package
        mother_tongue (str): Student's mother tongue
    
    Returns:
        str: JSON string with notifications
    """
    result = generate_placement_notifications(student_name, company_name, package, mother_tongue)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== Testing ====================

def test_notifications():
    """Test notification generation for different languages"""
    
    print("\n" + "="*80)
    print("Testing Notification Generator")
    print("="*80)
    
    test_cases = [
        ("Harshith D", "Google", "25", "Kannada"),
        ("Priya Sharma", "Microsoft", "30", "Hindi"),
        ("Amit Kumar", "Amazon", "28", "English"),
        ("Rajesh V", "TCS", "20", "Tamil"),
        ("Sanjana G", "Infosys", "22", "Telugu"),
    ]
    
    for student_name, company, pkg, lang in test_cases:
        print(f"\n{'-'*80}")
        print(f"Student: {student_name} | Company: {company} | Package: {pkg} | Language: {lang}")
        print(f"{'-'*80}")
        
        notifications = generate_placement_notifications(student_name, company, pkg, lang)
        
        print("\n[OUTPUT]")
        print(json.dumps(notifications, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    test_notifications()