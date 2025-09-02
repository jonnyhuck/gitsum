import sys
from git import Repo
from datetime import datetime
from statistics import mean, stdev
from tempfile import TemporaryDirectory

def git_numstat(url):
    """
    * Gather summary statistics about a git repo by cloning into a local repo
    """
    # open a temp directory (deletes when with block exits)
    print(f"\n{url}\n")
    with TemporaryDirectory() as tmpdir:

        # clone repo from url
        repo = Repo.clone_from(url, tmpdir, depth=None)  # full history

        # loop through the commits
        commits_info = []
        for commit in repo.iter_commits():

            # catch commits with no parent (should judt be first one)
            parent = commit.parents[0] if commit.parents else None
            try:
                # diff against parent
                diffs = commit.diff(parent, create_patch=True)
            except Exception as e:
                print(f"Skipping commit {commit.hexsha} due to diff error: {e}")
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
            print(f"{commit.hexsha[:9]}  {commit_date}  +{added:<4} -{deleted}")

            # store details for this commit
            commits_info.append({
                'commit': commit.hexsha,
                'date': datetime.fromtimestamp(commit.committed_date),
                'added': added,
                'deleted': deleted
            })

        # print summary statistics for this repo
        if commits_info:
            print("\nSummary:")
            print(f"{"Total commits:":<32} {len(commits_info)}")
            print(f"{"Timespan (days):":<32} {(commits_info[0]['date'] - commits_info[-1]['date']).days:,}")
            insertions = [c['added'] for c in commits_info]
            print(f"{"Mean insertions per commit:":<32} {mean(insertions):.2f} (std: {stdev(insertions) if len(insertions) > 1 else 0:.2f})")
            largest = max(commits_info, key=lambda c: c['added'] - c['deleted'])
            print(f"{"Commit with most net insertions:":<32} {largest['date']} +{largest['added']} (-{largest['deleted']})\n")


# run the script using the first argument as the URL
if __name__ == "__main__":
    git_numstat(sys.argv[1])