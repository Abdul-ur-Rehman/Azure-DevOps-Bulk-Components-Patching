import requests
import json
import pandas as pd

# Azure DevOps organization and project details
organization = "astera"
project = "Centerprise"

# Personal Access Token (PAT) for authentication
pat = "cmnds7rklampik25zp6xke7brl5xpm2qzufbaa2spoo2nlqschra"

# ID of the query that returns work item IDs
query_id = "0da36394-a79f-4a75-a4fe-7b18561f3cc4"

# Azure DevOps REST API base URL
base_url = f"https://dev.azure.com/{organization}/{project}/_apis/wit"


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

    if updates_list:
        # Assuming the last dictionary has a key containing another nested dictionary
        last_dict = updates_list[-1]

        # Assuming the last nested dictionary has two values and you want the first one
        nested_dict = last_dict.get("fields", {})

        # Retrieve the desired value of the dictionary
        nes_nested_dic = nested_dict.get("Microsoft.VSTS.Common.Component", {})

        # Return the dictionary
        return nes_nested_dic

    return {}


# Main function to iterate through work items and store history
def main():
    work_item_ids = get_work_item_ids()
    df = pd.DataFrame(columns=["WorkItemID", "OldValue", "NewValue"])

    for work_item_id in work_item_ids:
        print(work_item_id)
        updates = get_work_item_updates(work_item_id)

        old_value = updates['oldValue']
        new_value = updates['newValue']

        # print(f"Old Value: {old_value}")
        # print(f"New Value: {new_value}")

        # Append data to DataFrame
        df = df._append({"WorkItemID": work_item_id, "OldValue": old_value, "NewValue": new_value}, ignore_index=True)

        # Save DataFrame to Excel file
    df.to_excel("F:/WorkItems/work_item_history_pycharm_last.xlsx", index=False)


if __name__ == "__main__":
    main()
