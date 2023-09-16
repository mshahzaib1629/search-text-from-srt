from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    search_text = ''
    if request.method == 'POST':
        search_text = request.form.get('search_text')
        results = find_text_in_srt_files('../', search_text)
        return render_template('index.html', results=results, search_text=search_text)
    return render_template('./index.html', results=None)


def find_text_in_srt_files(root_directory, search_text):
    
    result = {}

    # Define a regular expression pattern for matching the search text
    pattern = re.compile(re.escape(search_text), re.IGNORECASE)

    # Regular expression pattern for matching time strings in the format HH:MM:SS,sss --> HH:MM:SS,sss
    time_pattern = re.compile(
        r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}')

    # Recursively traverse the directory
    for root, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.srt'):
                srt_file_path = os.path.join(root, file)
                with open(srt_file_path, 'r', encoding='utf-8', errors='ignore') as srt_file:
                    srt_content = srt_file.read()
                    # Split the content by subtitle blocks
                    subtitle_blocks = srt_content.split('\n\n')
                    for block in subtitle_blocks:
                        # Search for the pattern within each block
                        if pattern.search(block):
                            # Find the time string
                            time_match = time_pattern.search(block)
                            if time_match:
                                time_string = time_match.group(0)
                            else:
                                time_string = "Time not found"

                            # Remove the time string and trailing numbers (if any) from the snippet
                            snippet_lines = block.split('\n')
                            if len(snippet_lines) > 1:
                                # Remove the time string line
                                snippet_lines.pop(0)
                                snippet = '\n'.join(
                                    snippet_lines).rstrip('0123456789')
                            else:
                                snippet = ''

                            folder_name = srt_file_path.split('/')[1]
                            file_name = file

                            # Group results by folder_name
                            if folder_name not in result:
                                result[folder_name] = []
                            result[folder_name].append({
                                'file_name': file_name,
                                'time_string': time_string,
                                'snippet': highlight_search_text(snippet.strip(), search_text)
                            })

    return result

def highlight_search_text(snippet, search_text):
    # Use regular expression to replace search_text with a highlighted version (case-insensitive)
    highlighted_snippet = re.sub(
        re.escape(search_text), lambda m: f'<span class="highlight">{m.group()}</span>', snippet, flags=re.IGNORECASE
    )
    return highlighted_snippet

if __name__ == '__main__':
    app.run(debug=True)
