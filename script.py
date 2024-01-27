import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

SUBJECT_CODES = ["CSE", "MATH", "E E", "INFO", "PHYS"]
SUBJECT_CODES = ["CSE"]

def main():            
    # Get all URLs for various subjects at UW
    subjects = dict()
    for subject in SUBJECT_CODES:
        subjects[subject] = f"https://www.washington.edu/students/crscat/{''.join(subject.split()).lower()}.html"

    course_prereqs = dict()
    for subject in subjects:
        # Fetch HTML, if unsuccessful, skip all further steps for this subject
        success = download_HTML(subject, subjects[subject])
        if(not success):
            continue

        # Construct dict of courses to course details
        course_details = parse_courses(f"{subject}.html")

        # Get a map of courses to course prereqs, and add to overall map
        course_prereqs.update(extract_prereqs(course_details))

    # Construct the graph and visualize it
    course_graph = create_course_graph(course_prereqs)
    nt = Network(height="500px", width="100%", bgcolor="#222222", font_color="white")
    nt.from_nx(course_graph)
    nt.show("course_prerequisites.html", notebook=False)


def create_course_graph(course_dict):
    G = nx.DiGraph()

    for course in course_dict:
        G.add_node(course)

    for course, prerequisites in course_dict.items():
        for prerequisite in prerequisites:
            G.add_edge(prerequisite, course)

    return G


def extract_prereqs(course_details):
    """
    Extract courses and course prereqs from the HTML.
    Key observation: if a course is mentioned in another course's description, 
    it is probably a pre-req.
    """
    # Basic formatting to make the process easier
    formatted_subject_codes = [code.replace(" ", "") for code in SUBJECT_CODES]
    formatted_course_details = {
        key.upper(): value.replace(' ', '')
        for key, value in course_details.items()
    }

    # Remove all courses that have mutual exclusion:
    # courses that cannot be taken for credit if credit received for another course
    for key, value in formatted_course_details.items():
        new_value = value.replace(key, '')
        sentences = new_value.split('.')
        filtered_sentences = [sentence.strip() for sentence in sentences if "creditreceived" not in sentence]
        result_string = '.'.join(filtered_sentences)
        formatted_course_details[key] = result_string

    # Go through and extract all the mentioned courses from course descriptions
    course_prereqs = {}
    for course, details in formatted_course_details.items():
        prereqs = set()
        for code in formatted_subject_codes:
            index = 0
            while index != -1:
                index = details.find(code, index)
                if index != -1 and index + len(code) + 3 <= len(details):
                    following_chars = details[index + len(code):index + len(code) + 3]
                    if following_chars.isdigit():
                        prereqs.add(details[index:index + len(code) + 3])
                    index += 1 
        course_prereqs[course] = list(prereqs)
    return course_prereqs


def parse_courses(file_path):
    """
    Parses out all locations in an HTML file that contain courses.
    """
    courses_details_map = {}

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('<a name='):
                course_start = line.find('"') + 1
                course_end = line.find('"', course_start)
                course = line[course_start:course_end]
                details = line[course_end + 1:].strip()
                courses_details_map[course] = details

    return courses_details_map


def download_HTML(course, url):
    """
    Download the HTML for a page given its url.
    """
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        with open(f"{course}.html", "w", encoding="utf-8") as file:
            file.write(response.text)
        return True

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return False


if __name__ == "__main__":
    main()