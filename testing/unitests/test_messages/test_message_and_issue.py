from cba.messages import *


SENDER_NAME = "name"


class TestIssue:
    RESOLVED = 'RESOLVED'

    def test_add_prefix(self):
        issue = Issue("id1", "PROBLEM", prefix="test_")
        assert issue.id_ == "test_id1"

    def test_status(self):
        issue = Issue("id1", "PROBLEM", prefix="test_")
        assert issue.resolved is False
        issue = Issue("id1", self.RESOLVED, prefix="test_")
        assert issue.resolved is True


def get_message(*, target=MessageTarget("user", "user_id", "123"), **kwargs):
    return TelegramMessage(
        _id="123",
        cmd="cmd",
        sender_name=SENDER_NAME,
        target=target,
        **kwargs
    )


class TestMessage:

    def test_build_message(self):
        expected_result = f"<i><b>{SENDER_NAME}\nlol\n</b></i>kek"
        message = get_message(text="kek", subject="lol")
        assert message._text == expected_result
        assert message.payload["message"] == expected_result

    def test_check_commands(self):
        commands = {"cmd": "cmd_description"}
        message = get_message(commands=commands)
        assert message.payload["commands"] == commands

    def test_check_many_images(self):
        images = ["image1", "image2"]
        message = get_message(images=images)
        assert message.payload["replies"] == [{"image": image} for image in images]

    def test_one_image(self):
        images = ["image", ]
        message = get_message(images=images)
        assert message.payload["image"] == images[0]

    def test_check_replies(self):
        replies = ["message1", "message2"]
        message = get_message(replies=replies)
        assert message.payload["replies"] == [{"message": message} for message in replies]

    def test_check_replies_and_images(self):
        """ Replies should only contain images or only Replies """
        replies = ["message1", "message2"]
        images = ["image1", "image2"]
        message = get_message(replies=replies, images=images)
        assert message.payload["replies"] == [{"image": image} for image in images]

    def test_check_document(self):
        document = dict(
            content="content",
            filename="filename",
            caption="caption"
        )
        message = get_message(document=document)
        assert message.payload["document"] == document

    def test_check_issue(self):
        issue = Issue("id_1", "PROBLEM")
        message = get_message(issue=issue)
        assert message.payload["issue"]["issue_id"] == issue.id_
        assert message.payload["issue"]["resolved"] == issue.resolved

    def test_check_target(self):
        target = MessageTarget("user", "123123", "007")
        message = get_message(target=target)
        target_dict = target._asdict()
        target_dict.pop("message_id")
        assert message.payload["target"] == target_dict

    def test_check_target_with_edit(self):
        target = MessageTarget("user", "123123", "007")
        message = get_message(target=target, inline_edit_button=True)
        assert message.payload["target"] == target._asdict()

    def test_check_buttons(self):
        buttons = {"button1": "action1", "button2": "action2"}
        message = get_message(buttons=buttons)
        assert message.payload["buttons"] == buttons
