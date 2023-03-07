"""********************************************************************"""
"""                                                                    """
"""   [prompt] DelayPrompt.py                                          """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 16:32:15                                     """
"""   Updated: 04/09/2021 16:38:54                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary

from questionary import Validator, ValidationError, prompt

class DelayValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Please enter a delay",
                cursor_position=len(document.text),
            )

        values = document.text.split(",")

        if (len(values) != 2):
            raise ValidationError(
                message='Enter a delay in seconds like : 5, 45 (Must be an Number separated by comma)',
                cursor_position=len(document.text))  # Move cursor to end

        try:
            min = int(values[0])
            max = int(values[1])
        except ValueError:
            raise ValidationError(
                message='Enter a delay in seconds like : 5, 45 (Must be an Number separated by comma)',
                cursor_position=len(document.text))  # Move cursor to end

def PromptDelay(default=""):
    answer = questionary.text("Enter delay in seconds here (Separated by comma like 1,5)", validate=DelayValidator, default=default).ask()

    if (answer is None):
        return None, None

    values = answer.split(",")

    try:
        min = int(values[0])
        max = int(values[1])
    except ValueError:
        return PromptDelay()

    return (min, max)


