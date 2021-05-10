from unittest.mock import patch

import pytest
import pytest_mock

from cba.commands.base_commands import *
from cba.publishers import HTTPPublisher


@pytest.fixture(scope="function")
def test_cmd_class(cmd="test"):

    class Cmd4Testing(BaseCommand):
        """ Команда для юнит-тестов """
        CMD = cmd

        async def _execute(self): ...

    yield Cmd4Testing


@pytest.fixture(scope="function")
def test_cmd_instance(test_cmd_class):
    target = MessageTarget(target_type="service", target_name="test")
    client_info = ClientInfo(name="test")
    publishers = [HTTPPublisher(url="", headers={}), ]
    cmd = test_cmd_class(
        target=target,
        client_info=client_info,
        publishers=publishers
    )
    yield cmd


class TestBaseCommandClassMethods:

    def test_hide(self, test_cmd_class):
        test_cmd_class.hide()
        assert test_cmd_class.hidden is True

    def test_show(self, test_cmd_class):
        test_cmd_class.show()
        assert test_cmd_class.hidden is False

    def test_admin_only(self, test_cmd_class):
        test_cmd_class.mark_as_admin_only()
        assert test_cmd_class.behavior__admin is test_cmd_class
        assert test_cmd_class.admin_only is True

    def test_admin_behavior(self, test_cmd_class):

        @test_cmd_class.admin_behavior
        class CmdAdminBehavior(BaseCommand): ...

        assert test_cmd_class.behavior__admin is CmdAdminBehavior
        assert CmdAdminBehavior.CMD == test_cmd_class.CMD

    def test_admin_only_with_admin_behavior(self, test_cmd_class):

        @test_cmd_class.admin_behavior
        class CmdAdminBehavior(BaseCommand): ...

        with pytest.raises(AttributeError):
            test_cmd_class.mark_as_admin_only()

    def test_admin_behavior_with_admin_only(self, test_cmd_class):
        test_cmd_class.mark_as_admin_only()

        with pytest.raises(AttributeError):

            @test_cmd_class.admin_behavior
            class CmdAdminBehavior(BaseCommand): ...


class TestBaseCommandRegularMethods:

    def test_create_subcommand(self, test_cmd_instance, test_cmd_class):
        command_args = dict(arg1="val1")
        sub_cmd = test_cmd_instance.create_subcommand(
            test_cmd_class,
            command_args=command_args
        )
        assert sub_cmd.target == test_cmd_instance.target
        assert sub_cmd.publishers == test_cmd_instance.publishers
        assert sub_cmd.client_info == test_cmd_instance.client_info
        assert sub_cmd.command_args == command_args
        assert sub_cmd.parent_id == test_cmd_instance.id

    @pytest.mark.asyncio
    async def test_send_message(self, test_cmd_instance, mocker):
        images = ["image1", "image2", "image3"]
        mocker.patch("src.publishers.HTTPPublisher.publish_message")
        target = MessageTarget("test", "test")
        message_kwargs = dict(
            subject="subject",
            text="text",
            images=images
        )

        spy = mocker.spy(HTTPPublisher, "publish_message")
        await test_cmd_instance.send_message(
            target=target, **message_kwargs
        )

        message_obj = spy.await_args.args[0]
        assert target == MessageTarget(**message_obj.payload["target"])
        assert len(images) == len(message_obj.payload["replies"])

    @pytest.mark.asyncio
    async def test_send_message_without_target(self, test_cmd_instance, mocker):
        mocker.patch("src.publishers.HTTPPublisher.publish_message")
        spy = mocker.spy(HTTPPublisher, "publish_message")
        await test_cmd_instance.send_message(
            text="text"
        )
        message_obj = spy.await_args.args[0]
        assert test_cmd_instance.target == MessageTarget(**message_obj.payload["target"])

    def test_add_inline_button(self, test_cmd_instance, test_cmd_class):
        test_cmd_instance.add_inline_button(
            test_cmd_class, "button", "arg1", "arg2"
        )
        button_info = test_cmd_instance.inline_buttons[0]
        assert button_info["text"] == "button"
        assert button_info["callback_data"] == \
               test_cmd_instance.reverse_command(test_cmd_class, "arg1", "arg2")

    def test_reverse_command(self, test_cmd_instance, test_cmd_class):
        cmd_macros = test_cmd_instance.reverse_command(test_cmd_class, "arg1", "arg2")
        client_name = test_cmd_instance.client_info.name
        assert cmd_macros == f"/{client_name}_{test_cmd_class.CMD}_arg1_arg2"

    @pytest.mark.asyncio
    async def test_execute(self, test_cmd_class, test_cmd_instance):

        @patch.object(test_cmd_class, '_execute')
        async def test(mock_execute):
            await test_cmd_instance.execute()
            mock_execute.assert_called()

        await test()

    def test_check_sender_name(self, test_cmd_class):
        target = MessageTarget(target_type="service", target_name="test")
        client_info_1 = ClientInfo(name="test")
        client_info_2 = ClientInfo(name="test", verbose_name="TEST")
        client_info_3 = ClientInfo(name="test", hide_name=True)
        cmd_1 = test_cmd_class(target=target, publishers=[], client_info=client_info_1)
        cmd_2 = test_cmd_class(target=target, publishers=[], client_info=client_info_2)
        cmd_3 = test_cmd_class(target=target, publishers=[], client_info=client_info_3)

        assert cmd_1._check_sender_name() == "test"
        assert cmd_2._check_sender_name() == "TEST"
        assert cmd_3._check_sender_name() == ""


class TestDecorators:

    def test_admin_only(self):
        @admin_only
        class Cmd4Testing(BaseCommand): ...
        assert Cmd4Testing.behavior__admin == Cmd4Testing

    def test_hide(self):
        @hide
        class Cmd4Testing(BaseCommand): ...
        assert Cmd4Testing.hidden is True
