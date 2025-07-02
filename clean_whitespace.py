#!/usr/bin/env python3
"""
Clean up trailing whitespace in Python files
"""
import os

def clean_file(filepath):
    """Remove trailing whitespace from a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove trailing whitespace from each line
        lines = content.splitlines()
        cleaned_lines = [line.rstrip() for line in lines]
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Add final newline if original had one
        if content.endswith('\n'):
            cleaned_content += '\n'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"✓ Cleaned {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error cleaning {filepath}: {e}")
        return False

if __name__ == '__main__':
    files_to_clean = [
        'accounting/models.py',
        'accounting/admin.py', 
        'accounting/views.py'
    ]
    
    cleaned_count = 0
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            if clean_file(file_path):
                cleaned_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎉 Cleaned {cleaned_count} files successfully!")
