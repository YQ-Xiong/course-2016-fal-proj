import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class example(dml.Algorithm):
    contributor = 'aydenbu_huangyh'
    reads = []
    writes = ['aydenbu_huangyh.lost', 'aydenbu_huangyh.found']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aydenbu_huangyh', 'aydenbu_huangyh')

        # url = 'http://cs-people.bu.edu/lapets/591/examples/lost.json'
        # response = urllib.request.urlopen(url).read().decode("utf-8")
        # r = json.loads(response)
        # s = json.dumps(r, sort_keys=True, indent=2)
        # repo.dropPermanent("lost")
        # repo.createPermanent("lost")
        # repo['aydenbu_huangyh.lost'].insert_many(r)
        #
        # url = 'http://cs-people.bu.edu/lapets/591/examples/found.json'
        # response = urllib.request.urlopen(url).read().decode("utf-8")
        # r = json.loads(response)
        # s = json.dumps(r, sort_keys=True, indent=2)
        # repo.dropPermanent("found")
        # repo.createPermanent("found")
        # repo['aydenbu_huangyh.found'].insert_many(r)
        #
        # url = "https://data.cityofboston.gov/resource/jsri-cpsq.json"
        # response = urllib.request.urlopen(url).read().decode("utf-8")
        # r = json.loads(response)
        # s = json.dumps(r, sort_keys=True, indent=2)
        # repo.dropPermanent("jsri-cpsq")
        # repo.createPermanent("jsri-cpsq")
        # repo['aydenbu_huangyh.jsri-cpsq'].insert_many(r)

        url = "https://data.cityofboston.gov/resource/u6fv-m8v4.json"
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropPermanent("hospitalLocation")
        repo.createPermanent("hospitalLocation")
        repo['aydenbu_huangyh.hospitalLocation'].insert_many(r)

        url = "https://data.cityofboston.gov/resource/bejm-5s9g.json"
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropPermanent("earningsReport")
        repo.createPermanent("earningsReport")
        repo['aydenbu_huangyh.earningsReport'].insert_many(r)

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
        Create the provenance document describing everything happening
        in this script. Each run of the script will generate a new
        document describing that invocation event.
        '''

         # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aydenbu_huangyh', 'aydenbu_huangyh')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:aydenbu_huangyh#example', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_earningsReport = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_hospitalLocation = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_hospitalLocation, this_script)
        doc.wasAssociatedWith(get_earningsReport, this_script)
        doc.usage(get_earningsReport, resource, startTime, None,
                {prov.model.PROV_TYPE:'ont:Retrieval',
                 'ont:Query':'?type=POSTAL, Earnings'
                }
            )
        doc.usage(get_hospitalLocation, resource, startTime, None,
                {prov.model.PROV_TYPE:'ont:Retrieval',
                 'ont:Query':'?type=zipcode'
                }
            )

        earningsReport = doc.entity('dat:aydenbu_huangyh#earningsReport', {prov.model.PROV_LABEL:'Earnings Report', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(earningsReport, this_script)
        doc.wasGeneratedBy(earningsReport, get_earningsReport, endTime)
        doc.wasDerivedFrom(earningsReport, resource, get_earningsReport, get_earningsReport, get_earningsReport)

        hospitalLocation = doc.entity('dat:aydenbu_huangyh#hospitalLocation', {prov.model.PROV_LABEL:'Animals Found', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(hospitalLocation, this_script)
        doc.wasGeneratedBy(hospitalLocation, get_hospitalLocation, endTime)
        doc.wasDerivedFrom(hospitalLocation, resource, get_hospitalLocation, get_hospitalLocation, get_hospitalLocation)

        repo.record(doc.serialize()) # Record the provenance document.
        repo.logout()

        return doc

example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof