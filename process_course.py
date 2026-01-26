"""
Run the GitSummary for each directory in an existing file structure, and run each script

    Git report is written to repo/git.txt and the output of the script is written to repo/out.txt
    All script runtimes are stored in timings.csv
"""
from re import sub
from time import perf_counter
from gitsum import git_numstat
from os import makedirs, listdir
from subprocess import run, STDOUT
from collections import defaultdict
from os.path import join, exists, isdir
from pandas import read_csv, DataFrame

# setup
output_dir = 'UGIS-2025-A2'     # directory in which to clone the repositories
input_csv = 'UGIS-2025-A2/26_January 26, 2026_06.55.csv'    # csv of student IDs and repo links
student_column = 'Student ID'   # column in the CSV containing the student ID
repo_column = 'Link'             # column in the repo containing the remote repository reference
script_name = "assessment2.py"  # name of the script to run
recalc_git = True               # recalculate git summaries, even where they exist
run_new_only = True             # only run scripts in repos that are new
invalid_users = ['jonny-huck', 'gis-123456789']  # invalid users

# output data structures
inaccessible_repos = []
unrunnable_repos = []
invalid_repos = []
timings = defaultdict(list)

# read in csv
repos = read_csv(input_csv)

# for each repo
N = len(repos.index)
for n, row in repos.iterrows():
    print(f"processing {row[student_column]} ({n}/{N})")

    ''' get git summary '''
    
    # if they sent a template URL, then report and skip
    cont = False
    for invalid_user in invalid_users:
        if invalid_user in row[repo_column]:
            invalid_repos.append(row)
            cont = True
            break
    if cont:
        continue

    # get repo path
    student_dir = f"{output_dir}/{row[student_column]}"
    outpath = join(student_dir, "git.txt")

    # only calculate git summary if it doesn't already exist, or if asked to recalculate
    if not exists(outpath) or recalc_git:
        
        # ensure it exists
        makedirs(student_dir, exist_ok=True)

        # get the git summary
        # try:
        msg = git_numstat(row[repo_column], student_dir)
        # except:
        #     inaccessible_repos.append((row['Student ID'], row['Link']))
        #     continue

        # write msg to student_dir/git.txt
        with open(outpath, "w", encoding="utf-8") as f:
            f.write(msg)

    ''' run the script '''

    # get file paths
    children = [d for d in listdir(student_dir) if isdir(join(student_dir, d))]
    script_path = join(student_dir, children[0])  # each of these is in a subdirectory of unknown name
    script_file = join(script_path, script_name)
    output_path = join(student_dir, "output.txt")

    # if the script is in place
    if exists(script_file):

        # if set to run new repos only, then only run if an output isn't in place
        if not run_new_only or (run_new_only and not exists(output_path)):

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
                proc = run(["python", script_name], stdout=f, stderr=STDOUT, cwd=script_path)
                timings['ID'].append(row['Student ID']) 
                timings['time'].append(perf_counter() - start) 
        else:
            print(f"Skipping...")
    else:
        unrunnable_repos.append((row['Student ID'], row['Link']))

# report any URLs that I could not access
if len(inaccessible_repos) > 0:
    print(f'\nCould not access the following repos:')
    for id, url in inaccessible_repos:
        print(f"- {id} ({url})")

# report any URLs that I could not run
if len(unrunnable_repos) > 0:
    print(f'\nCould not run {script_name} in the following repos:')
    for id, url in unrunnable_repos:
        print(f"- {id} ({url})")

# report any invalid URLs (e.g., my template or 123456789)
if len(invalid_repos) > 0:
    print(f'\nThe following students submitted invalid repos:')
    for id, url in invalid_repos:
        print(f"- {id} ({url})")

# output timings
DataFrame(timings).to_csv(join(output_dir, 'timings.csv'))