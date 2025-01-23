import re

# Define the regex for UK postcodes
postcode_regex = re.compile(
    r"^(GIR 0AA|[A-Z]{1,2}[0-9R][0-9A-Z]? ?[0-9][A-Z]{2})$"
)

# Test postcodes
postcodes = [
    "M1 1AA", "M60 1NW", "CR2 6XH", "DN55 1PT", "W1A 1HQ", "EC1A 1BB", "ST7 9HV"
]

# Validate postcodes
for postcode in postcodes:
    if postcode_regex.match(postcode):
        print(f"{postcode} is valid.")
    else:
        print(f"{postcode} is invalid.")


