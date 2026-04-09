"""
Twilio Integration Module
Handles phone call notifications using Twilio API with real-time translation
Uses Google Translator for real-time language conversion
Only used for phone calls - does NOT affect WhatsApp messages
"""

import os
from datetime import datetime
from html import escape

# Twilio language code mappings (used in <Say> tag in TwiML)
# Full list: https://www.twilio.com/docs/voice/twiml/say
TWILIO_LANGUAGE_MAP = {
    'en': 'en-IN',      # English (India)
    'hi': 'hi-IN',      # Hindi
    'ta': 'ta-IN',      # Tamil
    'te': 'te-IN',      # Telugu  
    'kn': 'kn-IN',      # Kannada
    'ml': 'ml-IN',      # Malayalam
    'gu': 'gu-IN',      # Gujarati
    'mr': 'mr-IN',      # Marathi
    'pa': 'pa-IN',      # Punjabi
    'bn': 'bn-IN',      # Bengali
    'or': 'or-IN',      # Odia (Oriya)
}

# Preferred Twilio/Polly TTS voices per language. If Polly is not configured, Twilio will fall back.
# You can change these to different Polly voices as needed (e.g., Polly.Joanna, Polly.Aditi).
TWILIO_VOICE_MAP = {
    'en': 'Polly.Joanna',
    'hi': 'Polly.Aditi',
    # Default: use 'alice' if not using Polly
}

# Per-language default SSML prosody settings for more natural speech.
# Values will be used in <prosody rate="" pitch=""> wrapper when present.
TWILIO_PROSODY_MAP = {
    'en': {'rate': '0%', 'pitch': '0%'},
    'hi': {'rate': '5%', 'pitch': '2%'}
}

# Import translator for real-time language conversion
try:
    from translator import translate_message
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("[WARNING] translator module not available. Multilingual Twilio calls may be limited.")



# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')  # Your Twilio phone number

TWILIO_AVAILABLE = TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER

if TWILIO_AVAILABLE:
    try:
        from twilio.rest import Client
        TWILIO_CLIENT_AVAILABLE = True
    except ImportError:
        print("[WARNING] Twilio library not installed. Install with: pip install twilio")
        TWILIO_CLIENT_AVAILABLE = False
else:
    TWILIO_CLIENT_AVAILABLE = False

# Twilio client instance (lazily initialized)
_twilio_client = None


def get_twilio_client():
    """Get or initialize Twilio client"""
    global _twilio_client
    
    if not TWILIO_AVAILABLE:
        return None
    
    if not TWILIO_CLIENT_AVAILABLE:
        return None
    
    if _twilio_client is None:
        try:
            _twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            print("[TWILIO] Client initialized successfully")
        except Exception as e:
            print(f"[TWILIO] Failed to initialize client: {e}")
            return None
    
    return _twilio_client


def check_twilio_available():
    """
    Check if Twilio calling is available
    
    Returns:
        bool: True if Twilio is configured and available, False otherwise
    """
    if not TWILIO_AVAILABLE:
        print("[TWILIO] Credentials not found. Configure:")
        print("  export TWILIO_ACCOUNT_SID=your_account_sid")
        print("  export TWILIO_AUTH_TOKEN=your_auth_token")
        print("  export TWILIO_PHONE_NUMBER=your_twilio_phone_number")
        return False
    
    if not TWILIO_CLIENT_AVAILABLE:
        print("[TWILIO] Twilio library not available")
        return False
    
    return True




