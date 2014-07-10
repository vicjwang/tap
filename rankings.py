import json
import urllib


queries = ["taiwanese american new york", "tap ny", "taiwanese american professionals", "new york taiwanese", "tap new york"]

def get_rank(query):
    query = urllib.urlencode({'q': query})
    url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
    search_response = urllib.urlopen(url)
    search_results = search_response.read()
    results = json.loads(search_results)
    data = results['responseData']
    if data is None:
        return "-1"
    hits = data['results']
    for i, hit in enumerate(hits):
        if "tap-ny.org" in hit['url']:
            return str(i+1)
    print 'For more results, see %s' % data['cursor']['moreResultsUrl']
    return ">5"

def main():
    for query in queries:
        rank = get_rank(query)
        print "%s: %s" % (query, rank)
    

if __name__ == "__main__":
    main()
