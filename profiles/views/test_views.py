from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from profiles.models import CustomUser, Follow, Post, Like, Comment, Favorite, Story
from io import BytesIO
from django.contrib.auth import get_user_model

class UserTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = CustomUser.objects.create_user(
            username='testuser1',
            fullname='Test User One',
            email='testuser1@example.com',
            dob='1990-01-01',
            password='password123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='testuser2',
            fullname='Test User Two',
            email='testuser2@example.com',
            dob='1991-02-02',
            password='password123'
        )

        # Obtain JWT token for user1
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

        # Define URLs
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.list_users_url = reverse('list_users')

        # Test data for signup and login
        self.signup_data = {
            'username': 'newuser',
            'fullname': 'New User',
            'email': 'newuser@example.com',
            'dob': '1995-05-05',
            'password': 'newpassword123'
        }

        self.login_data = {
            'username_or_email': 'testuser1',
            'password': 'password123'
        }

    def test_signup(self):
        response = self.client.post(self.signup_url, self.signup_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Signup successful')

    def test_login(self):
        response = self.client.post(self.login_url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Token', response.data)

    def test_list_users_without_search(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.list_users_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)  # Exclude current user

    def test_list_users_with_search(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.list_users_url, {'username': 'testuser2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['username'], 'testuser2')

    def test_list_users_search_no_results(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.list_users_url, {'username': 'nonexistentuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')

class FollowTests(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = CustomUser.objects.create_user(
            username='testuser1',
            fullname='Test User One',
            email='testuser1@example.com',
            dob='1990-01-01',
            password='password123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='testuser2',
            fullname='Test User Two',
            email='testuser2@example.com',
            dob='1991-02-02',
            password='password123'
        )
        self.user3 = CustomUser.objects.create_user(
            username='testuser3',
            fullname='Test User Three',
            email='testuser3@example.com',
            dob='1992-03-03',
            password='password123'
        )

        # Obtain JWT token for user1
        refresh = RefreshToken.for_user(self.user1)
        self.access_token = str(refresh.access_token)

        # Define URLs
        self.follow_url = reverse('follow-user', args=[self.user2.id])
        self.unfollow_url = reverse('unfollow-user', args=[self.user2.id])
        self.followers_count_url = reverse('followers-count')
        self.following_count_url = reverse('following-count-user')
        self.followers_url = reverse('user-followers')
        self.following_url = reverse('user-following')

    def test_follow_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.follow_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], f"You followed {self.user2.username}")
        self.assertTrue(Follow.objects.filter(follower=self.user1, followed=self.user2).exists())

    def test_unfollow_user(self):
        Follow.objects.create(follower=self.user1, followed=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.delete(self.unfollow_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "You have unfollowed this user.")
        self.assertFalse(Follow.objects.filter(follower=self.user1, followed=self.user2).exists())

    def test_user_follower_count(self):
        Follow.objects.create(follower=self.user2, followed=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.followers_count_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['follower_count'], 1)

    def test_user_following_count(self):
        Follow.objects.create(follower=self.user1, followed=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.following_count_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['following_count'], 1)

    # def test_user_followers(self):
    #     # Create follow relationship
    #     Follow.objects.create(follower=self.user2, followed=self.user1)
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    #     response = self.client.get(self.followers_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    #     # Verify correct followers are returned
    #     followers_usernames = [f['username'] for f in response.data['data']]
    #     self.assertIn(self.user2.username, followers_usernames)
    #     self.assertEqual(len(response.data['data']), 1)

    # def test_user_following(self):
    #     # Create follow relationship
    #     Follow.objects.create(follower=self.user1, followed=self.user2)
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    #     response = self.client.get(self.following_url, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    #     # Verify correct following users are returned
    #     following_usernames = [f['username'] for f in response.data['data']]
    #     self.assertIn(self.user2.username, following_usernames)
    #     self.assertEqual(len(response.data['data']), 1)

class PostTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.create_post_url = reverse('create-post')

    def test_create_post(self):
        data = {
            'title': 'Test Post',
            'description': 'This is a test post.',
            'image': ''  # Use a valid image file path if testing with images
        }
        response = self.client.post(self.create_post_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Post created successfully.')
        # Ensure the post is created by the logged-in user
        self.assertEqual(Post.objects.filter(user=self.user).count(), 1)

class PostListTests(APITestCase):  
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        # Log in to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        if not self.token:
            raise ValueError("Token not found in login response")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Set up URLs
        self.create_post_url = reverse('create-post')
        self.list_posts_url = reverse('post-list')
        
        # Create a post
        self.client.post(self.create_post_url, {
            'title': 'Test Post',
            'description': 'This is a test post.',
            'image': ''  # Mock or provide a valid image file path if needed
        }, format='multipart')
    
    def test_list_posts(self):
        response = self.client.get(self.list_posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully retrieved all posts.')
        self.assertGreater(len(response.data['data']), 0)  # Ensure there is at least one post

class PostUpdateTests(APITestCase):
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.create_post_url = reverse('create-post')
        self.post_id = None
        self.update_post_url = None
        
        # Create a post and capture the post ID
        response = self.client.post(self.create_post_url, {
            'title': 'Test Post',
            'description': 'This is a test post.',
            'image': ''
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post_id = response.data['data']['id']
        self.update_post_url = reverse('post-detail', kwargs={'pk': self.post_id})
        
        self.updated_data = {
            'title': 'Updated Post Title',
            'description': 'Updated description.',
            'image': ''
        }

    def test_update_post(self):
        response = self.client.put(self.update_post_url, self.updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Post updated successfully.')
        post = Post.objects.get(pk=self.post_id)
        self.assertEqual(post.title, 'Updated Post Title')  # Check if the title was updated

class PostDeleteTests(APITestCase):
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.create_post_url = reverse('create-post')
        self.delete_post_url = None
        
        # Create a post and capture the post ID
        response = self.client.post(self.create_post_url, {
            'title': 'Test Post',
            'description': 'This is a test post.',
            'image': ''
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.post_id = response.data['data']['id']
        self.delete_post_url = reverse('post-detail', kwargs={'pk': self.post_id})

    def test_delete_post(self):
        response = self.client.delete(self.delete_post_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Post deleted successfully.')
        self.assertFalse(Post.objects.filter(pk=self.post_id).exists())  # Ensure the post is deleted

class FollowingPostsTests(APITestCase):
    
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.followed_user = CustomUser.objects.create_user(
            username='followeduser',
            password='password123',
            fullname='Followed User',
            email='followeduser@example.com',
            dob='1990-01-01'
        )
        Follow.objects.create(follower=self.user, followed=self.followed_user)
        
        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.create_post_url = reverse('create-post')
        self.following_posts_url = reverse('following-posts')
        
        # Create a post by the followed user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        post_response = self.client.post(self.create_post_url, {
            'title': 'Followed User Post',
            'description': 'This post is by someone I am following.',
            'image': ''
        }, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Debugging: Print the response data of post creation
        # print("Post Creation Response:", post_response.data)
        
        # Also, ensure the post is created by the followed_user
        Post.objects.create(
            user=self.followed_user,
            title='Followed User Post',
            description='This post is by someone I am following.',
            image=None
        )

    def test_following_posts(self):
        response = self.client.get(self.following_posts_url)
        
        # Debugging: print the response data
        # print("Following Posts Response:", response.data)  
        
        # Debugging: Check if posts are correctly saved and associated
        # print("All Posts:", Post.objects.all())
        # print("Posts by Followed User:", Post.objects.filter(user=self.followed_user))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully retrieved posts from users you are following.')
        self.assertGreater(len(response.data['data']), 0)  # Ensure there is at least one post from followed users

class FollowingAndFollowersPostsTests(APITestCase):
    
    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.followed_user = CustomUser.objects.create_user(
            username='followeduser',
            password='password123',
            fullname='Followed User',
            email='followeduser@example.com',
            dob='1990-01-01'
        )
        self.follower_user = CustomUser.objects.create_user(
            username='followeruser',
            password='password456',
            fullname='Follower User',
            email='followeruser@example.com',
            dob='1985-01-01'
        )
        
        # Create follow relationships
        Follow.objects.create(follower=self.user, followed=self.followed_user)
        Follow.objects.create(follower=self.follower_user, followed=self.user)
        
        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.create_post_url = reverse('create-post')
        self.following_and_followers_posts_url = reverse('following-and-followers-posts')
        
        # Create a post by the followed user
        self.client.post(self.create_post_url, {
            'title': 'Post by Followed User',
            'description': 'This post is by a user I am following.',
            'image': ''
        }, format='multipart', HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create a post by the follower user
        Post.objects.create(
            user=self.follower_user,
            title='Post by Follower User',
            description='This post is by a user who follows me.',
            image=None
        )

    def test_following_and_followers_posts(self):
        response = self.client.get(self.following_and_followers_posts_url)
        # Debugging: print the response data
        # print("Following and Followers Posts Response:", response.data)  
        
        # Debugging: Check if posts are correctly saved and associated
        # print("All Posts:", Post.objects.all())
        # print("Posts by Followed User:", Post.objects.filter(user=self.followed_user))
        # print("Posts by Follower User:", Post.objects.filter(user=self.follower_user))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully retrieved posts from users you are following and those following you.')
        self.assertGreater(len(response.data['data']), 0)  # Ensure there is at least one post from followed or follower users

class SharePostToTimelineTests(APITestCase):

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='password123',
            fullname='Other User',
            email='otheruser@example.com',
            dob='1990-01-01'
        )

        # Create a valid image file
        self.image_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=self.generate_image_content(),
            content_type="image/jpeg"
        )

        # Create a post with an image by the other user
        self.existing_post = Post.objects.create(
            user=self.other_user,
            title='Original Post',
            description='This is an original post.',
            image=self.image_file  # Add the image here
        )

        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.share_post_url = reverse('share-post-to-timeline')

    def generate_image_content(self):
        # Generate a simple image content
        image = BytesIO()
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(image, format='JPEG')
        image.seek(0)
        return image.read()

    def test_share_post_to_timeline(self):
        # Share the post
        response = self.client.post(self.share_post_url, {
            'post_id': self.existing_post.id
        }, format='multipart')  # Use multipart format for file uploads

        # # Debugging: print the response data
        # print("Share Post Response:", response.data)  
        
        # Check if the post is shared correctly
        shared_post = Post.objects.filter(
            user=self.user,
            title=self.existing_post.title,
            description=self.existing_post.description
        ).first()
        
        # Debugging: Print the shared post
        # print("Shared Post:", shared_post)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Post reshared to timeline successfully.')
        self.assertIsNotNone(shared_post)  # Ensure that the post was created
        self.assertEqual(shared_post.user, self.user)  # Ensure that the post is associated with the correct user
        self.assertEqual(shared_post.title, self.existing_post.title)
        self.assertEqual(shared_post.description, self.existing_post.description)
        # Check that the image is copied correctly
        if self.existing_post.image:
            self.assertTrue(shared_post.image)
            self.assertNotEqual(shared_post.image, '')  # Check that the image field is not empty
        else:
            self.assertIsNone(shared_post.image)

class LikePostTests(APITestCase):

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='password123',
            fullname='Other User',
            email='otheruser@example.com',
            dob='1990-01-01'
        )

        # Create a post
        self.post = Post.objects.create(
            user=self.other_user,
            title='Test Post',
            description='This is a test post.'
        )

        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.like_post_url = reverse('like-post', kwargs={'post_id': self.post.id})

    def test_like_post(self):
        # Like the post
        response = self.client.post(self.like_post_url, {}, format='json')
        # Debugging: print the response data
        # print("Like Post Response:", response.data)  

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Post liked successfully.')

        # Verify that the post is liked
        like = Like.objects.filter(user=self.user, post=self.post).first()
        self.assertIsNotNone(like)

    def test_unlike_post(self):
        # First, like the post
        self.client.post(self.like_post_url, {}, format='json')

        # Unlike the post
        response = self.client.post(self.like_post_url, {}, format='json')
        # Debugging: print the response data
        # print("Unlike Post Response:", response.data)  

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Post unliked successfully.')

        # Verify that the post is unliked
        like = Like.objects.filter(user=self.user, post=self.post).first()
        self.assertIsNone(like)

    def test_like_nonexistent_post(self):
        # Attempt to like a post that does not exist
        nonexistent_post_url = reverse('like-post', kwargs={'post_id': 999})
        response = self.client.post(nonexistent_post_url, {}, format='json')
        # Debugging: print the response data
        # print("Like Nonexistent Post Response:", response.data)  

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Post not found.')

class CommentOnPostTests(APITestCase):

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='password123',
            fullname='Other User',
            email='otheruser@example.com',
            dob='1990-01-01'
        )

        # Create a post
        self.post = Post.objects.create(
            user=self.other_user,
            title='Test Post',
            description='This is a test post.'
        )

        # Login to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.comment_post_url = reverse('comment-post', kwargs={'post_id': self.post.id})

    def test_comment_on_post(self):
        # Comment on the post
        comment_data = {
            'content': 'This is a test comment.'
        }
        response = self.client.post(self.comment_post_url, comment_data, format='json')
        # Debugging: print the response data
        # print("Comment On Post Response:", response.data)  

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], comment_data['content'])

        # Verify that the comment is created
        comment = Comment.objects.filter(user=self.user, post=self.post).first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, comment_data['content'])

    def test_comment_on_nonexistent_post(self):
        # Attempt to comment on a post that does not exist
        nonexistent_post_url = reverse('comment-post', kwargs={'post_id': 999})
        comment_data = {
            'content': 'This should fail.'
        }
        response = self.client.post(nonexistent_post_url, comment_data, format='json')
        # Debugging: print the response data
        # print("Comment On Nonexistent Post Response:", response.data)  

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Post not found.')

class EditCommentTests(APITestCase):

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='password123',
            fullname='Other User',
            email='otheruser@example.com',
            dob='1990-01-01'
        )

        # Create a post
        self.post = Post.objects.create(
            user=self.other_user,
            title='Test Post',
            description='This is a test post.'
        )

        # Create a comment
        self.comment = Comment.objects.create(
            user=self.user,
            post=self.post,
            content='Original comment content.'
        )

        # Login to get the token for self.user
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # URL for editing the comment
        self.edit_comment_url = reverse('edit-comment', kwargs={'pk': self.comment.id})

    def test_edit_comment_success(self):
        # Successfully edit the comment
        updated_data = {'content': 'Updated comment content.'}
        response = self.client.patch(self.edit_comment_url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], updated_data['content'])

        # Verify the comment is updated in the database
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, updated_data['content'])

    def test_edit_comment_forbidden(self):
        # Log in as the other user to get their token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'otheruser',
            'password': 'password123'
        }, format='json')
        other_user_token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_user_token}')
        
        updated_data = {'content': 'Updated content by another user.'}
        response = self.client.patch(self.edit_comment_url, updated_data, format='json')

        # Debugging: print the response data
        # print("Edit Comment Forbidden Response:", response.data)  

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Expecting 404 due to object mismatch
        self.assertEqual(response.data['detail'], 'No Comment matches the given query.')

    def test_edit_nonexistent_comment(self):
        # Attempt to edit a comment that does not exist
        nonexistent_comment_url = reverse('edit-comment', kwargs={'pk': 999})
        updated_data = {'content': 'Content for nonexistent comment.'}
        response = self.client.patch(nonexistent_comment_url, updated_data, format='json')
        
        # Debugging: print the response data
        # print("Edit Nonexistent Comment Response:", response.data)  

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Comment matches the given query.')
    
