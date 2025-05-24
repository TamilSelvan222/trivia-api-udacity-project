from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

"""
Function: paginate_questions
Purpose: Handles pagination for a list of questions.
Parameters:
    - request: The HTTP request object to retrieve the 'page' query parameter.
    - selection: A list of questions to paginate.
Returns: A list of formatted questions for the requested page.
Logic:
    - Determines the start and end indices based on the requested page number.
    - Formats the questions and returns only the subset of questions for the current page.
"""


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


"""
Function: create_app
Purpose: Creates and configures the Flask application, including database setup,
         CORS configuration, and error handling.
Parameters:
    - test_config: Optional configuration for testing purposes (default: None).
Returns: The configured Flask app instance.
Setup:
    - Initializes the Flask app.
    - Sets up the database connection, including the test configuration if provided.
    - Configures CORS to allow cross-origin requests from specified origins.
    - Applies middleware for setting CORS headers after every request.
"""


def create_app(test_config=None):

    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    """
    Set up CORS:
    - Allows cross-origin requests from the specified origin (http://localhost:3000).
    - Supports credentials to handle secure connections.
    """
    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True,
    )

    with app.app_context():
        db.create_all()

    """
    Middleware: after_request
    Purpose: Adds Access-Control-Allow headers to all HTTP responses to manage CORS.
    Logic:
        - Allows specific headers like Content-Type and Authorization.
        - Permits HTTP methods such as GET, PUT, POST, DELETE, and OPTIONS.
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    Endpoint: /categories
    Method: GET
    Purpose: Retrieve all available categories.
    Response: A JSON object containing categories as a dictionary.
    Errors: 404 - If no categories are found.
    """

    @app.route("/categories")
    def retrieve_categories():

        try:
            categories = Category.query.order_by(Category.type).all()
          
            return jsonify({"success": True, "categories": {
               category.id: category.type for category in categories}, })
        
        except Exception as e:
            print(f"Error: {e}")
            abort(404, description="resource not found")

    """
    Endpoint: /questions
    Method: GET
    Purpose: Retrieve all questions, paginated by 10 questions per page.
    Response: A JSON object containing questions, total questions, and categories.
    Errors: 404 - If no questions are found for the requested page.
    """

    @app.route("/questions")
    def retrieve_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            categories = Category.query.order_by(Category.type).all()

            if len(current_questions) == 0:
                abort(404, description="resource not found")

            return jsonify(
                {
                    "success": True,
                    "questions": current_questions,
                    "total_questions": len(selection),
                    "categories": {
                        category.id: category.type for category in categories},
                    "current_category": None,
                })
        except Exception as e:
            print(f"Error: {e}")
            abort(404, description="resource not found")

    """
    Endpoint: /questions/<question_id>
    Method: DELETE
    Purpose: Delete a specific question by its ID.
    Response: A JSON object confirming the deletion of the question.
    Errors: 422 - If the question cannot be deleted.
    """

    @app.route("/questions/<question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404, description="Question not found")
            question.delete()
            return jsonify({"success": True, "deleted": question_id})
        except BaseException:
            abort(422)

    """
    Endpoint: /questions
    Method: POST
    Purpose: Add a new question.
    Response:
      - If adding: Confirms the creation of the question.
    Errors:
      - 400 - If the request is missing required fields
      - 422 - If the request cannot be processed.
    """

    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json()

        try:
            required_fields = (
                "question", "answer", "difficulty", "category")
            if not all(field in body for field in required_fields):
                abort(400, description="Missing required fields")

            new_question = body["question"]
            new_answer = body["answer"]
            new_difficulty = body["difficulty"]
            new_category = body["category"]

            if not new_question.strip() or not new_answer.strip():
                abort(400, description="Question and Answer cannot be empty or only whitespace")

            question = Question(
                question=new_question,
                answer=new_answer,
                difficulty=int(new_difficulty),
                category=int(new_category),
            )
            question.insert()

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                }
            ),201
        except Exception as e:
            print(f"Error: {e}")
            abort(422, description="Unprocessable request")

    """
    Endpoint: /questions/search
    Method: POST
    Purpose: search for questions based on a search term.
    Response:
      - Returns matching questions and the total number of matches.
    Errors:
      - 400 - If the request is missing required fields or the search term is invalid.
      - 422 - If the request cannot be processed.
    """

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        
        data = request.get_json()
        search_term = data.get('searchTerm', '').strip()

        if not search_term:
            abort(400, description="Search term is required")
        try:
            # Search questions in the database
            results = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).all()

            if not results:
                return jsonify({
                    "success": True,
                    "questions": [],
                    "total_questions": 0
                }), 200

            # Format the results
            formatted_questions = [q.format() for q in results]

            return jsonify({
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(formatted_questions)
            }), 200

        except Exception as e:
            print(f"Error: {e}")
            abort(422, description="Unprocessable request")

    """
    Endpoint: /categories/<int:category_id>/questions
    Method: GET
    Purpose: Retrieve questions filtered by a specific category ID.
    Response: A JSON object containing questions, total questions, and the category ID.
    Errors: 404 - If the category or questions for the category are not found.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def retrieve_questions_by_category(category_id):

        try:
            questions = Question.query.filter(
                Question.category == str(category_id)
            ).all()
            if not questions:
                abort(404, description="resource not found")

            return jsonify(
                {
                    "success": True,
                    "questions": [question.format() for question in questions],
                    "total_questions": len(questions),
                    "current_category": category_id,
                }
            )
        except BaseException:
            abort(404, description="resource not found")

    """
    Endpoint: /quizzes
    Method: POST
    Purpose: Retrieve a random question for a quiz session based on a category
             and previously asked questions.
    Response: A JSON object containing a single question.
    Errors:
       - 400 - If the request is missing required fields.
        -422 - If the request cannot be processed.
    """

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        body = request.get_json()

        if not ("quiz_category" in body and "previous_questions" in body):
            abort(404, description="quiz_category and previous_question is required")
        try:
            category = body.get("quiz_category")
            previous_questions = body.get("previous_questions")

            if category["type"] == "click":
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))
                ).all()
            else:
                available_questions = (
                    Question.query.filter_by(category=category["id"])
                    .filter(Question.id.notin_((previous_questions)))
                    .all()
                )

            new_question = (
                available_questions[
                    random.randrange(0, len(available_questions))
                ].format()
                if len(available_questions) > 0
                else None
            )

            return jsonify({"success": True, "question": new_question})
        except BaseException:
            abort(422)

    """
    Endpoint: /categories
    Method: POST
    Purpose: Add a new category to the database.
    Response: A JSON object confirming the creation of the category.
    Errors:
      - 404 - If the category name is missing or empty.
      - 400 - If the category already exists.
      - 422 - If the request cannot be processed.
    """

    @app.route("/categories", methods=["POST"])
    def create_category():
        body = request.get_json()

        if not body or "category" not in body:
            abort(400, description="Category name is required")

        new_category = body.get("category").strip()

        if not new_category:
            abort(400, description="Category name cannot be empty or whitespace")

        existing_category = Category.query.filter_by(type=new_category).first()
        if existing_category:
            abort(400, description="Category already exists")

        try:

            category = Category(type=new_category)

            db.session.add(category)
            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "created": category.id,
                }
            )

        except Exception as e:
            print(f"Error: {e}")
            abort(422, description="Unable to process the request")

    """
    Error Handler: 404
    Purpose: Handle resource not found errors.
    Response: A JSON object with an error code and a description of the error.
    """

    @app.errorhandler(404)
    def not_found(error):
        message = (
            error.description if hasattr(
                error,
                "description") else "resource not found")
        return jsonify(
            {"success": False, "error": 404, "message": message}), 404

    """
    Error Handler: 422
    Purpose: Handle unprocessable entity errors.
    Response: A JSON object with an error code and a description of the error.
    """

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    """
    Error Handler: 400
    Purpose: Handle bad request errors.
    Response: A JSON object with an error code and a description of the error.
    """

    @app.errorhandler(400)
    def bad_request(error):
        message = error.description if hasattr(
            error, "description") else "bad request"
        return jsonify(
            {"success": False, "error": 400, "message": message}), 400

    return app
