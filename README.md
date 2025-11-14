# GitSum(mary)
Simple tool to summarise the history of a Git repository (primarily intended to support marking for my programming courses). The output is similar to that of `git log --numstat`, but with some additional summary information at the end.

Local or remote repos can be analysed, local repos will be read directly, whereas remotes will be cloned into a temporary directory. Remote URLs can be in the form `https://...` or `git@...`, but the latter will be required if you want to make use of SSH keys (instead of typing in credentials).

### Usage
#### Run Directly
Call the script directly simply by passing the path or url of a Git repository as the first argument:

`python gitsum.py <repo path or url>` e.g., `python gitsum.py https://github.com/jonnyhuck/gitsum`.

If you just want to test it, running `python gitsum.py` with no argument will run the analysis for this repository.

#### Call as a Library
See `process_course.py` for an example where you read Student IDs and Git URLs from a spreadsheet. Each repo is cloned, and files are added for the GitSum output and the output of running the `assessment1.py` file.

### Example Output
The script ereturns a list of all of the commits in the form (date, inserted lines, removed lines, message). It then provides a summary of the commits, including the number, timespan, mean insertions per commmit and the commit with the greatest net insertions:

```txt
No URL provided - defaulting to https://github.com/jonnyhuck/gitsum

https://github.com/jonnyhuck/gitsum

Timeline:
 2025-09-03 08:51:50 +6    -5    update README output example with active days
 2025-09-03 08:50:54 +5    -1    added active days as well as timespan
 2025-09-02 19:59:18 +19   -16   fix link in README
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
 Total commits:                   18
 Timespan (days):                 32 (3 active)
 Total lines in HEAD:             860
 Mean insertions per commit:      34.39 (std: 45.39)
 Commit with most net insertions: 2025-08-01 14:09:00 +168 (-0)
```

### Dependencies
This script relies on the excellent [`GitPython`](https://github.com/gitpython-developers/GitPython) library.
The `process_course.py` example also uses [pandas](https://pandas.pydata.org/) and [openpyxl](https://openpyxl.readthedocs.io/en/stable/).