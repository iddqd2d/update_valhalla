import re
import time
import subprocess
import os

from AppConstant import AppConstant
from util.FileUtil import FileUtil


class Run:

    ERROR_KEYWORDS = [r"runtime_error", r"Aborted", r"command not found"]
    ERROR_REGEX = re.compile("|".join(ERROR_KEYWORDS), re.IGNORECASE)

    def __init__(self):
        self.fileUtil = FileUtil.instance()

        if not AppConstant.VALHALLA_DIR:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            AppConstant.VALHALLA_DIR = os.path.abspath(os.path.expanduser(base_dir))
            os.makedirs(AppConstant.VALHALLA_DIR, exist_ok=True)

        self.TILES_DIR = os.path.join(AppConstant.VALHALLA_DIR, "valhalla_tiles")
        self.TILES_TAR_FILE = os.path.join(AppConstant.VALHALLA_DIR, "valhalla_tiles.tar")
        self.TEMP_TILES_TAR_FILE = os.path.join(AppConstant.VALHALLA_DIR, "temp_valhalla_tiles.tar")
        self.CONFIG_FILE = os.path.join(AppConstant.VALHALLA_DIR, "valhalla.json")
        self.REGION_PBF_FILE_ABSOLUTE_PATH = os.path.join(AppConstant.VALHALLA_DIR, "tiles.pbf")
        self.ADMINS_PBF_FILE_ABSOLUTE_PATH = os.path.join(AppConstant.VALHALLA_DIR, "admins.pbf")

    def scanAndRaise(self, title: str, output: str):
        if not output:
            return
        m = self.ERROR_REGEX.search(output)
        if m:
            start = max(0, m.start() - 80)
            end = min(len(output), m.end() + 80)
            ctx = output[start:end]
            self.fileUtil.writeLog(f"[error-scan] context: {ctx}")
            raise RuntimeError(f"'{title}' failed due to error keywords in output")


    def executeCommand(self, title, command, stopOnKeywords: bool = True):
        self.fileUtil.writeLog(f"Title: {title}")
        self.fileUtil.writeLog(f"Command: {command}")
        output = subprocess.getoutput(command)
        self.fileUtil.writeLog("Output: " + (output if output else "Done!"))
        if stopOnKeywords:
            self.scanAndRaise(title, output)
        return output

    def killProcessByStr(self, pid, containsStr):
        if containsStr not in subprocess.getoutput(f"ps -p {pid} -o args="):
            return
        ppid = subprocess.getoutput(f"ps -p {pid} -o ppid=")
        self.executeCommand(title="Stop Valhalla PID: ",
                             command=f"kill -9 {pid}")
        return self.killProcessByStr(ppid, containsStr)


    def updateTiles(self):
        try:
            if not os.path.exists(f"{self.CONFIG_FILE}"):
                self.executeCommand(title=f"Create config file: {self.CONFIG_FILE}",
                                    command=f"valhalla_build_config --mjolnir-tile-dir {self.TILES_DIR}"
                                            f" --mjolnir-tile-extract {self.TILES_TAR_FILE} "
                                            f" --mjolnir-timezone {self.TILES_DIR}/timezones.sqlite "
                                            f" --mjolnir-admin {self.TILES_DIR}/admins.sqlite > {self.CONFIG_FILE}")


            if AppConstant.CHECK_EXPIRED_TIME and os.path.exists(f"{self.TILES_TAR_FILE}"):
                tilesTime = self.fileUtil.getModificationDate(f"{self.TILES_TAR_FILE}")
                if time.time() - tilesTime < AppConstant.EXPIRED_TIME:
                    self.fileUtil.writeLog("Your tiles are up to date")
                    return

            self.executeCommand(title=f"Start download region PBF file from url: {AppConstant.REGION_PBF_FILE_URL}",
                                command=f"curl -L -o {self.REGION_PBF_FILE_ABSOLUTE_PATH} {AppConstant.REGION_PBF_FILE_URL}")

            self.executeCommand(title=f"Start download admins PBF file from url: {AppConstant.ADMINS_PBF_FILE_URL}",
                                command=f"curl -L -o {self.ADMINS_PBF_FILE_ABSOLUTE_PATH} {AppConstant.ADMINS_PBF_FILE_URL}")

            if os.path.exists(f"{self.TILES_DIR}"):
                self.executeCommand(title=f"Remove old tiles data from dir: {self.TILES_DIR}",
                                    command=f"rm -r {self.TILES_DIR}/*")
            else:
                self.executeCommand(title=f"Create new tiles dir: {self.TILES_DIR}",
                                    command=f"mkdir  {self.TILES_DIR}")

            self.executeCommand(title=f"Build admins in: {self.TILES_DIR}",
                                command=f"valhalla_build_admins --config {self.CONFIG_FILE} {self.ADMINS_PBF_FILE_ABSOLUTE_PATH}")

            self.executeCommand(title=f"Build timezones in: {self.TILES_DIR}",
                                command=f"valhalla_build_timezones > {self.TILES_DIR}/timezones.sqlite")

            self.executeCommand(title=f"Build tiles in: {self.TILES_DIR}",
                                command=f"valhalla_build_tiles -c {self.CONFIG_FILE} {self.REGION_PBF_FILE_ABSOLUTE_PATH}")

            self.executeCommand(title=f"Build tiles tar file in: {self.TILES_DIR}",
                                command=f"find {self.TILES_DIR} | sort -n | tar -cf '{self.TEMP_TILES_TAR_FILE}' --no-recursion -T -")

            sizeInBytes = os.path.getsize(f"{self.TEMP_TILES_TAR_FILE}")
            if sizeInBytes < 10 * 1024 * 1024 * 1024:
                self.fileUtil.writeLog("Build tiles tar file failed")
                return

            self.executeCommand(title="Get All Valhalla processes", command="ps -ax | grep valhalla")
            valhallaPidStr = subprocess.getoutput("pgrep 'valhalla'")
            if valhallaPidStr:
                valhallaPidArr = valhallaPidStr.split("\n")
                for valhallaPid in valhallaPidArr:
                    self.killProcessByStr(valhallaPid, "valhalla")

            if os.path.exists(f"{self.TILES_TAR_FILE}"):
                self.executeCommand(title=f"Remove old tiles tar {self.TILES_TAR_FILE}",
                                    command=f"rm {self.TILES_TAR_FILE}")


            self.executeCommand(title="Rename temp tiles tar",
                                    command=f"mv {self.TEMP_TILES_TAR_FILE} {self.TILES_TAR_FILE}")

            self.executeCommand(title=f"Start Valhalla Server",
                                    command=f"valhalla_service {self.CONFIG_FILE} {AppConstant.VALHALLA_THREADS}")
        except Exception as error:
            self.fileUtil.writeLog(f"App Exception: {error}")


if __name__ == '__main__':
    Run().updateTiles()
