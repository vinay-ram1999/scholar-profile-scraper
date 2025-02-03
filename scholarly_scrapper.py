from scholarly import scholarly
from scholarly import ProxyGenerator

pg = ProxyGenerator()
pg.FreeProxies()
scholarly.use_proxy(pg)

search_query = scholarly.search_author('Prateek Shekhar')
first_author_result = next(search_query)

author = scholarly.fill(first_author_result )
scholarly.pprint(author['scholar_id'])

first_publication = author['publications'][0]
first_publication_filled = scholarly.fill(first_publication)
#scholarly.pprint(first_publication_filled)


