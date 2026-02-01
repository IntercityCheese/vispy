from types_classes.vispyDataTypes import types
from types_classes.node_data import NodeData

def make_start_node():
    return NodeData(
        node_type= "Start",
        category="Logic Flow",
        inputs={},
        outputs={"": types.exec},
        python_template=""
    )

def make_add_node():
    return NodeData(
        node_type="Add",
        category="Math",
        inputs={
            "a": types.float,
            "b": types.float
        },
        outputs={
            "result": types.float
        },
        python_template="{a} + {b}"
    )

def make_print_node():
    return NodeData(
        node_type="Print",
        category="I/O",
        inputs={
            "": types.exec,
            "text": types.string
        },
        outputs={"": types.exec},
        python_template="print({text})"
    )

def make_cast_to_String_node():
    return NodeData(
        node_type="Cast to String",
        category="Data Manipulation",
        inputs={
            "value": types.any
        },
        outputs={
            "string": types.string
        },
        python_template="str({value})"
    )
    
def make_cast_to_Bool_node():
    return NodeData(
        node_type="Cast to Bool",
        category="Data Manipulation",
        inputs={
            "value": types.any
        },
        outputs={
            "bool": types.boolean
        },
        python_template="bool({value})"
    )
    
def make_cast_to_Int_node():
    return NodeData(
        node_type="Cast to Integer",
        category="Data Manipulation",
        inputs={
            "value": types.any
        },
        outputs={
            "integer": types.integer
        },
        python_template="int({value})"
    )

def make_cast_to_Float_node():
    return NodeData(
        node_type="Cast to Float",
        category="Data Manipulation",
        inputs={
            "value": types.any
        },
        outputs={
            "Float": types.float
        },
        python_template="float({value})"
    )
    
def make_evaluate_node():
    return NodeData(
        node_type="Evaluate",
        category="Selection",
        inputs={
            "a": types.any,
            "Operator": types.eval,
            "b": types.any
        },
        outputs={
            "" : types.boolean
        },
        python_template="{a}{Operator}{b}"
    )
    
def make_input_node():
    return NodeData(
        node_type="Input",
        category="I/O",
        inputs={
            "": types.exec,
            "message": types.string
        },
        outputs={
            "": types.exec,
            "input": types.string
        },
        python_template="input({message})"
    )
    
def make_selection_node():
    return NodeData(
        node_type="Selection",
        category="Logic Flow",
        inputs={
            "": types.exec,
            "condition": types.boolean
        },
        outputs={
            "True" : types.exec,
            "False": types.exec
        },
        python_template="if {condition} == True:"
    )
    
def make_new_text_node():
    return NodeData(
        node_type="Text Value",
        category="Values",
        inputs={"Text Value": types.text},
        outputs={"string": types.string},
        python_template=""
    )