def make_call_with_script(parent_phone, call_script, student_name, company_name, language_code='en', call_voice=None, call_prosody=None):
    """
    Make a phone call with the given script using Twilio with real-time language translation.
    
    Uses Google Translator to translate the call script to the target language, then
    passes the translated text to Twilio with the appropriate language code in the TwiML <Say> tag.

    Args:
        parent_phone (str): Parent's phone number (with country code, e.g., +918088915514)
        call_script (str): The script (in English) to be read during the call
        student_name (str): Student's name (for logging)
        company_name (str): Company name (for logging)
        language_code (str): Language code (e.g., 'en', 'kn', 'hi', 'ta')

    Returns:
        dict: {
            'success': bool,
            'call_sid': str,
            'message': str,
            'error': str or None
        }
    """

    # NOTE: Twilio availability will be checked after building TwiML, so we can
    # provide an accurate TwiML preview showing the intended language and text
    # even if credentials are missing (useful for local debugging).

    try:
        # Normalize legacy codes
        if language_code == 'ka':
            language_code = 'kn'

        # Format phone number
        if not parent_phone.startswith('+'):
            # Assume India number if no country code
            parent_phone = f'+91{parent_phone[-10:]}'

        # NOTE: Twilio client initialization is done after building TwiML so that
        # the TwiML preview can be returned even when credentials or client are not available.

        print(f"\n[TWILIO] Initiating call to {parent_phone}")
        print(f"[TWILIO] Student: {student_name} | Company: {company_name}")
        print(f"[TWILIO] Script length: {len(call_script)} characters")
        print(f"[TWILIO] Requested language: {language_code}")

        # Determine the target call language for Twilio: only Hindi is supported as non-English
        target_call_lang = 'hi' if language_code == 'hi' else 'en'

        # Decide whether we need to translate the script so it matches the target call language
        actual_script = call_script
        try:
            from translator import LANGUAGE_MAP
        except Exception:
            LANGUAGE_MAP = {}

        is_ascii = all(ord(c) < 128 for c in call_script)
        try:
            if target_call_lang == 'en':
                # If the script is not ASCII (i.e., not English), translate it to English
                if not is_ascii and TRANSLATOR_AVAILABLE:
                    try:
                        english_name = LANGUAGE_MAP.get('en', {}).get('name', 'English')
                        translated_text, _, _ = translate_message(call_script, english_name)
                        actual_script = translated_text
                        print(f"[TWILIO] Translated to English (for Twilio call)")
                        print(f"[TWILIO] Translated (first 100 chars): {actual_script[:100]}...")
                    except Exception as trans_err:
                        print(f"[TWILIO] [WARN] Translation to English failed: {trans_err}")
                        actual_script = call_script
                elif not is_ascii and not TRANSLATOR_AVAILABLE:
                    # Translator not available; create a simple English fallback to avoid playing
                    # non-English text as English TTS.
                    actual_script = f"Hello, this is an automated call from placement cell. {student_name} has been placed in {company_name}. Congratulations."
            else:
                # target_call_lang == 'hi'
                if is_ascii and TRANSLATOR_AVAILABLE:
                    try:
                        hindi_name = LANGUAGE_MAP.get('hi', {}).get('name', 'Hindi')
                        translated_text, _, _ = translate_message(call_script, hindi_name)
                        actual_script = translated_text
                        print(f"[TWILIO] Translated to {hindi_name}")
                        print(f"[TWILIO] Translated (first 100 chars): {actual_script[:100]}...")
                    except Exception as trans_err:
                        print(f"[TWILIO] [WARN] Translation to Hindi failed: {trans_err}")
                        actual_script = call_script
                else:
                    actual_script = call_script
        except Exception as _e:
            actual_script = call_script

        # Get the Twilio language code (maps internal code to Twilio's format)
        twilio_lang = TWILIO_LANGUAGE_MAP.get(target_call_lang, 'en-IN')
        
        print(f"[TWILIO] Using Twilio language: {twilio_lang}")
        print(f"[TWILIO] Final call script (first 200 chars): {actual_script[:200]}")

        # Ensure the final script has content; if not, fall back to a simple English message
        if not actual_script or not str(actual_script).strip():
            actual_script = f"Hello, this is an automated call from placement cell regarding {student_name}'s placement."

        # NOTE: Twilio's <Say> tag does not accept arbitrary SSML markup in all environments.
        # Including <speak> or <prosody> inside <Say> can cause an application error from Twilio.
        # To avoid that, we will not inject SSML directly. Instead, we split the text into
        # sentences and create one <Say> per sentence with a small <Pause> between sentences.
        # Prosody overrides are approximated using pause length adjustments rather than SSML.
        prosody = call_prosody if call_prosody else TWILIO_PROSODY_MAP.get(target_call_lang)
        # Determine pause length based on prosody rate (faster rate -> shorter pause)
        default_pause = 0.5
        pause_length = default_pause
        if prosody and isinstance(prosody, dict) and 'rate' in prosody:
            try:
                rate_str = str(prosody.get('rate', '0%')).strip()
                if rate_str.endswith('%'):
                    rate_val = float(rate_str[:-1])
                else:
                    rate_val = float(rate_str)
                # Map rate percent to pause length (capped)
                pause_length = max(0.1, default_pause - (rate_val / 100.0) * 0.3)
            except Exception:
                pause_length = default_pause
        # Split script into sentences for multiple <Say> tags
        import re
        sentence_split_re = re.compile(r'(?<=[\.\?!।])\s+')
        sentences = [s.strip() for s in sentence_split_re.split(actual_script) if s.strip()]
        # Escape sentences and build TwiML per sentence
        safe_sentences = [escape(s) for s in sentences]
        # Localized thank-you/farewell based on requested language
        THANK_YOU_TEXT = {
            'en': 'Thank you for listening. Goodbye.',
            'hi': 'सुनने के लिए धन्यवाद। अलविदा।'
        }
        safe_thank_you = escape(THANK_YOU_TEXT.get(language_code, THANK_YOU_TEXT['en']))
        # Determine Twilio voice for the chosen language. Prioritize an explicit
        # call_voice override (from student_data), otherwise use our preferred
        # per-language voice mapping. If neither is available, fall back to 'alice'.
        if call_voice:
            twilio_voice = call_voice
        else:
            twilio_voice = TWILIO_VOICE_MAP.get(target_call_lang, 'alice')
        voice_attr = f'voice="{twilio_voice}" '
        print(f"[TWILIO] Using voice attribute: {voice_attr.strip() or 'default'} for language: {twilio_lang}")

        # Build TwiML using multiple <Say> blocks for each sentence (and an internal pause)
        say_blocks = []
        for s in safe_sentences:
            say_blocks.append(f'    <Say {voice_attr}language="{twilio_lang}">{s}</Say>')
            say_blocks.append(f'    <Pause length="{pause_length}"/>')
        # Thank-you message(s) as separate say block(s)
        thank_sentences = [escape(t) for t in sentence_split_re.split(THANK_YOU_TEXT.get(language_code, THANK_YOU_TEXT['en'])) if t.strip()]
        for ts in thank_sentences:
            say_blocks.append(f'    <Say {voice_attr}language="{twilio_lang}">{ts}</Say>')

        twiml_body = "\n".join(say_blocks)
        twiml_response = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>\n{twiml_body}\n</Response>"""

        # Log TwiML (short preview) for diagnostics
        print(f"[TWILIO] TwiML Preview: {twiml_response[:200]}")

        # Validate TwiML (parse as XML) before sending to Twilio to avoid application errors
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(twiml_response)
        except Exception as xml_err:
            print(f"[TWILIO] [ERROR] Generated TwiML is invalid: {xml_err}. Falling back to single <Say> message.")
            # Fallback: single <Say> with escaped plain text (no pauses / no SSML)
            single_text = escape(actual_script)
            twiml_response = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>\n    <Say {voice_attr}language=\"{twilio_lang}\">{single_text}</Say>\n</Response>"""
            print(f"[TWILIO] TwiML Fallback Preview: {twiml_response[:200]}")

        # Check Twilio credentials availability. If Twilio is not configured, show a full TwiML preview and return.
        if not check_twilio_available():
            print(f"[TWILIO] Twilio not configured, skipping actual call (preview above)")
            return {
                'success': False,
                'call_sid': None,
                'message': 'Twilio not configured',
                'error': 'Missing Twilio credentials',
                'call_script': call_script,
                'call_language': target_call_lang,
                'twiml_preview': twiml_response
            }

        # Get Twilio client now that we've built TwiML and verified credentials are present
        client = get_twilio_client()
        if not client:
            return {
                'success': False,
                'call_sid': None,
                'message': 'Failed to initialize Twilio',
                'error': 'Client initialization failed',
                'call_script': call_script,
                'call_language': target_call_lang,
                'twiml_preview': twiml_response
            }

        # Make the call
        call = client.calls.create(
            to=parent_phone,
            from_=TWILIO_PHONE_NUMBER,
            twiml=twiml_response,
            timeout=30
        )

        print(f"[TWILIO] Call initiated successfully!")
        print(f"[TWILIO] Call SID: {call.sid}")
        print(f"[TWILIO] Status: {call.status}")

        return {
            'success': True,
            'call_sid': call.sid,
            'message': f'Call initiated. SID: {call.sid}',
            'error': None,
            'status': call.status,
            'timestamp': datetime.now().isoformat()
            , 'twiml_preview': twiml_response
        }

    except Exception as e:
        error_msg = str(e)
        print(f"[TWILIO] Error making call: {error_msg}")

        return {
            'success': False,
            'call_sid': None,
            'message': 'Failed to make call',
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }



