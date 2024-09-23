from pydantic import BaseModel
from typing import List, Dict


class WorkItemType(BaseModel):
    id: str
    name: str


class WorkItemTypeResponse(BaseModel):
    workItemTypes: List[WorkItemType]

    @classmethod
    def from_api_response(cls, response: List[dict]) -> "WorkItemTypeResponse":
        """
        Validates the API response and returns an instance of WorkItemTypeResponse.
        """
        work_item_types = [WorkItemType.model_validate(
            item) for item in response]
        return cls(workItemTypes=work_item_types)

    def map_work_item_types_to_ids(self, state_to_type_map: Dict[str, str]) -> Dict[str, str]:
        """
        Maps the work item type names to their respective IDs based on a given state_to_type_map.
        """
        type_to_id_map: Dict[str, str] = {}
        for work_item_type in self.workItemTypes:
            if work_item_type.name in state_to_type_map.values():
                type_to_id_map[work_item_type.name] = work_item_type.id
        return type_to_id_map
