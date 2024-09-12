from pydantic import BaseModel

class A(BaseModel):
    a: str

class B(A):
    b: str
