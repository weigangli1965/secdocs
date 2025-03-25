import os
import json
import sys
import argparse
from dotenv import load_dotenv
import anthropic
from json_repair import repair_json

# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--cases-dir", default="../summarize_cases/summarize_case_output/", help="Path to directory with case JSON files")
parser.add_argument("--cached-customer", action="store_true", help="Use cached customer data")
parser.add_argument("--cached-allocation", action="store_true", help="Use cached allocation data")
parser.add_argument("--cached-transactions", action="store_true", help="Use cached transactions data")
parser.add_argument("--casefile", help="Single case file to process (overrides directory read)")
parser.add_argument("--plaintiff-index", help="Single plaintiff index to process (overrides all plaintiffs)", type=int)
parser.add_argument("--save-adjudication", action="store_true", help="Save adjudication response to file")
parser.add_argument("--skip-if-exists", action="store_true", help="Skip processing if output directory exists")

args = parser.parse_args()

CASES_DIR = args.cases_dir

# Cleaning: Sometimes Claude or GPT will return this random json format
def clean_and_load_json(s):
    content_with_removed_backticks = s.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    repaired_json_string = repair_json(content_with_removed_backticks)
    return json.loads(repaired_json_string)

def case_number_from_file_path(file_path):
    basename = os.path.basename(file_path)
    return basename.removesuffix('.json')  

def get_case_data(casefile):
    cases_map = {}

    # KEY IS FULL PATH
    # If a single casefile is specified, load only that
    if casefile:
        filepaths = [casefile]
    else:
        filepath_ends = os.listdir(CASES_DIR)
        filepaths = [os.path.join(CASES_DIR, filepath) for filepath in filepath_ends]

    print(filepaths)

    # Otherwise, read from the specified directory
    for filepath in filepaths:
        if filepath.endswith(".json"):
            with open(filepath, "r") as file:
                print("READING FILENAME:", filepath)
                data_string = file.read()
                try:
                    data = clean_and_load_json(data_string)
                    case_number = case_number_from_file_path(filepath) 
                    cases_map[case_number] = data
                    print("CASE NAME:", case_number)   
                except Exception as e:
                    print(f"File {filepath} has error decoding JSON : {e}. SKIPPING.")
                    continue

    return cases_map

# Load environment variables from .env file

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")

anthropic_client = anthropic.Anthropic(api_key=API_KEY)


PROMPTS_DIR = "./synthesize_prompts"
def load_prompts():
    prompts_map = {}
    # Read and process each JSON file in the directory
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

def fake_send_anthropic_message(messages, user_message, anthropic_response, system_message=""):
    new_user_message_record = {"role": "user", "content": user_message}

    messages.append(new_user_message_record)
    new_assistant_message_record =  {"role": "assistant", "content": anthropic_response}
    messages.append(new_assistant_message_record)
    return messages[-1]['content'] # convenience


def select_relevant_keys(plaintiff_record):
    relevant_keys = [
    "Demographics", 
    "InvestmentType",
    "Account Information"
    "FinancialLossSuffered"
    ]

    filtered_record = {key: plaintiff_record[key] for key in relevant_keys if key in plaintiff_record }
    return filtered_record


def prepare_system_message():
    return (
        "You are a financial assistant. "
        "Your task is to help users synthesize transactions from their bank statements. "
        "Please provide a summary of the transactions in a structured format."
    )



def nice_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def process_plaintiff(plaintiff_record, plaintiff_index, plaintiff_filename_prefix):
    

    nice_mkdir("./synthesize_output")
    nice_mkdir(f"./synthesize_output/{plaintiff_filename_prefix}")
    nice_mkdir(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}")
    
    plaintiff_record_cleaned = select_relevant_keys(plaintiff_record)
    if not plaintiff_record_cleaned:
        return # skip any empty records 
    
    messages = []
    prompts = load_prompts()

#   == Customer prompt ==
    customer_prompt = prompts['customer.txt']
    customer_prompt= customer_prompt.replace("{CASE_DATA}", json.dumps(plaintiff_record_cleaned))
    if not args.cached_customer:
        print("No customer caching")
        customer_response = send_anthropic_message(messages, customer_prompt)
        with open(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}/customer_response.txt", "w") as f:
            f.write(customer_response)
        print("** Customer Response: ", customer_response)
    else:
        with open(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}/customer_response.txt", "r") as f:
            customer_response = f.read()
        fake_send_anthropic_message(messages, customer_prompt, customer_response)

        print("** Using cached Customer Response: ", customer_response)

#   == Allocation prompt ==


    allocation_prompt = prompts['allocation.txt']
    if not args.cached_allocation:
        print("No allocation caching")
        allocation_response = send_anthropic_message(messages, allocation_prompt)
        with open(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}/allocation_response.txt", "w") as f:
            f.write(allocation_response)
        print("** Allocation Response: ", allocation_response)

    else:
        with open(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}/allocation_response.txt", "r") as f:
            allocation_response = f.read()
        fake_send_anthropic_message(messages, allocation_prompt, allocation_response)
        print("** Using cached Allocation Response: ", allocation_response)

#   == Transactions prompt ==

    transactions_prompt = prompts['transactions.txt']
    transactions_response = send_anthropic_message(messages, transactions_prompt)
        
    if not args.cached_transactions:
        print("No transactions caching")

        with open(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}/transactions_response.txt", "w") as f:
            f.write(transactions_response)
        print("** Transactions Response: ", transactions_response)
    else:
        with open(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}/transactions_response.txt", "r") as f:
            transactions_response = f.read()
        fake_send_anthropic_message(messages, transactions_prompt, transactions_response)
        print("** Using cached Transactions Response: ", transactions_response)

#   == Adjudication prompt ==
    adjudication_prompt = prompts['adjudication.txt']
    adjudication_prompt = adjudication_prompt.replace("{CUSTOMER}", customer_response)
    adjudication_prompt = adjudication_prompt.replace("{ALLOCATION}", allocation_response)
    adjudication_prompt = adjudication_prompt.replace("{TRANSACTIONS}", transactions_response)

    adjudication_response = send_anthropic_message(messages, adjudication_prompt)
    print("** Adjudication Response: ", adjudication_response)

    if args.save_adjudication:
        print ("** Saving Adjudication Response")
        with open(f"./synthesize_output/{plaintiff_filename_prefix}/{plaintiff_index}/adjudication_response.txt", "w") as f:
            f.write(adjudication_response)



def main():
    case_data = get_case_data(args.casefile)
    
    for plaintiff_filename in case_data.keys():
        plaintiff_filename_prefix = plaintiff_filename.replace('.json', '')
        if args.skip_if_exists and os.path.exists(f"./synthesize_output/{plaintiff_filename_prefix}"):
            print(f"Skipping existing plaintiff ./synthesize_output/{plaintiff_filename_prefix}")
            continue
        if args.plaintiff_index is not None:
            process_plaintiff(case_data[plaintiff_filename]['Customers'][args.plaintiff_index], args.plaintiff_index, plaintiff_filename_prefix)
        else:
            for plaintiff_index, plaintiff_record in enumerate(case_data[plaintiff_filename]['Customers']):
                print(f"Processing plaintiff {plaintiff_index} for {plaintiff_filename_prefix}")
                process_plaintiff(plaintiff_record, plaintiff_index, plaintiff_filename_prefix)

if __name__ == "__main__":
    main()

