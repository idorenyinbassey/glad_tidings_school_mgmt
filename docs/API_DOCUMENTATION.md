# 📡 API Documentation

## Result Management API Endpoints

### Authentication Required
All API endpoints require user authentication and appropriate role permissions.

## 🎯 Result Management Endpoints

### Get Class Students
**Endpoint**: `GET /results/api/class-students/`  
**Description**: Retrieve students in a specific class  
**Required Role**: Staff, Admin  

**Parameters**:
- `class_id` (required): ID of the student class

**Response**:
```json
{
  "students": [
    {
      "id": 1,
      "name": "John Doe",
      "admission_number": "2024001"
    }
  ],
  "class_name": "JSS1A"
}
```

### Result Entry
**Endpoint**: `POST /results/entry/`  
**Description**: Submit individual student result  
**Required Role**: Staff, Admin  

**Form Data**:
- `session`: Academic session ID
- `term`: Academic term ID  
- `student_class`: Student class ID
- `student`: Student ID
- `subject`: Subject ID
- `assessment`: Assessment ID
- `score`: Numeric score
- `remarks`: Teacher's remarks (optional)

### Bulk Result Upload
**Endpoint**: `POST /results/bulk-upload/`  
**Description**: Upload multiple results via CSV  
**Required Role**: Staff, Admin  

**Form Data**:
- `csv_file`: CSV file with result data
- `session`: Academic session ID
- `term`: Academic term ID

**CSV Format**:
```csv
admission_number,subject_code,assessment_type,score,remarks
2024001,MATH,ca1,85,Excellent performance
2024002,ENG,exam,78,Good improvement
```

### Compile Results
**Endpoint**: `POST /results/compile/`  
**Description**: Compile term results from individual assessments  
**Required Role**: Staff, Admin  

**Form Data**:
- `session`: Academic session ID
- `term`: Academic term ID
- `student_class`: Student class ID

### Result Sheets
**Endpoint**: `GET /results/sheets/`  
**Description**: View available result sheets  
**Required Role**: Staff, Admin, Student  

**Parameters**:
- `session`: Session ID (optional filter)
- `term`: Term ID (optional filter)
- `student`: Student ID (for student users)

### Print Result Sheet
**Endpoint**: `GET /results/print/<int:sheet_id>/`  
**Description**: Generate and download PDF result sheet  
**Required Role**: Staff, Admin, Student (own results)  

**Response**: PDF file download

## 🎓 Student Portal Endpoints

### Student Results
**Endpoint**: `GET /students/results/`  
**Description**: View student's academic results  
**Required Role**: Student  

**Parameters**:
- `session`: Session ID (optional filter)
- `term`: Term ID (optional filter)
- `subject`: Subject ID (optional filter)

### Student Result Sheets
**Endpoint**: `GET /students/result-sheets/`  
**Description**: View student's available result sheets  
**Required Role**: Student  

**Parameters**:
- `session`: Session ID (required for sheet display)
- `term`: Term ID (required for sheet display)

### Print Student Result
**Endpoint**: `GET /students/print-result/<int:session_id>/<int:term_id>/`  
**Description**: Download student's result sheet as PDF  
**Required Role**: Student  

**Response**: PDF file download

## 🔐 Authentication & Permissions

### Role-Based Access
All endpoints use the `@role_required` decorator to enforce permissions:

```python
@role_required(['staff', 'admin'])  # Staff and Admin only
@role_required(['student'])         # Students only
@role_required(['admin'])           # Admin only
```

### Decorator Usage
```python
from core.decorators import role_required

@login_required
@role_required(['staff', 'admin'])
def result_entry(request):
    # View logic here
    pass
```

## 📊 Data Models

### AcademicSession
```python
{
  "id": 1,
  "name": "2024/2025",
  "start_date": "2024-09-01",
  "end_date": "2025-07-31",
  "is_current": true
}
```

### AcademicTerm
```python
{
  "id": 1,
  "session": 1,
  "name": "first",
  "start_date": "2024-09-01",
  "end_date": "2024-12-15",
  "is_current": true
}
```

