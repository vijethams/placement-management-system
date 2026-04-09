"""
Voice Message Generator for Placement Notifications
Uses Google Text-to-Speech (gTTS) with translation support for multilingual messages
"""
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("[WARNING] gTTS not installed. Install with: pip install gtts==2.4.0")

import os
from pathlib import Path
import threading

# Import translator module
try:
    from translator import translate_message, get_language_code
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("[WARNING] translator module not found. Multilingual translation disabled.")
    translate_message = None
    get_language_code = None


class VoiceGenerator:
    """Generate voice messages for placement notifications with translation support"""
    
    def __init__(self, audio_dir='static/audio'):
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.gtts_available = GTTS_AVAILABLE
        self.translator_available = TRANSLATOR_AVAILABLE
        
        if GTTS_AVAILABLE:
            print("[INFO] gTTS voice generator initialized successfully")
        else:
            print("[ERROR] gTTS not available - voice generation disabled")
        
        if TRANSLATOR_AVAILABLE:
            print("[INFO] Translation module available - multilingual support enabled")
        else:
            print("[WARNING] Translation module not available - using English messages only")
    
    def get_available_voices(self):
        """Get available voices (gTTS supports 100+ languages)"""
        return ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'gu', 'mr', 'pa', 'bn', 'or']
    
    def set_language_voice(self, language_code='en'):
        """
        Set language for voice generation.
        gTTS automatically handles this through the language parameter.
        """
        pass  # gTTS handles language in generate_placement_message
    
    def generate_placement_message(self, student_name, company_name, package, 
                                   mother_tongue='English', student_id=1):
        """
        Generate a placement notification voice message using gTTS with automatic translation
        
        Pipeline:
        1. Create English message
        2. Translate to student's mother tongue
        3. Generate voice in translated language
        4. Save MP3 file
        
        Args:
            student_name: Student's full name
            company_name: Company name
            package: Salary package (e.g., "25 LPA")
            mother_tongue: Student's mother tongue (e.g., 'Kannada', 'Tamil', 'English')
            student_id: Student ID for unique filename
        
        Returns:
            dict: {
                'success': bool,
                'file_path': str or None,
                'filename': str or None,
                'file_size': int,
                'language': str,
                'language_name': str,
                'original_text': str,
                'translated_text': str,
                'error': str or None
            }
        """
        try:
            if not self.gtts_available:
                print("[ERROR] gTTS not available - voice generation disabled")
                return {
                    'success': False,
                    'file_path': None,
                    'filename': None,
                    'file_size': 0,
                    'language': 'en',
                    'language_name': 'English',
                    'original_text': '',
                    'translated_text': '',
                    'error': 'gTTS not available'
                }
            
            # Step 1: Create English message
            english_message = f"Congratulations! Your child {student_name} has been placed in {company_name} with a package of {package} LPA. Congratulations to the entire family!"
            
            # Step 2: Translate message if translator available
            translated_text = english_message
            lang_code = 'en'
            lang_name = 'English'
            
            if self.translator_available and translate_message and mother_tongue.lower() != 'english':
                print(f"[INFO] Student mother tongue: {mother_tongue}")
                translated_text, lang_code, lang_name = translate_message(english_message, mother_tongue)
            else:
                print(f"[INFO] Using English message (no translation)")
            
            # Step 3: Generate audio file with translated text
            audio_filename = f'placement_msg_{student_id}_{int(os.urandom(2).hex(), 16)}_{lang_code}.mp3'
            audio_path = self.audio_dir / audio_filename
            
            print(f"[INFO] Generating voice message in {lang_name} ({lang_code}) for {student_name}...")
            print(f"[INFO] Message to be converted: {translated_text}")
            
            # Use gTTS to generate speech with translated text
            tts = gTTS(text=translated_text, lang=lang_code, slow=False)
            tts.save(str(audio_path))
            
            # Verify file was created
            if not audio_path.exists():
                return {
                    'success': False,
                    'file_path': None,
                    'filename': None,
                    'file_size': 0,
                    'language': lang_code,
                    'language_name': lang_name,
                    'original_text': english_message,
                    'translated_text': translated_text,
                    'error': 'Audio file creation failed'
                }
            
            file_size = audio_path.stat().st_size
            print(f"[SUCCESS] Voice message generated: {audio_filename} ({file_size} bytes)")
            
            return {
                'success': True,
                'file_path': str(audio_path),
                'filename': audio_filename,
                'file_size': file_size,
                'language': lang_code,
                'language_name': lang_name,
                'original_text': english_message,
                'translated_text': translated_text,
                'error': None
            }
                
        except Exception as e:
            print(f"[ERROR] Error generating voice message: {str(e)}")
            return {
                'success': False,
                'file_path': None,
                'filename': None,
                'file_size': 0,
                'language': 'en',
                'language_name': 'English',
                'original_text': '',
                'translated_text': '',
                'error': str(e)
            }
    
    def stop(self):
        """Stop method (not needed for gTTS but kept for compatibility)"""
        pass


