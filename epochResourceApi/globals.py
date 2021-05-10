from pytz import timezone

config = None
TZ = None
logger = None

def init(app):
    """共通変数初期化
    """
    global config
    global TZ
    global logger

    config = app.config
    TZ = timezone(config['TZ'])
    logger = app.logger

