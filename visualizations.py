import os
import elasticsearch
from elasticsearch import helpers
import urllib3
from pprint import pprint
from collections import Counter

import numpy as np                      # To help us perform operations such as percentile
import pandas as pd                     # To help us read the csv and write to it
from pandas import Series, DataFrame    # To help us convert the read data to a DataFrame
import os.path                          # To check if a file already exists, if it does then create another one

import seaborn as sns
import matplotlib.pyplot as plt
sns.set()

urllib3.disable_warnings()

PART_INDEX = "part-read-prod"

def main(category,size):
    es_url = os.getenv('ES_URL', 'http://admin.us-east-1.octopart.net:9201/')

    # Setup the ES client
    c = elasticsearch.Elasticsearch(es_url)

    body = {
      "size": 0,
        "query": {
        "terms": {
          "best_category.id": [
            4320
          ]
        }
        },
      "aggs": {
        "resistance": {
          "terms": {
            "field": "specs2.50.numbers",
            "size": 50
          },
          "aggs": {
            "median_value": {
              "percentiles": {
                "field": "median_price_1000"
              }
            }
          }
        }
      }
    }

    response = c.search(index=PART_INDEX, doc_type='part', body=body)
    data = DataFrame([])
    resistance = []
    price = []

    for bucket in response['aggregations']['resistance']['buckets']:
        resistance.append(bucket["key"])
        price.append(bucket["median_value"]["values"]["50.0"])

    data["Current Rating"] = resistance
    data["Median Price"] = price
    print data

    plotrec = sns.lmplot("Current Rating","Median Price",data=data,fit_reg = True, ci=None)
    #plotrec = sns.distplot(data)
    plt.ylim(0,)
    #plt.xlim(-1,12)
    sns.plt.title("Price vs Current for Voltage Regulators - Linear")
    sns.plt.show()

if __name__ == "__main__":
    main(['6309'],100)