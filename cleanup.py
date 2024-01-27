import os
import glob

def main():
    check_cleanup()

def check_cleanup():
    """
    Check if user wants to cleanup HTML files from before.
    """
    user_input = input("Do you want to perform cleanup (delete all HTML files in directory)? (y/n): ")
    if user_input.lower() == 'y':
        cleanup()
        print("Cleanup completed.")
    elif user_input.lower() == 'n':
        print("No cleanup performed.")
    else:
        print("Invalid input. Please enter 'y' or 'n'.")


def cleanup():
    """
    Delete all HTML files in the current directory.
    """
    html_files = glob.glob('*.html')
    for file in html_files:
        os.remove(file)

if __name__ == "__main__":
    main()