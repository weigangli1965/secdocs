# summarize_cases

- Generally, ../../cases_summaries/* -> ./synthesize_output

```
parser.add_argument("--cases-dir", default="../../cases_summaries", help="Path to directory with case JSON files")
parser.add_argument("--cached-customer", action="store_true", help="Use cached customer data")
parser.add_argument("--cached-allocation", action="store_true", help="Use cached allocation data")
parser.add_argument("--cached-transactions", action="store_true", help="Use cached transactions data")
parser.add_argument("--casefile", help="Single case file to process (overrides directory read)")
parser.add_argument("--plaintiff-index", help="Single plaintiff index to process (overrides all plaintiffs)", type=int)
parser.add_argument("--save-adjudication", action="store_true", help="Save adjudication response to file")
```
