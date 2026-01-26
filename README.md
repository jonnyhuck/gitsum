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
created tmp directory: /var/folders/9_/7s25zcsn2jjc8gr0k6k6fqnw0000gn/T/tmpuczmceth

Git Summary:
 Repo:                            https://github.com/jonnyhuck/gitsum
 Total commits:                   32
 Timespan (days):                 175 (14 active)
 Estimated work time (H:M):       1:43
 Total lines in HEAD:             390
 Estimated unedited lines:        0
 Mean lines per minute:           2.25 (std: 7.67)
 Max lines per minute:            42.35
 Mean insertions per commit:      36.44 (std: 49.55)
 Commit with most net insertions: 2025-08-01 14:09:00 b440520 +168 -0 (168)


Timeline:
 2026-01-26 16:32:12 3cc14b5 (0.0  l/min)     +86   -69   (17)   added more info on timing, move summary info to top, make precess_course able to re-run existing repos
 2026-01-23 10:23:15 da392b0 (0.0  l/min)     +1    -1    (0)    fixed bug in misreported largest sha
 2026-01-20 14:15:20 81322e1 (0.3  l/min) !!  +1    -1    (0)    fix bug in timespan
 2026-01-20 14:12:13 5614038 (0.0  l/min)     +23   -16   (7)    bangs and lines/minute now appear on the correct row
 2026-01-19 14:28:47 f14937c (0.0  l/min)     +47   -9    (38)   add coding speed to report
 2026-01-13 17:00:13 fe61d7f (0.0  l/min)     +9    -7    (2)    fix bug where it was not printing the report for local repos
 2025-12-04 13:20:19 7fca720 (0.6  l/min) !!! +1    -2    (-1)   fix formatting of difference and remove print statement
 2025-12-04 13:18:35 6cd5f0e (0.0  l/min)     +24   -9    (15)   first stab at highlighting short gaps between commits
 2025-12-04 11:26:45 0fa70c6 (0.0  l/min)     +91   -56   (35)   tweaks after UGIS A1 including limiting counts to files in root
 2025-12-01 16:50:03 f2594fc (0.0  l/min)     +26   -12   (14)   updates following use in marking assessment
 2025-11-21 16:02:25 3de5339 (0.0  l/min)     +19   -2    (17)   add script pre-processing for student submissions
 2025-11-14 19:18:25 c123ee0 (0.0  l/min)     +205  -82   (123)  added course processing
 2025-10-08 16:16:47 9b36c07 (0.0  l/min)     +3    -1    (2)    add unedited lines estimate
 2025-09-12 15:19:31 9fc5724 (0.0  l/min)     +11   -8    (3)    changed nested string literals to single quotes for stability
 2025-09-03 08:51:50 9b8527a (6.4  l/min) !!! +6    -5    (1)    update README output example with active days
 2025-09-03 08:50:54 f8c447c (0.0  l/min)     +5    -1    (4)    added active days as well as timespan
 2025-09-02 19:59:18 9bc554c (11.3 l/min) !!! +19   -16   (3)    fix link in README
 2025-09-02 19:57:37 51525d3 (3.1  l/min)     +92   -75   (17)   add total lines count and fix tmp directory not deleting
 2025-09-02 19:28:01 083679a (0.0  l/min)     +61   -10   (51)   add commit messages to the log output and update README
 2025-09-02 17:02:39 72afed4 (1.5  l/min) !!! +1    -4    (-3)   remove outdated references to dulwich
 2025-09-02 17:01:58 fd04002 (1.3  l/min) !!  +3    -2    (1)    fix comments
 2025-09-02 16:59:39 9910490 (3.0  l/min)     +82   -52   (30)   avoid cloning for local repos
 2025-09-02 16:31:59 38e0159 (0.0  l/min)     +73   -208  (-135) replace dulwich with gitpython
 2025-09-02 15:00:14 70ce948 (1.0  l/min) !   +8    -8    (0)    uncomment report
 2025-09-02 14:52:22 24af795 (0.0  l/min)     +46   -25   (21)   update for more detailed report
 2025-08-01 16:08:21 a6aa7c7 (1.1  l/min) !!! +1    -1    (0)    fix link
 2025-08-01 16:07:28 0f9f448 (0.0  l/min)     +3    -0    (3)    added note on porcelain
 2025-08-01 14:31:52 1c8f96c (0.1  l/min)     +3    -4    (-1)   updated deprecated function
 2025-08-01 14:09:00 3efac42 (0.0  l/min)     +18   -8    (10)   add timespan reporting
 2025-08-01 14:09:00 094e981 (0.0  l/min)     +30   -16   (14)   initial commit
 2025-08-01 14:09:00 b440520 (42.4 l/min) !!  +168  -0    (168)  initial commit
 2025-08-01 14:05:02 c5012f4 (0.0  l/min)     +0    -0    (0)    Initial commit
```

The timeline is formatted as: 
`<datatime> <sha> (<coding speed>) <flags> +<inserts> -<deletions> (<net change>) <message>`
`!!!` flags commits within 2 mins of the previous, `!!` within 5 mins, and `!` within 10 mins.

### Dependencies
This script relies on the excellent [`GitPython`](https://github.com/gitpython-developers/GitPython) library.
The `process_course.py` example also uses [`pandas`](https://pandas.pydata.org/) and [`openpyxl`](https://openpyxl.readthedocs.io/en/stable/).