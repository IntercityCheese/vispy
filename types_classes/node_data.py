from dataclasses import dataclass, field
from typing import Dict
import uuid
from types_classes.vispyDataTypes import TypeProfile


@dataclass
class NodeData:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    node_type: str = ""
    category: str = ""

    inputs: Dict[str, TypeProfile] = field(default_factory=dict)
    outputs: Dict[str, TypeProfile] = field(default_factory=dict)

    python_template: str = ""
