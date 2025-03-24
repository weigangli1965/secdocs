# summarize_cases

- Generally, ../../casestxts/* -> ./summarize_case_output.

```

parser.add_argument("--cases-dir", default="../../casestxts/", help="Path to directory with case txt files")
parser.add_argument("--casefile", help="Single case file to summarize (overrides directory read)")
parser.add_argument("--save-output", action="store_true", help="Save summarizeed response to file")
parser.add_argument("--sleep", default="0", help="Sleep time between requests (in seconds) to avoid rate limiting")
```
