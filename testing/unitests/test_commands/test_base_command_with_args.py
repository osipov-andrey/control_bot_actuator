import pytest
from typing import Type

from cba.commands import ClientInfo, MessageTarget, arguments, \
    HumanCallableCommandWithArgs, WrongArguments, exceptions


ARG1_VALID = "1"
ARG2_VALID = "2"


class ClassForTesting(HumanCallableCommandWithArgs):
    """ Тестовая команда """
    CMD = "test"
    ARGS = (
        arguments.String("arg1", "description 1"),
        arguments.String("arg2", "description 2"),
    )

    def _execute(self):
        ...

    def _validate(self):
        wrong_arguments = []
        if self.arg1 != ARG1_VALID:
            wrong_arguments.append(self.arg1)
        if self.arg2 != ARG2_VALID:
            wrong_arguments.append(self.arg2)
        return wrong_arguments


def get_cmd_object(
        cls: Type[HumanCallableCommandWithArgs] = ClassForTesting,
        target=MessageTarget(target_type="service", target_name="test"),
        client_info=ClientInfo(name="test"),
        args: dict = {}
):
    cmd = cls(
        target=target,
        client_info=client_info,
        publishers=[],
        command_args=dict(args)
    )
    return cmd


class TestSetArgs:

    def test_set_args(self):
        cmd = get_cmd_object(args=dict(arg1=1, arg2=2))
        assert cmd.arg1 == 1
        assert cmd.arg2 == 2

    def test_unexpected_argument(self):
        cmd = get_cmd_object(args=dict(arg1=1, arg2=2))
        with pytest.raises(ValueError):
            cmd._set_args(dict(arg1=1, arg2=2, arg3=3))

    def test_missing_arguments(self):
        try:
            cmd = get_cmd_object(args=dict(arg1=1))
        except exceptions.NotEnoughArgumentsError as err:
            assert err.missing_args == ["arg2", ]
        else:
            pytest.fail()

    def test_set_default_args(self):
        class _ClassForTesting(HumanCallableCommandWithArgs):
            """ Тестовая команда """
            CMD = "test"
            ARGS = (
                arguments.Integer("arg1", "description 1", default=1),
                arguments.String("arg2", "description 2", default=2),
            )
            def _execute(self):
                ...

        cmd = get_cmd_object(cls=_ClassForTesting)
        assert cmd.arg1 == 1
        assert cmd.arg2 == 2


class TestCommandWithArgs:

    def test_init(self):
        cmd = get_cmd_object(args=dict(
            arg1=1, arg2=2
        ))
        assert cmd.arg1 == 1
        assert cmd.arg2 == 2

    def test_validate_good(self):
        cmd = get_cmd_object(args=dict(
            arg1="1", arg2="2"
        ))
        validated_cmd = cmd.validate()
        assert validated_cmd == cmd

    def test_validate_bad(self):
        cmd = get_cmd_object(args=dict(
            arg1=1, arg2=2
        ))
        validated_cmd = cmd.validate()
        assert isinstance(validated_cmd, WrongArguments)
        assert validated_cmd.wrong_arguments == [1, 2]

    def test_args_description(self):
        required_description = {arg.name: arg.arg_info for arg in ClassForTesting.ARGS}
        description = ClassForTesting.args_description()
        assert required_description == description



