"""********************************************************************"""
"""                                                                    """
"""   [prompt] ModulePrompt.py                                         """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 29/09/2021 05:55:34                                     """
"""   Updated: 11/10/2021 03:48:44                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary

from modules.Controller import ModuleController
from user import User

from questionary import Validator, ValidationError, Style

class ModuleLaunchValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="You need to choose a valid module!",
                cursor_position=len(document.text),
            )
        try:
            identifier = int(document.text)

            module = ModuleController().getModuleById(identifier)
            
            if (module is None):
                raise ValidationError(
                    message="This module doesn't exist!",
                    cursor_position=len(document.text)
                )
                
            if (User().hasPermissions(module['permission']) is False):
                raise ValidationError(
                    message="Insuffisent permission!",
                    cursor_position=len(document.text)
                )

            if (module['locked'] is True and "admin" not in User().permissions):
                raise ValidationError(
                    message="This module is locked!",
                    cursor_position=len(document.text)
                )
        except ValueError:
            raise ValidationError(
                message='You need to choose a valid module!',
                cursor_position=len(document.text))  # Move cursor to end

custom_style_dope = Style(
    [
        ("separator", "fg:#6C6C6C"),
        ("qmark", "fg:#FF9D00 bold"),
        ("question", ""),
        ("selected", "fg:#FF9D00"),
        ("pointer", "fg:#FF9D00 bold"),
        ("answer", "fg:#FF9D00 bold"),
    ]
)

def PromptModule(offset):

    spacer = " " * (offset - 10)

    answer = questionary.text("Choose Module:", validate=ModuleLaunchValidator, style=custom_style_dope, qmark=f"{spacer}>>").ask()

    if (answer is None):
        return (None)

    try:
        moduleId = int(answer)
    except ValueError:
        return PromptModule()

    return (moduleId)


