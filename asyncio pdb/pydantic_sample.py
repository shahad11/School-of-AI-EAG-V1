from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

user = User(name="John", age=30, email="john@example.com")
print(user)

