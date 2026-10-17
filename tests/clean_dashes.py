"""
Batch cleaner for Unicode em-dashes and en-dashes across HTML files.
Replaces:
- \u2014 (em-dash) with ' - ' or ': '
- \u2013 (en-dash) with '-'
Preserves zero em-dashes / en-dashes rule.
"""

import os

def clean_dashes():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modified = 0

    for dirpath, _, filenames in os.walk(root):
        if any(ignored in dirpath for ignored in ['.git', 'node_modules', '.agents', '.gemini', 'tmp']):
            continue
        for fn in filenames:
            if fn.endswith('.html'):
                fpath = os.path.join(dirpath, fn)
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                new_content = content
                if '\u2014' in new_content:
                    new_content = new_content.replace('\u2014', ' - ')
                if '\u2013' in new_content:
                    new_content = new_content.replace('\u2013', '-')
                # Also check HTML entities &mdash; and &ndash;
                if '&mdash;' in new_content:
                    new_content = new_content.replace('&mdash;', ' - ')
                if '&ndash;' in new_content:
                    new_content = new_content.replace('&ndash;', '-')

                if new_content != content:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    modified += 1
                    print(f"Cleaned dashes in {os.path.relpath(fpath, root)}")

    print(f"Total HTML files sanitized: {modified}")

if __name__ == '__main__':
    clean_dashes()
