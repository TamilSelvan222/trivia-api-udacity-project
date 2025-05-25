from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

ITEMS_PER_PAGE = 10


def paginate_items(req, items):
    page_num = req.args.get("page", 1, type=int)
    start_idx = (page_num - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE

    formatted_items = [item.format() for item in items]
    return formatted_items[start_idx:end_idx]


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        db_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=db_path)
    else:
        setup_db(app)

    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

    with app.app_context():
        db.create_all()

    @app.after_request
    def add_cors_headers(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response

    @app.route("/categories")
    def get_categories():
        try:
            all_categories = Category.query.order_by(Category.type).all()
            categories_dict = {cat.id: cat.type for cat in all_categories}
            if not categories_dict:
                abort(404, description="No categories found")
            return jsonify({"success": True, "categories": categories_dict})
        except Exception as err:
            print(f"Error retrieving categories: {err}")
            abort(404, description="Resource not found")

    @app.route("/questions")
    def get_questions():
        try:
            all_questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_items(request, all_questions)
            all_categories = Category.query.order_by(Category.type).all()

            if not paginated_questions:
                abort(404, description="No questions found for this page")

            categories_dict = {cat.id: cat.type for cat in all_categories}

            return jsonify(
                {
                    "success": True,
                    "questions": paginated_questions,
                    "total_questions": len(all_questions),
                    "categories": categories_dict,
                    "current_category": None,
                }
            )
        except Exception as err:
            print(f"Error retrieving questions: {err}")
            abort(404, description="Resource not found")

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def remove_question(question_id):
        try:
            question = Question.query.get(question_id)
            if not question:
                abort(404, description="Question not found")
            question.delete()
            return jsonify({"success": True, "deleted": question_id})
        except Exception as err:
            print(f"Error deleting question: {err}")
            abort(422, description="Unable to process request")

    @app.route("/questions", methods=["POST"])
    def create_question():
        data = request.get_json()
        required_fields = ("question", "answer", "difficulty", "category")

        if not data or not all(field in data for field in required_fields):
            abort(400, description="Missing required fields")

        question_text = data["question"].strip()
        answer_text = data["answer"].strip()
        difficulty_level = data["difficulty"]
        category_id = data["category"]

        if not question_text or not answer_text:
            abort(400, description="Question and Answer cannot be empty")

        try:
            new_question = Question(
                question=question_text,
                answer=answer_text,
                difficulty=int(difficulty_level),
                category=int(category_id),
            )
            new_question.insert()
            return jsonify({"success": True, "created": new_question.id}), 201
        except Exception as err:
            print(f"Error creating question: {err}")
            abort(422, description="Unprocessable request")

    @app.route("/questions/search", methods=["POST"])
    def search_for_questions():
        data = request.get_json()
        search_term = data.get("searchTerm", "").strip()

        if not search_term:
            abort(400, description="Search term is required")

        try:
            matched_questions = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ).all()

            formatted_results = [q.format() for q in matched_questions]

            return jsonify(
                {
                    "success": True,
                    "questions": formatted_results,
                    "total_questions": len(formatted_results),
                }
            )
        except Exception as err:
            print(f"Error searching questions: {err}")
            abort(422, description="Unprocessable request")

    @app.route("/categories/<int:cat_id>/questions", methods=["GET"])
    def get_questions_by_category(cat_id):
        try:
            questions_in_category = Question.query.filter(
                Question.category == str(cat_id)
            ).all()

            if not questions_in_category:
                abort(404, description="No questions found for this category")

            formatted_questions = [q.format() for q in questions_in_category]

            return jsonify(
                {
                    "success": True,
                    "questions": formatted_questions,
                    "total_questions": len(formatted_questions),
                    "current_category": cat_id,
                }
            )
        except Exception as err:
            print(f"Error retrieving questions by category: {err}")
            abort(404, description="Resource not found")

    @app.route("/quizzes", methods=["POST"])
    def quiz_game():
        data = request.get_json()

        if not data or "quiz_category" not in data or "previous_questions" not in data:
            abort(400, description="quiz_category and previous_questions are required")

        quiz_category = data.get("quiz_category")
        previous_questions = data.get("previous_questions")

        try:
            if quiz_category["type"] == "click":
                available_questions = Question.query.filter(
                    Question.id.notin_(previous_questions)
                ).all()
            else:
                available_questions = Question.query.filter_by(
                    category=quiz_category["id"]
                ).filter(Question.id.notin_(previous_questions)).all()

            if available_questions:
                selected_question = random.choice(available_questions).format()
            else:
                selected_question = None

            return jsonify({"success": True, "question": selected_question})
        except Exception as err:
            print(f"Error during quiz play: {err}")
            abort(422, description="Unprocessable request")

    @app.route("/categories", methods=["POST"])
    def add_category():
        data = request.get_json()

        if not data or "category" not in data:
            abort(400, description="Category name is required")

        category_name = data.get("category").strip()

        if not category_name:
            abort(400, description="Category name cannot be empty")

        existing = Category.query.filter_by(type=category_name).first()
        if existing:
            abort(400, description="Category already exists")

        try:
            new_category = Category(type=category_name)
            db.session.add(new_category)
            db.session.commit()
            return jsonify({"success": True, "created": new_category.id})
        except Exception as err:
            print(f"Error adding category: {err}")
            abort(422, description="Unable to process request")

    @app.errorhandler(404)
    def handle_404(error):
        message = getattr(error, "description", "Resource not found")
        return jsonify({"success": False, "error": 404, "message": message}), 404

    @app.errorhandler(422)
    def handle_422(error):
        return jsonify({"success": False, "error": 422, "message": "Unprocessable"}), 422

    @app.errorhandler(400)
    def handle_400(error):
        message = getattr(error, "description", "Bad request")
        return jsonify({"success": False, "error": 400, "message": message}), 400

    return app
