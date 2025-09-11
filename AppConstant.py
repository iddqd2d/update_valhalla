
class AppConstant:
    VALHALLA_DIR = "/root/valhalla_result"
    VALHALLA_THREADS = 1
    REGION_PBF_FILE_URL = "https://download.geofabrik.de/north-america-latest.osm.pbf"
    ADMINS_PBF_FILE_URL = "https://planet.openstreetmap.org/pbf/planet-latest.osm.pb"


    CHECK_EXPIRED_TIME = False
    EXPIRED_TIME = 604800  # 1 week

    TILES_DIR = VALHALLA_DIR + "/valhalla_tiles"
    TILES_TAR_FILE = VALHALLA_DIR + "/valhalla_tiles.tar"
    TEMP_TILES_TAR_FILE = VALHALLA_DIR + "/temp_valhalla_tiles.tar"
    CONFIG_FILE = VALHALLA_DIR + "/valhalla.json"
    LOG_FILE_PATH = VALHALLA_DIR + "/valhalla_update.log"
    REGION_PBF_FILE_ABSOLUTE_PATH = VALHALLA_DIR + "/tiles.pbf"
    ADMINS_PBF_FILE_ABSOLUTE_PATH = VALHALLA_DIR + "/admins.pbf"








