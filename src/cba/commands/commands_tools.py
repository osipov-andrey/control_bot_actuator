import pathlib
import json

from cba import exceptions

TEMPLATE_DIR = "feedback_templates"  # Папка с шаблонами в пользовательской программе


def load_json_template(file_name: str, path_to_file) -> dict:
    """
    Для обращений к API используются готовые JSON-шаблоны.
    Файлы с шаблонами должны лежать в директории рядом
    с пользовательским модулем.
    """
    path = pathlib.Path(str(path_to_file)).parent
    path = path.joinpath(TEMPLATE_DIR)
    path = path.joinpath(file_name)
    try:
        with open(str(path), "r", encoding="utf-8") as json_:
            message_template = json.load(json_)
    except json.decoder.JSONDecodeError:
        raise exceptions.BadCommandTemplateException(file_name)
    return message_template
