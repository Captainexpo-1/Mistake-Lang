import mistake.runtime.runtime_types as rt
from pyairtable import Base, Api
import requests
from mistake.runtime.errors.runtime_errors import RuntimeError

AIRTABLE_API: Api = None
API_KEY = None


def create_airtable_api_instance(key: "rt.RuntimeString", *_):
    global AIRTABLE_API, API_KEY
    if not isinstance(key, rt.RuntimeString):
        raise rt.RuntimeTypeError(f"Expected RuntimeString, got {type(key)}")

    AIRTABLE_API = Api(key.value)
    API_KEY = AIRTABLE_API.api_key
    return rt.RuntimeUnit()


def create_base(base_id: "rt.RuntimeString"):
    if isinstance(base_id, rt.RuntimeString):
        base_id = base_id.value
    return rt.RuntimeAirtableBase(Base(API_KEY, base_id))


def create_table(base: "rt.RuntimeAirtableBase", table_id: str):
    if isinstance(table_id, rt.RuntimeString):
        table_id = table_id.value
    return rt.RuntimeAirtableTable(AIRTABLE_API.table(base.base.id, table_id))


def list_table_records(table: "rt.RuntimeAirtableTable"):
    if table.table is None:
        raise RuntimeError("Table not found")
    try:
        a = table.table.all()
        return rt.RuntimeListType([rt.RuntimeAirtableRecord(record) for record in a])
    except Exception as e:
        raise e


def get_record(table: "rt.RuntimeAirtableTable", record_id: str):
    return rt.RuntimeAirtableRecord(table.table.get(record_id))


def create_record(table: "rt.RuntimeAirtableTable", record: "rt.RuntimeAirtableRecord"):
    result = table.table.create(record.to_record_dict())
    record.id = result["id"]
    record.creation_time = result["createdTime"]
    return rt.RuntimeUnit()


def update_record(table: "rt.RuntimeAirtableTable", record: "rt.RuntimeAirtableRecord"):
    table.table.update(record.id, record.to_record_dict())
    return rt.RuntimeUnit()


def delete_record(table: "rt.RuntimeAirtableTable", record_id: str):
    table.table.delete(record_id)
    return rt.RuntimeUnit()


def new_record(fields: dict):
    return rt.RuntimeAirtableRecord(
        record={"id": None, "createdTime": None, "fields": fields}
    )


def create_new_field(
    raw_table: "rt.RuntimeAirtableTable",
    field_name: "rt.RuntimeString",
    field_type: "rt.RuntimeString",
    raw_options: "rt.RuntimeDictType",
):
    table = raw_table.table
    # base = table.base
    field_name = rt.un_convert_type(field_name)
    field_type = rt.un_convert_type(field_type)
    options = raw_options.as_regular_dict()
    resp = table.create_field(name=field_name, field_type=field_type, options=options)
    return rt.RuntimeString(resp.model_dump()["id"])


def update_field(
    raw_table: "rt.RuntimeAirtableTable",
    field_id: "rt.RuntimeString",
    new_data: "rt.RuntimeDictType",
):
    table = raw_table.table
    base = table.base
    field_id = rt.un_convert_type(field_id)

    # Endpoint URL
    url = f"https://api.airtable.com/v0/meta/bases/{base.id}/tables/{table.id}/fields/{rt.un_convert_type(field_id)}"

    # Headers
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    # Data payload
    data = new_data.as_regular_dict()

    # PATCH request
    response = requests.patch(url, json=data, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to update field: {response.text}")
    return rt.RuntimeUnit()


def all_bases():
    return rt.RuntimeListType(
        [rt.RuntimeAirtableBase(base) for base in AIRTABLE_API.bases()]
    )


def base_schema(base: "rt.RuntimeAirtableBase"):
    return rt.RuntimeDictType(rt.runtime_dictify(base.base.schema().model_dump()))
