from PyQt5.QtCore import QSettings
from pymongo import MongoClient

class Database():

    def __init__(self):
        self.database = self.readSettings()
        usrpwd=''
        if self.database['username'] and self.database['password']:
            usrpwd = self.database['username']+':'+self.database['password']+'@'

        self.connection = 'mongodb://'+usrpwd+ self.database['host']+':'+self.database['port']+'/'+self.database['database_name']
        #self.check_connection()

    def check_connection(self, serverSelectionTimeoutMS=10, connectTimeoutMS=20000):
        msg = ""
        try:
            self.mongo_client = MongoClient(self.connection, serverSelectionTimeoutMS=serverSelectionTimeoutMS, connectTimeoutMS=connectTimeoutMS)
            self.mongo_client.server_info()
        except Exception as e:
            msg = str(e)
        if not msg:
            self.db = self.mongo_client.lakeer
        return False if msg else True, msg

    def fetch_department(self):
        '''
        fetch_department to get all list of departments with levels like GHMC:zone GHMC:circle GHMC:ward etc.
        :return:
        '''

        combo_list = ['-']
        try:
            departments = self.db.departments.find()
        except Exception as e:
             print (e)
        for department in departments:
            levels = self.db.levels.distinct('level_type', {'department_id': department['_id']})
            combo_list.extend([department['name']+ ':'+ level for level in levels])
        return combo_list

    def service_categories(self):
        """
        Fetch categories to be displayed in the load data list
        :return:
        """
        return self.db.service_categories.find()

    def service_per_category(self, category_id):
        """
        Fetch category wise services to be displayed in a tree format
        :param category_id:
        :return:
        """
        service_categories = self.db.services.aggregate([{"$lookup": {"localField": "_id", "from": "service_metrics",
                                                                 "foreignField": "service_id",
                                                                 "as": "metrics"}},
                                                    {"$match": {"service_category_id": category_id}}
                                                    ])
        return service_categories

    def department_polygon(self, selected_department):
        """
        Data used to load selected department geometry.
        :param selected_department:
        :return:
        """
        level_boundaries = []
        levels = selected_department.split(':')
        department = self.db.departments.find({'name': levels[0]})
        if department.count() > 0:
            level_boundaries = self.db.levels.find({'department_id': department[0]['_id'], 'level_type': levels[1]})
        return level_boundaries

    def service_metrics_geometry(self, metric_id):
        """
        service asset to be displayed layer-wise.
        :param metric_id:
        :return:
        """
        return self.db.service_assets.find({"service_metric_id": metric_id})

    def writeSettings(self, data):
        """
        Write databse configuration settings for the user.
        :param data:
        :return:
        """
        print (data)
        self.settings = QSettings("Lakeer", "configuration")
        self.settings.beginGroup("database")
        self.settings.setValue("database_name", data['database_name'])
        self.settings.setValue("host", data['host'])
        self.settings.setValue("port", data['port'])
        self.settings.setValue("username", data['username'])
        self.settings.setValue("password", data['password'])
        self.settings.endGroup()

    def readSettings(self):
        """
        Read database configuration settings for the user.
        :return:
        """
        self.settings = QSettings("Lakeer", "configuration")
        self.settings.beginGroup("database")
        config = {}
        config['database_name'] = self.settings.value("database_name") or 'lakeer'
        config['host'] = self.settings.value("host") or '127.0.0.1'
        config['port'] = self.settings.value("port") or '27017'
        config['username'] = self.settings.value("username") or ''
        config['password'] = self.settings.value("password") or ''
        self.settings.endGroup()
        return config


