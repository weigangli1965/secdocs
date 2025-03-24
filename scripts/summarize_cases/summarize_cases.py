import os
import argparse
import anthropic
import time

# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--cases-dir", default="../../casestxts/", help="Path to directory with case txt files")
parser.add_argument("--casefile", help="Single case file to summarize (overrides directory read)")
parser.add_argument("--save-output", action="store_true", help="Save summarizeed response to file")
parser.add_argument("--sleep", default="0", help="Sleep time between requests (in seconds) to avoid rate limiting")

args = parser.parse_args()

CASES_DIR = args.cases_dir

# Load environment variables from .env file

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")

anthropic_client = anthropic.Anthropic(api_key=API_KEY)

PROMPTS_DIR = "./prompts"

def nice_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def get_case_text_data(casefile):
    cases_map = {}

    # If a single casefile is specified, load only that
    if casefile:
        with open(casefile, "r") as file:
            data = file.read()
        print("READING FILE:", casefile)
        case_name = os.path.basename(casefile)[:-4]    # Drop .txt
        cases_map[case_name] = data
        return cases_map

    files = os.listdir(CASES_DIR)
    files.sort()

    # Otherwise, read from the specified directory
    for filename in files:
        if filename.endswith(".txt"):
            filepath = os.path.join(CASES_DIR, filename)
            with open(filepath, "r") as file:
                data = file.read()
            print("READING FILENAME:", filename)
            case_name = filename[:-4]    # Drop .txt
            print("CASE NAME:", case_name)
            cases_map[case_name] = data

    return cases_map


def load_prompts():
    prompts_map = {}
    # Read and summarize each txt file in the directory
    for filename in os.listdir(PROMPTS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(PROMPTS_DIR, filename)
            with open(filepath, "r") as file:
                data = file.read()

            prompts_map[filename] = data
    return prompts_map


# Stateful (gross)
def send_anthropic_message(messages, user_message, system_message="", max_tokens=4096):
    new_user_message_record = {"role": "user", "content": user_message}

    messages.append(new_user_message_record)

    print ("Sending message to Anthropic: ...")    
    response = anthropic_client.messages.create(
        model="claude-3-7-sonnet-20250219",
        system=system_message,
        max_tokens=max_tokens,
        messages=messages)

    new_assistant_message_record =  {"role": "assistant", "content": response.content[0].text}
    messages.append(new_assistant_message_record)
    return messages[-1]['content'] # convenience


def summarize_case(case_raw_text, case_filename):
    print (f"SUMARRIZING {case_filename}: ", case_raw_text)

    nice_mkdir("./summarize_case_output")
    
    messages = []
    prompts = load_prompts()

#   == Case Summary prompt ==
    summarize_case_prompt = prompts['summarize_case_teddy.txt']
    summarize_case_prompt = summarize_case_prompt.replace("{CASE}", case_raw_text)
    summarize_case_response = send_anthropic_message(messages, summarize_case_prompt)
    print("** Process Case Response: ", summarize_case_response)

    if args.save_output:
        print ("** Saving Process Case Response")
        with open(f"./summarize_case_output/{case_filename}", "w") as f:
            f.write(summarize_case_response)

def main():
    case_data = get_case_text_data(args.casefile)

    case_names = list(case_data.keys())
    case_names.sort()
    for case_name in case_names:
        summarize_case(case_data[case_name], case_name)
        if args.sleep != "0":
            print(f"Sleeping for {args.sleep} seconds to avoid rate limiting...")
            time.sleep(int(args.sleep))

if __name__ == "__main__":
    main()

