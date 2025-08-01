import sys
import tempfile
import difflib
from dulwich.repo import Repo
from dulwich import porcelain
from time import perf_counter
from urllib.parse import urlparse
from datetime import datetime, timezone
from dulwich.diff_tree import tree_changes

def clone_or_open(source):
    """ Load a local or remote repo into a Repo object"""

    # parse the URL
    parsed = urlparse(source)
    
    # load remote
    if parsed.scheme in ("http", "https", "git", "ssh"):
        target_dir = tempfile.mkdtemp()
        print(f"Cloning {source} to {target_dir} ...")
        porcelain.clone(source, target_dir)
        return Repo(target_dir)
    
    # load local
    else:
        return Repo(source)


def get_head_commit_id(repo):
    """ Get the commit ID of the repo HEAD """
    
    # get the HEAD ref
    head_ref = repo.refs.read_ref(b"HEAD")
    
    # raise error if there isn't one
    if head_ref is None:
        raise ValueError("No HEAD found in repository")
    
    # tidy up so we have the ID only and return
    if head_ref.startswith(b"ref: "):
        head_ref = head_ref[5:]
    return repo.refs[head_ref]


def count_files_in_commit(repo, commit_id):
    """Count the number of files in a commit."""

    # get tree ID for the commit
    tree_id = repo[commit_id].tree
    
    # loop through files
    count = 0
    for path, mode, sha in repo.object_store.iter_tree_contents(tree_id):
        
        # convert mode from bytes to int (octal)
        if isinstance(mode, bytes):
            mode = int(mode.decode(), 8)
        
        # check for regular file using bitmask, increment counter if so
        if mode & 0o170000 == 0o100000:
            count += 1
    return count


def analyze(repo, detail):
    """ Analyse commit summary for a given Repo object """
    
    # get the latest commit from the repo
    commit_id = get_head_commit_id(repo)
    
    # get a walker object to examine the log
    walker = repo.get_walker(include=[commit_id])

    # collect commits and sort oldest to newest
    commits = [entry.commit for entry in walker]
    commits.reverse()

    # record first and last commit timestamps
    first_commit_date = datetime.fromtimestamp(commits[0].author_time, tz=timezone.utc)
    last_commit_date = datetime.fromtimestamp(commits[-1].author_time, tz=timezone.utc)
    timespan_days = (last_commit_date - first_commit_date).days

    # init the output for the detailed output
    if detail:
        print(f"{'Commit':<8} {'Files':<8} {'Insertions':<12} {'Deletions':<10}")

    # loop through commits
    total_commits = total_edits = 0
    for commit in commits:
        
        # increment counter
        total_commits += 1
        
        # get the immediate parent in the tree
        parents = commit.parents
        parent_tree = repo[parents[0]].tree if parents else None

        # init counters
        files_changed = insertions = deletions = 0

        # if not the first commit, compare to parent (otherwise compare to None)
        changes = list(tree_changes(repo.object_store, parent_tree, commit.tree))

        # get number of files changed
        files_changed = len(changes)

        # loop through the changes
        for change in changes:

            # get the checksum IDs
            old_sha = getattr(change.old, "sha", None)
            new_sha = getattr(change.new, "sha", None)

            old_blob_lines = []
            new_blob_lines = []

            # if there is an old version, get it (otherwise empty)
            if old_sha:
                try:
                    old_blob = repo[old_sha]
                    old_blob_lines = old_blob.data.decode("utf-8", errors="ignore").splitlines()
                except (KeyError, AttributeError):
                    old_blob_lines = []

            # if there is a new version, get it (otherwise empty)
            if new_sha:
                try:
                    new_blob = repo[new_sha]
                    new_blob_lines = new_blob.data.decode("utf-8", errors="ignore").splitlines()
                except (KeyError, AttributeError):
                    new_blob_lines = []

            # diff old and new and count insertions and deletions
            for line in difflib.unified_diff(old_blob_lines, new_blob_lines, lineterm=""):
                if line.startswith("+") and not line.startswith("+++"):
                    insertions += 1
                elif line.startswith("-") and not line.startswith("---"):
                    deletions += 1

        # output data into table for detailed output
        if detail:
            print(f"{commit.id.decode()[:8]} {files_changed:<8} {insertions:<12} {deletions:<10}")
        
        # accumulate total edits (insert only to avoid duplication)
        total_edits += insertions

    # calculate total files in the HEAD of the repo
    total_files = count_files_in_commit(repo, commit_id)

    # report the brief summary
    print(f"\n{'Total files in HEAD:':<31} {total_files}")
    print(f"{'Total commits:':<31} {total_commits}")
    print(f"{'Mean Edits per file per commit:':<31} {total_edits / total_commits / total_files:,.2f}")
    print(f"{'Timespan (days):':<31} {timespan_days:,}")


if __name__ == "__main__":

    # if no args, print help and exit
    if len(sys.argv) < 2:
        print("Usage: python git_stats.py <github-url-or-local-path> <detailed-output: True/False>")
        exit()

    # get the detailed output flag (default False)
    try:
        detail = sys.argv[2] == 'True'
    except:
        detail = False

    # get the repo and analyse it
    repo = clone_or_open(sys.argv[1])
    t1_start = perf_counter() 
    analyze(repo, detail)
    t1_stop = perf_counter()
    print(f"{t1_stop-t1_start:.1f} secs.")
    print('\ndone!')