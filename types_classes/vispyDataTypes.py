from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TypeProfile:
    name: str
    color: str
    shape: str
    default: Any


class types:
    string  = TypeProfile("String",  "#00FF00", "Ellipse" ,"")
    float   = TypeProfile("Float",   "#00FFEA", "Ellipse" ,0.0)
    integer = TypeProfile("Integer", "#0055FF", "Ellipse" ,0)
    boolean = TypeProfile("Boolean", "#FF00FF", "Ellipse" ,False)
    exec    = TypeProfile("Exec",    "#FFFFFF", "Rect" ,None)
    any     = TypeProfile("Any",     "#AAAAAA", "Ellipse" ,None)
    text    = TypeProfile("Text", "#005500", "TextInput", "")
    eval    = TypeProfile("Evaluation", "#FF0000", "EvalInput", "==")
