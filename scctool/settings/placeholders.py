"""Define placeholders."""
import logging

# create logger
module_logger = logging.getLogger('scctool.placeholders')


class PlaceholderList:
    """Define placeholder list."""

    def __init__(self):
        """Init placeholder list."""
        self.__ls = "("
        self.__rs = ")"
        self.__data = {}
        self.__type = {}

    def addConnection(self, placeholder, connection):
        """Add a placeholder that connects to a function."""
        self.__data[placeholder] = connection
        self.__type[placeholder] = "connection"

    def addString(self, placeholder, string):
        """Add a placeholder as string."""
        self.__data[placeholder] = string
        self.__type[placeholder] = "string"

    def replace(self, string):
        """Replace placeholders in string."""
        for placeholder in self.__data:
            if(self.__type[placeholder] == "string"):
                replacement = self.__data[placeholder]
            elif(self.__type[placeholder] == "connection"):
                replacement = self.__data[placeholder]()
            else:
                replacement = ""

            string = string.replace(
                self.__ls + placeholder + self.__rs, replacement)

        return string

    def available(self):
        """Return a list of available placeholders."""
        placeholders = []

        for placeholder in self.__data.keys():
            placeholders.append(self.__ls + placeholder + self.__rs)

        placeholders.sort()

        return placeholders
