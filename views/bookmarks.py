from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db, Post
import json
from . import can_view_post

import flask_jwt_extended

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        # get all bookmarks owned by the current user
        bookmarks = Bookmark.query.filter_by(user_id=self.current_user.id).order_by('id').all()
        bookmarks_json = [bookmark.to_dict() for bookmark in bookmarks]
 
        return Response(json.dumps(bookmarks_json), mimetype="application/json", status=200)

    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new "bookmark" based on the data posted in the body 
        body = request.get_json()

        if not body.get('post_id'):
            return Response(json.dumps({"message": "missing post id"}), mimetype="application/json", status=400)

        try:
             post_id = int(body.get('post_id'))

        except:
            return Response(json.dumps({'message': 'invalid post id format'}), mimetype="application/json", status=400)

        # if not can_view_post(body.get("post_id"), self.current_user):
        #     return Response(json.dumps({"messsage": "unauthorized post id"}), mimetype="application/json", status=404) 

        bookmark_db= (
            db.session
                .query(Bookmark.id)
                .filter(Bookmark.post_id == body.get('post_id'))
                .filter(Bookmark.user_id == self.current_user.id)
                .all()
        )

        if len(bookmark_db) >= 1:
            return Response(json.dumps({"messsage": "duplicate post"}), mimetype="application/json", status=400) 

        if not can_view_post(body.get("post_id"), self.current_user):
            return Response(json.dumps({"messsage": "unauthorized post id"}), mimetype="application/json", status=404) 

        post_db = (
            db.session
                .query(Post.id)
                .filter(Post.id == body.get('post_id'))
                .all()
        )

        if len(post_db) != 1:
            return Response(json.dumps({"messsage": "invalid post id"}), mimetype="application/json", status=404) 
        
        bookmark = Bookmark(self.current_user.id, body.get('post_id'))

        db.session.add(bookmark)
        db.session.commit()
        
        return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)


class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete "bookmark" record where "id"=id
        bookmark = Bookmark.query.get(id)
        
        try:
            id = int(id) 
        
        except:
            return Response(json.dumps({'message': 'invalid id format'}), mimetype="application/json", status=404)
        
        if bookmark is None:
            return Response(json.dumps({'message': 'invalid id'}), mimetype="application/json", status=404)
        
        if bookmark.user_id is not self.current_user.id:
            return Response(json.dumps({'message': 'unauthorized id'}), mimetype="application/json", status=404)
        
        Bookmark.query.filter_by(id = id).delete()
        db.session.commit()

        return Response(json.dumps({'message': 'Bookmark {0} successfully deleted.'.format(id)}), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<int:id>', 
        '/api/bookmarks/<int:id>',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
