import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry_exists(title):
    return get_entry(title) is not None


def markdown_to_html(markdown_content):
    html_content = markdown_content

    html_content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)

    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)

    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)

    html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)

    lines = html_content.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('- ') or line.startswith('* '):
            list_items = []

            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                list_content = lines[i].strip()[2:]
                list_items.append(f'<li>{list_content}</li>')
                i += 1

            if list_items:
                result_lines.append('<ul>')
                result_lines.extend(list_items)
                result_lines.append('</ul>')
        else:
            if line:
                line = line.replace('\n', '<br>')
                result_lines.append(f'<p>{line}</p>')
            else:
                result_lines.append('')
            i += 1

    return '\n'.join(result_lines)


def get_entry(title):
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None
