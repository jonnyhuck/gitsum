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
from git.exc import GitCommandError
from os.path import exists, basename
from tempfile import TemporaryDirectory


def count_lines_in_head(repo):
    """
    * Count the total number of lines across all tracked files at HEAD.
    """
    total = 0
    tree = repo.head.commit.tree
    for blob in tree.traverse():
        if blob.type == "blob":  # it's a file
            try:
                # decode file contents (skip binaries)
                data = blob.data_stream.read().decode("utf-8", errors="ignore")
                total += len(data.splitlines())
            except Exception:
                continue  # skip if unreadable
    return total


def get_report(url, repo):
    """
    * Produce a summary report for a repo object
    """
    # init empty message
    msg = f"\n{url}\n\nTimeline:"

    # loop through the commits
    commits_info = []
    active_dates = set()
    for commit in repo.iter_commits():

        # log commit date
        active_dates.add(datetime.fromtimestamp(commit.committed_date).date())

        # catch commits with no parent (should judt be first one)
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
        commit_date = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')

        # print details for this commit
        msg += f"\n {commit_date} ({commit.hexsha[:7]}) +{added:<4} -{deleted:<4} ({added - deleted:<4}) {commit.message.strip()}"

        # store details for this commit
        commits_info.append({
            'commit': commit.hexsha,
            'date': datetime.fromtimestamp(commit.committed_date),
            'added': added,
            'deleted': deleted
        })

    # create summary statistics text for this repo
    if commits_info:
        msg += "\n\nSummary:"
        msg += f"\n {'Total commits:':<32} {len(commits_info)}"
        msg += f"\n {'Timespan (days):':<32} {(commits_info[0]['date'] - commits_info[-1]['date']).days + 1:,} ({len(active_dates)} active)"
        n_lines_head = count_lines_in_head(repo)
        msg += f"\n {'Total lines in HEAD:':<32} {n_lines_head}"
        insertions = [c['added'] for c in commits_info]
        msg += f"\n {'Estimated unedited lines:':<32} {max(n_lines_head - sum(insertions), 0)}"
        msg += f"\n {'Mean insertions per commit:':<32} {mean(insertions):.2f} (std: {stdev(insertions) if len(insertions) > 1 else 0:.2f})"
        largest = max(commits_info, key=lambda c: c['added'] - c['deleted'])
        msg += f"\n {'Commit with most net insertions:':<32} {largest['date']} +{largest['added']} -{largest['deleted']} ({added - deleted:<4})\n"
    
    # return the text
    return msg


def git_numstat(url, clone_path=None):
    """
    * Gather summary statistics about a git repo by cloning into a local repo
    """
    # if local, just read it directly
    if exists(url):
        repo = Repo(url)

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
    except:
        print("\nNo URL provided - defaulting to https://github.com/jonnyhuck/gitsum")
        url = "https://github.com/jonnyhuck/gitsum"

    # launch the tool using the url
    msg = git_numstat(url)
    print(msg)