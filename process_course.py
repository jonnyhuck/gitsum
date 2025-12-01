from re import sub
from time import perf_counter
from gitsum import git_numstat
from os import makedirs, listdir
from subprocess import run, STDOUT
from collections import defaultdict
from os.path import join, exists, isdir
from pandas import read_excel, read_csv, DataFrame


# setup
output_dir = 'UGIS-2025-A1'
# repos = read_excel('UGIS-2025-A1/dashboard-export-01-21-pm-2025-11-14.xlsx')
repos = read_csv('UGIS-2025-A1/26_December 1, 2025_09.26.csv')

# outut data structures
inaccessible_repos = []
unrunnable_repos = []
invalid_repos = []
timings = defaultdict(list)

# for each repo
N = len(repos.index)
for n, row in repos.iterrows():
    print(f"processing {row['Student ID']} ({n}/{N})")

    ''' get git summary '''
    
    # if they sent a template URL, then report and skip
    if row['Link'] in ["https://github.com/jonny-huck/ugis-assessment1.git", "https://github.com/gis-123456789/ugis-assessment1.git"]:
        invalid_repos.append(row)
        continue

    # get repo path
    student_dir = f"{output_dir}/{row['Student ID']}"
    outpath = join(student_dir, "git.txt")

    # only re-calculate git summary if it doesn't already exist
    if not exists(outpath):
        
        # ensure it exists
        makedirs(student_dir, exist_ok=True)

        # get the git summary
        try:
            msg = git_numstat(row['Link'], student_dir)
        except:
            inaccessible_repos.append((row['Student ID'], row['Link']))
            continue

        # write msg to student_dir/git.txt
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(msg)

    ''' run the script '''

    # get file paths
    children = [d for d in listdir(student_dir) if isdir(join(student_dir, d))]
    script_path = join(student_dir, children[0])  # each of these is in a subdirectory of unknown name
    script_file = join(script_path, "assessment1.py")
    output_path = join(student_dir, "output.txt")

    # if the script is in place
    if exists(script_file):

        '''fix file path (if needed)'''

        # read python file
        with open(script_file, "r", encoding="utf-8") as f:
            script_text = f.read()

        # process code to avoid show statements and incorrect file paths
        fixed_text = sub(r"\.\./(?:\.\./)?data", "data", script_text)
        fixed_text = sub(r"(?:plt\.)?show\(\)", r"# \g<0>", fixed_text)

        # write back to the same file
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(fixed_text)

        ''' run the script'''
        
        # run the script in its directory, capture stdout and stderr in file
        with open(output_path, "w", encoding="utf-8") as f:
            start = perf_counter()
            proc = run(["python", "assessment1.py"], stdout=f, stderr=STDOUT, cwd=script_path)
            timings['ID'].append(row['Student ID']) 
            timings['time'].append(perf_counter() - start) 

    else:
        unrunnable_repos.append((row['Student ID'], row['Link']))

# report any URLs that I could not access
if len(inaccessible_repos) > 0:
    print(f'\nCould not access the following repos:')
    for id, url in inaccessible_repos:
        print(f"- {id} ({url})")

# report any URLs that I could not run
if len(unrunnable_repos) > 0:
    print(f'\nCould not run assessment1.py in the following repos:')
    for id, url in unrunnable_repos:
        print(f"- {id} ({url})")

# report any invalid URLs (e.g., my template or 123456789)
if len(invalid_repos) > 0:
    print(f'\nThe following students submitted invalid repos:')
    for id, url in invalid_repos:
        print(f"- {id} ({url})")

# output timings
DataFrame(timings).to_csv(join(output_dir, 'timings.csv'))