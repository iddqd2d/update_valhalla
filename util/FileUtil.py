import glob
import json
import os
import requests
from datetime import datetime


from AppConstant import AppConstant


class FileUtil:
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def writeToFile(self, data, absolutePathToFile):
        with open(absolutePathToFile, 'w') as im:
            json.dump(data, im)
            im.write('\n')

    def writeLog(self, data, consoleLogNeed=True):
        with open(AppConstant.LOG_FILE_PATH, 'a') as file:
            dtString = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            file.write(f"{dtString} - {data}")
            if consoleLogNeed: print(f"{dtString} - {data}")

    def getFileNameFromAbsoluteFilePath(self, absoluteFilePath):
        return absoluteFilePath.split("/")[-1]

    def getAbsolutePathToFile(self, filepath, fileName):
        paths = glob.glob(filepath + fileName, recursive=True)
        return paths[0] if (paths) else None

    def getModificationDate(self, filePath):
        return os.path.getmtime(filePath)
