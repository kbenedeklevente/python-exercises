import argparse
import requests

import urllib.error

from collections import defaultdict

def fetch_github_activity_with_requests(url):
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print("User doesn't exist.")
            return None
        elif response.status_code == 200:
            return response
        else:
            print(f"Unexpected status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occured {e}")
        return None


def format_github_json(response):
    if response == None:
        return
    activity_summary = defaultdict(lambda: defaultdict(int))

    for activity in response.json():
        repo_name = activity['repo']['name']
        activity_type = activity['type']
        activity_summary[repo_name][activity_type] += 1

    for repo in activity_summary:
        print("Repository: " + repo)
        for activity_type, count in activity_summary[repo].items():
            print(f"    {activity_type}: {count}")

def __main__():
    parser = argparse.ArgumentParser("CLI for github user activity.")
    parser.add_argument('name', type=str, help="Github username")

    while True:
        command = input("github-activity ").strip()
        if command.lower() == "quit":
            break

        args = parser.parse_args(command.split())
        API_endpoint = f"https://api.github.com/users/{args.name}/events"

        response = fetch_github_activity_with_requests(API_endpoint)
        format_github_json(response)

if __name__ == "__main__":
    __main__()