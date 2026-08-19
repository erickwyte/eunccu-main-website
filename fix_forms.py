#!/usr/bin/env python3
"""
Script to replace the corrupted KENYA_COUNTIES in CompleteRegistrationForm
"""

# Read the original file
with open(r'website\forms.py', 'r') as f:
    lines = f.readlines()

# The correct KENYA_COUNTIES list  
CORRECT_COUNTIES = '''    KENYA_COUNTIES = [
        ('', '--- Select County ---'),
        ('Mombasa', 'Mombasa'),
        ('Kwale', 'Kwale'),
        ('Kilifi', 'Kilifi'),
        ('Tana River', 'Tana River'),
        ('Lamu', 'Lamu'),
        ('Taita–Taveta', 'Taita–Taveta'),
        ('Garissa', 'Garissa'),
        ('Wajir', 'Wajir'),
        ('Mandera', 'Mandera'),
        ('Marsabit', 'Marsabit'),
        ('Isiolo', 'Isiolo'),
        ('Meru', 'Meru'),
        ('Tharaka-Nithi', 'Tharaka-Nithi'),
        ('Embu', 'Embu'),
        ('Kitui', 'Kitui'),
        ('Machakos', 'Machakos'),
        ('Makueni', 'Makueni'),
        ('Nyandarua', 'Nyandarua'),
        ('Nyeri', 'Nyeri'),
        ('Kirinyaga', 'Kirinyaga'),
        ('Murang\\'a', 'Murang\\'a'),
        ('Kiambu', 'Kiambu'),
        ('Turkana', 'Turkana'),
        ('West Pokot', 'West Pokot'),
        ('Samburu', 'Samburu'),
        ('Trans Nzoia', 'Trans Nzoia'),
        ('Uasin Gishu', 'Uasin Gishu'),
        ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'),
        ('Nandi', 'Nandi'),
        ('Baringo', 'Baringo'),
        ('Laikipia', 'Laikipia'),
        ('Nakuru', 'Nakuru'),
        ('Narok', 'Narok'),
        ('Kajiado', 'Kajiado'),
        ('Kericho', 'Kericho'),
        ('Bomet', 'Bomet'),
        ('Kakamega', 'Kakamega'),
        ('Vihiga', 'Vihiga'),
        ('Bungoma', 'Bungoma'),
        ('Busia', 'Busia'),
        ('Siaya', 'Siaya'),
        ('Kisumu', 'Kisumu'),
        ('Homa Bay', 'Homa Bay'),
        ('Migori', 'Migori'),
        ('Kisii', 'Kisii'),
        ('Nyamira', 'Nyamira'),
        ('Nairobi City', 'Nairobi City'),
    ]
'''

# Find the corrupted KENYA_COUNTIES section in CompleteRegistrationForm
start_line = None
end_line = None
in_complete_registration = False

for i, line in enumerate(lines):
    if 'class CompleteRegistrationForm' in line:
        in_complete_registration = True
    
    if in_complete_registration and 'KENYA_COUNTIES = [' in line:
        start_line = i
        # Find the closing bracket
        bracket_count = 1
        for j in range(i + 1, len(lines)):
            for char in lines[j]:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_line = j
                        break
            if bracket_count == 0:
                break
        break

if start_line is not None and end_line is not None:
    print(f"Found corrupted KENYA_COUNTIES from line {start_line + 1} to {end_line + 1}")
    print(f"Replacing {end_line - start_line + 1} lines...")
    
    # Reconstruct the file
    new_lines = lines[:start_line] + [CORRECT_COUNTIES + '\n'] + lines[end_line + 1:]
    
    # Write back
    with open(r'website\forms.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✓ File updated successfully")
else:
    print("Could not find the section to replace")
    print(f"start_line: {start_line}, end_line: {end_line}")
