"""
WhatsApp Automation Module
Twilio WhatsApp API integration
"""
import os
import json
import time
from datetime import datetime
import pytz
from pathlib import Path
from twilio.rest import Client

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# Initialize Twilio Client
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    except Exception as e:
        print(f"[ERROR] Failed to initialize Twilio client: {e}")

# Configure timezone for India
IST = pytz.timezone('Asia/Kolkata')


def delete_audio_file_safe(path, reason='sent'):
    """
    Delete audio file safely only if it's under static/audio directory.
    Returns True if deletion succeeded, False otherwise.
    """
    try:
        if not path:
            return False
        # Only delete under static/audio to be extra-safe
        safe_root = os.path.abspath(os.path.join(os.getcwd(), 'static', 'audio'))
        abs_path = os.path.abspath(path)
        # Normalize case for cross-platform path comparisons
        norm_safe_root = os.path.normcase(safe_root)
        norm_abs_path = os.path.normcase(abs_path)
        if not norm_abs_path.startswith(norm_safe_root):
            print(f"[WARN] Not deleting audio file outside static/audio: {abs_path}")
            return False
        if os.path.exists(abs_path):
            os.remove(abs_path)
            print(f"[OK] Deleted audio file after {reason}: {abs_path}")
            return True
        else:
            print(f"[INFO] Audio file not found for deletion: {abs_path}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to delete audio file {path}: {e}")
        return False

# ============================================================================
# BOT HEALTH CHECK
# ============================================================================

def is_bot_running():
    """Check if Twilio credentials are configured"""
    return TWILIO_ACCOUNT_SID is not None and TWILIO_AUTH_TOKEN is not None and twilio_client is not None


def wait_for_bot(timeout=5):
    """Wait for Twilio connection (simple check)"""
    return is_bot_running()


# ============================================================================
# MESSAGE SENDING FUNCTIONS
# ============================================================================

def send_whatsapp_message(phone, message):
    """
    Send a text message via Twilio WhatsApp API
    
    Args:
        phone (str): Phone number (e.g., +91XXXXXXXXXX)
        message (str): Message text to send
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        if not twilio_client:
            print("[ERROR] Twilio client not initialized")
            return False

        # Format phone number for Twilio WhatsApp
        to_phone = phone.strip()
        if not to_phone.startswith('whatsapp:'):
            if not to_phone.startswith('+'):
                # Default to India if no country code
                to_phone = f'+91{to_phone[-10:]}'
            to_phone = f'whatsapp:{to_phone}'

        print(f"[SEND] Sending Twilio WhatsApp message to {to_phone}...")
        
        message_res = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_phone
        )
        
        print(f"[OK] Twilio WhatsApp message SID: {message_res.sid}")
        return True
    
    except Exception as e:
        print(f"[ERROR] Error sending Twilio WhatsApp message: {e}")
        return False


def send_whatsapp_audio(phone, audio_path, caption=''):
    """
    [DEPRECATED] Twilio WhatsApp API requires public URLs for media.
    Local files cannot be sent directly without a public tunnel (ngrok) or S3.
    """
    print("[WARN] send_whatsapp_audio is deprecated for Twilio Local. Use Voice Call instead.")
    # For now, we'll send the caption as a text message if audio fails
    if caption:
        return send_whatsapp_message(phone, f"{caption} (Voice note sent via call)")
    return False


def send_placement_whatsapp(student_data):
    """
    Send placement notification with both text and voice message to PARENT'S phone
    
    Features:
    1. Creates English placement message
    2. Automatically generates translated voice message based on student's mother tongue
    3. Sends text message to parent
    4. Sends translated voice message to parent
    
    Args:
        student_data (dict): Student information containing:
            - full_name (str): Student name
            - parent_phone (str): Parent's phone number (RECEIVER)
            - parent_name (str): Parent's name
            - company_name (str): Company name
            - package (str): Package/salary
            - mother_tongue (str): Student's mother tongue (e.g., 'Kannada', 'Tamil')
            - id (int): Student ID
            - audio_path (str): Optional pre-generated audio file path
    
    Returns:
        dict: {
            'success': bool,
            'text_sent': bool,
            'audio_sent': bool,
            'audio_file': str,
            'language': str,
            'translated_text': str
        }
    """
    try:
        from voice_generator import create_placement_notification_voice
        
        student_name = student_data.get('full_name', 'Student')
        parent_name = student_data.get('parent_name', 'Parent')
        parent_phone = student_data.get('parent_phone', '')  # PARENT'S phone
        company_name = student_data.get('company_name', '')
        package = student_data.get('package', '')
        mother_tongue = student_data.get('mother_tongue', 'English')
        student_id = student_data.get('id', 1)
        pre_generated_audio_path = student_data.get('audio_path', None)

        if not parent_phone:
            print(f"[ERROR] No parent phone number for student {student_name}")
            return {
                'success': False,
                'text_sent': False,
                'audio_sent': False,
                'audio_file': None,
                'language': None,
                'translated_text': None
            }

        # Format message to PARENT
        message = f"""🎉 Congratulations! 🎉

