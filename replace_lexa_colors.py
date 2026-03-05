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
        "#08142C": "#08142C", # Deep Black to Navy Blue
        "#00A3FF": "#00A3FF", # Gold to Bright Cyan
        "#007BCC": "#007BCC", # Darker Gold to Darker Cyan
        "#0F295E": "#0F295E", # Dark Gray to Lighter Navy Blue
        
        # Tailwind classes
        "bg-cyan-50": "bg-cyan-50",
        "bg-cyan-100": "bg-cyan-100",
        "bg-cyan-200": "bg-cyan-200",
        "bg-cyan-300": "bg-cyan-300",
        "bg-cyan-400": "bg-cyan-400",
        "bg-cyan-500": "bg-cyan-500",
        "bg-cyan-600": "bg-cyan-600",
        "bg-cyan-700": "bg-cyan-700",
        "bg-cyan-800": "bg-cyan-800",
        "bg-cyan-900": "bg-cyan-900",
        
        "text-cyan-50": "text-cyan-50",
        "text-cyan-100": "text-cyan-100",
        "text-cyan-200": "text-cyan-200",
        "text-cyan-300": "text-cyan-300",
        "text-cyan-400": "text-cyan-400",
        "text-cyan-500": "text-cyan-500",
        "text-cyan-600": "text-cyan-600",
        "text-cyan-700": "text-cyan-700",
        "text-cyan-800": "text-cyan-800",
        "text-cyan-900": "text-cyan-900",
        
        "border-cyan-50": "border-cyan-50",
        "border-cyan-100": "border-cyan-100",
        "border-cyan-200": "border-cyan-200",
        "border-cyan-300": "border-cyan-300",
        "border-cyan-400": "border-cyan-400",
        "border-cyan-500": "border-cyan-500",
        "border-cyan-600": "border-cyan-600",
        "border-cyan-700": "border-cyan-700",
        "border-cyan-800": "border-cyan-800",
        "border-cyan-900": "border-cyan-900",
        
        "ring-cyan-50": "ring-cyan-50",
        "ring-cyan-100": "ring-cyan-100",
        "ring-cyan-200": "ring-cyan-200",
        "ring-cyan-300": "ring-cyan-300",
        "ring-cyan-400": "ring-cyan-400",
        "ring-cyan-500": "ring-cyan-500",
        "ring-cyan-600": "ring-cyan-600",
        "ring-cyan-700": "ring-cyan-700",
        "ring-cyan-800": "ring-cyan-800",
        "ring-cyan-900": "ring-cyan-900",
        
        "shadow-cyan-50": "shadow-cyan-50",
        "shadow-cyan-100": "shadow-cyan-100",
        "shadow-cyan-200": "shadow-cyan-200",
        "shadow-cyan-300": "shadow-cyan-300",
        "shadow-cyan-400": "shadow-cyan-400",
        "shadow-cyan-500": "shadow-cyan-500",
        "shadow-cyan-600": "shadow-cyan-600",
        "shadow-cyan-700": "shadow-cyan-700",
        "shadow-cyan-800": "shadow-cyan-800",
        "shadow-cyan-900": "shadow-cyan-900",
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
