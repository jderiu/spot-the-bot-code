from pymongo import MongoClient
from templates.src.utils import load_config

config = load_config()

DATABASE_NAME = config['database_name']
SAMPLED_COLLECTION_NAME = config['sampled_collection_name']
ANNOTATED_COLLECTION_NAME = config['labelled_collection_name']
PACKET_COLLECTION_NAME = config['package_collection_name']

SEMI_SUPERVISED_COLLECTION_NAME = config['unlabelled_data']

client = MongoClient(
    config['host'],
    config['port'],
    username=config['user'],
    password=config['password'],
    authSource=DATABASE_NAME
)

db = client[DATABASE_NAME]
sampled_collection = db[SAMPLED_COLLECTION_NAME]
labelled_collection = db[ANNOTATED_COLLECTION_NAME]
package_collection = db[PACKET_COLLECTION_NAME]
semi_supervised_collection = db[SEMI_SUPERVISED_COLLECTION_NAME]
