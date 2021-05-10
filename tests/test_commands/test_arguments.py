from typing import List, Optional

import pytest
from cba.commands.arguments import *

from pydantic import BaseModel, ValidationError


class IntegerSchema(BaseModel):
    type = "integer"
    minimum: Optional[int]
    maximum: Optional[int]
    allowed: Optional[List[int]]


class StringSchema(BaseModel):
    type = "string"
    regex: Optional[str]
    allowed: Optional[List[str]]


class ListSchema(BaseModel):
    type = "list"


class MyUserSchema(IntegerSchema):
    is_client = True


class BaseArgInfo(BaseModel):
    description: str


class IntegerArgInfo(BaseArgInfo):
    arg_schema: IntegerSchema
    options: Optional[List[int]]


class StringArgInfo(BaseArgInfo):
    arg_schema: StringSchema
    options: Optional[List[str]]


class ListArgInfo(BaseArgInfo):
    arg_schema: ListSchema


class MyUserArgInfo(BaseArgInfo):
    arg_schema = MyUserSchema


class TestArguments:
    @staticmethod
    def _validate_arg(argument, arg_model):
        try:
            arg_model(**argument.arg_info)
        except ValidationError as err:
            pytest.fail(str(err))

    def test_description(self):
        arg = String("testArg", "test Arg description", example="hehe")
        assert arg._build_description() == "test Arg description <i>[hehe]</i>"

    def test_string_arg(self):
        arg = String(
            name="name",
            description="description",
            example="example",
            options=["1", "2"],
            allowed=["1", "2", "3"],
        )
        assert arg.arg_info["arg_schema"]["allowed"] == ["1", "2", "3"]
        assert arg.arg_info["options"] == ["1", "2"]
        self._validate_arg(arg, StringArgInfo)

    def test_allow_options(self):

        arg = String(name="name", description="description", options=["1", "2"], allow_options=True)
        assert arg.arg_info["arg_schema"]["allowed"] == ["1", "2"]

    def test_int_arg(self):
        arg = Integer(
            name="name",
            description="description",
            options=[1, 2],
            maximum=1,
            minimum=2,
            allow_options=True,
        )
        self._validate_arg(arg, IntegerArgInfo)

    def test_list_arg(self):
        arg = ListArg(
            name="name",
            description="description",
        )
        self._validate_arg(arg, ListArgInfo)

    def test_user_arg(self):
        arg = MyUser(
            name="name",
            description="description",
        )
        self._validate_arg(arg, MyUserArgInfo)
