import time
import subprocess
import os

from AppConstant import AppConstant
from util.FileUtil import FileUtil


class Run:

    def __init__(self):
        self.fileUtil = FileUtil.instance()

    def executeCommand(self, title, command):
        self.fileUtil.writeLog(f"Title: {title}")
        self.fileUtil.writeLog(f"Command: {command}")
        output = subprocess.getoutput(command)
        self.fileUtil.writeLog("Output: " + (output if output else "Done!"))


    def killProcessByStr(self, pid, containsStr):
        if containsStr not in subprocess.getoutput(f"ps -p {pid} -o args="):
            return
        ppid = subprocess.getoutput(f"ps -p {pid} -o ppid=")
        self.executeCommand(title="Stop Valhalla PID: ",
                             command=f"kill -9 {pid}")
        return self.killProcessByStr(ppid, containsStr)


    def updateTiles(self):
        try:
            if not os.path.exists(f"{AppConstant.VALHALLA_DIR}"):
                self.executeCommand(title=f"Create new project dir: {AppConstant.VALHALLA_DIR}",
                                    command=f"mkdir  {AppConstant.VALHALLA_DIR}")

                self.executeCommand(title=f"Create new project dir: {AppConstant.VALHALLA_DIR}",
                                    command=f"valhalla_build_config --mjolnir-tile-dir {AppConstant.TILES_DIR}"
                                            f" --mjolnir-tile-extract {AppConstant.TILES_TAR_FILE} "
                                            f" --mjolnir-timezone {AppConstant.TILES_DIR}/timezones.sqlite "
                                            f" --mjolnir-admin {AppConstant.TILES_DIR}/admins.sqlite > valhalla.json")


            if AppConstant.CHECK_EXPIRED_TIME and os.path.exists(f"{AppConstant.TILES_TAR_FILE}"):
                tilesTime = self.fileUtil.getModificationDate(f"{AppConstant.TILES_TAR_FILE}")
                if time.time() - tilesTime < AppConstant.EXPIRED_TIME:
                    self.fileUtil.writeLog("Your tiles are up to date")
                    return

            self.executeCommand(title=f"Start download region PBF file from url: {AppConstant.REGION_PBF_FILE_URL}",
                                command=f"curl -L -o {AppConstant.REGION_PBF_FILE_ABSOLUTE_PATH} {AppConstant.REGION_PBF_FILE_URL}")

            self.executeCommand(title=f"Start download admins PBF file from url: {AppConstant.ADMINS_PBF_FILE_URL}",
                                command=f"curl -L -o {AppConstant.ADMINS_PBF_FILE_ABSOLUTE_PATH} {AppConstant.ADMINS_PBF_FILE_URL}")

            if os.path.exists(f"{AppConstant.TILES_DIR}"):
                self.executeCommand(title=f"Remove old tiles data from dir: {AppConstant.TILES_DIR}",
                                    command=f"rm -r {AppConstant.TILES_DIR}/*")
            else:
                self.executeCommand(title=f"Create new tiles dir: {AppConstant.TILES_DIR}",
                                    command=f"mkdir  {AppConstant.TILES_DIR}")

            self.executeCommand(title=f"Build admins in: {AppConstant.TILES_DIR}",
                                command=f"valhalla_build_admins --config {AppConstant.CONFIG_FILE} {AppConstant.ADMINS_PBF_FILE_ABSOLUTE_PATH}")

            self.executeCommand(title=f"Build timezones in: {AppConstant.TILES_DIR}",
                                command=f"valhalla_build_timezones > {AppConstant.TILES_DIR}/timezones.sqlite")

            self.executeCommand(title=f"Build tiles in: {AppConstant.TILES_DIR}",
                                command=f"valhalla_build_tiles -c {AppConstant.CONFIG_FILE} {AppConstant.REGION_PBF_FILE_ABSOLUTE_PATH}")

            self.executeCommand(title=f"Build tiles tar file in: {AppConstant.TILES_DIR}",
                                command=f"find {AppConstant.TILES_DIR} | sort -n | tar -cf '{AppConstant.TEMP_TILES_TAR_FILE}' --no-recursion -T -")

            sizeInBytes = os.path.getsize(f"{AppConstant.TEMP_TILES_TAR_FILE}")
            if sizeInBytes == 0:
                self.fileUtil.writeLog("Build tiles tar file failed")
                return

            self.executeCommand(title="Get All Valhalla processes", command="ps -ax | grep valhalla")
            valhallaPidStr = subprocess.getoutput("pgrep 'valhalla'")
            if valhallaPidStr:
                valhallaPidArr = valhallaPidStr.split("\n")
                for valhallaPid in valhallaPidArr:
                    self.killProcessByStr(valhallaPid, "valhalla")

            if os.path.exists(f"{AppConstant.TILES_TAR_FILE}"):
                self.executeCommand(title=f"Remove old tiles tar {AppConstant.TILES_TAR_FILE}",
                                    command=f"rm {AppConstant.TILES_TAR_FILE}")


            self.executeCommand(title="Rename temp tiles tar",
                                    command=f"mv {AppConstant.TEMP_TILES_TAR_FILE} {AppConstant.TILES_TAR_FILE}")

            self.executeCommand(title=f"Start Valhalla Server",
                                    command=f"valhalla_service {AppConstant.CONFIG_FILE} {AppConstant.VALHALLA_THREADS}")
        except Exception as error:
            self.fileUtil.writeLog(f"App Exception: {error}")


if __name__ == '__main__':
    Run().updateTiles()
