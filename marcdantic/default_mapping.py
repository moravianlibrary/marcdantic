DEFAULT_MAPPING = {
    "001": {"section": "control_fields", "field": "control_number"},
    "003": {"section": "control_fields", "field": "control_number_identifier"},
    "006": {"section": "control_fields", "field": "latest_transaction"},
    "008": {
        "section": "control_fields",
        "field": "fixed_length_data_elements",
    },
    "015": {
        "section": "numbers_and_codes",
        "field": "nbn",
        "repeatable": True,
        "subfields": {"a": {"subfield": "active"}},
    },
    "020": {
        "section": "numbers_and_codes",
        "field": "isbn",
        "repeatable": True,
        "subfields": {
            "a": {"subfield": "active"},
            "c": {"subfield": "terms_of_availability"},
        },
    },
    "022": {
        "section": "numbers_and_codes",
        "field": "issn",
        "repeatable": True,
        "subfields": {"a": {"subfield": "active"}},
    },
    "245": {
        "section": "title_related",
        "field": "title_statement",
        "subfields": {
            "a": {"subfield": "title"},
            "b": {"subfield": "subtitle"},
        },
    },
    "910": {
        "section": "local",
        "field": "location",
        "repeatable": True,
        "subfields": {
            "a": {"subfield": "sigla"},
            "b": {"subfield": "singature", "repeatable": True},
        },
    },
}
