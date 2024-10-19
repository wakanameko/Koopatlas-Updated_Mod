from common import *

class KP:
    @staticmethod
    def run():
        KP.app = QtWidgets.QApplication(sys.argv)

        if os.path.isfile('portable.txt'):
            KP.app.settings = QtCore.QSettings('settings_Koopatlas.ini', QtCore.QSettings.IniFormat)
        else:
            KP.app.settings = QtCore.QSettings('Koopatlas', 'Newer Team')

        KP.loadAnySettings()

        from mapdata import KPMap
        KP.map = KPMap()

        from ui import KPMainWindow

        KP.mainWindow = KPMainWindow()
        KP.mainWindow.show()

        KP.enumerateTilesets()

        KP.app.exec_()

    @classmethod
    def icon(cls, name):
        try:
            cache = cls.iconCache
        except AttributeError:
            cache = {}
            cls.iconCache = cache

        try:
            return cache[name]
        except KeyError:
            icon = QtGui.QIcon('Resources/%s.png' % name)
            cache[name] = icon
            return icon

    @classmethod
    def loadAnySettings(cls):
        global language
        global appearance
        if os.path.isfile('data.ini'):
            with open('data.ini', mode = 'r') as f:
                s = f.read().splitlines()
                appearance = s[0]
                language = s[1]
        else:
            with open('data.ini', mode = 'w') as f:
                s = 'light\neng'
                f.write(s)
                appearance = 'light'
                language = 'eng'




    @classmethod
    def enumerateTilesets(cls):
        try:
            registry = cls.knownTilesets
        except AttributeError:
            registry = {}
            cls.knownTilesets = registry
            cls.loadedTilesets = {}

        path = os.path.join(os.getcwd(), 'Tilesets')
        if not os.path.exists(path):
            os.mkdir(path)

        foundAnyTilesets = False
        for file in os.listdir(path):
            name = file[:-4]

            if file.endswith('.arc'):
                foundAnyTilesets = True
                filepath = os.path.join(path, file)
                registry[name] = {'path': filepath}

        if not foundAnyTilesets:
            if language == 'eng':
                QtWidgets.QMessageBox.warning(None, 'Warning', "Your Tilesets folder seems to be empty. You won't be able to load any world maps without them! You can get Newer Wii's world map and tileset files at <a href=\"https://github.com/Newer-Team/NewerSMBW/tree/no-translations/NewerResources\">https://github.com/Newer-Team/NewerSMBW/tree/no-translations/NewerResources</a>.")
            if language == 'jpn':
                QtWidgets.QMessageBox.warning(None, '警告', "タイルセットが見つかりません。マップを正常に読み込むために、こちらからタイルセットをダウンロードしてください。<a href=\"https://github.com/Newer-Team/NewerSMBW/tree/no-translations/NewerResources\">https://github.com/Newer-Team/NewerSMBW/tree/no-translations/NewerResources</a>")


    @classmethod
    def loadTileset(cls, name):
        from hashlib import sha256 as sha

        if name in cls.loadedTilesets:
            return True

        if name not in cls.knownTilesets:
            if language == 'eng':
                QtWidgets.QMessageBox.critical(None, 'Error', "Could not find the tileset \"%s\" in the Tilesets folder. Please put it there, restart Koopatlas, and try again." % name)
            if language == 'jpn':
                QtWidgets.QMessageBox.critical(None, 'エラー', "タイルセット \"%s\" が見つかりません。KoopatlasのTilesetsフォルダにファイルを追加し、再度試してください。" % name)
            return False

        filepath = cls.knownTilesets[name]['path']
        with open(filepath, 'rb') as file:
            data = file.read()

        tsInfo = cls.knownTilesets[name]
        newHash = sha(data).hexdigest()
        if 'hash' in tsInfo and tsInfo['hash'] == newHash:
            # file hasn't changed
            return True

        tsInfo['hash'] = newHash

        from tileset import KPTileset

        import time
        b = time.time()

        cls.loadedTilesets[name] = KPTileset.loadFromArc(data)

        e = time.time()
        print("Loading set: {0} in {1}".format(name, e-b))

        return True


    @classmethod
    def tileset(cls, name):
        cache = cls.loadedTilesets

        try:
            return cache[name]
        except KeyError:
            if cls.loadTileset(name):
                return cache[name]
            else:
                return None

