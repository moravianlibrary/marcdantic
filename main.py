from marc_record import MarcRecord

TEST_FILE = "/home/robert/documents/scripts/records/MZK01/000002519.mrc"


with open(TEST_FILE, "rb") as file:
    content = file.read()
    print(MarcRecord.model_validate(content))
