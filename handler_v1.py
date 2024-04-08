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
features = []
name_part_groups = []  # Container for NamePartGroups


# Function to recursively extract information from elements
def extract_info(element, parent_ref=None, distinct_party_ref=None):
    if element.tag == f"{{{ns['ns']}}}DistinctParty":
        distinct_party = {"FixedRef": element.get("FixedRef")}
        distinct_parties.append(distinct_party)
        parent_ref = distinct_party["FixedRef"]
        distinct_party_ref = distinct_party[
            "FixedRef"
        ]  # Capture the FixedRef for DistinctParty

    for child in element:
        tag = child.tag.replace(f"{{{ns['ns']}}}", "")
        if tag == "Alias":
            alias = {
                "FixedRef": child.get("FixedRef"),
                "AliasTypeID": child.get("AliasTypeID"),
                "Primary": child.get("Primary"),
                "LowQuality": child.get("LowQuality"),
                "ParentRef": parent_ref,
            }
            # Alias parsing logic remains the same
            aliases.append(alias)
        elif tag == "Feature":
            feature = {
                "ID": child.get("ID"),
                "FeatureTypeID": child.get("FeatureTypeID"),
                "ParentRef": parent_ref,
            }
            # Feature parsing logic remains the same
            features.append(feature)
        elif tag == "NamePartGroup":
            name_part_group = {
                "NamePartGroupID": child.get("ID"),
                "NamePartTypeID": child.get("NamePartTypeID"),
                "ParentRef": parent_ref,  # Assuming parent_ref is the reference to the parent Identity
                "DistinctPartyRef": distinct_party_ref,  # Add DistinctPartyRef to NamePartGroup
            }
            name_part_groups.append(name_part_group)

        extract_info(
            child, parent_ref, distinct_party_ref
        )  # Pass distinct_party_ref down the recursion


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
write_to_csv(distinct_parties, "namepartgroup/distinct_parties.csv", ["FixedRef"])
write_to_csv(
    aliases,
    "namepartgroup/aliases.csv",
    ["FixedRef", "AliasTypeID", "Primary", "LowQuality", "ParentRef"],
)
write_to_csv(
    features,
    "namepartgroup/features.csv",
    ["ID", "FeatureTypeID", "ParentRef", "FeatureVersionID", "ReliabilityID"],
)
write_to_csv(
    name_part_groups,
    "namepartgroup/name_part_groups.csv",
    ["NamePartGroupID", "NamePartTypeID", "ParentRef", "DistinctPartyRef"],
)
