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

https://github.com/jonnyhuck/gitsum

Timeline:
 2025-09-02 19:57:37 +92   -75   add total lines count and fix tmp directory not deleting
 2025-09-02 19:28:01 +61   -10   add commit messages to the log output and update README
 2025-09-02 17:02:39 +1    -4    remove outdated references to dulwich
 2025-09-02 17:01:58 +3    -2    fix comments
 2025-09-02 16:59:39 +82   -52   avoid cloning for local repos
 2025-09-02 16:31:59 +73   -208  replace dulwich with gitpython
 2025-09-02 15:00:14 +8    -8    uncomment report
 2025-09-02 14:52:22 +46   -25   update for more detailed report
 2025-08-01 16:08:21 +1    -1    fix link
 2025-08-01 16:07:28 +3    -0    added note on porcelain
 2025-08-01 14:31:52 +3    -4    updated deprecated function
 2025-08-01 14:09:00 +18   -8    add timespan reporting
 2025-08-01 14:09:00 +30   -16   initial commit
 2025-08-01 14:09:00 +168  -0    initial commit
 2025-08-01 14:05:02 +0    -0    Initial commit

Summary:
 Total commits:                   15
 Timespan (days):                 32
 Total lines in HEAD:             852
 Mean insertions per commit:      39.27 (std: 48.38)
 Commit with most net insertions: 2025-08-01 14:09:00 +168 (-0)
```

### Dependencies
This script relies on the excellent [`GitPython`](https://github.com/gitpython-developers/GitPython) library.