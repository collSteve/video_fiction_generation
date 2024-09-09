import json
import os
from typing import Any, Callable, List

from pydantic import BaseModel

class QueryObj(BaseModel):
    attribute: str
    is_valid: Callable[[Any], bool]

# create JsonDBStoreError class
class DBStoreError(Exception):
    pass

class FieldProperties(BaseModel):
    required: bool = True
    default_value: Any = None



class JsonDBStore():
    

    def __init__(self, path):
        self.path = path
        self.fields: dict[str, FieldProperties] = {"id": FieldProperties(required=True)} # field name: FieldProperties

    def save_list_json(self, json_list: List[dict[str, Any]]):
        if not self.is_json_list_valid(json_list):
            raise DBStoreError("")

        if not os.path.isfile(self.path):
            json.dump([], open(self.path, "w+"))

        # read data from file
        with open(self.path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                raise DBStoreError("Error when loading json file")

        if not self.is_json_list_valid(data):
            raise DBStoreError("")
        
        with open(self.path, "w") as f:
            # validate data is List
            if not isinstance(data, list):
                raise DBStoreError("Data in json file is not a list")

            for json_obj in json_list:
                if not isinstance(json_obj, dict):
                    try:
                        json_obj = json_obj.dict()
                    except:
                        raise DBStoreError("Json object is not a dictionary")
                data.append(json_obj)
            
            json.dump(data, f, indent=4)

    def query_items(self, query: List[QueryObj]) -> List[dict[str,Any]]:
        # check validity of query objects
        for queryObj in query:
            if queryObj.attribute not in self.fields.keys():
                raise Exception(f"Invalid query object: attribut {queryObj.attribute} is not a valid field")

        # check if file exists
        if not os.path.isfile(self.path):
            json.dump([], open(self.path, "w+"))
        
        # load all db
        with open(self.path, "r") as f:
            try:
                dict_data: List[dict[str, Any]] = json.load(f)

            except json.JSONDecodeError:
                raise Exception("Error when loading json file")
            
        if not isinstance(dict_data, list):
            raise DBStoreError("Data in json file is not a list")
        
        
        valid_items: List[dict[str, Any]] = []
        for dict_item in dict_data:

            item_is_valid = True
            for queryObj in query:

                if not queryObj.is_valid(dict_item[queryObj.attribute]):
                    item_is_valid = False
                    break
            
            if item_is_valid:
                valid_items.append(dict_item)
        
        return valid_items
    
    def is_json_list_valid(self, json_list: List[dict[str,Any]]):
        # check if json list has every field except id
        value_fields = list(self.fields.keys())
        value_fields.remove("id")

        for field in value_fields:
            for json_item in json_list:
                if field not in json_item.keys():
                    return False
                
        return True

    