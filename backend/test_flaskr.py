"""
Module: test_trivia_app
Purpose: This module contains unit tests for the Trivia Flask application, 
         including tests for categories, questions, and quiz functionality.
Dependencies:
    - json: For handling JSON responses.
    - os: To interact with the operating system, though unused here.
    - unittest: For the testing framework.
    - sqlalchemy.orm: To interact with the database.
    - flaskr.create_app: To create the app instance for testing.
    - models: For database models such as Question and Category.
"""

import json
import os
import unittest
from sqlalchemy.orm import sessionmaker
from flaskr import create_app
from models import db, Question, Category
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """
        Purpose: Define test variables and initialize the application for testing.
        Setup:
            - Sets up a test database path and configuration.
            - Initializes the app with the test configuration.
            - Creates all required database tables for testing.
        """
        self.database_name = os.getenv('DB_NAME_TEST')
        self.database_user = os.getenv('DB_USER')
        self.database_password = os.getenv('DB_PASSWORD')
        self.database_host = os.getenv('DB_HOST')
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """
        Purpose: Cleanup tasks to run after each test.
        Note: Dropping all tables is commented out, likely to preserve test data.
        """
        pass

    def test_get_paginated_questions(self):
        """
        Test: Verify the /questions endpoint returns paginated questions.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - Total questions and questions list are returned.
            - Categories are included in the response.
        """
        res = self.client.get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_questions_beyond_valid_page(self):
        """
        Test: Verify a 404 error is returned for a non-existent page.
        Assertions:
            - Status code is 404.
            - Success flag is False.
            - Error message indicates "resource not found."
        """
        res = self.client.get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        """
        Test: Verify the /categories endpoint returns a list of categories.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - Categories list is not empty.
        """
        res = self.client.get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_non_existing_category(self):
        """
        Test: Verify a 404 error for requesting non-existent categories.
        Assertions:
            - Status code is 404.
            - Success flag is False.
            - Error message indicates "resource not found."
        """
        res = self.client.get('/categories/99/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_question(self):
        """
        Test: Verify a new question can be added successfully.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - Total questions count increases by 1.
        """
        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        with self.app.app_context():
            total_questions_before = len(Question.query.all())

        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)

        with self.app.app_context():
            total_questions_after = len(Question.query.all())

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)

    def test_422_add_question(self):
        """
        Test: Verify adding a question with incomplete data returns a 422 error.
        Assertions:
            - Status code is 422.
            - Success flag is False.
            - Error message indicates "unprocessable."
        """
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        res = self.client.post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_question(self):
        """
        Test: Verify a question can be deleted successfully.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - Deleted question is removed from the database.
        """
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        with self.app.app_context():
            question.insert()
            question_id = question.id

        res = self.client.delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        with self.app.app_context():
            question = db.session.get(Question, question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    def test_422_sent_deleting_non_existing_question(self):
        """
        Test: Verify a 422 error for attempting to delete a non-existent question.
        Assertions:
            - Status code is 422.
            - Success flag is False.
            - Error message indicates "unprocessable."
        """
        res = self.client.delete('/questions/a')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_questions(self):
        """
        Test: Verify searching for questions by term returns correct results.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - The 'questions' field contains results based on search term.
            - The 'total_questions' field is populated.
        """
        new_search = {'searchTerm': 'a'}
        res = self.client.post('/questions/search', json=new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_400_search_question(self):
        """
        Test: Verify a 400 error when missing or empty search term 
              for the search questions endpoint.
        Assertions:
            - Status code is 400.
            - Success flag is False.
            - Error message indicates "Search term is required."
        """
        new_search = {}  # Empty search term should trigger a 404 error
        res = self.client.post('/questions/search', json=new_search)
        data = json.loads(res.data)
        print(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Search term is required")

    def test_search_no_results(self):
        """
        Test: Verify searching for questions by term returns no results.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - The 'questions' field contains results based on search term.
            - The 'total_questions' field is populated.
        """
        no_result_search = {"searchTerm": "dog"}
        res = self.client.post('/questions/search', json=no_result_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data['questions'], [])
        self.assertEqual(data['total_questions'], 0)


    def test_get_questions_per_category(self):
        """
        Test: Verify retrieving questions for a specific category.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - Questions for the specified category are returned.
            - 'total_questions' and 'current_category' fields are populated.
        """
        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions_per_category(self):
        """
        Test: Verify a 404 error is returned when trying to get questions for a non-existent category.
        Assertions:
            - Status code is 404.
            - Success flag is False.
            - Error message indicates "resource not found."
        """
        res = self.client.get('/categories/99/questions')  # Invalid category
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        """
        Test: Verify that a quiz round can be played successfully with a selected category.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - The quiz results are returned.
        """
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 5}}

        res = self.client.post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_play_quiz(self):
        """
        Test: Verify a 404 error is returned if required fields are missing for a quiz.
        Assertions:
            - Status code is 404.
            - Success flag is False.
            - Error message indicates missing required fields: quiz_category and previous_question.
        """
        new_quiz_round = {'previous_questions': []}  # Missing 'quiz_category'
        res = self.client.post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "quiz_category and previous_question is required")

    def test_create_category_200(self):
        """
        Test: Verify successfully creating a new category.
        Assertions:
            - Status code is 200.
            - Success flag is True.
            - 'created' field contains the new category's ID.
            - The created category is valid (check type).
        """
        new_category = {'category': 'Rocket'}
        res = self.client.post('/categories', json=new_category)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('created', data)
        self.assertIsInstance(data['created'], int)  # Assuming `created` is the category ID

    def test_create_category_404(self):
        """
        Test: Verify a 404 error is returned when category data is missing or invalid.
        Assertions:
            - Status code is 404.
            - Success flag is False.
            - Error message indicates "Category name is required."
        """
        invalid_category = {}  # Missing category field
        res = self.client.post('/categories', json=invalid_category)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "Category name is required")
        self.assertFalse(data['success'])

    def test_create_category_duplicate(self):
        """
        Test: Verify a 400 error is returned when trying to create a category that already exists.
        Assertions:
            - Status code is 400.
            - Success flag is False.
            - Error message indicates "Category already exists."
        """
        with self.app.app_context():
            category = Category(type='Poll')
            db.session.add(category)
            db.session.commit()

        duplicate_category = {'category': 'Poll'}  # Duplicate category name
        res = self.client.post('/categories', json=duplicate_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], "Category already exists")
        self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

