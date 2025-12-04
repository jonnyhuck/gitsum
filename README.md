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
created tmp directory: /var/folders/9_/7s25zcsn2jjc8gr0k6k6fqnw0000gn/T/tmpf9zqdwfu
883

https://github.com/jonnyhuck/gitsum

Timeline:
 2025-12-01 16:50:03 f2594fc +26   -12   (14) updates following use in marking assessment
 2025-11-21 16:02:25 3de5339 +19   -2    (17) add script pre-processing for student submissions
 2025-11-14 19:18:25 c123ee0 +205  -82   (123) added course processing
 2025-10-08 16:16:47 9b36c07 +3    -1    (2)  add unedited lines estimate
 2025-09-12 15:19:31 9fc5724 +11   -8    (3)  changed nested string literals to single quotes for stability
 2025-09-03 08:51:50 9b8527a +6    -5    (1)  update README output example with active days
 2025-09-03 08:50:54 f8c447c +5    -1    (4)  added active days as well as timespan
 2025-09-02 19:59:18 9bc554c +19   -16   (3)  fix link in README
 2025-09-02 19:57:37 51525d3 +92   -75   (17) add total lines count and fix tmp directory not deleting
 2025-09-02 19:28:01 083679a +61   -10   (51) add commit messages to the log output and update README
 2025-09-02 17:02:39 72afed4 +1    -4    (-3) remove outdated references to dulwich
 2025-09-02 17:01:58 fd04002 +3    -2    (1)  fix comments
 2025-09-02 16:59:39 9910490 +82   -52   (30) avoid cloning for local repos
 2025-09-02 16:31:59 38e0159 +73   -208  (-135) replace dulwich with gitpython
 2025-09-02 15:00:14 70ce948 +8    -8    (0)  uncomment report
 2025-09-02 14:52:22 24af795 +46   -25   (21) update for more detailed report
 2025-08-01 16:08:21 a6aa7c7 +1    -1    (0)  fix link
 2025-08-01 16:07:28 0f9f448 +3    -0    (3)  added note on porcelain
 2025-08-01 14:31:52 1c8f96c +3    -4    (-1) updated deprecated function
 2025-08-01 14:09:00 3efac42 +18   -8    (10) add timespan reporting
 2025-08-01 14:09:00 094e981 +30   -16   (14) initial commit
 2025-08-01 14:09:00 b440520 +168  -0    (168) initial commit
 2025-08-01 14:05:02 c5012f4 +0    -0    (0)  Initial commit

Summary:
 Total commits:                   23
 Timespan (days):                 123 (8 active)
 Total lines in HEAD:             1027
 Estimated unedited lines:        1170
 Mean insertions per commit:      38.39 (std: 54.61)
 Commit with most net insertions: 2025-08-01 14:09:00 +168 -0 (168)
```

### Dependencies
This script relies on the excellent [`GitPython`](https://github.com/gitpython-developers/GitPython) library.
The `process_course.py` example also uses [`pandas`](https://pandas.pydata.org/) and [`openpyxl`](https://openpyxl.readthedocs.io/en/stable/).