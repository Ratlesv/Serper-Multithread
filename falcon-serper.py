import requests
import json
import threading
import logging
import time
import argparse
import os
from queue import Queue
from ratelimit import limits, sleep_and_retry

def parse_arguments():
    parser = argparse.ArgumentParser(description="Multi-threaded search query script.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Path to the input file containing search queries.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the output file to save search results.")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of worker threads to use.")
    parser.add_argument("-k", "--apikey", type=str, required=True, help="Google SERP API key.")
    parser.add_argument("-p", "--pages", type=int, default=1, help="Number of pages to search.")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of results per page.")
    
    return parser.parse_args()

args = parse_arguments()
API_KEY = args.apikey
THREAD_COUNT = args.threads
INPUT_FILE = args.input
OUTPUT_FILE = args.output
PAGES = args.pages
NUM_RESULTS = args.num

RATE_LIMIT_CALLS = 60
RATE_LIMIT_PERIOD = 60
total_links = [0]
query_links = {}

@sleep_and_retry
@limits(calls=RATE_LIMIT_CALLS, period=RATE_LIMIT_PERIOD)
def search_request(query, api_key, num=100, page=10):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "page": page,
        "num": num
    })
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}.")
    return response.text

# Rest of the script remains the same

def extract_links(response_text):
    data = json.loads(response_text)
    links = []
    if "organic" in data:
        links = [item["link"] for item in data["organic"]]
    else:
        print(f"No organic results in API response:\n{response_text}")
    return links

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_banner(completed, failed, total, total_links):
    while not all_threads_completed.is_set():
        clear_screen()
        print(f"Processing search queries: {completed[0]}/{total} (Failed: {failed[0]})")
        print(f"Total links saved: {total_links[0]}")
        time.sleep(0.1)


def worker(output_file, num, pages, completed, failed, lock, failed_file):
    while not search_queue.empty():
        query = search_queue.get()
        try:
            result = search_request(query, API_KEY, num=num, page=pages)
            print(f"API response for query '{query}':\n{result}\n")
            links = extract_links(result)
            if not links:
                print(f"No links found for query '{query}'.")
                with lock:
                    failed[0] += 1
                    with open(failed_file, "a", encoding="utf-8") as f:
                        f.write(f"{query}\n")
            else:
                with open(output_file, "a", encoding="utf-8") as file:
                    for link in links:
                        file.write(f"{link}\n")
                with lock:
                    total_links[0] += len(links)
                    query_links[query] = len(links)
                    completed[0] += 1  # Move the completed increment here
                print(f"Links for query '{query}' saved to file.")
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            with lock:
                failed[0] += 1
                with open(failed_file, "a", encoding="utf-8") as f:
                    f.write(f"{query}\n")
        finally:
            search_queue.task_done()

def load_queries_from_file(file_path):
    with open(file_path, "r") as file:
        queries = [line.strip() for line in file.readlines()]
    return queries

def save_top_queries(query_links, output_file):
    sorted_queries = sorted(query_links.items(), key=lambda x: x[1], reverse=True)
    with open(output_file, "w", encoding="utf-8") as file:
        for query, link_count in sorted_queries:
            file.write(f"{query}: {link_count} links\n")

def display_summary(done_queries, failed_queries, unique_queries, total_links):
    print("\nSummary:")
    print(f"Done Queries: {done_queries}")
    print(f"Failed Queries: {failed_queries}")
    print(f"Unique Queries: {unique_queries}")
    print(f"Total Links: {total_links}\n")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

search_queue = Queue()

# Load queries from the file
queries = load_queries_from_file(INPUT_FILE)

# Put queries into the queue
for query in queries:
    search_queue.put(query)

FAILED_FILE = "failed.txt"

# Start the worker threads
threads = []
completed = [0]
failed = [0]
total_queries = len(queries)
lock = threading.Lock()
all_threads_completed = threading.Event()

for _ in range(THREAD_COUNT):
    thread = threading.Thread(target=worker, args=(OUTPUT_FILE, NUM_RESULTS, PAGES, completed, failed, lock, FAILED_FILE))
    thread.start()
    threads.append(thread)

# Start the banner display thread
banner_thread = threading.Thread(target=display_banner, args=(completed, failed, total_queries, total_links))
banner_thread.start()

# Wait for all the threads to finish
for thread in threads:
    thread.join()

all_threads_completed.set()
banner_thread.join()

save_top_queries(query_links, "unique.txt")
display_summary(completed[0], failed[0], len(query_links), total_links[0])
logging.info("All search queries completed.")

