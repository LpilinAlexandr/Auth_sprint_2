from gevent import monkey

monkey.patch_all()

from app import main

app = main()
