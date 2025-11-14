# PrepPal API Documentation

Complete API reference for the PrepPal backend server.

## Base URL

```
http://localhost:8000
```

For production, replace with your deployed API URL.

## Authentication

Currently, no authentication is required for the prototype. For production deployment, implement JWT-based authentication.

---

## Endpoints

### 1. Health Check

**GET** `/`

Check if the API is running.

**Response:**
```json
{
  "message": "PrepPal API is running!",
  "version": "1.0.0"
}
```

---

### 2. Upload Document

**POST** `/upload`

Upload and process a PDF document for RAG.

**Request:**
- Content-Type: `multipart/form-data`
- Body Parameters:
  - `file` (file, required): PDF file to upload
  - `subject` (string, optional): Subject category (e.g., "Physics", "Math")

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@notes.pdf" \
  -F "subject=Computer Science"
```

**Response:**
```json
{
  "doc_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "notes.pdf",
  "num_chunks": 15,
  "subject": "Computer Science",
  "message": "Document uploaded and processed successfully"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid file format
- `500`: Processing error

---

### 3. Chat with Documents

**POST** `/chat`

Send a query and receive an answer based on uploaded documents using RAG.

**Request Body:**
```json
{
  "user_id": "default_user",
  "message": "What is the OSI model?",
  "doc_ids": ["a1b2c3d4-...", "b2c3d4e5-..."]  // optional
}
```

**Parameters:**
- `user_id` (string): User identifier
- `message` (string, required): User's question
- `doc_ids` (array of strings, optional): Specific documents to query. If not provided, searches all documents.

**Example:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student123",
    "message": "Explain TCP vs UDP",
    "doc_ids": ["a1b2c3d4-..."]
  }'
```

**Response:**
```json
{
  "answer": "TCP (Transmission Control Protocol) is a connection-oriented protocol that ensures reliable delivery...",
  "sources": [
    {
      "filename": "networks.pdf",
      "chunk_index": 3,
      "relevance_score": 0.87
    },
    {
      "filename": "protocols.pdf",
      "chunk_index": 7,
      "relevance_score": 0.82
    }
  ],
  "timestamp": "2025-11-14T10:30:00.123456"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid request
- `500`: Processing error

---

### 4. Generate Quiz

**POST** `/quiz`

Generate AI-powered quiz questions from uploaded documents.

**Request Body:**
```json
{
  "topic": "Network Security",
  "doc_ids": ["a1b2c3d4-..."],
  "num_questions": 5
}
```

**Parameters:**
- `topic` (string, optional): Focus topic for questions
- `doc_ids` (array of strings, optional): Documents to generate questions from
- `num_questions` (integer, default: 5): Number of questions (1-10)

**Example:**
```bash
curl -X POST "http://localhost:8000/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Data Structures",
    "num_questions": 5
  }'
```

**Response:**
```json
{
  "questions": [
    {
      "question": "What is a binary search tree?",
      "options": [
        "A tree with at most two children per node",
        "A sorted tree structure",
        "A balanced tree",
        "A tree with binary values"
      ],
      "correct_index": 1,
      "explanation": "A binary search tree is a sorted tree structure where left children are smaller and right children are larger than the parent node."
    },
    {
      "question": "What is the time complexity of binary search?",
      "options": [
        "O(n)",
        "O(log n)",
        "O(n²)",
        "O(1)"
      ],
      "correct_index": 1,
      "explanation": "Binary search has O(log n) time complexity as it eliminates half the search space in each iteration."
    }
  ]
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid parameters
- `500`: Generation error

---

### 5. Create Study Plan

**POST** `/plan`

Generate a personalized day-by-day study schedule.

**Request Body:**
```json
{
  "exam_date": "2025-12-31",
  "hours_per_day": 4.0,
  "subjects": [
    "Mathematics",
    "Physics",
    "Chemistry"
  ]
}
```

**Parameters:**
- `exam_date` (string, required): Target exam date (YYYY-MM-DD)
- `hours_per_day` (float, required): Daily study hours (1.0 - 12.0)
- `subjects` (array of strings, required): List of subjects to study

**Example:**
```bash
curl -X POST "http://localhost:8000/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_date": "2025-12-31",
    "hours_per_day": 4.0,
    "subjects": ["Math", "Physics", "Chemistry"]
  }'
```

**Response:**
```json
{
  "plan": [
    {
      "day": 1,
      "date": "2025-11-15",
      "subject": "Mathematics",
      "hours": 4.0,
      "topics": ["Algebra - Topic 1"],
      "completed": false
    },
    {
      "day": 2,
      "date": "2025-11-16",
      "subject": "Physics",
      "hours": 4.0,
      "topics": ["Mechanics - Topic 1"],
      "completed": false
    }
  ],
  "total_days": 47,
  "total_hours": 188.0
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid date or parameters
- `500`: Generation error

---

### 6. List Documents

**GET** `/documents`

Retrieve all uploaded documents.

**Example:**
```bash
curl -X GET "http://localhost:8000/documents"
```

**Response:**
```json
{
  "documents": [
    {
      "doc_id": "a1b2c3d4-...",
      "filename": "networks.pdf",
      "subject": "Computer Science",
      "num_chunks": 15,
      "upload_date": "2025-11-14T09:00:00.123456"
    },
    {
      "doc_id": "b2c3d4e5-...",
      "filename": "physics.pdf",
      "subject": "Physics",
      "num_chunks": 22,
      "upload_date": "2025-11-14T10:15:00.123456"
    }
  ]
}
```

**Status Codes:**
- `200`: Success

---

### 7. Delete Document

**DELETE** `/documents/{doc_id}`

Delete a specific document by ID.

**Parameters:**
- `doc_id` (path parameter): Document UUID

**Example:**
```bash
curl -X DELETE "http://localhost:8000/documents/a1b2c3d4-..."
```

**Response:**
```json
{
  "message": "Document networks.pdf deleted successfully"
}
```

**Status Codes:**
- `200`: Success
- `404`: Document not found

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

---

## Rate Limiting

Currently no rate limiting in prototype. For production:
- Implement rate limiting per user/IP
- Suggested limit: 100 requests per hour per endpoint

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Test endpoints directly in the browser
- View request/response schemas
- See detailed parameter information

---

## Integration Examples

### Python

```python
import requests

# Upload document
with open('notes.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f},
        data={'subject': 'Math'}
    )
    doc_id = response.json()['doc_id']

# Chat
response = requests.post(
    'http://localhost:8000/chat',
    json={
        'user_id': 'user123',
        'message': 'What is calculus?',
        'doc_ids': [doc_id]
    }
)
answer = response.json()['answer']
```

### JavaScript

```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('subject', 'Math');

const uploadResponse = await fetch('http://localhost:8000/upload', {
  method: 'POST',
  body: formData
});
const { doc_id } = await uploadResponse.json();

// Chat
const chatResponse = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    message: 'Explain derivatives',
    doc_ids: [doc_id]
  })
});
const { answer } = await chatResponse.json();
```

---

## WebSocket Support (Future)

Planned for real-time features:
- Live chat streaming
- Progress updates
- Collaborative study sessions

---

## Versioning

Current version: `v1`

Future versions will be prefixed: `/v2/chat`, etc.

---

## Support

For issues or questions:
- GitHub Issues: [your-repo]/issues
- Email: support@preppal.dev
- API Status: http://localhost:8000/health