class DeleteCommentTests(APITestCase):
    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='password123',
            fullname='Other User',
            email='otheruser@example.com',
            dob='1990-01-01'
        )

        # Create a post
        self.post = Post.objects.create(
            user=self.other_user,
            title='Test Post',
            description='This is a test post.'
        )

        # Create a comment by self.user
        self.comment = Comment.objects.create(
            user=self.user,
            post=self.post,
            content='This is a test comment.'
        )

        # Login to get the token for self.user
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # URL for deleting a comment
        self.delete_comment_url = reverse('delete-comment', kwargs={'pk': self.comment.id})

    def test_delete_comment_success(self):
        # Attempt to delete the comment by the comment owner
        response = self.client.delete(self.delete_comment_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
        self.assertEqual(response.data['message'], 'Comment deleted successfully.')

    def test_delete_comment_forbidden(self):
        # Login as another user
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'otheruser',
            'password': 'password123'
        }, format='json')
        other_user_token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_user_token}')

        # Attempt to delete the comment by another user
        response = self.client.delete(self.delete_comment_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'You do not have permission to delete this comment.')

    def test_delete_nonexistent_comment(self):
        # Attempt to delete a non-existent comment
        nonexistent_comment_url = reverse('delete-comment', kwargs={'pk': 999})
        response = self.client.delete(nonexistent_comment_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Comment matches the given query.')

class DeleteAnyCommentTests(APITestCase):

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='password123',
            fullname='Other User',
            email='otheruser@example.com',
            dob='1990-01-01'
        )

        # Create a post
        self.post = Post.objects.create(
            user=self.user,  # The user is the post owner
            title='Test Post',
            description='This is a test post.'
        )

        # Create a comment on the post
        self.comment = Comment.objects.create(
            user=self.other_user,  # Another user created the comment
            post=self.post,
            content='This is a test comment.'
        )

        # Login to get the token for self.user (post owner)
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # URL for deleting a comment
        self.delete_comment_url = reverse('delete-any-comment', kwargs={'post_id': self.post.id, 'pk': self.comment.id})

    def test_delete_any_comment_success(self):
        # Attempt to delete a comment by the post owner
        response = self.client.delete(self.delete_comment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Comment deleted successfully.')
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_any_comment_forbidden(self):
        # Login as another user
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'otheruser',
            'password': 'password123'
        }, format='json')
        other_user_token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_user_token}')

        # Attempt to delete the comment by a user who is not the post owner
        response = self.client.delete(self.delete_comment_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to delete this comment.')

    def test_delete_nonexistent_comment(self):
        # Attempt to delete a non-existent comment
        nonexistent_comment_url = reverse('delete-any-comment', kwargs={'post_id': self.post.id, 'pk': 999})
        response = self.client.delete(nonexistent_comment_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No Comment matches the given query.')

class PostCommentsTests(APITestCase):

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )

        # Create a post
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            description='This is a test post.'
        )

        # Create comments on the post
        self.comment1 = Comment.objects.create(
            user=self.user,
            post=self.post,
            content='First comment on the post.'
        )
        self.comment2 = Comment.objects.create(
            user=self.user,
            post=self.post,
            content='Second comment on the post.'
        )

        # URL for getting comments on a post
        self.post_comments_url = reverse('post-comments', kwargs={'post_id': self.post.id})

    def test_get_post_comments_success(self):
        response = self.client.get(self.post_comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Successfully retrieved all post comments.')
        self.assertEqual(len(response.data['data']), 2)  # Expecting 2 comments

    def test_get_post_comments_post_not_found(self):
        nonexistent_post_url = reverse('post-comments', kwargs={'post_id': 999})
        response = self.client.get(nonexistent_post_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Post not found.')
    
class AddFavoriteTests(APITestCase):

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            fullname='Test User',
            email='testuser@example.com',
            dob='2000-01-01'
        )

        # Create a post
        self.post = Post.objects.create(
            user=self.user,
            title='Test Post',
            description='This is a test post.'
        )

        # URL for adding/removing a favorite
        self.add_favorite_url = reverse('add_or_remove_favorite', kwargs={'post_id': self.post.id})

        # Log in to get the token
        login_response = self.client.post(reverse('login'), {
            'username_or_email': 'testuser',
            'password': 'testpassword'
        }, format='json')
        self.token = login_response.data.get('Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_add_favorite_success(self):
        response = self.client.post(self.add_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Post added to favorites.')
        self.assertTrue(Favorite.objects.filter(user=self.user, post=self.post).exists())

    def test_remove_favorite_success(self):
        # First add the favorite
        self.client.post(self.add_favorite_url)
        response = self.client.post(self.add_favorite_url)  # This should remove the favorite
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Post removed from favorites.')
        self.assertFalse(Favorite.objects.filter(user=self.user, post=self.post).exists())

    def test_post_not_found(self):
        nonexistent_post_url = reverse('add_or_remove_favorite', kwargs={'post_id': 999})
        response = self.client.post(nonexistent_post_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Post not found.')

# class ListFavoritesTests(APITestCase):
    
#     def setUp(self):
#         # Create users
#         self.user = CustomUser.objects.create_user(
#             username='testuser',
#             password='testpassword',
#             fullname='Test User',
#             email='testuser@example.com',
#             dob='2000-01-01'
#         )
        
#         self.other_user = CustomUser.objects.create_user(
#             username='otheruser',
#             password='otherpassword',
#             fullname='Other User',
#             email='otheruser@example.com',
#             dob='1990-01-01'
#         )

#         # Create posts
#         self.post = Post.objects.create(
#             user=self.user,
#             title='Test Post',
#             description='This is a test post.'
#         )
#         self.other_post = Post.objects.create(
#             user=self.other_user,
#             title='Other Post',
#             description='This is another test post.'
#         )

#         # Create a favorite
#         Favorite.objects.create(user=self.user, post=self.post)

#         # URL for listing favorites
#         self.list_favorites_url = reverse('list_favorites')

#     def authenticate(self):
#         # Log in to get the token
#         login_response = self.client.post(reverse('login'), {
#             'username_or_email': 'testuser',
#             'password': 'testpassword'
#         }, format='json')
#         self.token = login_response.data.get('Token')
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

#     def test_list_favorites_authenticated(self):
#         self.authenticate()
#         response = self.client.get(self.list_favorites_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['code'], status.HTTP_200_OK)
#         self.assertEqual(response.data['message'], 'Successfully retrieved all favorite posts.')
#         self.assertIn('data', response.data)
#         self.assertEqual(len(response.data['data']), 1)  # Assuming there is one favorite for the user

#     def test_list_favorites_unauthenticated(self):
#         # Ensure no authentication is applied
#         response = self.client.get(self.list_favorites_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

# User = get_user_model()

# class CreateStoryTests(APITestCase):

#     def setUp(self):
#         # Create users
#         self.user = CustomUser.objects.create_user(
#             username='testuser',
#             fullname='Test User',
#             email='testuser@example.com',
#             dob='2000-01-01',
#             password='testpassword'
#         )

#         # Create a post for sharing in stories
#         self.post = Post.objects.create(
#             user=self.user,
#             title='Test Post',
#             description='This is a test post.'
#         )

#         # URL for creating a story
#         self.create_story_url = reverse('create-story')

#     def authenticate(self):
#         # Log in to get the token
#         login_response = self.client.post(reverse('login'), {
#             'username_or_email': 'testuser',
#             'password': 'testpassword'
#         }, format='json')
#         self.token = login_response.data.get('Token')
#         self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

#     def test_create_story(self):
#         self.authenticate()
#         # Create a dummy image file if your model requires an image field
#         image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

#         data = {
#             'description': 'This is a test story.',
#             'image': image,  # Provide a valid image
#             'shared_post': self.post.id
#         }
#         response = self.client.post(self.create_story_url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['code'], status.HTTP_201_CREATED)
#         self.assertEqual(response.data['message'], 'Story created successfully.')
#         self.assertIn('data', response.data)
#         self.assertEqual(response.data['data']['description'], data['description'])
#         self.assertEqual(response.data['data']['shared_post'], self.post.id)