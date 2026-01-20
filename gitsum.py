"""
* GitSum(mary) provides a simple summary of the commit history of a git repo. It is primarily 
*   intended to support marking for my programming courses.
* 
* Local or remote repos can be analysed, local repos will be read directly, whereas remotes 
*   will be cloned into a temporary directory for analysis.
*
* Remote URLs can be in the form https://... or git@..., - the latter will be required 
*   if you want to make use of SSH keys (instead of typing in credentials).
*
* @author jonnyhuck
"""

import sys
from git import Repo
from pathlib import Path
from datetime import datetime
from statistics import mean, stdev
from os.path import exists, basename
from tempfile import TemporaryDirectory
from git.exc import GitCommandError, InvalidGitRepositoryError


def count_lines_in_head(repo, extensions=[".py", ".R"]):
    """
    * Count the total number of lines across all tracked files at HEAD.
    """
    total = 0
    tree = repo.head.commit.tree
    
    # walk through the tree
    for blob in tree.traverse():
        
        # it's a file
        if blob.type == "blob":  
            
            # limit to desired file extensions only
            if blob.path[-3:] not in extensions:
                continue

            try:
                # decode file contents (skip binaries)
                data = blob.data_stream.read().decode("utf-8", errors="ignore")
                
                # count the lines
                total += len(data.splitlines())
            
            # skip if unreadable
            except Exception:
                continue  
    return total


def get_report(url, repo):
    """
    * Produce a summary report for a repo object
    """
    # init empty message
    msg = []

    # loop through the commits in reverse (so oldest to newest)
    commits_info = []
    active_dates = set()
    last_date = datetime.fromtimestamp(0)
    for commit in repo.iter_commits("HEAD", reverse=True):

        # log commit date
        active_dates.add(datetime.fromtimestamp(commit.committed_date).date())

        # catch commits with no parent (should just be first one)
        parent = commit.parents[0] if commit.parents else None
        try:
            # diff against parent
            diffs = parent.diff(commit, create_patch=True) if parent else []
        except Exception as e:
            msg += f"\nSkipping commit {commit.hexsha} due to diff error: {e}"
            continue

        # check each line in the diff
        added, deleted = 0, 0
        for d in diffs:
            patch = d.diff.decode('utf-8', errors='ignore').splitlines()
            for line in patch:

                # ignore metadata
                if line.startswith('+++') or line.startswith('---'):
                    continue
                
                # count insertions
                elif line.startswith('+'):
                    added += 1
                
                # count deletions
                elif line.startswith('-'):
                    deleted += 1

        # get commit date
        commit_date = datetime.fromtimestamp(commit.committed_date)

        # add warning flags for short gaps between commits
        mins_between = (commit_date - last_date).total_seconds() / 60
        if 0 < mins_between < 2:    # < 2 mins
            bang = "!!!"
        elif 0 < mins_between < 5:  # < 5 mins
            bang = "!!"
        elif 0 < mins_between < 10: # < 10 mins
            bang = "!"
        else:
            bang = ""

        # writing speed (if less than an hour between commits)
        lines_min = added / mins_between if 0 < mins_between < 60 else 0

        # cache last time
        last_date = commit_date

        # print details for this commit
        msg.append(f"\n {commit_date.strftime('%Y-%m-%d %H:%M:%S')} {commit.hexsha[:7]} ({lines_min:<4.1f} l/min) {bang:<3} +{added:<4} -{deleted:<4} {f'({added - deleted})':<6} {commit.message.strip()}")

        # store details for this commit
        commits_info.append({
            'commit': commit.hexsha,
            'date': datetime.fromtimestamp(commit.committed_date),
            'added': added,
            'deleted': deleted,
            'lines_per_min': lines_min
        })
    
    # reverse the message (because we constructed it backwards)
    msg.append(f"\n{url}\n\nTimeline:")
    msg.reverse()

    # create summary statistics text for this repo
    if commits_info:
        msg.append("\n\nSummary:")
        msg.append(f"\n {'Total commits:':<32} {len(commits_info)}")
        msg.append(f"\n {'Timespan (days):':<32} {(commits_info[0]['date'] - commits_info[-1]['date']).days + 1:,} ({len(active_dates)} active)")
        n_lines_head = count_lines_in_head(repo)
        msg.append(f"\n {'Total lines in HEAD:':<32} {n_lines_head}")
        insertions = [c['added'] for c in commits_info]
        msg.append(f"\n {'Estimated unedited lines:':<32} {max(n_lines_head - (sum(insertions) - n_lines_head) - 1, 0)}")
        speeds = [c['lines_per_min'] for c in commits_info]
        msg.append(f"\n {'Mean lines per minute:':<32} {mean(speeds):.2f} (std: {stdev(speeds) if len(speeds) > 1 else 0:.2f})")
        msg.append(f"\n {'Max lines per minute:':<32} {max(speeds):.2f}")
        msg.append(f"\n {'Mean insertions per commit:':<32} {mean(insertions):.2f} (std: {stdev(insertions) if len(insertions) > 1 else 0:.2f})")
        largest = max(commits_info, key=lambda c: c['added'] - c['deleted'])
        msg.append(f"\n {'Commit with most net insertions:':<32} {largest['date']} {commit.hexsha[:7]} +{largest['added']} -{largest['deleted']} {f"({largest['added'] - largest['deleted']})":<4}\n")
    
    # return the text
    return "".join(msg)


def git_numstat(url, clone_path=None):
    """
    * Gather summary statistics about a git repo by cloning into a local repo
    """
    # if local, just read it directly
    if exists(url):
        try:
            repo = Repo(url)
            return get_report(url, repo)
        except InvalidGitRepositoryError:
            print("ERROR: {url} is not a valid Git Repository.")
            exit()

    # otherwise, it is remote
    else:

        # if there is a clone path, make a copy of the repo there
        if clone_path:

            # get the path and make sure it exists
            path = Path(clone_path)
            path.mkdir(parents=True, exist_ok=True)

            # create a subdirectory name based on the repo name
            repo_name = basename(url.rstrip("/")).replace(".git", "")
            clone_dir = path / repo_name

            # clone the repo into the desired directory
            try:
                repo = Repo.clone_from(url, clone_dir, depth=None)
            except GitCommandError:
                print(f"\nERROR: could not fetch remote {url} \nEither it doesn't exist, or you don't have permission.\n")
                exit()
            
            # get the summary text and return
            return get_report(url, repo)
            
        # if not, use a temp directory
        else:

            # prep a tmp directory just in case (can't get it to delete reliably without with statement)
            with TemporaryDirectory() as tmpdir:    # NB: all repo refs must be inside with statement
                print(f"created tmp directory: {tmpdir}")
                
                # clone the repo into the tmp directory
                try:
                    repo = Repo.clone_from(url, tmpdir, depth=None)
                except GitCommandError:
                    print(f"\nERROR: could not fetch remote {url} \nEither it doesn't exist, or you don't have permission.\n")
                    exit()
                
                # get the summary text and return
                return get_report(url, repo)
            

# run the script using the first argument as the URL
if __name__ == "__main__":

    # if no url is passed, just use the repo for this tool
    try:
        url = sys.argv[1]
    except IndexError:
        print("\nNo URL provided - defaulting to https://github.com/jonnyhuck/gitsum")
        url = "https://github.com/jonnyhuck/gitsum"

    # launch the tool using the url (store in directory if required)
    try:
        output_dir = sys.argv[2]
        msg = git_numstat(url, output_dir)
    except IndexError:
        msg = git_numstat(url)
    
    # print the resulting message
    print(msg)