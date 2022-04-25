#importando moduli
import os
import sys

#definisco funzione per cancellare i file che hanno un nome che inizia per 'tempi'
def clear_tempi(path):
    for file in os.listdir(path):
        if file.startswith('times'):
            os.remove(os.path.join(path, file))
if __name__=='__main__':
    sys.stdout.write("---Deleting files that startswith 'times'---\nPress enter to confirm...")
    sys.stdin.readline()
    
    clear_tempi(os.getcwd())
    sys.exit()