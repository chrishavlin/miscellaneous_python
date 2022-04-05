"""
automated generation of a magicgui pydantic-widget!

run from the command line:

>>> python pydantic_magicgui_roundtrip.py

"""
import pydantic
from typing import Optional, Union
from magicgui import widgets
from magicgui.type_map import get_widget_class
import warnings


# write some pydantic classes with simple fields
class Hello(pydantic.BaseModel):
    hello: str = 'hi'
    what: int = 3


class NestedModel(pydantic.BaseModel):
    nested_thing: str = 'a'
    nice_field: float = 10.0
    further_nesting: Hello


class InheritedNester(NestedModel):
    extra_new_field: str = 'extra'


class TestModel(pydantic.BaseModel):
    intfield: int = 1
    testy: float = 10.0
    multinests: InheritedNester
    basic: Optional[int] = 10
    basic_notopt: int = 10

def add_pydantic_to_container(py_model: Union[pydantic.BaseModel, pydantic.main.ModelMetaclass], container: widgets.Container):
    # recursively traverse a pydantic model adding widgets to a container. When a nested
    # pydantic model is encountered, add a new nested container
    for field, field_def in py_model.__fields__.items():
        ftype = field_def.type_
        if isinstance(ftype, pydantic.BaseModel) or isinstance(ftype, pydantic.main.ModelMetaclass):
            # the field is a pydantic class, add a container for it and fill it
            new_widget_cls = widgets.Container
            new_widget = new_widget_cls(name=field_def.name)
            add_pydantic_to_container(ftype, new_widget)
        else:
            # parse the field, add appropriate widget
            new_widget_cls, ops = get_widget_class(None, ftype, dict(name=field_def.name, value=field_def.default))
            new_widget = new_widget_cls(**ops)
            if isinstance(new_widget, widgets.EmptyWidget):
                warnings.warn(message=f"magicgui could not identify a widget for {py_model}.{field}, which has type {ftype}")
        container.append(new_widget)


def get_pydantic_kwargs(container: widgets.Container, pydantic_model, pydantic_kwargs: dict):
    # given a container that was instantiated from a pydantic model, get the arguments
    # needed to instantiate that pydantic model from the container.

    # traverse model fields, pull out values from container
    for field, field_def in pydantic_model.__fields__.items():
        ftype = field_def.type_
        if isinstance(ftype, pydantic.BaseModel) or isinstance(ftype, pydantic.main.ModelMetaclass):
            # go deeper
            pydantic_kwargs[field] = {} # new dictionary for the new nest level
            # any pydantic class will be a container, so pull that out to pass
            # to the recursive call
            sub_container = getattr(container, field_def.name)
            get_pydantic_kwargs(sub_container, ftype, pydantic_kwargs[field])
        else:
            # not a pydantic class, just pull the field value from the container
            if hasattr(container, field_def.name):
                value = getattr(container, field_def.name).value
                pydantic_kwargs[field] = value


# initialize the top container and specify what pydantic class to map from
big_container = widgets.Container(name=TestModel.__name__)
pydantic_class = TestModel

# recursively traverse the pydantic class, adding to the container
add_pydantic_to_container(pydantic_class, big_container)

# add a button with callbacks to instantiate a pydantic model from the container
build_button = widgets.PushButton(name="Build pydantic model")
json_display = widgets.Label(value="")  # we will display the json!

# the callback that we will connect:
def display_json_callback():

    # build up the arguments for the pydantic model given the current container
    pydantic_kwargs = {}
    get_pydantic_kwargs(big_container, pydantic_class, pydantic_kwargs)

    # instantiate the pydantic model form the kwargs we just pulled
    pydantic_model = pydantic_class.parse_obj(pydantic_kwargs)

    # generate a json from the instantiated model, update the json_display
    json_format = pydantic_model.json(indent=4)
    json_display.value = json_format


# connect the button to the callback function
build_button.clicked.connect(display_json_callback)

# add the button and display to the container
big_container.append(build_button)
big_container.append(json_display)

# run it!
big_container.show(run=True)