def make_call_simple(parent_phone, call_script, language_code='en', call_voice=None, call_prosody=None):
    """
    Simple wrapper for making calls
    
    Args:
        parent_phone (str): Parent's phone number
        call_script (str): Script to be read during the call
    
    Returns:
        dict: Call result
    """
    return make_call_with_script(parent_phone, call_script, 'Student', 'Company', language_code, call_voice=call_voice, call_prosody=call_prosody)


def make_placement_call(student_data):
    """
    Make a placement notification call using Twilio
    
    Args:
        student_data (dict): Student data dictionary containing:
            - full_name: Student's full name
            - parent_phone: Parent's phone number
            - company_name: Company name
            - package: Salary package
            - mother_tongue: Language code
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'call_sid': str or None
        }
    """
    try:
        from notification_generator import CALL_SCRIPTS
        
        # Extract data
        student_name = student_data.get('full_name', 'Student')
        parent_phone = student_data.get('parent_phone', '').strip()
        company_name = student_data.get('company_name', 'Company')
        package = student_data.get('package', 'Unknown')
        mother_tongue = student_data.get('mother_tongue', 'en')
        # Normalize mother_tongue to language code for CALL_SCRIPTS
        try:
            from translator import get_language_code
            mother_tongue = get_language_code(mother_tongue)
        except Exception:
            # If translator not available, fall back to provided value
            pass
        
        # Validate phone number
        if not parent_phone:
            return {
                'success': False,
                'message': 'Parent phone number not found',
                'call_sid': None
            }
        
        # Determine Twilio call language: Hindi only results in Hindi calls, otherwise default to English
        # This ensures Twilio TTS speaks Hindi only when mother tongue is Hindi
        call_lang_code = 'hi' if mother_tongue == 'hi' else 'en'

        # Get call script in the chosen language for Twilio. Always generate the call script
        # text to match the language selected for the call itself.
        call_script_template = CALL_SCRIPTS.get(call_lang_code, CALL_SCRIPTS['en'])
        call_script = call_script_template.format(
            name=student_name,
            company=company_name,
            package=package
        )
        
        print(f"\n{'='*60}")
        print(f"Making placement notification call")
        print(f"{'='*60}")
        print(f"Parent: {student_name}'s parent | Phone: {parent_phone}")
        print(f"Company: {company_name} | Package: {package} LPA")
        print(f"Language: {mother_tongue}")
        print(f"[TWILIO CALL] Chosen call language for Twilio: {call_lang_code}")
        print(f"{'='*60}\n")
        
        # Normalize mother_tongue value (handle legacy 'ka') and pass to call
        lang_code = call_lang_code
        if lang_code == 'ka':
            lang_code = 'kn'

        # Make the call (pass language_code so gTTS vs Twilio TTS selection works)
        # Allow a voice override and prosody override in student_data to control Twilio TTS.
        voice_override = student_data.get('call_voice') if isinstance(student_data, dict) else None
        prosody_override = student_data.get('call_prosody') if isinstance(student_data, dict) else None
        result = make_call_with_script(
            parent_phone=parent_phone,
            call_script=call_script,
            student_name=student_name,
            company_name=company_name,
            language_code=lang_code
            , call_voice=voice_override
            , call_prosody=prosody_override
        )
        
        # Attach the call script and language used for diagnostic purposes
        result['call_script'] = call_script
        result['call_language'] = lang_code
        return result
        
    except Exception as e:
        print(f"[ERROR] Error making placement call: {e}")
        return {
            'success': False,
            'message': str(e),
            'call_sid': None,
            'call_script': '',
            'call_language': mother_tongue
        }


