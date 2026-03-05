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
        "Lexa": "Lexa",
        "LEXA": "LEXA",
        "Lexa Assistant": "Lexa Assistant",
        "lexa": "lexa",
        "LEXA": "LEXA",
        "Lexa": "Lexa",
        "lexa": "lexa",
        
        # Colors
        "#0A0A0A": "#0A0A0A",
        "#D4AF37": "#D4AF37",
        "#B8962E": "#B8962E", # A darker shade of gold for hover states replacing purple hover
        "#1A1A1A": "#1A1A1A",
        
        # Tailwind classes
        "bg-yellow-50": "bg-yellow-50",
        "bg-yellow-100": "bg-yellow-100",
        "bg-yellow-200": "bg-yellow-200",
        "bg-yellow-300": "bg-yellow-300",
        "bg-yellow-400": "bg-yellow-400",
        "bg-yellow-500": "bg-yellow-500",
        "bg-yellow-600": "bg-yellow-600",
        "bg-yellow-700": "bg-yellow-700",
        "bg-yellow-800": "bg-yellow-800",
        "bg-yellow-900": "bg-yellow-900",
        
        "text-yellow-50": "text-yellow-50",
        "text-yellow-100": "text-yellow-100",
        "text-yellow-200": "text-yellow-200",
        "text-yellow-300": "text-yellow-300",
        "text-yellow-400": "text-yellow-400",
        "text-yellow-500": "text-yellow-500",
        "text-yellow-600": "text-yellow-600",
        "text-yellow-700": "text-yellow-700",
        "text-yellow-800": "text-yellow-800",
        "text-yellow-900": "text-yellow-900",
        
        "border-yellow-50": "border-yellow-50",
        "border-yellow-100": "border-yellow-100",
        "border-yellow-200": "border-yellow-200",
        "border-yellow-300": "border-yellow-300",
        "border-yellow-400": "border-yellow-400",
        "border-yellow-500": "border-yellow-500",
        "border-yellow-600": "border-yellow-600",
        "border-yellow-700": "border-yellow-700",
        "border-yellow-800": "border-yellow-800",
        "border-yellow-900": "border-yellow-900",
        
        "ring-yellow-50": "ring-yellow-50",
        "ring-yellow-100": "ring-yellow-100",
        "ring-yellow-200": "ring-yellow-200",
        "ring-yellow-300": "ring-yellow-300",
        "ring-yellow-400": "ring-yellow-400",
        "ring-yellow-500": "ring-yellow-500",
        "ring-yellow-600": "ring-yellow-600",
        "ring-yellow-700": "ring-yellow-700",
        "ring-yellow-800": "ring-yellow-800",
        "ring-yellow-900": "ring-yellow-900",
        
        "shadow-yellow-50": "shadow-yellow-50",
        "shadow-yellow-100": "shadow-yellow-100",
        "shadow-yellow-200": "shadow-yellow-200",
        "shadow-yellow-300": "shadow-yellow-300",
        "shadow-yellow-400": "shadow-yellow-400",
        "shadow-yellow-500": "shadow-yellow-500",
        "shadow-yellow-600": "shadow-yellow-600",
        "shadow-yellow-700": "shadow-yellow-700",
        "shadow-yellow-800": "shadow-yellow-800",
        "shadow-yellow-900": "shadow-yellow-900",
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
