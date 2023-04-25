from pymongo import MongoClient

client = MongoClient(
    'mongodb+srv://neighbourly4:UQXg0Cnn5edMoSIK@cluster0.hwmwqdi.mongodb.net/?retryWrites=true&w=majority')


def get_db():
    db = client['neighbourly']
    return db

