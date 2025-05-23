# Trivia API Documentation
## API Endpoints
### 1. GET /questions
Fetch a paginated list of questions.

**Query Parameters:**
- `page`: Page number (default: 1)

**Response:**
- `questions`: A list of question objects.
- `total_questions`: The total number of questions in the database.
- `categories`: A list of available categories.

***Example Response:***
```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 2
    }
  ],
  "totalQuestions": 100,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": "History"
}
```
### 2. POST /questions
Add a new question to the database.

**Request Body:**
```json
{
  "question": "What is the capital of France?",
  "answer": "Paris",
  "difficulty": 1,
  "category": 1
}
```
**Response:**
-`success`: True if the question was successfully created.
-`created`: The ID of the created question.

***Example Response:***

```json
{
  "success": true,
  "created": 42
}
```
### 3. DELETE /questions/int:id
Delete a question by its ID.

**Response:**
-`success`: True if the question was deleted.
-`deleted`: The ID of the deleted question.

***Example Response:***

```json
{
  "success": true,
  "deleted": 42
}
```
### 4. GET /categories
Fetch a list of all available categories.

**Response:**
-`categories`: A list of category objects.

***Example Response:***
```json
{
  "success": true,
  "categories": [
    { "id": 1, "type": "Science" },
    { "id": 2, "type": "Art" }
  ]
}
```

### 5. GET /categories/int:id/questions
Fetch questions for a specific category.

**Response:**

-`questions`: A list of questions in the requested category.
-`total_questions`: The total number of questions in the category.
-`current_category`: The ID and type of the requested category.
***Example Response:***

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 2
    }
  ],
  "currentCategory": "History",
  "total_questions": 15,
  "current_category": { "id": 1, "type": "Science" }
}
```
### 6. POST /quizzes
Start a quiz round with a specified category.

**Request Body:**

```json
{
  "previous_questions": [1, 2],
  "quiz_category": {"id": 2, "type": "Art"}
}
```
**Response:**
-`success`: True if the quiz was successfully started.
-`question`: A random question to be asked in the quiz round.

***Example Response:***

```json
{
  "success": true,
  "question": { 
    "id": 1,
    "question": "This is a question",
    "answer": "This is an answer",
    "difficulty": 5,
    "category": 4
  }
}
```
### 7. POST /questions/search
Sends a post request in order to search for a specific question by search term

**Request Body:**
```json
{
  "searchTerm": "this is the term the user is looking for"
}
```
**Response:**
- Returns: any array of questions, a number of totalQuestions that met the search term and the current category string

***Example Response:***
```json
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 5
    }
  ],
  "totalQuestions": 100,
  "currentCategory": "Entertainment"
}
```
### 8. POST /categories
Add a new categories to the database.

**Request Body:**
```json
{
  "category":"Science"
}
```
**Response:**
-`success`: True if the question was successfully created.
-`created`: The ID of the created question.

***Example Response:***

```json
{
  "success": true,
  "created": 7
}
```

### Error Handling
The app uses standard HTTP status codes to indicate the success or failure of an API request:

`200 OK`: The request was successful, and the response contains the expected data.
`404 Not Found`: The requested resource was not found (e.g., invalid question ID or category).
`422 Unprocessable Entity`: The request is valid, but the data is incomplete or incorrect (e.g., missing required fields in a POST request).
`400 Bad Request`: Invalid data or duplicate entries (e.g., trying to create a category that already exists).

***Example of error response: 400 ***
```json
{
    "success": False,
    "error": 400,
    "message": bad request
}
```
***Example of error response: 422 ***
```json
{
    "success": False,
    "error": 422,
    "message": "unprocessable"
}
```
***Example of error response: 404 ***
```json
{
    "success": False,
    "error": 404,
    "message": message
}
```

## SAMPLE CURL REQUEST 🕵️‍♀️
> --------------- CURL QUERIES TO TEST ENDPOINTS -------------

```bash
curl http://127.0.0.1:5000/categories
```

```bash
curl http://127.0.0.1:5000/questions
```

```bash
curl http://127.0.0.1:5000/questions?page=2
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{"question":"what is my name", "answer":"Stephen Nwankwo", "category":"5", "difficulty":"2"}' http://127.0.0.1:5000/questions 
```

```bash
curl -X DELETE http://127.0.0.1:5000/questions/25 
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{"searchTerm":"American artist"}' http://127.0.0.1:5000/questions/search
```

```bash
curl http://127.0.0.1:5000/categories/1/questions
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{"previous_questions":[],"quiz_category":{"type":"Science","id":"1"}}' http://127.0.0.1:5000/quizzes
```

```bash
curl -X POST -H "Content-Type: application/json" -d '{"category":"Political"}' http://127.0.0.1:5000/categories
```