import os

def cleartimes(path):
    for file in os.listdir(path):
        if file.startswith('times'):
            os.remove(os.path.join(path, file))
if __name__=='__main__':
    try:
        input("---Deleting files that startswith 'times'---\nPress ^C to Cancel and Enter to confirm...")
        cleartimes(os.getcwd())
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except PermissionError:
        print("PermissionError: user is not permitted to delete files.")