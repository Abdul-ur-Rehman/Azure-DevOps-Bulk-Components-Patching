import os
import requests
import json
import pandas as pd

# Azure DevOps organization and project details
organization = #Write your organization name
project = #Write project name

# Personal Access Token (PAT) for authentication
pat = #provide personal access token here

# ID of the query that returns work item IDs
# query_id = "555db6d9-abae-4336-a021-e99756558281"
query_id = #write query here
# Azure DevOps REST API base URL
base_url = #write your base url here

# Function to get work item IDs from the query
def get_work_item_ids():
    query_url = f"{base_url}/wiql/{query_id}?api-version=6.0"
    response = requests.get(query_url, auth=("", pat))
    data = response.json()
    work_item_ids = [work_item["id"] for work_item in data["workItems"]]
    return work_item_ids


# Function to get work item updates (history)
def get_work_item_updates(work_item_id):
    updates_url = f"{base_url}/workItems/{work_item_id}/updates?api-version=5.1"
    response = requests.get(updates_url, auth=("", pat))
    data = response.json()

    updates_list = data.get("value", [])

    # Iterate through updates_list to find "newValue"
    for update in updates_list:
        # Assuming the nested dictionary has two values and you want the first one
        nested_dict = update.get("fields", {})

        # Retrieve the desired value of the dictionary
        nes_nested_dic = nested_dict.get("Microsoft.VSTS.Common.Component", {})

        # Check if 'newValue' key is present in the dictionary
        new_value = nes_nested_dic.get("newValue")

        # If 'newValue' is found, return it
        if new_value is not None:
            return new_value

    # If 'newValue' is not found, return None
    return None


# Function to update work item using Azure DevOps REST API
def update_work_item(work_item_id, new_component_value):
    update_url = f"{base_url}/workItems/{work_item_id}?api-version=7.1-preview.3&suppressNotifications=true"
    headers = {"Content-Type": "application/json-patch+json"}
    payload = [
        {
            "op": "replace",
            "path": "/fields/Microsoft.VSTS.Common.Component",
            "value": new_component_value
        }
    ]

    response = requests.patch(update_url, json=payload, headers=headers, auth=("", pat))

    if response.status_code == 200:
        print(f"Work Item {work_item_id} updated successfully.")
    else:
        print(f"Failed to update Work Item {work_item_id}. Status Code: {response.status_code}")


# Main function to iterate through work items, store history, and update work items
def main():
    work_item_ids = get_work_item_ids()
    df = pd.DataFrame(columns=["WorkItemID", "OldValue", "NewValue"])

    for work_item_id in work_item_ids:
        print(work_item_id)
        updates = get_work_item_updates(work_item_id)

        # old_value = updates.get('oldValue')
        # new_value = updates.get('newValue')

        # Append data to DataFrame
        # df = df._append({"WorkItemID": work_item_id, "OldValue": old_value, "NewValue": new_value}, ignore_index=True)

        # Update work item with new component value
        if updates:
            update_work_item(work_item_id, updates)

    # Specify the directory
    # directory = "F:/WorkItems"

    # # Create the directory if it doesn't exist
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    #
    # # Save DataFrame to Excel file
    # df.to_excel(os.path.join(directory, "work_item_history_and_updates.xlsx"), index=False)


if __name__ == "__main__":
    main()
