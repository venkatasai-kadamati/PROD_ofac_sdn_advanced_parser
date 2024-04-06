import csv
from lxml import etree

# Define the namespace
ns = {"ns": "http://www.un.org/sanctions/1.0"}

# Load the XML file
tree = etree.parse("sdn_advanced.xml")
root = tree.getroot()


# Function to recursively extract information from elements
def extract_info(element, path=""):
    info = {}
    # Update path with current element
    if path:
        path += f"/{element.tag.replace('{http://www.un.org/sanctions/1.0}', '')}"
    else:
        path = element.tag.replace("{http://www.un.org/sanctions/1.0}", "")

    # Add element's text if it has one
    if element.text and element.text.strip():
        info[path] = element.text.strip()

    # Add attributes
    for attr, value in element.items():
        info[f"{path}@{attr}"] = value

    # Recursively extract information from children
    for child in element:
        child_info = extract_info(child, path)
        for key, value in child_info.items():
            # Handle multiple occurrences of the same path
            if key in info:
                if isinstance(info[key], list):
                    info[key].append(value)
                else:
                    info[key] = [info[key], value]
            else:
                info[key] = value
    return info


# Extract information for all DistinctParty elements
distinct_parties_info = [
    extract_info(dp) for dp in root.findall(".//ns:DistinctParty", namespaces=ns)
]

# Determine unique headers
headers = set()
for party_info in distinct_parties_info:
    headers.update(party_info.keys())
headers = list(headers)

# Write to CSV
with open("dp_report_v1.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    for party_info in distinct_parties_info:
        # Flatten lists into strings
        for key, value in party_info.items():
            if isinstance(value, list):
                party_info[key] = "; ".join(
                    [
                        (
                            ", ".join(map(str, item))
                            if isinstance(item, list)
                            else str(item)
                        )
                        for item in value
                    ]
                )

        writer.writerow(party_info)
