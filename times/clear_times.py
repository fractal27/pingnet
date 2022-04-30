import os

def cleartimes(path):
    """
    Clears the times of all files in a directory.
    """
    files=[os.path.join(path, file) for file in os.listdir(path) if file.startswith('times')]
    for file in files:
        os.remove(file)
if __name__=='__main__':
    try:
        input("---Deleting files that startswith 'times'---\nPress ^C to Cancel and Enter to confirm...")
        cleartimes(os.getcwd())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except PermissionError:
        print("PermissionError: user is not permitted to delete files.")