# -*- coding: UTF-8 -*-

class Args:
    ''''这个类用来管理不同的参数'''
    def __init__(self):
        self.__readfile()
        self.version = self.argument_dict['version']

    def __readfile(self):
        file_object = open('argument.txt')
        text = file_object.read()
        self.argument_dict = dict(eval(text))



if __name__ == '__main__':
    args=Args()
    print(args.argument_dict)