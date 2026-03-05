import os
import glob
import re

def replace_in_file(filepath, replacements):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return False
    
    orig_content = content
    for old, new in replacements.items():
        if old.startswith('re:'):
            # regex replacement
            pattern = re.compile(old[3:])
            content = pattern.sub(new, content)
        else:
            # string replacement
            content = content.replace(old, new)
            
    if content != orig_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    base_dir = r"c:\Users\jorte\OneDrive\Escritorio\AppLegal_Cloud"
    
    replacements = {
        # Colors
        "#050D1C": "#050D1C", # Dark purple to Darker Navy Blue
        "#102652": "#102652", # Purple header to Navy Blue header
        "#00E5FF": "#00E5FF"  # Light purple to Bright Cyan
    }
    
    extensions = ['*.html', '*.py', '*.txt', '*.md', '*.js', '*.css']
    files_to_process = []
    
    for ext in extensions:
        pattern = os.path.join(base_dir, '**', ext)
        files_to_process.extend(glob.glob(pattern, recursive=True))
        
    # ignore venv and stuff
    files_to_process = [f for f in files_to_process if 'venv' not in f and '.git' not in f and '__pycache__' not in f]
    
    modified_count = 0
    for f in files_to_process:
        if replace_in_file(f, replacements):
            print(f"Updated {f}")
            modified_count += 1
            
    print(f"Total files updated: {modified_count}")

if __name__ == '__main__':
    main()
