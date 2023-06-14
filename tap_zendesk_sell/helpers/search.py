# %%
import requests
from os import environ
from yaml import safe_load
import json

indexes = [
    # "leads",
    "deals",
    # "contacts",
    # "notes",
    # "tasks",
]

for index in indexes:
    url = f"https://api.getbase.com/v3/{index}/schema"
    schema = requests.get(url)
    schema = safe_load(schema.text)
    # schema_attributes = [{"name": key} for key, value in schema["attributes"].items()]
    with open(f"tap_zendesk_sell/schemas/search/{index}.json", "w") as f:
        f.write(json.dumps(schema, indent=4))
schema_attributes = [{"name": key} for key, value in schema["attributes"].items()]
# %%

TOKEN = environ["ACCESS_TOKEN"]
url = "https://api.getbase.com/v3/deals/search"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

data = {
    "items": [{"data": {"per_page": 1000, "query": {"projection": schema_attributes}}}]
}
response = requests.post(url, headers=headers, json=data)
print(response.status_code)

# %% test filter with updated_at field

TOKEN = environ["ACCESS_TOKEN"]
url = "https://api.getbase.com/v3/deals/search"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
filter_dict = (
    {
        "and": [
            {
                "filter": {
                    "attribute": {"name": "updated_at"},
                    "parameter": {"range": {"gte": "2023-05-18T00:00:00Z"}},
                },
            },
        ],
    },
)

data = {
    "items": [
        {
            "data": {
                "per_page": 1000,
                "query": {
                    "projection": schema_attributes,
                    "sort": [
                        {"attribute": {"name": "updated_at"}, "order": "ascending"}
                    ],
                    # "filter": filter_dict,
                },
            }
        }
    ]
}
response = requests.post(url, headers=headers, json=data)
# print(response.status_code)

# %%
deals = []
while True:
    response = requests.post(url, headers=headers, json=data)
    new_data = response.json()
    print(response.status_code)
    print(new_data["items"][0]["items"][0]["data"]["id"])
    deals.extend(new_data["items"][0]["items"])
    # print(response.json())
    if not new_data["items"][0]["meta"]["links"].get("next_page"):
        break
    data["items"][0]["data"]["cursor"] = new_data["items"][0]["meta"]["links"]["next_page"]
# %%
