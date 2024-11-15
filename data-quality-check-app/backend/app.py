import os

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
from DQC_TEMPLATE import DQC_TEMPLATE  # Import the Data Quality Checks template
from openai import OpenAI
import yaml
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.dom import minidom


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

mapping_cache = {}


user_sql_content = None
config_content = None
saved_sql_checks = {}


@app.route('/upload_schema_files', methods=['POST'])
def upload_schema_files():
    inferred_schemas = {}
    mapped_schemas = {}

    for alias, file in request.files.items():
        # Step 1: Infer schema from each uploaded file
        df = pd.read_csv(file)
        inferred_schemas[alias] = [{"field": col, "dtype": str(df[col].dtype)} for col in df.columns]

        # Step 2: Generate LLM-derived mappings for the inferred schema
        mapped_schemas[alias] = map_fields_with_llm(inferred_schemas[alias])

    # Step 3: Return both inferred and mapped schemas for each alias
    return jsonify({
        "inferred_schemas": inferred_schemas,
        "mapped_schemas": mapped_schemas
    })


@app.route('/upload_files', methods=['POST'])
def upload_config():
    global data_sources
    global config_content, user_sql_content

    config_file = request.files.get('yaml_file')
    sql_file = request.files.get('sql_file')

    # Load User SQL
    if sql_file:
        user_sql_content = sql_file.read().decode('utf-8')

    if config_file:
        config_content = yaml.safe_load(config_file.read())
        data_sources = config_content.get("data_sources", {})

        # Prepare a response with the list of source aliases for the frontend
        source_aliases = list(data_sources.keys())
        return jsonify({"message": "Files uploaded successfully","sourceAliases": source_aliases})
    return jsonify({"error": "No config YAML provided"}), 400

@app.route('/save_mappings', methods=['POST'])
def save_mappings():
    mappings = request.json.get('mappings', [])
    # Save the mappings in memory, cache, or a database as needed
    global saved_mappings
    saved_mappings = mappings
    return jsonify({"status": "Mappings saved successfully"})

saved_sql_checks = {}

@app.route('/save_sql_checks', methods=['POST'])
def save_sql_checks():
    global saved_sql_checks
    sql_checks = request.json.get('sql_checks', [])

    if not sql_checks:
        return jsonify({"error": "No SQL checks provided"}), 400

    # Save the provided SQL checks
    saved_sql_checks = sql_checks
    return jsonify({"status": "SQL checks saved successfully"}), 200


def map_fields_with_llm(schema):
    print("testing")
    client = OpenAI(
        api_key="<your-open-api-key>",
    )
    mapped_schema = []
    for field in schema:
        prompt = (
                "Map the schema field '" + field["field"] + "' with data type '" + field["dtype"] + "' "
                                                                                                    "to the best match in the following Data Quality Checks: " + ", ".join(DQC_TEMPLATE["Field"].unique()) + " Respond only with the closest match name."
        )

        prompt = (
                f"Map the schema field '{field['field']}' with data type '{field['dtype']}' "
                "to the best match in the following Data Quality Checks: " + ", ".join(DQC_TEMPLATE["Field"].unique()) + ". "
                                                                                                                         "If no suitable match exists, respond with a blank. Ensure the mapping reflects the semantic meaning of the field "
                                                                                                                         "and aligns with similar attributes. For example, a field named 'email' should map to 'Email Address' if available."
                                                                                                                         "Respond only with the closest match name."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,  # Set a low max_tokens to limit verbosity
            temperature=0.0  # Set temperature to 0 to make the response deterministic
        )
        mapped_field = response.choices[0].message.content.strip()
        mapped_schema.append({"user_field": field["field"], "mapped_field": mapped_field})
        print(mapped_schema)
    return mapped_schema

@app.route('/approve', methods=['POST'])
def approve_mappings():
    # Cache the approved mappings
    approved_mappings = request.json.get('approved_mappings', [])
    for mapping in approved_mappings:
        mapping_cache[mapping['user_field']] = mapping['mapped_field']

    return jsonify({"status": "Mappings approved and cached"}), 200

@app.route('/generate_checks', methods=['POST'])
def generate_checks():
    mappings = request.json.get('mappings')
    final_checks = generate_sql_checks(mappings)
    return jsonify(final_checks)


