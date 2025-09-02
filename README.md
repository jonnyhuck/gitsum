# GitSum(mary)
Simple tool to summarise the history of a Git repository (primarily intended to support marking for my programming courses). The output is similar to that of `git log --numstat`, but with some additional summary information at the end.

Local or remote repos can be analysed, local repos will be read directly, whereas remotes will be cloned into a temporary directory. Remote URLs can be in the form `https://...` or `git@...`, but the latter will be required if you want to make use of SSH keys (instead of typing in credentials).

### Usage
Call the script directly simply by passing the path or url of a Git repository as the first argument:

`python gitsum.py <repo path or url>` e.g., `python gitsum.py https://github.com/jonnyhuck/gitsum`.

If you just want to test it, running `python gitsum.py` with no argument will run the analysis for this repository.

### Example Output
The script ereturns a list of all of the commits in the form (date, inserted lines, removed lines, message). It then provides a summary of the commits, including the number, timespan, mean insertions per commmit and the commit with the greatest net insertions:

```txt

git@github.com:jonnyhuck/gitsum.git

Timeline:
 2025-09-02 17:02:39 +4    -1    remove outdated references to dulwich
 2025-09-02 17:01:58 +2    -3    fix comments
 2025-09-02 16:59:39 +52   -82   avoid cloning for local repos
 2025-09-02 16:31:59 +208  -73   replace dulwich with gitpython
 2025-09-02 15:00:14 +8    -8    uncomment report
 2025-09-02 14:52:22 +25   -46   update for more detailed report
 2025-08-01 16:08:21 +1    -1    fix link
 2025-08-01 16:07:28 +0    -3    added note on porcelain
 2025-08-01 14:31:52 +4    -3    updated deprecated function
 2025-08-01 14:09:00 +8    -18   add timespan reporting
 2025-08-01 14:09:00 +16   -30   initial commit
 2025-08-01 14:09:00 +0    -168  initial commit
 2025-08-01 14:05:02 +109  -1    Initial commit

Summary:
 Total commits:                   13
 Timespan (days):                 32
 Mean insertions per commit:      33.62 (std: 60.69)
 Commit with most net insertions: 2025-09-02 16:31:59 +208 (-73)
```

### Dependencies
This script relies on the excellent (`GitPython`)[https://github.com/gitpython-developers/GitPython] library.