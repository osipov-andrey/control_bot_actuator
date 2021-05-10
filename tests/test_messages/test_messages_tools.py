import pytest

from cba.messages.messages_tools import parse_and_paste_emoji, _clear_html, _build_message_subject


@pytest.mark.parametrize(
    "input_string, output_string",
    [
        ("Info about emoji: >>hankey<<!", "Info about emoji: 💩!"),
        ("Maybe many emojies?? >>Disaster<< >>High<<>>OK", "Maybe many emojies?? 🔥 🛑>>OK"),
    ],
)
def test_parse_and_paste_emoji(input_string, output_string):
    assert parse_and_paste_emoji(input_string) == output_string


@pytest.mark.parametrize(
    "subject, client, output",
    [
        ("Subject", "Client", "<i><b>Client\nSubject\n</b></i>"),
        ("", "Client", "<i><b>Client\n</b></i>"),
        ("Subject", "", "<i><b>Subject\n</b></i>"),
        ("", "", "<i><b></b></i>"),
    ],
)
def test_build_message_subject(subject, client, output):
    assert _build_message_subject(subject, client) == output


class TestCleanHtml:
    linear_html_structure_input = """
    <a>Ссылка</a>
    <employer@vertex.spb.ru> Принтер сдох
    <b>Жирный</b>
    Просто текст
    """

    linear_html_structure_output = """
    <a>Ссылка</a>
    Принтер сдох
    <b>Жирный</b>
    Просто текст
    """

    tree_html_structure_input = """
    <b>From: Татаренко Елена Владимировна <etatarenko@vertex.spb.ru>
    Sent: Monday, November 23, 2020 9:40 AM
    To: Менеджер технического отдела <techmanager@vertex.spb.ru>
    Subject: FW: не работает принтер.</b>
    
    Добрый день!
    
    Повторно прошу подойти и посмотреть принтер.
    
    From: Татаренко Елена Владимировна
    Sent: Friday, November 20, 2020 3:13 PM
    To: Менеджер технического отдела <techmanager@vertex.spb.ru>
    Subject: не работает принтер.
    
    Добрый день!
    
    В кабинете 2.8.18 не работает принтер. 
    Не открывается лоток с бумагой, внутри застряла бумага и не печатает с ОА.
    """

    tree_html_structure_output = """
    <b>From: Татаренко Елена Владимировна
    Sent: Monday, November 23, 2020 9:40 AM
    To: Менеджер технического отдела
    Subject: FW: не работает принтер.</b>
    
    Добрый день!
    
    Повторно прошу подойти и посмотреть принтер.
    
    From: Татаренко Елена Владимировна
    Sent: Friday, November 20, 2020 3:13 PM
    To: Менеджер технического отдела
    Subject: не работает принтер.
    
    Добрый день!
    
    В кабинете 2.8.18 не работает принтер. 
    Не открывается лоток с бумагой, внутри застряла бумага и не печатает с ОА.
    """

    @pytest.mark.parametrize(
        "input_html, output_html",
        [
            (linear_html_structure_input, linear_html_structure_output),
            (tree_html_structure_input, tree_html_structure_output),
        ],
    )
    def test_clear_html(self, input_html, output_html):
        expected_data = [line.strip() for line in output_html.split("\n")]
        actual_data = [line.strip() for line in _clear_html(input_html).split("\n")]
        assert actual_data == expected_data
