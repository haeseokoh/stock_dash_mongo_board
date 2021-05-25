from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web import server
from index import server as application

resource = WSGIResource(reactor, reactor.getThreadPool(), application)
site = server.Site(resource)
reactor.listenTCP(8050, site)
reactor.run()

# C:\Python\Python372_64\python.exe D:/project/pythonProject/stock_dash_mongo_board/twisted_run_tac.py