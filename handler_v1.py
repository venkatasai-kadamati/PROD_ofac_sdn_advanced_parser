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


def extract_info(element, parent_ref=None):
    # Check if the element is a DistinctParty
    if element.tag == f"{{{ns['ns']}}}DistinctParty":
        distinct_party = {
            "FixedRef": element.get("FixedRef"),
            # Initialize PartySubTypeID to None; it will be updated when a Profile is encountered
            "PartySubTypeID": None,
        }
        parent_ref = distinct_party["FixedRef"]

    # Check if the element is a Profile and update the PartySubTypeID
    if element.tag == f"{{{ns['ns']}}}Profile":
        distinct_party["PartySubTypeID"] = element.get("PartySubTypeID")

    # Process Alias elements
    if element.tag == f"{{{ns['ns']}}}Alias":
        alias = {
            "FixedRef": element.get("FixedRef"),
            "AliasTypeID": element.get("AliasTypeID"),
            "Primary": element.get("Primary"),
            "LowQuality": element.get("LowQuality"),
            "ParentRef": parent_ref,
            "PartySubTypeID": distinct_party[
                "PartySubTypeID"
            ],  # Use the updated PartySubTypeID
        }
        # Process DocumentedName elements within Alias
        for documented_name in element.findall(f"{{{ns['ns']}}}DocumentedName"):
            alias["DocumentedNameID"] = documented_name.get("ID")
            alias["DocNameStatusID"] = documented_name.get("DocNameStatusID")
            # Process DocumentedNamePart elements within DocumentedName
            for name_part in documented_name.findall(
                f"{{{ns['ns']}}}DocumentedNamePart"
            ):
                for name_value in name_part.findall(f"{{{ns['ns']}}}NamePartValue"):
                    alias["NamePartValue"] = name_value.text
                    alias["NamePartGroupID"] = name_value.get("NamePartGroupID")
                    alias["ScriptID"] = name_value.get("ScriptID")
                    alias["Acronym"] = name_value.get("Acronym")
        aliases.append(alias)

    # Recursively process child elements
    for child in element:
        extract_info(child, parent_ref)


# Function to write entities to CSV
def write_to_csv(data, filename, fieldnames):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# Write each entity type to its own CSV file
write_to_csv(distinct_parties, "distinct_parties.csv", ["FixedRef", "PartySubTypeID"])

# Define the fieldnames for the aliases CSV, including PartySubTypeID
alias_fieldnames = [
    "FixedRef",
    "AliasTypeID",
    "Primary",
    "LowQuality",
    "ParentRef",
    "DocumentedNameID",
    "NamePartValue",
    "NamePartGroupID",
    "DocNameStatusID",
    "ScriptID",
    "Acronym",
    "PartySubTypeID",  # Include PartySubTypeID in the CSV headers
]

# Write the aliases to their CSV file
write_to_csv(aliases, "aliases.csv", alias_fieldnames)
