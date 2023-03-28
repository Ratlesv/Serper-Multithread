# Serper-Multithread Made With Love By Th3-Gr34T-Falcon

This is a Python script that performs Google search queries using the Google SERP API. The script is multi-threaded and allows you to specify the number of worker threads to use to make the API requests in parallel.

The script takes several arguments as input, such as the path to the input file containing the search queries, the path to the output file to save the search results, the number of pages to search, the number of results per page, and the Google SERP API key.

# The script performs the following steps:

1-Parses the arguments passed to the script

2-Loads the search queries from the input file

3-Creates a queue of search queries

4-Starts a specified number of worker threads to process the search queries in the queue

5-Each worker thread performs the following steps:

6-Makes an API request using the Google SERP API with the search query, number of pages and number of results per page

7-Extracts the links from the API response and saves them to the output file

8-Writes the search query and number of links found to a file that tracks unique queries and their link counts

9-Keeps track of the number of completed and failed search queries

10-After all worker threads have finished processing the search queries, the script saves the top search queries with the most links found to a file

11-The script then displays a summary of the search results, including the number of completed, failed and unique search queries, and the total number of links found.
The script also logs information about the processing of search queries, including the API response and any errors that may have occurred, to a log file.




# To use this script, you need to:

# 1-Install the required Python packages mentioned in the script: 

requests, json, threading, logging, time, argparse, os, and queue. You can install these packages using the pip package manager by running the following command in your terminal/command prompt:


sudo pip install requests json threading logging time argparse os queue

# 2-Create an input file with the search queries you want to perform, one query per line.

# 3-Obtain a Google SERP API key from the Google SERP API website.



# Run the script in your terminal/command prompt, passing the required arguments:

python script_name.py -i input_file.txt -o output_file.txt -k API_KEY -t NUM_THREADS -p NUM_PAGES -n NUM_RESULTS_PER_PAGE
