from flask import Response, request
from flask_restful import Resource
from models import User, Following
from views import get_authorized_user_ids
import json
from sqlalchemy import desc

class SuggestionsListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # suggestions should be any user with an ID that's not in this list:
        # print(get_authorized_user_ids(self.current_user))

        suggestions_json = [suggestion.to_dict() for suggestion in User.query.order_by(User.date_created).all() \
            if (suggestion.id not in get_authorized_user_ids(self.current_user)) and (self.current_user.id not in \
                 get_authorized_user_ids(suggestion) and (suggestion.is_disabled == False))]

        return Response(json.dumps(suggestions_json[0:7]), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        SuggestionsListEndpoint, 
        '/api/suggestions', 
        '/api/suggestions/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
