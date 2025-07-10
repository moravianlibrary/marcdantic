import argparse
import os

from lxml import etree

from .record import MarcRecord


def process_file(file_path: str) -> None:
    """
    Processes a single file by reading its content
    and validating it using MarcRecord.

    Parameters
    ----------
    file_path : str
        The path to the file to be processed.
    """
    try:
        with open(file_path, "rb") as file:
            content = file.read()
            # Validate and print the JSON output from MarcRecord
            print(f"Processing file: {file_path}")

            record: MarcRecord | None = None

            if file_path.endswith(".json"):
                MarcRecord.model_validate(content)
            elif file_path.endswith(".mrc"):
                record = MarcRecord.from_mrc(content)
            elif file_path.endswith(".xml"):
                record = MarcRecord.from_xml(etree.fromstring(content))

            print(record.model_dump_json(exclude_none=True, indent=2))
    except NotADirectoryError as e:
        print(f"Error processing file {file_path}: {e}")


def process_directory(directory_path: str) -> None:
    """
    Processes all files in a directory by validating them using MarcRecord.

    Parameters
    ----------
    directory_path : str
        The path to the directory containing files to be processed.
    """
    try:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                process_file(file_path)
    except Exception as e:
        print(f"Error processing directory {directory_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process MARC files or directories."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f", "--files", nargs="+", help="One or more MARC files to process."
    )
    group.add_argument(
        "-d", "--dirs", nargs="+", help="One or more directories to process."
    )

    args = parser.parse_args()

    if args.files:
        # Process each file in the list of provided files
        for file_path in args.files:
            process_file(file_path)
    elif args.dirs:
        # Process each directory, and process all files within them
        for directory_path in args.dirs:
            process_directory(directory_path)
