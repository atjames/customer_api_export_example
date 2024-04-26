import requests
from api_tokens import API_TOKEN
from datetime import datetime
import time
import csv

# Function to filter downloaded CSV rows and write to a new CSV file
def filter_and_write_csv(input_csv, output_csv):
    # Open the input CSV file for reading
    with open(input_csv, "r", newline="") as input_file:
        reader = csv.DictReader(input_file)
        
        # Create a list to hold the filtered rows
        filtered_rows = []
        
        # Iterate over each row
        for row in reader:
            # Check if the row matches the criteria. We are matching on Tag event types where the tag name is "Bug" and an Account Name exists
            if row["Type"] == "tag" and "Bug" in row["Tags"] and  row["Account names"] != "":
                # Add the row to the filtered rows list if the row meets our criteria 
                filtered_rows.append(row)

    # Open the output CSV file for writing
    with open(output_csv, "w", newline="") as output_file:
        # Write the headers to the output CSV file
        writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        # Write the filtered rows to the output CSV file
        writer.writerows(filtered_rows)

url = "https://api2.frontapp.com/analytics/exports"

# Convert start and end dates to Unix timestamps
# Change these dates to what you require and feel free to use the actual Unix timestampes in the request rather than a conversation as I did here
start_date = datetime.strptime("2023-01-01T00:00:00+00", "%Y-%m-%dT%H:%M:%S+00").timestamp() 
end_date = datetime.strptime("2024-01-01T00:00:00+00", "%Y-%m-%dT%H:%M:%S+00").timestamp()

payload = {
    "columns": ["Activity ID", "Segment", "Segment start", "Segment end", "Type", "Tags", "Contact name", "Contact handle", "Account names"],
    "type": "events",
    "filters": { "tag_ids": ["tag_37lxsi"] },
    "start": start_date,
    "end": end_date
}

# API Token is imported  from my persoanl config file. You'll need to update this to use your own API token.
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "accept": "application/json",
    "content-type": "application/json"
}


response = requests.post(url, json=payload, headers=headers)

if response.status_code != 201:
    print("Failed to initiate export:", response.text)
    exit()

export_id = response.json().get("_links").get("self").split("/")[-1]

# Loops and issues a GET request until progress is at 100%. Might need to add additional checks to ensure the export hasn't timed out. 
# I would suggest only looping a total of 20-30 times (rather than endlessly) to avoid a never-ending request loop. But to save time,  this example will do to show as an example.
while True:
    print("Issuing GET request for Export...")
    get_response = requests.get(f"{url}/{export_id}", headers=headers)
    progress = get_response.json().get("progress")
    #Fails if the GET request returns anything other than a 200 response
    if get_response.status_code != 200:
        print("Failed to retrieve progress:", response.text)
        exit()
    print(f"Progress at {progress}...")
    if progress == 100:
        print("Progress at 100! Downloading CSV")
        export_url = get_response.json().get("url")
        break
    time.sleep(10)  

# Download the exported CSV file
csv_response = requests.get(export_url)

# Print the CSV content to a file so we can use it in our function call
with open("exported_data.csv", "wb") as file:
    file.write(csv_response.content)
    print("CSV content printed to file 'exported_data.csv'")

output_csv = "filtered_data.csv"

#call funtion to perform filtering
filter_and_write_csv("exported_data.csv", output_csv)
