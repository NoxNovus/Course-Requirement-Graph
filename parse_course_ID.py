import requests
import re
from bs4 import BeautifulSoup

url = "https://www.washington.edu/students/crscat/"

result = []

response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    parenthesized_strings = [text for text in soup.stripped_strings if '(' in text and ')' in text]
    for string in parenthesized_strings:
        result.append(string)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

course_IDs_raw = []

for string in result:
    matches = re.findall(r'\((.*?)\)', string)
    course_IDs_raw.extend(matches)

course_IDs = [s.replace('\xa0', ' ') for s in course_IDs_raw]

output_file_path = "course_ids.txt"
with open(output_file_path, 'w') as file:
    for course_id in course_IDs:
        file.write(course_id + '\n')

print(f"Course IDs have been written to {output_file_path}")