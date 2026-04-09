from twilio_calling import make_placement_call

kn_data = {'full_name': 'Harshith D', 'parent_phone': '+918088915514', 'company_name': 'Google', 'package': '25', 'mother_tongue': 'kn'}
hi_data = {'full_name': 'Priya Sharma', 'parent_phone': '+919999999999', 'company_name': 'Microsoft', 'package': '30', 'mother_tongue': 'hi'}

print('--- Kannada (should use English for call with Polly.Joanna) ---')
print(make_placement_call(kn_data))

print('\n--- Hindi (should use Hindi for call with Polly.Aditi) ---')
print(make_placement_call(hi_data))

# Example: override voice
print('\n--- Hindi with override Polly.Joanna (should force English voice on a Hindi message) ---')
hi_data_override = hi_data.copy()
hi_data_override['call_voice'] = 'Polly.Joanna'
print(make_placement_call(hi_data_override))

print('\n--- Hindi with SSML override (rate +10%, pitch +4%) ---')
hi_data_prosody = hi_data.copy()
hi_data_prosody['call_prosody'] = {'rate': '10%', 'pitch': '4%'}
print(make_placement_call(hi_data_prosody))
