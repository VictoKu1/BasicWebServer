"""Tests for the Flask application."""
import json
from app.models import Comment


class TestRoutes:
    """Test Flask routes."""
    
    def test_index_page(self, client):
        """Test index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Anonymous Forum' in response.data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_get_comments_empty(self, client):
        """Test getting comments when database is empty."""
        response = client.get('/api/comments')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_post_comment_api(self, client, db):
        """Test posting a comment via API."""
        comment_data = {'content': 'This is a test comment'}
        response = client.post(
            '/api/comments',
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['content'] == 'This is a test comment'
        assert 'created_at' in data
        
        # Verify comment was saved
        comments = Comment.query.all()
        assert len(comments) == 1
        assert comments[0].content == 'This is a test comment'
    
    def test_post_comment_empty(self, client):
        """Test posting empty comment returns error."""
        comment_data = {'content': '   '}
        response = client.post(
            '/api/comments',
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_post_comment_missing_content(self, client):
        """Test posting comment without content returns error."""
        response = client.post(
            '/api/comments',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_post_comment_too_long(self, client):
        """Test posting comment that's too long returns error."""
        long_content = 'x' * 5001
        comment_data = {'content': long_content}
        response = client.post(
            '/api/comments',
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_post_comment_form(self, client, db):
        """Test posting a comment via form."""
        response = client.post(
            '/post',
            data={'content': 'Form test comment'},
            follow_redirects=False
        )
        assert response.status_code == 302  # Redirect
        
        # Verify comment was saved
        comments = Comment.query.all()
        assert len(comments) == 1
        assert comments[0].content == 'Form test comment'
    
    def test_get_comments_ordered(self, client, db):
        """Test comments are returned in chronological order."""
        # Add multiple comments
        comments_data = [
            'First comment',
            'Second comment',
            'Third comment'
        ]
        
        for content in comments_data:
            comment = Comment(content=content)
            db.session.add(comment)
        db.session.commit()
        
        response = client.get('/api/comments')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data) == 3
        assert data[0]['content'] == 'First comment'
        assert data[1]['content'] == 'Second comment'
        assert data[2]['content'] == 'Third comment'


class TestModels:
    """Test database models."""
    
    def test_comment_creation(self, db):
        """Test creating a comment."""
        comment = Comment(content='Test comment')
        db.session.add(comment)
        db.session.commit()
        
        assert comment.id is not None
        assert comment.content == 'Test comment'
        assert comment.created_at is not None
    
    def test_comment_to_dict(self, db):
        """Test comment to_dict method."""
        comment = Comment(content='Test comment')
        db.session.add(comment)
        db.session.commit()
        
        comment_dict = comment.to_dict()
        assert 'id' in comment_dict
        assert 'content' in comment_dict
        assert 'created_at' in comment_dict
        assert comment_dict['content'] == 'Test comment'
