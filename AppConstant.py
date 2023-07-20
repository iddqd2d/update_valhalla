
class AppConstant:
    VALHALLA_DIR = "/root/valhalla_result"
    VALHALLA_THREADS = 1
    PBF_FILE_URL = "https://download.geofabrik.de/north-america/canada/new-brunswick-latest.osm.pbf"

    CHECK_EXPIRED_TIME = False
    EXPIRED_TIME = 604800  # 1 week

    TILES_DIR = VALHALLA_DIR + "/valhalla_tiles"
    TILES_TAR_FILE = VALHALLA_DIR + "/valhalla_tiles.tar"
    TEMP_TILES_TAR_FILE = VALHALLA_DIR + "/temp_valhalla_tiles.tar"
    CONFIG_FILE = VALHALLA_DIR + "/conf/valhalla.json"
    LOG_FILE_PATH = VALHALLA_DIR + "/valhalla_update.log"
    PBF_FILE_ABSOLUTE_PATH = VALHALLA_DIR + "/tiles.pbf"








