import argparse

from lerxml.xsd import validate_xsd_file
from lerxml.schematron import validate_sch_file
from lerxml.constraints import validate_con_file

from lerxml import ValidationError


def validate_xsd():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    errors = validate_xsd_file(args.file)
    if len(errors) == 0:
        print("Validation successful: The XML file is valid according to the LER XSD schema.")
    else:
        print("Validation failed: The XML file is not valid according to the LER XSD schema.")
        for error in errors:
            print(f"- {error.message} (line {error.line})")


def validate_sch():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    errors = validate_sch_file(args.file)
    if len(errors) == 0:
        print("Validation successful: The XML file is valid according to the LER Schematron schema.")
    else:
        print("Validation failed: The XML file is not valid according to the LER Schematron schema.")
        for error in errors:
            print(f"- {error.message} (line {error.line})")


def validate_con():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    errors = validate_con_file(args.file)

    if len(errors) == 0:
        print("Validation successful: The XML file is valid according to the LER Constraints.")
    else:
        print("Validation failed: The XML file is not valid according to the LER Constraints.")
        for error in errors:
            print(f"- {error.message} (line {error.line})")
