from flask import Flask
from flask_restful import Api, Resource

backend = Flask(__name__)
api = Api(backend)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


api.add_resource(HelloWorld, '/hello-world')