def test_twilio_config():
    """Test Twilio configuration"""
    
    print("\n" + "="*80)
    print("TWILIO CONFIGURATION TEST")
    print("="*80)
    
    print(f"\n[CONFIG] Account SID: {TWILIO_ACCOUNT_SID[:10] + '...' if TWILIO_ACCOUNT_SID else 'NOT SET'}")
    print(f"[CONFIG] Auth Token: {'SET' if TWILIO_AUTH_TOKEN else 'NOT SET'}")
    print(f"[CONFIG] Phone Number: {TWILIO_PHONE_NUMBER if TWILIO_PHONE_NUMBER else 'NOT SET'}")
    
    print(f"\n[CHECK] Twilio Available: {check_twilio_available()}")
    print(f"[CHECK] Client Available: {TWILIO_CLIENT_AVAILABLE}")
    
    if check_twilio_available():
        client = get_twilio_client()
        if client:
            print("[OK] Twilio client initialized successfully")
            print("[OK] Ready to make calls")
        else:
            print("[ERROR] Failed to initialize Twilio client")
    else:
        print("[INFO] Twilio not configured - calling disabled")
        print("[INFO] To enable, set these environment variables:")
        print("      TWILIO_ACCOUNT_SID")
        print("      TWILIO_AUTH_TOKEN")
        print("      TWILIO_PHONE_NUMBER")
    
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    test_twilio_config()