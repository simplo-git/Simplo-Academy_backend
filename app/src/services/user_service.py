from bson.objectid import ObjectId
from app.src.services.db_service import DBService
from app.src.models.user_model import UserModel
from app.src.services.auth_service import AuthService
import os
from dotenv import load_dotenv

load_dotenv()

class UserService:
    def __init__(self):
        mongo_uri = os.getenv("MONGO")
        self.db_service = DBService(mongo_uri)
        self.collection = self.db_service.get_db()["users"]

    def create_user(self, user_data: dict):
        # Validate with Pydantic (optional here if handled in route, but good for safety)
        # user = UserModel(**user_data) # We will trust data passed from route for now or validate there
        
        # Check if email already exists
        if self.collection.find_one({"email": user_data["email"]}):
            return {"status": "error", "message": "Email already exists"}

        # Hash password
        user_data["password"] = AuthService.hash_password(user_data["password"])
        
        result = self.collection.insert_one(user_data)
        return {"status": "success", "message": "User created", "id": str(result.inserted_id)}

    def list_users(self):
        users = []
        for user in self.collection.find():
            user["_id"] = str(user["_id"])
            user.pop("password", None) # Do not return password
            users.append(user)
        return users

    def get_user(self, user_id: str):
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
                user.pop("password", None)
                return user
            return None
        except:
            return None

    def update_user(self, user_id: str, data: dict):
        try:
            if "password" in data:
                 data["password"] = AuthService.hash_password(data["password"])
            
            result = self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
            if result.modified_count > 0:
                return {"status": "success", "message": "Usuário atualizado"}
            return {"status": "error", "message": "Usuário não encontrado ou sem alterações"}
        except:
             return {"status": "error", "message": "ID inválido"}

    def delete_user(self, user_id: str):
        try:
            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count > 0:
                return {"status": "success", "message": "Usuário deletado"}
            return {"status": "error", "message": "Usuário não encontrado"}
        except:
            return {"status": "error", "message": "ID inválido"}

    def login(self, email, password):
        user = self.collection.find_one({"email": email})
        if user and AuthService.verify_password(password, user["password"]):
            user["_id"] = str(user["_id"])
            user.pop("password", None)
            return {"status": "success", "message": "Login realizado com sucesso", "user": user}
        return {"status": "error", "message": "Credenciais inválidas"}
