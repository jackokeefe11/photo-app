from flask import Response, request
from flask_restful import Resource
from models import LikePost, db, LikeComment
import json
from . import can_view_post
from sqlalchemy import and_
from views import get_authorized_user_ids

class CommentLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "like_comment" based on the data posted in the body 
        body = request.get_json()

        try:
            comment_id = int(body.get('comment_id'))
            post_id = int(body.get('post_id'))
        
        except:
            return Response(json.dumps({'message': 'invalid comment id format'}), mimetype="application/json", status=400)

        comment_db = (
            db.session
                .query(LikeComment.id)
                .filter(LikeComment.id == body.get('comment_id'))
                .all()
        )

        if len(comment_db) != 1:
            return Response(json.dumps({"messsage": 'invalid comment id'}), mimetype="application/json", status=404) 

        if not can_view_post(post_id, self.current_user):
            return Response(json.dumps({'message': 'unauthorized user'}), mimetype="application/json", status=404)

        likecomment_db = (
            db.session
                .query(LikeComment.comment_id)
                .filter(and_(LikeComment.user_id == self.current_user.id, LikeComment.comment_id == comment_id))
                .all()
        )

        if len(likecomment_db) >= 1:
            return Response(json.dumps({'message': 'duplicated like'}), mimetype="application/json", status=400)
       
        like = LikeComment(self.current_user.id, comment_id)
        
        db.session.add(like)
        db.session.commit()
        
        return Response(json.dumps(like.to_dict()), mimetype="application/json", status=201)

class CommentLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "like_comment" where "id"=id
        try:
            id = int(id)
        
        except:
            return Response(json.dumps({'message': 'invalid id format'}), mimetype="application/json", status=404)
        
        comment = LikeComment.query.get(id)

        if comment is None:
           return Response(json.dumps({'message': 'invalid id'}), mimetype="application/json", status=404)

        if comment.user_id is not self.current_user.id:
            return Response(json.dumps({'message': 'unauthorized id'}), mimetype="application/json", status=404)

        LikeComment.query.filter_by(id = id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Like {0} is deleted'.format(id)}), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        CommentLikesListEndpoint, 
        '/api/comments/likes', 
        '/api/comments/likes/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        CommentLikesDetailEndpoint, 
        '/api/comments/likes/<int:id>', 
        '/api/comments/likes/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
