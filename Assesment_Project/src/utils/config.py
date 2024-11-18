# Configuration constants
QUERY_TEMPLATES = {
    "Basic Info": "Extract basic information about {company}",
    "Contact Details": "Get the email and address for {company}",
    "Full Analysis": "Provide a detailed analysis of {company} including contact info, main business areas, and key personnel",
    "Custom": "Custom prompt..."
}

DEFAULT_FIELDS = ["Email", "Address", "Phone", "Website", "Description"]
BATCH_SIZE = 10
