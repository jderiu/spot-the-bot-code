from templates.src.mongo_client import sampled_collection, PACKET_COLLECTION_NAME, package_collection
from os.path import join
import random
from templates.src.packaging.naive_strategy import Naive

data_path = 'data/uri_dumps'

BASE_URL = 'http://160.85.252.225:5003/pkgsg?id='

ofile = open(join(data_path, '{}.csv'.format(PACKET_COLLECTION_NAME)), 'wt', encoding='utf-8')
ofile.write('uri\n')
results = sampled_collection.find({})
package_collection.remove({})

strategy = Naive(list(results), 20, segments=[5, 9, 13]) #
#strategy = RatioStrategy(list(results), 20, 4, segments=[3, 5, 9])

uri_list = []
for package in strategy.create_chunks():
    data_point = {}
    data_point['package'] = package
    inserted_id = package_collection.insert_one(data_point)
    pid = inserted_id.inserted_id
    url = BASE_URL + str(pid)
    uri_list.append(url)

random.shuffle(uri_list)
for url in uri_list:
    ofile.write(url + '\n')

ofile.close()