Dear {parent_name},

Placement Confirmed! [INFO]

Your child {student_name} has been successfully placed at:
🏢 Company: {company_name}
💰 Package: {package}

Contact our office for further details.

- Placement Team"""

        print(f"\n{'='*60}")
        print(f"Sending placement notification to parent")
        print(f"Parent: {parent_name} | Phone: {parent_phone}")
        print(f"Student: {student_name}")
        print(f"Mother Tongue: {mother_tongue}")
        print(f"{'='*60}")

        # Send text message to parent's phone
        text_sent = send_whatsapp_message(parent_phone, message)

        # Generate and send audio message with automatic translation
        audio_sent = False
        audio_file = None
        language = None
        translated_text = None
        
        # Local wrapper uses top-level helper to allow testing
        def _safe_delete_audio_file(path, reason='sent'):
            try:
                return delete_audio_file_safe(path, reason=reason)
            except Exception as e:
                print(f"[ERROR] Failed to delete audio file {path}: {e}")
                return False

        # Check if audio was pre-generated
        if pre_generated_audio_path and os.path.exists(pre_generated_audio_path):
            print(f"[OK] Using pre-generated audio: {pre_generated_audio_path}")
            audio_file = pre_generated_audio_path
            time.sleep(2)
            audio_sent = send_whatsapp_audio(
                parent_phone,
                audio_file,
                caption=f'Placement Notification - {mother_tongue}'
            )
            # If audio was provided by user (pre-generated) and configured to delete, check flag
            if audio_sent and student_data.get('delete_after_send'):
                # Small delay to allow bot to read the file before deletion
                time.sleep(1)
                _safe_delete_audio_file(audio_file, reason='sent (pre-generated)')
        else:
            # Generate voice message with translation
            print(f"[INFO] Generating voice message with translation to {mother_tongue}...")
            
            voice_result = create_placement_notification_voice({
                'id': student_id,
                'full_name': student_name,
                'company_name': company_name,
                'package': package,
                'mother_tongue': mother_tongue
            })
            
            if voice_result.get('success'):
                audio_file = voice_result.get('file_path')
                language = voice_result.get('language')
                translated_text = voice_result.get('translated_text')
                
                print(f"[OK] Voice message generated successfully!")
                print(f"   Language: {voice_result.get('language_name')} ({language})")
                print(f"   File: {voice_result.get('filename')}")
                print(f"   Text: {translated_text}")
                
                # Send audio to parent
                time.sleep(2)
                audio_sent = send_whatsapp_audio(
                    parent_phone,
                    audio_file,
                    caption=f'Placement Notification - {voice_result.get("language_name")}'
                )
                # By default auto-delete generated audio files after successful send
                if audio_sent:
                    # Small delay to allow bot to read the file before deletion
                    time.sleep(1)
                    _safe_delete_audio_file(audio_file, reason='sent (generated)')
            else:
                print(f"[WARN] Voice generation failed: {voice_result.get('error')}")
                print(f"[INFO] Continuing with text message only")

        print(f"{'='*60}\n")

        return {
            'success': text_sent or audio_sent,
            'text_sent': text_sent,
            'audio_sent': audio_sent,
            'audio_file': audio_file,
            'language': language,
            'translated_text': translated_text
        }

    except Exception as e:
        print(f"[ERROR] Error in send_placement_whatsapp: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'text_sent': False,
            'audio_sent': False,
            'audio_file': None,
            'language': None,
            'translated_text': None
        }


def initialize_whatsapp():
    """Check Twilio initialization"""
    print("\n" + "="*70)
    print("[SECURE] Twilio WhatsApp API Initialization")
    print("="*70)
    
    if is_bot_running():
        print("\n[OK] Twilio WhatsApp client is initialized!")
        print(f"[OK] From: {TWILIO_WHATSAPP_NUMBER}")
        print("="*70 + "\n")
        return True
    else:
        print("\n[ERROR] Twilio credentials missing in .env")
        print("="*70 + "\n")
        return False


def send_bulk_whatsapp(students_data):
    """
    Send notifications to multiple students
    
    Args:
        students_data (list): List of student data dictionaries
    
    Returns:
        dict: Summary of sent/failed messages
    """
    results = {
        'total': len(students_data),
        'sent': 0,
        'failed': 0,
        'students': []
    }

    print(f"\n{'='*60}")
    print(f"📢 Bulk WhatsApp Campaign - {results['total']} students")
    print(f"{'='*60}\n")

    for i, student_data in enumerate(students_data, 1):
        name = student_data.get('name', 'Unknown')
        print(f"[{i}/{results['total']}] Sending to {name}...")
        
        if send_placement_whatsapp(student_data):
            results['sent'] += 1
            results['students'].append({
                'name': name,
                'status': 'sent'
            })
        else:
            results['failed'] += 1
            results['students'].append({
                'name': name,
                'status': 'failed'
            })
        
        # Delay between messages to avoid rate limiting
        if i < results['total']:
            time.sleep(3)

    print(f"\n{'='*60}")
    print(f"📊 Campaign Summary:")
    print(f"   Total: {results['total']}")
    print(f"   Sent: {results['sent']} [OK]")
    print(f"   Failed: {results['failed']}")
    print(f"{'='*60}\n")

    return results


# ============================================================================
# STATUS AND DEBUGGING
# ============================================================================

def get_bot_status():
    """Get current Twilio API status"""
    if is_bot_running():
        return {'ready': True, 'api': 'Twilio WhatsApp'}
    return {'ready': False, 'error': 'Missing credentials'}


def print_bot_info():
    """Print Twilio connection information"""
    print("\n" + "="*60)
    print("[BOT] Twilio WhatsApp API Information")
    print("="*60)
    print(f"Account SID: {TWILIO_ACCOUNT_SID[:10]}..." if TWILIO_ACCOUNT_SID else "Not set")
    print(f"WhatsApp Number: {TWILIO_WHATSAPP_NUMBER}")
    
    status = get_bot_status()
    if status.get('ready'):
        print(f"Status: [OK] API Ready")
    else:
        print(f"Status: [ERROR] {status.get('error')}")
    
    print("="*60 + "\n")


# ============================================================================
# NOTIFICATION GENERATOR INTEGRATION
# ============================================================================

def get_placement_notifications(student_name, company_name, package, mother_tongue='Kannada'):
    """
    Get complete notification package with WhatsApp message, voice script, and call script
    
    This function generates all notification content in the student's mother tongue
    and checks if calling API is available for phone call notifications.
    
    Args:
        student_name (str): Student's full name
        company_name (str): Company name
        package (str): Salary package (e.g., "25 LPA")
        mother_tongue (str): Student's mother tongue (default: 'Kannada')
    
    Returns:
        dict: Notification package with structure:
        {
            "whatsapp_message": "...",
            "voice_note_script": "...",
            "call_enabled": true/false,
            "call_script": "",
            "language": "Kannada",
            "language_code": "kn"
        }
    
    Example:
        >>> notifications = get_placement_notifications(
        ...     "Harshith D", 
        ...     "Google", 
        ...     "25", 
        ...     "Kannada"
        ... )
        >>> print(notifications['whatsapp_message'])
        >>> print(notifications['call_enabled'])
    """
    try:
        from notification_generator import generate_placement_notifications
        
        notifications = generate_placement_notifications(
            student_name,
            company_name,
            package,
            mother_tongue
        )
        
        return notifications
        
    except ImportError:
        print("[WARN] notification_generator module not found. Using basic messages.")
        
        # Fallback to basic messages
        return {
            "whatsapp_message": f"Congratulations! {student_name} placed at {company_name} with {package} LPA package.",
            "voice_note_script": f"Congratulations. {student_name} placed at {company_name} with {package} LPA package.",
            "call_enabled": False,
            "call_script": "",
            "language": "English",
            "language_code": "en"
        }
    except Exception as e:
        print(f"[ERROR] Error getting notifications: {e}")
        return {
            "whatsapp_message": f"Congratulations! {student_name} placed at {company_name}.",
            "voice_note_script": f"Congratulations. {student_name} placed at {company_name}.",
            "call_enabled": False,
            "call_script": "",
            "language": "English",
            "language_code": "en",
            "error": str(e)
        }


# ============================================================================
# TWILIO CALLING INTEGRATION
# ============================================================================

def send_placement_call_with_twilio(parent_phone, call_script, student_name, company_name, language_code='en', call_voice=None, call_prosody=None):
    """
    Send a phone call notification using Twilio
    Only for phone calls - does NOT affect WhatsApp messages
    
    Args:
        parent_phone (str): Parent's phone number
        call_script (str): Script to be read during the call
        student_name (str): Student's name (for logging)
        company_name (str): Company name (for logging)
    
    Returns:
        dict: {
            'success': bool,
            'call_sid': str,
            'message': str,
            'error': str or None
        }
    
    Example:
        >>> result = send_placement_call_with_twilio(
        ...     '+918088915514',
        ...     'Congratulations! Your child has been placed.',
        ...     'Harshith D',
        ...     'Google'
        ... )
        >>> if result['success']:
        ...     print(f"Call sent: {result['call_sid']}")
    """
    try:
        from twilio_calling import make_call_with_script
        
        call_result = make_call_with_script(
            parent_phone,
            call_script,
            student_name,
            company_name,
            language_code
            , call_voice
            , call_prosody
        )
        
        return call_result
        
    except ImportError:
        print("[WARN] twilio_calling module not found.")
        return {
            'success': False,
            'call_sid': None,
            'message': 'Twilio module not available',
            'error': 'twilio_calling import failed'
        }
    except Exception as e:
        print(f"[ERROR] Error sending call: {e}")
        return {
            'success': False,
            'call_sid': None,
            'message': 'Failed to send call',
            'error': str(e)
        }


if __name__ == '__main__':
    # Test the module
    print_bot_info()
    initialize_whatsapp()