from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json
from views import get_authorized_user_ids


def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # return all of the "following" records that the current user is following

        followings = Following.query.filter_by(user_id = self.current_user.id)
        followings_json = [following.to_dict_following() for following in followings]

        return Response(json.dumps(followings_json), mimetype="application/json", status=200)

    def post(self):
        # create a new "following" record based on the data posted in the body 
        body = request.get_json()
        id = body.get('user_id')

        if id is None:
            return Response(json.dumps({'message': 'missing user id'}), mimetype="application/json", status=400)    

        else: 
            try:
                id = int(id)
            
            except:
                return Response(json.dumps({'message': 'invalid user id format'}), mimetype="application/json", status=400)

        following = User.query.get(id)

        if following is None:
            return Response(json.dumps({'message': 'invalid user id'}), mimetype="application/json", status=404)

        duplicates = Following.query.filter_by(user_id = self.current_user.id)
        
        for duplicate in duplicates: 
            
            if duplicate.following_id == id:
                return  Response(json.dumps({'message': 'duplicate following'}), mimetype="application/json", status=400)
       
        new = Following(self.current_user.id, id)
        db.session.add(new)
        db.session.commit()
        
        return Response(json.dumps(new.to_dict_following()), mimetype="application/json", status=201)
        

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "following" record where "id"=id
        delete = Following.query.get(id)
        
        try:
            id = int(id)
        
        except:
            return Response(json.dumps({'message': 'invalid id format'}), mimetype="application/json", status=400)

        if delete is None:
            return Response(json.dumps({'message': 'invalid id'}), mimetype="application/json", status=404)

        if delete.user_id is not self.current_user.id:
            return Response(json.dumps({'message': 'unauthorized user'}), mimetype="application/json", status=404)

        Following.query.filter_by(id = id).delete()
        db.session.commit()

        return Response(json.dumps({ 'message': 'Follower {0} is deleted'.format(id)}), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
