from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post
from . import can_view_post

import flask_jwt_extended

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new "Comment" based on the data posted in the body 
        body = request.get_json()
        text = body.get('text')
        post_id = body.get('post_id')
        user_id = self.current_user.id

        try:
            post_id = int(post_id)
        except:
            return Response(json.dumps({'message': 'invalid post id format'}), mimetype="application/json", status=400)

        post = Post.query.get(post_id)
        if post is None:
            return Response(json.dumps({'message': 'invalid post id'}), mimetype="application/json", status=404)
        
        if not can_view_post(post_id, self.current_user):
            return Response(json.dumps({'message': 'unauthorized post id'}), mimetype="application/json", status=404)
        
        if text is not None:
            comment = Comment(text, user_id, post_id)
            
            db.session.add(comment)
            db.session.commit()
            
            return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)
        
        else:
            return Response(json.dumps({'message': 'post missing text'}), mimetype="application/json", status=400)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete "Comment" record where "id"=id
        comment = Comment.query.get(id)

        if comment is None:
           return Response(json.dumps({'message': 'invalid id'}), mimetype="application/json", status=404)
        
        if comment.user_id is not self.current_user.id:
            return Response(json.dumps({'message': 'unathorized id'}), mimetype="application/json", status=404)

        Comment.query.filter_by(id = id).delete()
        
        db.session.commit()
 
        return Response(json.dumps({'message': 'Comment {0} is deleted'.format(id)}), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<int:id>', 
        '/api/comments/<int:id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