### Subject
```python
{
  "id": 1,
  "name": "Mathematics",
  "code": "MATH",
  "department": "Core",
  "is_active": true
}
```

### StudentClass
```python
{
  "id": 1,
  "name": "JSS1A",
  "level": "JSS1",
  "is_active": true,
  "subjects": [1, 2, 3, 4, 5]
}
```

### Assessment
```python
{
  "id": 1,
  "name": "First CA",
  "type": "ca1",
  "max_score": 15,
  "weight_percentage": 15.0,
  "is_active": true
}
```

### StudentResult
```python
{
  "id": 1,
  "student": 1,
  "subject": 1,
  "session": 1,
  "term": 1,
  "student_class": 1,
  "assessment": 1,
  "score": 85.0,
  "remarks": "Excellent performance",
  "entered_by": 2,
  "entered_at": "2024-10-15T10:30:00Z",
  "percentage": 85.0
}
```

### TermResult
```python
{
  "id": 1,
  "student": 1,
  "subject": 1,
  "session": 1,
  "term": 1,
  "student_class": 1,
  "total_score": 87.5,
  "total_possible": 100.0,
  "percentage": 87.5,
  "grade": "A",
  "position_in_class": 2,
  "total_students": 30,
  "teacher_remarks": "Outstanding performance"
}
```

## 🚨 Error Handling

### Standard Error Responses

**400 Bad Request**:
```json
{
  "error": "Invalid input data",
  "details": "Score cannot exceed maximum allowed value"
}
```

**403 Forbidden**:
```json
{
  "error": "Permission denied",
  "details": "Staff role required for this operation"
}
```

**404 Not Found**:
```json
{
  "error": "Resource not found",
  "details": "Student with given ID does not exist"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Internal server error",
  "details": "An unexpected error occurred"
}
```

## 📝 Usage Examples

### JavaScript AJAX Example
```javascript
// Get students in a class
$.ajax({
    url: '/results/api/class-students/',
    data: {'class_id': classId},
    success: function(data) {
        const studentSelect = $('#student');
        studentSelect.empty();
        data.students.forEach(function(student) {
            studentSelect.append(`<option value="${student.id}">${student.name}</option>`);
        });
    },
    error: function() {
        alert('Error loading students');
    }
});
```

### Python Requests Example
```python
import requests

# Submit a result
data = {
    'session': 1,
    'term': 1,
    'student_class': 1,
    'student': 1,
    'subject': 1,
    'assessment': 1,
    'score': 85,
    'remarks': 'Good work'
}

response = requests.post(
    'http://localhost:8000/results/entry/',
    data=data,
    headers={'X-CSRFToken': csrf_token}
)
```

## 🔍 Data Validation

### Score Validation
- Must be numeric
- Cannot be negative
- Cannot exceed assessment max_score
- Supports decimal values (0.1 precision)

### Required Fields
- **Result Entry**: session, term, student_class, student, subject, assessment, score
- **Bulk Upload**: csv_file, session, term
- **Result Compilation**: session, term, student_class

### File Validation
- **CSV Upload**: Must be valid CSV format
- **File Size**: Maximum 10MB
- **Content Validation**: All rows must have required columns

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

### Validation Error Response
```json
{
  "success": false,
  "errors": {
    "score": ["Score cannot exceed 15"],
    "student": ["This field is required"]
  }
}
```

## 🎛️ Configuration

### Settings Variables
```python
# Maximum file upload size for CSV
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Supported file formats
ALLOWED_UPLOAD_EXTENSIONS = ['.csv']

# Default pagination
RESULTS_PER_PAGE = 50

# Grade boundaries
GRADE_BOUNDARIES = {
    'A': 80,
    'B': 70,
    'C': 60,
    'D': 50,
    'F': 0
}
```

---

**API documentation for Glad Tidings School Management Portal**  
**All endpoints follow RESTful principles and include proper error handling**
