# Scripts


## synthesize_transactions/

- Put Claude-generated case summaries in ../case_summaries (default) 
- set ANTHROPIC_API_KEY in environment
- From scripts directory, python synthesize_transactions.py
- From this directory, python synthesize_transactions.py will create:
  - synthesize_output/<CASE NAME>
  - synthesize_output/<CASE NAME>/<PLAINTIFF INDEX>
    - customer_response.txt # faked customer profile
    - allocation_response.txt # faked customer allocations
    - transactions_response.txt # faked transactions
    - adjudication_response.txt # adjudication to 24015-l ii.2../
- Prompts are in synthesize_prompts

Arguments to python
```
parser.add_argument("--cases-dir", default="../cases_summaries", help="Path to directory with case JSON files")
parser.add_argument("--cached-customer", action="store_true", help="Use cached customer data")
parser.add_argument("--cached-allocation", action="store_true", help="Use cached allocation data")
parser.add_argument("--cached-transactions", action="store_true", help="Use cached transactions data")
parser.add_argument("--casefile", help="Single case file to process (overrides directory read)")
parser.add_argument("--plaintiff-index", help="Single plaintiff index to process (overrides all plaintiffs)", type=int)
parser.add_argument("--save-adjudication", action="store_true", help="Save adjudication response to file")
```


## Cases Retrieval

- Source: https://www.finra.org/rules-guidance/key-topics/regulation-best-interest#enforcement
- Retrieval: ./retrieve-cases.sh
- PDF destination: ./casespdfs/{case-number}
- Txt destination: ./casestxt/{case-number}
- Summaries from Claude: ./cases_summaries/{case-number}