def create_placement_notification_voice(student_data, audio_dir='static/audio'):
    """
    Helper function to create voice notification with translation
    
    Args:
        student_data: Dictionary with student details:
            {
                'id': int,
                'full_name': str,
                'company_name': str,
                'package': str,
                'mother_tongue': str (e.g., 'Kannada', 'Tamil', 'English')
            }
        audio_dir: Directory to store audio files
    
    Returns:
        dict: Result with file path, language info, and translation details
    """
    try:
        voice_gen = VoiceGenerator(audio_dir)
        
        result = voice_gen.generate_placement_message(
            student_name=student_data.get('full_name', 'Student'),
            company_name=student_data.get('company_name', 'Company'),
            package=student_data.get('package', 'Package'),
            mother_tongue=student_data.get('mother_tongue', 'English'),
            student_id=student_data.get('id', 1)
        )
        
        voice_gen.stop()
        return result
        
    except Exception as e:
        print(f"[ERROR] Error in create_placement_notification_voice: {e}")
        return {
            'success': False,
            'file_path': None,
            'filename': None,
            'file_size': 0,
            'language': 'en',
            'language_name': 'English',
            'original_text': '',
            'translated_text': '',
            'error': str(e)
        }


# Global instance
_voice_generator = None


def get_voice_generator():
    """Get or create global voice generator instance"""
    global _voice_generator
    if _voice_generator is None:
        _voice_generator = VoiceGenerator()
    return _voice_generator


if __name__ == '__main__':
    # Test voice generation with translation
    generator = get_voice_generator()
    
    print("\n" + "="*70)
    print("Testing Voice Generation with Translation")
    print("="*70)
    
    test_students = [
        {'id': 1, 'full_name': 'Harshith D', 'company_name': 'Google', 'package': '25', 'mother_tongue': 'Kannada'},
        {'id': 2, 'full_name': 'Priya Kumar', 'company_name': 'Microsoft', 'package': '23', 'mother_tongue': 'Tamil'},
        {'id': 3, 'full_name': 'Raj Patel', 'company_name': 'TCS', 'package': '20', 'mother_tongue': 'Hindi'},
        {'id': 4, 'full_name': 'Anjali Singh', 'company_name': 'Amazon', 'package': '28', 'mother_tongue': 'English'},
        {'id': 5, 'full_name': 'Arjun Reddy', 'company_name': 'Infosys', 'package': '21', 'mother_tongue': 'Telugu'},
    ]
    
    for student in test_students:
        result = create_placement_notification_voice(student)
        if result['success']:
            print(f"\n✅ {student['mother_tongue']}:")
            print(f"   Student: {student['full_name']}")
            print(f"   File: {result['filename']} ({result['file_size']} bytes)")
            print(f"   Language: {result['language_name']} ({result['language']})")
            print(f"   Original: {result['original_text']}")
            print(f"   Translated: {result['translated_text']}")
        else:
            print(f"\n❌ {student['mother_tongue']}: {result['error']}")
    
    print("\n" + "="*70)