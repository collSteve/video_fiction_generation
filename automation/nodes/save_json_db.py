import json
from automation.automation_node import AutomationNode, TaskStatus, TaskVariable


class SaveJsonDBTask(AutomationNode):
    def __init__(self, global_graph, id):
        super().__init__(global_graph, id)

        # add inputs
        self._inputs["json_obj_list"] = TaskVariable(type="json_list", value=None, name="json_obj_list", link=None)
        self._inputs["db_path"] = TaskVariable(type="path", value=None, name="db_path", link=None)

        # add outputs
        self._outputs["directing"] = TaskVariable(type="router", value=None, name="directing", link=None)

    def validate_inputs(self):
        return super().validate_inputs() and isinstance(self._inputs["json_obj_list"].value, list)
    
    def _run(self):
        super()._run()

        with open(self._inputs["db_path"].value, "w+") as f:
            # add to json obj stored in file
            f.seek(0)

            data = json.load(f)

            # validate data is List
            if not isinstance(data, list):
                self._status = TaskStatus.Failed
                return

            for json_obj in self._inputs["json_obj_list"].value:
                data.append(json_obj)
            
            f.seek(0)
            json.dump(data, f, indent=4)
        
        self._status = TaskStatus.Completed