# model.py
from pydantic import BaseModel
from typing import List

# Input/Output models for tools

class AddInput(BaseModel):
    a: int
    b: int

class StringsToIntsOutput(BaseModel):
    ascii_values: List[int]

# example2.py or your mcp_server.py
from models import AddInput, AddOutput, StringsToIntsOutput
...
#addition tool
@mcp.tool()
def add(input: AddInput) -> AddOutput:
    """Add two numbers"""
    print("CALLED: add(AddInput) -> AddOutput")
    return AddOutput(result=input.a + input.b)

@mcp.tool()
def strings_to_chars_to_int(input: StringsToIntsInput) -> StringsToIntsOutput:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(StringsToIntsInput) -> StringsToIntsOutput")
    ascii_values = [ord(char) for char in input.string]
    return StringsToIntsOutput(ascii_values=ascii_values)
