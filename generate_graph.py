import requests
from bs4 import BeautifulSoup
import networkx as nx
from pyvis.network import Network

SUBJECT_CODES = []

# This KEY_PHRASES uses a rather ugly hack to solve edge cases with sentence breaks.
# TODO: Fix should be simple, just parse sentences better
KEY_PHRASES = [
    "prerequisite",
    "corequisite",
    "recommend",
    "0in",
    "1in",
    "2in",
    "3in",
    "4in",
    "5in",
    "6in",
    "7in",
    "8in",
    "9in"
]

# TODO: Is there a way to fetch old courses?
OLD_COURSE_LIST = [
    "CSE142",
    "CSE143",
    "CSE303",
    "CSE321",
    "CSE322",
    "CSE326",
    "CSE370",
    "CSE378"
]


def main():         
    print("Example subject codes:\nCSE\nMATH\nPHYS\nE E\nINFO\n")
    while True:
        subject_code = input("Enter a subject code (or 'done' to finish): ")
        if subject_code.lower() == 'done':
            break

        elif subject_code.lower() == 'computing':
            SUBJECT_CODES.extend(["CSE", "MATH", "PHYS", "E E", "INFO", "AMATH"])
        
        else:
            SUBJECT_CODES.append(subject_code)
            continue

        break

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

    # Prune old courses
    course_prereqs = {key: value for key, value in course_prereqs.items() if key not in OLD_COURSE_LIST}


    for course, prereqs in course_prereqs.items():
        for prereq_class in OLD_COURSE_LIST:
            if prereq_class in prereqs:
                prereqs.remove(prereq_class)

    # Construct the graph and visualize it
    course_graph = create_course_graph(course_prereqs)
    nt = Network(directed=True, height="500px", width="100%", bgcolor="#222222", font_color="white")
    nt.from_nx(course_graph)
    nt.show("course_prerequisites.html", notebook=False)


def create_course_graph(course_dict):
    """
    Construct the graph via networkx from the raw dependencies.
    """
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
        filtered_sentences = [
            sentence for sentence in sentences 
            if any(phrase.lower() in sentence.lower() for phrase in KEY_PHRASES)
        ]
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
    

def parse_course_ids(file_path):
    """
    Parse in course IDs from file.
    """
    try:
        with open(file_path, 'r') as file:
            course_ids = [line.strip() for line in file.readlines()]
        return course_ids
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []


if __name__ == "__main__":
    main()