@app.route('/generate_sql_checks', methods=['POST'])
def generate_sql_checks():
    data = request.json
    alias = data.get('alias')  # Alias of the current data source
    record_id_field = data.get('record_id_field')
    mappings = data.get('mappings')

    # Check for missing required fields
    if not alias or not record_id_field or not mappings:
        print(f"Received data: alias={alias}, record_id_field={record_id_field}, mappings={mappings}")
        return jsonify({"error": "Alias, record identifier, and mappings are required"}), 400
    import uuid
    run_id = str(uuid.uuid4())
    sql_checks = []
    for mapping in mappings:
        mapped_field = mapping['mapped_field']
        user_field = mapping['user_field']
        dqc_checks = DQC_TEMPLATE[DQC_TEMPLATE['Field'] == mapped_field]

        for _, row in dqc_checks.iterrows():
            sql_check = (
                row["SQL Template"]
                .replace("{runId}",run_id)
                .replace("{record_id_field}", record_id_field)
                .replace("{dq_field_to_check}", user_field)
                .replace("{table}", alias)  # Replace table placeholder with alias
            )
            sql_checks.append({
                "user_field": user_field,
                "check_type": row["Check Type"],
                "sql": sql_check,
                "alias": alias  # Include alias for identification in XML generation
            })
    saved_sql_checks[alias] = sql_checks  # Save per alias
    return jsonify({"sql_checks": sql_checks})



def prettify_xml(elem):
    rough_string = ElementTree(elem).write("temp.xml")
    with open("temp.xml", 'r') as temp:
        rough_string = temp.read()
    reparsed = minidom.parseString(rough_string)
    os.remove("temp.xml")
    return reparsed.toprettyxml(indent="  ")

@app.route('/generate_xml', methods=['POST'])
def generate_xml_from_sql_content():
    data = request.json
    record_id_fields = data.get('record_id_fields', {})  # Pass record_id_field for each alias from frontend

    queries_element = Element('Queries')

    # Add Saved Data Quality SQL Checks to XML
    for alias, sql_checks in saved_sql_checks.items():
        record_id_field = record_id_fields.get(alias, "record_id")  # Get the record ID field for this alias
        # Add DQ SQLs with <Insert> for each data source
        for dq in sql_checks:
            dq_query = SubElement(queries_element, 'LogDQResult', table="DeadLetterTable")
            dq_query.text = dq['sql']

        # Add exclusion query for each data source
        filter_query = SubElement(queries_element, 'Query', id=f"filtered_{alias}")
        filter_query.text = f"SELECT * FROM {alias} WHERE {record_id_field} NOT IN (SELECT field_value FROM DeadLetterTable)"


    # Add User-Provided SQL Queries to the XML
    sql_statements = [line.strip() for line in user_sql_content.splitlines() if line.strip() and not line.startswith('--')]
    sources = config_content.get('data_sources', {})
    user_id_counter = 1
    alias_to_id_map = {}

    for sql in sql_statements:
        if sql.startswith("WITH"):
            alias = sql.split("WITH ")[1].split(" AS")[0].strip()
            sql_core = sql.split(" AS (")[1].rstrip(")").strip()  # Extract core SQL
        else:
            alias = None
            sql_core = sql.strip()

        # Replace source names with identifiers from YAML
        for source_name in sources.keys():
            if source_name in sql_core:
                sql_core = sql_core.replace(source_name, f"filtered_{source_name}")

        # Replace references to previous aliases with their query IDs
        for alias_name, query_id in alias_to_id_map.items():
            if alias_name in sql_core:
                sql_core = sql_core.replace(alias_name, query_id)

        # Create XML Query element for user-provided SQL
        query_id = f"user_query_{user_id_counter}"
        query_element = SubElement(queries_element, 'Query', id=query_id, type="User")
        query_element.text = sql_core

        # Store alias for reference if it exists
        if alias:
            alias_to_id_map[alias] = query_id

        user_id_counter += 1

    # Return the prettified XML string
    xml_string= prettify_xml(queries_element)
    return Response(
        xml_string,
        mimetype='application/xml',
        headers={
            "Content-Disposition": "attachment;filename=generated_queries.xml"
        }
    )

@app.route('/get_mapped_field_options', methods=['GET'])
def get_mapped_field_options():
    try:
        # Assuming DQC_TEMPLATE has a list or dictionary of available fields
        mapped_field_options = list(DQC_TEMPLATE["Field"].unique())  # Adjust based on actual structure
        return jsonify({"mapped_field_options": mapped_field_options})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)
