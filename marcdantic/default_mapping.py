DEFAULT_LOCAL_MAPPING = {
    "910": {
        "name": "location",
        "subfields": {"a": "sigla", "b": "signature"},
    },
}
DEFAULT_INVERSE_LOCAL_MAPPING = {
    "location": {
        "tag": "910",
        "subfields": {"sigla": "a", "signature": "b"},
    }
}
DEFAULT_ISSUE_MAPPING = {
    "tag": "996",
    "barcode": "b",
    "issuance_type": "m",
    "volume_number": "a",
    "volume_year": "h",
    "bundle": "j",
}
