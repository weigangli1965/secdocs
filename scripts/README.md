# Scripts


## summarize_cases

- Put Claude-generated case summaries in ../casestxts (default)
- set ANTHROPIC_API_KEY in environment
- From scripts directory, python synthesize_transactions.py
- From this directory, python summarize_cases.py will create:
  - summarize_cases_output/<CASE NAME>
- Prompts are in summarize_cases/prompts

Arguments to python
```
parser.add_argument("--cases-dir", default="../../casestxts/", help="Path to directory with case txt files")
parser.add_argument("--casefile", help="Single case file to summarize (overrides directory read)")
parser.add_argument("--save-output", action="store_true", help="Save summarizeed response to file")
parser.add_argument("--sleep", default="0", help="Sleep time between requests (in seconds) to avoid rate limiting")
```



## synthesize_transactions/

- Put Claude-generated case summaries in ../cases_summaries (default) 
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


Claude Destkop is required for cases retrieval.  The other scripts can be run from the terminal.

### Claude Desktop (Mac Only)

- Download Claude Desktop.
- Edit claude_desktop_config: Claude->Settings->Developer->Edit Config.
```
{
  "mcpServers": {
    "brave-search": {
      "command":"/Users/fettermania/.nvm/versions/node/v22.14.0/bin/npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": "YOUR_KEY_HERE"
      }
    },
    "github": {
      "command":"/Users/fettermania/.nvm/versions/node/v22.14.0/bin/npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_KEY_HERE"
      }
    },
   "sequential-thinking": {
      "command":"/Users/fettermania/.nvm/versions/node/v22.14.0/bin/npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
  "fetch": {
    "command": "uvx",
    "args": ["mcp-server-fetch", "--ignore-robots-txt"]
  },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/fettermania/Desktop/claude"
      ]
    }
  }
  ```
- Note: Lines should be your own installations destinations of node.
- Note: Only two required ones are 'fetch' and 'filesystem'.
- Fetch extension config:
  - Instructions: https://4sysops.com/archives/install-mcp-server-fetch-for-claude-ai-on-mac-and-windows/
- Filesystem extension config:
  - Instructions: https://mcp.so/server/filesystem
  - Note: The last line of the 'filesystem' config is a location on your machine that Claude is allowed to access.  Work from there.

### Claude Desktop (Windows)

  - The whole idea should work on Windows too but the configuration and downloads are different.  I don't have a windows machine.  Instructions of the extensions (MCP Servers) at the MCP websites also typically include a Windows version.

### Claude prompts

  - In prompts directory.  Update to your file path.
