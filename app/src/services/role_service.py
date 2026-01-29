from bson.objectid import ObjectId
from app.src.services.db_service import DBService
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class RoleService:
    def __init__(self):
        mongo_uri = os.getenv("MONGO")
        self.db_service = DBService(mongo_uri)
        self.collection = self.db_service.get_db()["roles"]

    def create_role(self, data: dict):
        # Set created_at
        data["created_at"] = datetime.now()
        data["updated_at"] = data["created_at"]
        
        result = self.collection.insert_one(data)
        return {"status": "success", "message": "Role created", "id": str(result.inserted_id)}

    def list_roles(self):
        roles = []
        for role in self.collection.find():
            role["_id"] = str(role["_id"])
            roles.append(role)
        return roles

    def update_role(self, role_id: str, data: dict):
        try:
            data["updated_at"] = datetime.now()
            # Prevent created_at overwrite if passed
            data.pop("created_at", None)

            result = self.collection.update_one({"_id": ObjectId(role_id)}, {"$set": data})
            if result.modified_count > 0:
                return {"status": "success", "message": "Role updated"}
            return {"status": "error", "message": "Role not found or no changes made"}
        except:
             return {"status": "error", "message": "Invalid ID"}

    def delete_role(self, role_id: str):
        try:
            result = self.collection.delete_one({"_id": ObjectId(role_id)})
            if result.deleted_count > 0:
                return {"status": "success", "message": "Role deleted"}
            return {"status": "error", "message": "Role not found"}
        except:
            return {"status": "error", "message": "Invalid ID"}
