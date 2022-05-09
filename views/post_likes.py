from flask import Response, request
from flask_restful import Resource
from models import LikePost, db
import json
from . import can_view_post
from sqlalchemy import and_

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "like_post" based on the data posted in the body 
        body = request.get_json()

        try:
            post_id = int(body.get('post_id'))
        except:
            return Response(json.dumps({'message': 'invalid post id format'}), mimetype="application/json", status=400)

        post_db = (
            db.session
                .query(LikePost.id)
                .filter(LikePost.id == body.get('post_id'))
                .all()
        )

        if len(post_db) != 1:
            return Response(json.dumps({"messsage": 'invalid post id'}), mimetype="application/json", status=404) 

        # if not can_view_post(post_id, self.current_user):
        #     return Response(json.dumps({'message': 'unauthorized user'}), mimetype="application/json", status=404)

        likepost_db = (
            db.session
                .query(LikePost.post_id)
                .filter(and_(LikePost.user_id == self.current_user.id, LikePost.post_id == post_id))
                .all()
        )

        if len(likepost_db) >= 1:
            return Response(json.dumps({'message': 'duplicated like'}), mimetype="application/json", status=400)
        
        if not can_view_post(post_id, self.current_user):
            return Response(json.dumps({'message': 'unauthorized user'}), mimetype="application/json", status=404)
       
        like = LikePost(self.current_user.id, post_id)
        
        db.session.add(like)
        db.session.commit()
        
        return Response(json.dumps(like.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "like_post" where "id"=id
        try:
            id = int(id)
        
        except:
            return Response(json.dumps({'message': 'invalid id format'}), mimetype="application/json", status=404)
        
        post = LikePost.query.get(id)

        if post is None:
           return Response(json.dumps({'message': 'invalid id'}), mimetype="application/json", status=404)

        if post.user_id is not self.current_user.id:
            return Response(json.dumps({'message': 'unauthorized id'}), mimetype="application/json", status=404)

        LikePost.query.filter_by(id = id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Like {0} is deleted'.format(id)}), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/likes', 
        '/api/posts/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/likes/<int:id>', 
        '/api/posts/likes/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )