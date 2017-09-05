import logging

# create logger
module_logger = logging.getLogger('scctool.placeholders')


class PlaceholderList:

    def __init__(self):
        self.__ls = "("
        self.__rs = ")"
        self.__data = {}
        self.__type = {}

    def addConnection(self, placeholder, connection):
        self.__data[placeholder] = connection
        self.__type[placeholder] = "connection"

    def addString(self, placeholder, string):
        self.__data[placeholder] = string
        self.__type[placeholder] = "string"

    def replace(self, string):
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

        placeholders = []

        for placeholder in self.__data.keys():
            placeholders.append(self.__ls + placeholder + self.__rs)

        placeholders.sort()

        return placeholders
