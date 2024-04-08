import csv
from lxml import etree

# Define the namespace
ns = {"ns": "http://www.un.org/sanctions/1.0"}

# Load the XML file
tree = etree.parse("sdn_advanced.xml")
root = tree.getroot()

# Initialize containers for each entity type
distinct_parties = []
aliases = []


# Function to recursively extract information from elements
def extract_info(element, parent_ref=None):
    if element.tag == f"{{{ns['ns']}}}DistinctParty":
        distinct_party = {
            "FixedRef": element.get("FixedRef"),
            "PartySubTypeID": element.get("PartySubTypeID"),  # Extract PartySubTypeID
        }
        distinct_parties.append(distinct_party)
        parent_ref = distinct_party["FixedRef"]

    for child in element:
        tag = child.tag.replace(f"{{{ns['ns']}}}", "")
        if tag == "Alias":
            alias = {
                "FixedRef": child.get("FixedRef"),
                "AliasTypeID": child.get("AliasTypeID"),
                "Primary": child.get("Primary"),
                "LowQuality": child.get("LowQuality"),
                "ParentRef": parent_ref,
                "PartySubTypeID": distinct_party[
                    "PartySubTypeID"
                ],  # Include PartySubTypeID in alias
            }
            for documented_name in child.findall(f"{{{ns['ns']}}}DocumentedName"):
                alias["DocumentedNameID"] = documented_name.get("ID")
                alias["DocNameStatusID"] = documented_name.get("DocNameStatusID")  # New
                for name_part in documented_name.findall(
                    f"{{{ns['ns']}}}DocumentedNamePart"
                ):
                    for name_value in name_part.findall(f"{{{ns['ns']}}}NamePartValue"):
                        alias["NamePartValue"] = name_value.text
                        alias["NamePartGroupID"] = name_value.get("NamePartGroupID")
                        alias["ScriptID"] = name_value.get("ScriptID")  # New
                        alias["Acronym"] = name_value.get("Acronym")  # New

            aliases.append(alias)
        # ... rest of the code to handle other tags

        extract_info(child, parent_ref)  # Continue recursion without PartySubTypeID


# Extract information for all DistinctParty elements
for dp in root.findall(".//ns:DistinctParty", namespaces=ns):
    extract_info(dp)


# Function to write entities to CSV
def write_to_csv(data, filename, fieldnames):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# Write each entity type to its own CSV file
write_to_csv(distinct_parties, "distinct_parties.csv", ["FixedRef", "PartySubTypeID"])
write_to_csv(
    aliases,
    "aliases.csv",
    [
        "FixedRef",
        "AliasTypeID",
        "Primary",
        "LowQuality",
        "ParentRef",
        "DocumentedNameID",
        "NamePartValue",
        "NamePartGroupID",
        "DocNameStatusID",  # New
        "ScriptID",  # New
        "Acronym",  # New
    ],
)
