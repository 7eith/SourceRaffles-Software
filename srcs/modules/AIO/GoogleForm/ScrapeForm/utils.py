"""********************************************************************"""
"""                                                                    """
"""   [ScrapeForm] utilities.py                                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 20/09/2021 14:59:39                                     """
"""   Updated: 01/10/2021 14:23:24                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

import questionary

from questionary import Validator, ValidationError, prompt

class GoogleFormURLValidator(Validator):
	def validate(self, document):
		if (not str(document.text).startswith("https://docs.google.com/forms/")):
			raise ValidationError(
				message='Please enter a Google Form URL',
				cursor_position=len(document.text))

def PromptGoogleFormURL(default=""):
    answer = questionary.text("Enter URL of the Google Form:", validate=GoogleFormURLValidator, default=default).ask()

    if (answer is None):
        return None

    return (answer)

def getFieldType(identifier):
    if (identifier == 0):
        return ("SMALL_TEXT")
    if (identifier == 1):
        return ("LARGE_TEXT")
    if (identifier == 2):
        return ("MULTIPLE_CHOICE")
    if (identifier == 3):
        return ("DROPDOWN")
    if (identifier == 4):
        return ("CHECKBOX")
    if (identifier == 6):
        return ("TEXT")
    if (identifier == 8):
        return ("NEW_PAGE")
    if (identifier == 9):
        return ("DATE")
    if (identifier == 11):
        return ("IMAGE")
    return ("UNKNOWN")
