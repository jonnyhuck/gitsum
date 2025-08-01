import re
import sys
import tempfile
from io import BytesIO
from dulwich.repo import Repo
from dulwich import porcelain
from urllib.parse import urlparse

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
    # TODO: why?
    commits = [entry.commit for entry in walker]
    commits.reverse()

    # init the output
    if detail:
        print(f"{'Commit':<8} {'Files':<8} {'Insertions':<12} {'Deletions':<10}")

    # loop through commits
    total_commits = total_edits = 0
    for commit in commits:
        
        # increment counter
        total_commits += 1
        
        # get parent (if there is one)
        parents = commit.parents
        if parents:
            parent_tree = repo[parents[0]].tree
        else:
            parent_tree = None

        # count changed files in this commit
        changes = list(repo.object_store.tree_changes(parent_tree, commit.tree))
        files_changed = len(changes)
        
        # loop through the files and count insertions and deletions
        insertions = deletions = 0

        # Prepare diff text by file if we have a parent commit
        diffs_by_path = {}
        if parent_tree:
            buf = BytesIO()
            porcelain.diff_tree(repo, parent_tree, commit.tree, outstream=buf)
            diff_text = buf.getvalue().decode("utf-8", errors="ignore")

            # Split the diff text into per-file chunks using the 'diff --git' header lines
            file_paths = re.findall(r'^diff --git a/(.*) b/.*$', diff_text, flags=re.MULTILINE)
            file_diffs = re.split(r'^diff --git a/.* b/.*$', diff_text, flags=re.MULTILINE)

            # file_diffs[0] is everything before the first file diff, discard it
            # Map file path to its corresponding diff chunk
            diffs_by_path = dict(zip(file_paths, file_diffs[1:]))

        for change in changes:

            # unpack changes tuple
            old_path, new_path = change[0] 
            # old_mode, new_mode = changes[1]
            old_sha, new_sha = change[2]

            path = new_path or old_path

            # if there is a diff to be calculated, get it per file chunk
            if old_path and new_path and path in diffs_by_path:
                diff_lines = diffs_by_path[path].splitlines()
                for line in diff_lines:
                    if line.startswith("+") and not line.startswith("+++"):
                        insertions += 1
                    elif line.startswith("-") and not line.startswith("---"):
                        deletions += 1
            
            # if it's a new file, everything is an insertion
            elif new_path:
                try:
                    blob = repo[new_sha]
                    insertions += blob.data.count(b"\n")
                except KeyError:
                    pass
            
            # if the file is removed, everything is a deletion
            elif old_path:
                try:
                    blob = repo[old_sha]
                    deletions += blob.data.count(b"\n")
                except KeyError:
                    pass

        # output the counts
        if detail:
            print(f"{commit.id.decode()[:8]} {files_changed:<8} {insertions:<12} {deletions:<10}")
        
        # sum total edits
        total_edits += insertions + deletions

    # output a summary
    total_files = count_files_in_commit(repo, commit_id)
    print(f"\n{'Total files in HEAD:':<22} {total_files}")
    print(f"{'Total commits:':<22} {total_commits}")
    print(f"{'Mean Edits per commit:':22} {total_edits / total_commits:,.2f}")


if __name__ == "__main__":
    
    # if the argument wasn't provided print help and exit
    if len(sys.argv) < 2:
        print("Usage: python git_stats.py <github-url-or-local-path>")
        exit()

    # get oprtional argument as Boolean
    try:
        detail = sys.argv[2] == 'True'
    except:
        detail = False

    # load the repo and analyse it
    repo = clone_or_open(sys.argv[1])
    analyze(repo, detail)
    print('\ndone!')