import json
import os.path
from automation.automation_node import AutomationNode, TaskStatus, TaskInput


class SaveJsonDBTask(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self.add_input("json_obj_list", "json_list")
        self.add_input("db_path", "path")

        # add outputs
        self.add_output("directing", "router")

    def validate_inputs(self):
        return super().validate_inputs() and isinstance(self._inputs["json_obj_list"].value, list)
    
    def _run(self):
        # check if file exists
        if not os.path.isfile(self._inputs["db_path"].value):
            json.dump([], open(self._inputs["db_path"].value, "w+"))

        # read data from file
        with open(self._inputs["db_path"].value, "r+") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                raise Exception("Error when loading json file")
        
        with open(self._inputs["db_path"].value, "w+") as f:
            # validate data is List
            if not isinstance(data, list):
                self._status = TaskStatus.Failed
                return

            for json_obj in self._inputs["json_obj_list"].value:
                if not isinstance(json_obj, dict):
                    try:
                        json_obj = json_obj.dict()
                    except:
                        self._status = TaskStatus.Failed
                        return
                data.append(json_obj)
            
            json.dump(data, f, indent=4)

    def specify_input_list_type(self, variable_type:str):
        self._inputs["json_obj_list"].type = variable_type