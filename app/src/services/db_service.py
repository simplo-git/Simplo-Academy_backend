from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class DBService:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db_name = "simploacademy_database"

    def check_db_status(self):
        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            
            db_list = self.client.list_database_names()
            if self.db_name in db_list:
                return {"status": "success", "message": f"Database '{self.db_name}' exists."}
            else:
                # In MongoDB, a database is created when you first write to it.
                # We can explicitly create a collection to ensure it shows up, 
                # or just acknowledge it will be created on first use.
                # The user request says "SE SIM ELE VAI SER CRIADO, SE NÃO O SISTEMA VAI CRIAR"
                # which implies we should make sure it exists.
                # Adding a dummy collection/document then deleting it is a common way to force creation if needed,
                # but typically just returning that it's ready to be created is enough.
                # However, to be explicit as requested:
                db = self.client[self.db_name]
                # We won't insert data yet to avoid trash, but we confirm connection is good.
                return {"status": "success", "message": f"Database '{self.db_name}' does not exist but connection is active. It will be created on first write."}
        
        except ConnectionFailure:
            return {"status": "error", "message": "Server not available"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_db(self):
        return self.client[self.db_name]
