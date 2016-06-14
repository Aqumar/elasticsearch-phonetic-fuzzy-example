import time
from elasticsearch import Elasticsearch
from elasticsearch import helpers

ELASTICSEARCH_HOST = "localhost"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX_NAME = "phonetic_index"

es = Elasticsearch([{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT}])

if es.indices.exists(ELASTICSEARCH_INDEX_NAME):
  print("Deleting '%s' index..." % (ELASTICSEARCH_INDEX_NAME))
  res = es.indices.delete(index = ELASTICSEARCH_INDEX_NAME)
  print(" response: '%s'" % (res))

print("Creating '%s' index..." % (ELASTICSEARCH_INDEX_NAME))
request_body = {
  "settings": {
    "analysis": {
      "filter": {
        "haasephonetik": {
          "type": "phonetic",
          "encoder": "haasephonetik"
        }
      },
      "analyzer": {
        "haasephonetik": {
          "tokenizer": "standard",
          "filter": "haasephonetik"
        }
      }
    }
  },
  "mappings": {
    "type": {
      "properties": {
        "text": {
          "type": "string",
          "index": "not_analyzed",
          "fields": {
            "phonetic": {
              "type": "string",
              "analyzer": "haasephonetik"
            }
          }
        }
      }
    }
  }
}

res = es.indices.create(index = ELASTICSEARCH_INDEX_NAME, body = request_body)
print(" response: '%s'" % (res))

# Import sample data
print("Importing sample data...")
actions = []
file = open("sample_data.txt", "r")
x = 0
for line in file:
  x = x + 1

  action = {
    "_index" : ELASTICSEARCH_INDEX_NAME,
    "_type" : "type",
    "_id" : x,
    "_source" : {
      'text' : line.decode('utf-8')[0:-1]
    }
  }

  print action

  actions.append(action)

if len(actions) > 0:
  helpers.bulk(es, actions)

time.sleep(1)
print("\nRunning sample queries...\n")

def printSearchResult(caption, res):
  print(caption)
  hits = res['hits']['hits']
  for hit in hits:
    print("%0.2f %s" % (hit['_score'], hit['_source']['text']))
  print("\n")

request_body = {
  "query" : {
    "match" : {
      "text.phonetic" : {
        "query" : "Meier"
      }
    }
  },
  "size" : 15
}
result_phonetic_only = es.search(index = ELASTICSEARCH_INDEX_NAME, body = request_body)

printSearchResult("Result of search using only phonetic search:", result_phonetic_only)

request_body = {
  "query": {
    "bool": {
      "must": [
        {
          "query": {
            "match": {
              "text.phonetic": {
                "query": "Meier"
              }
            }
          }
        }],
      "should" : [
        {
          "fuzzy": {
            "text": {
              "value": "Meier",
              "fuzziness": 2
            }
          }
        }
      ]
    }
  },
  "size" : 15
}
result_phonetic_and_fuzzy2 = es.search(index = ELASTICSEARCH_INDEX_NAME, body = request_body)

printSearchResult("Result of search using phonetic search combined with fuzzy search with fuzziness 2:", result_phonetic_and_fuzzy2)

print("Script finished execution.")
