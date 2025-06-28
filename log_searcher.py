import os
import datetime
import zlib

from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.query import Every

WHOOSH_INDEX_DIR = 'whoosh_index'
DEFAULT_SEARCH_FIELD = 'message_raw'

def run_log_searcher():
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Starting Log Searcher...")

    if not os.path.exists(WHOOSH_INDEX_DIR):
        print(f"ERROR: Whoosh index directory '{WHOOSH_INDEX_DIR}' not found.")
        print("Please ensure log_processor.py has run successfully to create the index.")
        return

    try:
        ix = open_dir(WHOOSH_INDEX_DIR)
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Successfully opened Whoosh index at '{WHOOSH_INDEX_DIR}'.")
    except Exception as e:
        print(f"ERROR: Could not open Whoosh index: {e}")
        print("Please ensure log_processor.py has run and the index is not corrupted.")
        return

    query_parser = QueryParser(None, ix.schema)

    print("\nEnter your search query. Type 'exit' to quit.")
    print("Examples:")
    print("  - failed login")
    print("  - level:ERROR AND source_ip:203.0.113.1")
    print("  - event_type:FILE_ACCESS OR event_type:AUTH_ATTEMPT")
    print("  - message_raw:\"unauthorized access\"")
    print("  - *passwd*")
    print("  - level:[WARN TO CRITICAL]")

    while True:
        try:
            query_str = input("\nLogSearch > ").strip()
            if query_str.lower() == 'exit':
                break

            if not query_str:
                print("Please enter a query.")
                continue

            if query_str == "*:*":
                query = Every()
            else:
                try:
                    query = query_parser.parse(query_str)
                except Exception as e:
                    print(f"Error parsing query: {e}. Please check syntax.")
                    continue

            with ix.searcher() as searcher:
                results = searcher.search(query, limit=10)

                if not results:
                    print("No results found.")
                else:
                    print(f"Found {len(results)} of {results.scored_length()} total matches (showing top 10):")
                    for hit in results:
                        try:
                            full_log_decompressed = zlib.decompress(hit['full_log_bytes']).decode('utf-8')
                        except Exception as decompress_e:
                            full_log_decompressed = f"[Decompression Error: {decompress_e}]"

                        print("-" * 50)
                        print(f"Timestamp: {hit['timestamp']}")
                        print(f"Level: {hit['level']}")
                        print(f"Event: {hit['event_type']}")
                        print(f"Source IP: {hit['source_ip']}")
                        print(f"Status: {hit['status']}")
                        print(f"Raw Message: {hit['message_raw']}")
                        print(f"FULL LOG: {full_log_decompressed}")
                    print("-" * 50)

        except KeyboardInterrupt:
            print("\nExiting Log Searcher.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_log_searcher()
