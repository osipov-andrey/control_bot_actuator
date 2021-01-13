import re

from bs4 import BeautifulSoup as bs


__all__ = [
    'build_message',
    'parse_and_paste_emoji'
]
HTML_TAG_PATTERN = re.compile(r'(<\/*([\w@.]+)[^>]*>)')
VALID_HTML_TAGS = ('a', 'b', 'i', 'code', 'pre')


def build_message(subject: str, message: str, client_name: str):
    """
    Собирает сообщение для отправки в телеграм.
    """
    message_subject = _build_message_subject(subject, client_name)
    message = f'{message_subject}{message}'
    message = parse_and_paste_emoji(message)
    message = _clear_html(message)
    return message


def parse_and_paste_emoji(text: str):
    """ Подставляет emoji """
    pattern = re.compile(r'>>(\w+)<<')
    text = re.sub(pattern, lambda x: emoji_map[x.group(1)], text)
    return text


def _build_message_subject(subject: str, client_name: str) -> str:
    """ Подготавливает заголовок сообщения """
    if client_name:
        client_name += "\n"
    if subject:
        subject += "\n"
    subject = f"<i><b>{client_name}{subject}</b></i>"
    return subject


def _clear_html(message: str) -> str:
    """ Удаляет невалидные HTML-тэги """
    html_text = str(bs(message, 'html.parser'))  # для экранирования одиночных HTML-символов
    html_text = re.sub(HTML_TAG_PATTERN, _check_tag, html_text)
    return html_text


def _check_tag(match_object) -> str:
    if match_object.group(2).strip().lower() not in VALID_HTML_TAGS:
        return ''
    else:
        return match_object.group(1)


emoji_map = {
    "Disaster": "🔥",
    "High": "🛑",
    "Average": "❗",
    "Warning": "⚠️",
    "Information": "ℹ️",
    "Not_classified": "🔘",
    "OK": "✅",
    "PROBLEM": "❗",
    "info": "ℹ️",
    "WARNING": "⚠️",
    "DISASTER": "❌",
    "bomb": "💣",
    "fire": "🔥",
    "hankey": "💩",
    "nailed": "📌",
    "0": "⬜",   # white
    "1": "🟦",  # blue
    "2": "🟩",  # green
    "3": "🟨",  # yellow
    "4": "🟧",  # orange
    "5": "🟥",  # red
    "clock": "🕑",
    "voice": "📣",
    "drug": "💊",
    "glasses": "🥽",
    "lupa": "🔍",
    "graph1": "📈",
    "graph2": "〽",
    "repeat": "🔄",
    "start": "▶️",
    "stop": "⏹",
    "restart": "🔁",
    "portfolio": "💼",
    "archive": "🗄",
    "scroll": "🧾",
    "Not_classified2": "✳️",
    "red_null": "🅾️",
    "flag_arrow": "🔰",
    "!?": "⁉️",
    "author": "👨🏻",
    "assignee": "👨🏼‍💻",
    "phone": "☎️",
    "in": "↘️",
    "out": "↖️",
    "no_call": "📵",
    "no": "🚫",
    "handset": "📞",
}
