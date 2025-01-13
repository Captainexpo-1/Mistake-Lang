from typing import List, Any
import mistake.runtime.runtime_types as rt
from pyairtable import Table, Base, Api
from mistake.runtime.errors.runtime_errors import *
AIRTABLE_API: Api = None
API_KEY = None
def create_airtable_api_instance(key: 'rt.RuntimeString', *_):
    global AIRTABLE_API, API_KEY
    if not isinstance(key, rt.RuntimeString):
        raise rt.RuntimeTypeError(f"Expected RuntimeString, got {type(key)}")
    
    AIRTABLE_API = Api(key.value)
    API_KEY = AIRTABLE_API.api_key
    return rt.RuntimeUnit()



def create_base(base_id: 'rt.RuntimeString'):
    if isinstance(base_id, rt.RuntimeString):
        base_id = base_id.value
    return rt.RuntimeAirtableBase(Base(API_KEY, base_id))

def create_table(base: 'rt.RuntimeAirtableBase', table_id: str):
    if isinstance(table_id, rt.RuntimeString):
        table_id = table_id.value
    return rt.RuntimeAirtableTable(AIRTABLE_API.table(base.base.id, table_id))

def list_table_records(table: 'rt.RuntimeAirtableTable'):
    if table.table is None:
        raise RuntimeError("Table not found")
    try:
        a = table.table.all()
        return rt.RuntimeListType([rt.RuntimeAirtableRecord(record) for record in a])
    except Exception as e:
        raise e
    
    
def get_record(table: 'rt.RuntimeAirtableTable', record_id: str):
    return rt.RuntimeAirtableRecord(table.table.get(record_id))

def create_record(table: 'rt.RuntimeAirtableTable', record: 'rt.RuntimeAirtableRecord'):
    table.table.create(record.to_record_dict())
    
def update_record(table: 'rt.RuntimeAirtableTable', record: 'rt.RuntimeAirtableRecord'):
    table.table.update(record.id, record.to_record_dict())
    
def delete_record(table: 'rt.RuntimeAirtableTable', record: 'rt.RuntimeAirtableRecord'):
    table.table.delete(record.id)
    
def new_record(fields: dict):
    return rt.RuntimeAirtableRecord(record={"id": None, "createdTime": None, "fields": fields})