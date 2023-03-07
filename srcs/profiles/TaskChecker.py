"""********************************************************************"""
"""                                                                    """
"""   [profiles] TaskChecker.py                                        """
"""                                                                    """
"""   Author: seith <seith@synezia.com>                                """
"""                                                                    """
"""   Created: 30/08/2021 03:14:34                                     """
"""   Updated: 27/09/2021 11:06:34                                     """
"""                                                                    """
"""   Synezia Soft. (c) 2021                                           """
"""                                                                    """
"""********************************************************************"""

from utilities import Logger
from faker import Faker

class TaskChecker():

    def check_AlreadyEntered(self, task):

        if ("email" in task):
            if (task['email'] == "synezia@seith.fr"):
                return True
                
        return (False)

    def __init__(self, tasks, checkTasks=True) -> None:
        
        self.tasksList = []
        self.removedTasks = 0
        self.tasksEmails = []
        self.check = checkTasks

        # TODO improve IA, group tasks by Region and while region is same don't generate new Faker Instance, when its change switch it
        
        try:
            countryCode = tasks[0]['country_code']
            localize = "{}_{}".format(countryCode.lower(), countryCode.upper())
            self.Faker = Faker(localize)
            Logger.debug(f"[SourceIA] Using {countryCode} as default provider")
        except:
            Logger.debug("[SourceIA] Using World as default provider")
            self.Faker = Faker()

        for task in tasks:

            if self.check:

                if (not self.check_AlreadyEntered(task)):
                    self.formatTask(task)
                else:
                    self.removedTasks += 1
                    Logger.error(f"[{task['email']}] This email is already used!")

            else:
                self.formatTask(task)

    def formatTask(self, task: dict):
        hasError = False

        if "email" in task:
        
            if (task['email'] in self.tasksEmails):
                hasError = True
                Logger.error(f"[{task['email']}] Duplicate email!")
            
        for key, value in task.items():

            if (key == "first_name" and value.lower() == "random"):
                task[key] = self.Faker.first_name()

            if (key == "last_name" and value.lower() == "random"):
                task[key] = self.Faker.last_name()
                
            if (key == "phone" and value.lower() == "random"):
                task[key] = self.Faker.phone_number()

            if (key == "street" and value.lower() == "random"):
                task[key] = self.Faker.street_name()

            if (key == "zip" and value.lower() == "random"):
                task[key] = self.Faker.postcode()

            if (key == "city" and value.lower() == "random"):
                task[key] = self.Faker.city()

            if (key == "country" and value.lower() == "random"):
                task[key] = self.Faker.current_country()

            if (key == "country_code" and value.lower() == "random"):
                task[key] = self.Faker.current_country_code()

            if (key == "house_number" and value.lower() == "random"):
                task[key] = self.Faker.building_number()
                
            if (str(key).startswith("cc_") and value.lower() == "random"):
                if (not hasError):
                    Logger.error(f"[{task['email']}] Unsupported RANDOM field! Credit Card can't be random!")
                    hasError = True

        if "email" in task:
            if (not hasError):
                self.tasksEmails.append(task['email'])

                if ("status" not in task):
                    newTask = {"status": "PENDING"}
                    newTask.update(task)
                    self.tasksList.append(newTask)
                else:
                    self.tasksList.append(task)
        else:
            if ("status" not in task):
                newTask = {"status": "PENDING"}
                newTask.update(task)
                newTask["email"] = "Unknown"
                self.tasksList.append(newTask)
            else:
                task["email"] = "Unknown"
                self.tasksList.append(task)

    def getTasks(self):

        return (self.tasksList)