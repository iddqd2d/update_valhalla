import time
import subprocess
import os

from AppConstant import AppConstant
from util.FileUtil import FileUtil


class Run:

    def __init__(self):
        self.fileUtil = FileUtil.instance()

    def executeCommand(self, title, command):
        output = subprocess.getoutput(command)
        log = f"{title} \nCommand: {command}\nOutput: "
        log += output if output else "Done!"
        self.fileUtil.writeLog(log)

    def updateTiles(self):
        try:
            if AppConstant.CHECK_EXPIRED_TIME and os.path.exists(f"{AppConstant.TILES_DIR}"):
                tilesTime = self.fileUtil.getModificationDate(f"{AppConstant.TILES_DIR}")
                if time.time() - tilesTime < AppConstant.EXPIRED_TIME:
                    self.fileUtil.writeLog("Your tiles are up to date")
                    return

            self.executeCommand(title=f"Start download PBF file from url: {AppConstant.PBF_FILE_URL}",
                                command=f"curl -o {AppConstant.PBF_FILE_ABSOLUTE_PATH} {AppConstant.PBF_FILE_URL}")

            if os.path.exists(f"{AppConstant.TILES_DIR}"):
                self.executeCommand(title=f"Remove old tiles from dir: {AppConstant.TILES_DIR}",
                                    command=f"rm -r {AppConstant.TILES_DIR}/*")

            self.executeCommand(title=f"Build admins in: {AppConstant.TILES_DIR}",
                                command=f"valhalla_build_admins --config {AppConstant.CONFIG_FILE} {AppConstant.PBF_FILE_ABSOLUTE_PATH}")

            self.executeCommand(title=f"Build timezones in: {AppConstant.TILES_DIR}",
                                command=f"valhalla_build_timezones > {AppConstant.TILES_DIR}/timezones.sqlite")

            self.executeCommand(title=f"Build tiles in: {AppConstant.TILES_DIR}",
                                command=f"valhalla_build_tiles -c {AppConstant.CONFIG_FILE} {AppConstant.PBF_FILE_ABSOLUTE_PATH}")

            self.executeCommand(title=f"Build tiles tar file in: {AppConstant.TILES_DIR}",
                                command=f"find {AppConstant.TILES_DIR} | sort -n | tar -cf '{AppConstant.TEMP_TILES_TAR_FILE}' --no-recursion -T -")

            sizeInBytes = os.path.getsize(f"{AppConstant.TEMP_TILES_TAR_FILE}")
            if sizeInBytes == 0:
                self.fileUtil.writeLog("Build tiles tar file failed")
                return

            valhallaPid = subprocess.getoutput("pgrep valhalla")
            if (valhallaPid):
                self.executeCommand(title="Stop Valhalla Server",
                                    command=f"kill -9 {valhallaPid}")

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
