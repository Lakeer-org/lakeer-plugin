from PyQt5.QtCore import QSettings
from pymongo import MongoClient
import datetime

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

    def create_metrics_subcategory(self, tree_selection, layer_selection):
        """
        Method to create service metrics entry for the new layer. This contains layer description.
        :param tree_selection: sub category where the layer will be saved.
        :param layer_selection: layer to save.
        :return:
        """
        service_id, _id = None, None
        flag = False

        try:
            #Find the sub category id of the service
            services = self.db.services.find({'service_type' : tree_selection})
            if services:
                service_id = services[0]['service_category_id']

            if service_id:
                document = { 'name': layer_selection.replace(' ', '_'),
                             'display_name': layer_selection.replace('_', ' '),
                             'service_id': service_id
                             }

                #Check if service metrics already there. If found return the id
                found_entry = None
                #found_entry = self.db.service_metrics.find(document)

                if found_entry:
                    _id = found_entry[0]['_id']
                else:
                    #Find the count for setting up the position of the service metrics
                    count = self.db.service_metrics.find({'service_id':service_id}).count()
                    document.update({'crs': {},
                                     'updated_at': str(datetime.datetime.now()),
                                     'created_at':str(datetime.datetime.now()),
                                     'position':count+1,
                                     'description': layer_selection,
                                     'is_visible': True,
                                     'data_source': 'QGIS',
                                     'data_verification': '',
                                     'vintage': ''
                                     })
                    _id = self.db.service_metrics.insert(document)
            flag = True
        except Exception as e:
            print (e)
        return flag, _id

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


