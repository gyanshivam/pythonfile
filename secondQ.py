import csv
import requests
from requests.auth import HTTPBasicAuth
from time import sleep

# CrateJoy API details
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
BASE_URL = 'https://api.cratejoy.com/v1/'

# Function to cancel subscription on CrateJoy
def cancel_subscription(subscription_id):
    url = f'{BASE_URL}subscriptions/{subscription_id}/cancel/'
    headers = {'Content-Type': 'application/json'}
    auth = HTTPBasicAuth(API_KEY, API_SECRET)

    try:
        response = requests.post(url, headers=headers, auth=auth)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}, 500

# Function to handle API requests for each subscription ID
def process_subscription(subscription_id):
    # Check for blank cell
    if not subscription_id:
        return {'error': 'Subscription ID is blank'}, 400

    # Make API request to cancel subscription
    response_json, response_code = cancel_subscription(subscription_id)

    # Check for rate limiting
    if response_code == 429:
        # Retry after waiting for the specified time
        retry_after = int(response.headers.get('Retry-After', 10))
        sleep(retry_after)
        response_json, response_code = cancel_subscription(subscription_id)

    return response_json, response_code

# Main function to read CSV, make API requests, and store results in a new CSV
def main(input_csv_path, output_csv_path):
    with open(input_csv_path, 'r') as input_file, open(output_csv_path, 'w', newline='') as output_file:
        reader = csv.DictReader(input_file)
        fieldnames = ['platform_subscription_id', 'response_json', 'response_code']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            subscription_id = row.get('platform_subscription_id')
            response_json, response_code = process_subscription(subscription_id)

            # Write results to output CSV
            writer.writerow({
                'platform_subscription_id': subscription_id,
                'response_json': str(response_json),
                'response_code': response_code
            })

if __name__ == '__main__':
    input_csv_path = 'input.csv'  # Replace with your input CSV file path
    output_csv_path = 'output.csv'  # Replace with your output CSV file path
    main(input_csv_path, output_csv_path)
