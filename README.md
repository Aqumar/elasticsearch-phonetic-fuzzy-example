Phonetic + Fuzzy Search in Elasticsearch for retrieving relevant last names
===========================================================================

This example illustrates the combination of a phonetic search with a fuzzy search to find last names similar to those typed in a search query. 

As test data a list of most common german last names from wikipedia (https://de.wiktionary.org/wiki/Verzeichnis:Deutsch/Liste_der_häufigsten_Nachnamen_Deutschlands) is used.
A snapshot of this list taken at 2016-06-10 is included in this repository as sample_data.txt

The python script run.py creates an elasticsearch index, fills it with the sample data and runs sample queries illustrating various options of searching last names phonetically similar to the search term. 

Prerequisites
=============
This script requires the elasticsearch python client installed on your machine. You can install this via pip by calling:

```sh
pip install elasticsearch
```

The script uses the localhost and port 9200 for elasticsearch and the index name 'phonetic_index' as default. You can change these values by editing the constants at the top of the script file.

The script also requires elasticsearch to run. 

Details
==============

The script creates the following index inside elasticsearch. The important point here is that we use the analyzer "haasephonetik" which is optimized for the german language. 

```json
PUT /phonetic_index
{
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
```

The script then evaluations the following queries:

# Phonetic search only

```json
GET /phonetic_index/type/_search
{
  "query" : {
    "match" : {
      "text.phonetic" : {
        "query" : "Meier"
      }
    }
  },
  "size" : 15
}
```

# Phonetic search combined with fuzzy query with fuzziness 2

```json
GET /phonetic_index/type/_search
{
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
        }
      ],
      "should": [
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
  }
}
```

As you can see from the scripts' results, this query yields better results than the pure phonetic query. 
