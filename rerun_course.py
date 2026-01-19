"""
Re Run the GitSummary for each directory in an existing file structure
"""
from os import listdir
from gitsum import git_numstat
from os.path import join, isdir

# target directory
course_directory = 'UGIS-2025-A2'      

# get outer directory (student ID number)
for student_dir in listdir(course_directory):
    student_dir = join(course_directory, student_dir)
    if isdir(student_dir):

        # get inner directory (local repo)
        for repo_dir in listdir(student_dir):
            repo_dir = join(student_dir, repo_dir)
            if isdir(repo_dir):
                print(f"processing {repo_dir}...")

                # get the git summary
                msg = git_numstat(repo_dir, student_dir)

                # overwrite msg to student_dir/git.txt
                with open(join(student_dir, "git.txt"), "w", encoding="utf-8") as f:
                    f.write(msg)