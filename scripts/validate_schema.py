import sys, json
from jsonschema import validate, Draft202012Validator

def main():
    json_path = "content/scam-of-the-week.json"
    schema_path = "schema/scam.schema.json"
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
    if len(sys.argv) > 2:
        schema_path = sys.argv[2]

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    Draft202012Validator.check_schema(schema)
    validate(instance=data, schema=schema)
    print("Schema validation: OK")

if __name__ == "__main__":
    main()
