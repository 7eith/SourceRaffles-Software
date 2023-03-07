"""********************************************************************"""
"""                                                                    """
"""   [prompt] ThreadPrompt.py                                         """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 01/09/2021 21:22:26                                     """
"""   Updated: 05/09/2021 00:44:54                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary

from questionary import Validator, ValidationError

class ThreadValidator(Validator):
    def validate(self, document):
        if len(document.text) == 0:
            raise ValidationError(
                message="Please enter a threads number",
                cursor_position=len(document.text),
            )
        try:
            min = int(document.text)
        except ValueError:
            raise ValidationError(
                message='Invalid threads number',
                cursor_position=len(document.text))  # Move cursor to end

def PromptThread(default=""):
    answer = questionary.text("Enter threads number", validate=ThreadValidator, default=default).ask()

    if (answer is None):
        return (1)

    try:
        threadsNumber = int(answer)
    except ValueError:
        return PromptThread()

    return (threadsNumber)


