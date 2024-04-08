from lxml import etree
import csv

# Define the namespace
ns = {"ns": "http://www.un.org/sanctions/1.0"}

# Parse the XML file
tree = etree.parse("sdn_advanced.xml")
root = tree.getroot()
# Open a CSV file for writing
with open(
    "generated_csv/locations_output.csv", "w", newline="", encoding="utf-8"
) as csvfile:
    csvwriter = csv.writer(csvfile)

    # Write the header
    csvwriter.writerow(
        [
            "ID",
            "AreaCodeID",
            "CountryID",
            "CountryRelevanceID",
            "Values",
            "FeatureVersionID",
        ]
    )

    # Iterate over each 'Location' element
    for location in root.xpath("//ns:Locations/ns:Location", namespaces=ns):
        location_id = location.get("ID")
        area_code_id = (
            location.find("ns:LocationAreaCode", namespaces=ns).get("AreaCodeID")
            if location.find("ns:LocationAreaCode", namespaces=ns) is not None
            else "N/A"
        )
        country_id = (
            location.find("ns:LocationCountry", namespaces=ns).get("CountryID")
            if location.find("ns:LocationCountry", namespaces=ns) is not None
            else "N/A"
        )
        country_relevance_id = (
            location.find("ns:LocationCountry", namespaces=ns).get("CountryRelevanceID")
            if location.find("ns:LocationCountry", namespaces=ns) is not None
            else "N/A"
        )
        feature_version_id = (
            location.find("ns:FeatureVersionReference", namespaces=ns).get(
                "FeatureVersionID"
            )
            if location.find("ns:FeatureVersionReference", namespaces=ns) is not None
            else "N/A"
        )

        # Correctly concatenate all 'LocationPart' values for the current 'Location'
        values = ", ".join(
            [
                loc_part.find("ns:LocationPartValue/ns:Value", namespaces=ns).text
                for loc_part in location.findall("ns:LocationPart", namespaces=ns)
                if loc_part.find("ns:LocationPartValue/ns:Value", namespaces=ns)
                is not None
            ]
        )

        # Write the data to the CSV file
        csvwriter.writerow(
            [
                location_id,
                area_code_id,
                country_id,
                country_relevance_id,
                values,
                feature_version_id,
            ]
        )
