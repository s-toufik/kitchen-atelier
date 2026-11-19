from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FoodClassification:
    group_code: str
    subgroup_code: str
    sub_subgroup_code: str
    group_name: str
    subgroup_name: str
    sub_subgroup_name: str
