import os
import requests
from dotenv import load_dotenv

POLYGON_API_KEY = os.getenv('POLYGON_API_KEY')

class polygon:
    def __init__(self, sides):
        self.sides = sides

    def perimeter(self):
        return sum(self.sides)

    def area(self):
        raise NotImplementedError("Area calculation not implemented for this polygon.")
