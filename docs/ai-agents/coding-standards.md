# Coding Standards and Best Practices

## Overview

This document establishes comprehensive coding standards and best practices for the Agentic AI Platform. These standards ensure code quality, maintainability, security, and consistency across the entire codebase.

## General Principles

### Code Quality Principles
1. **Readability**: Code should be self-documenting and easy to understand
2. **Maintainability**: Code should be easy to modify and extend
3. **Reliability**: Code should be robust and handle edge cases
4. **Performance**: Code should be efficient and scalable
5. **Security**: Code should follow security best practices
6. **Testability**: Code should be easy to test

### SOLID Principles
- **Single Responsibility**: Each class/function has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for base types
- **Interface Segregation**: Clients shouldn't depend on unused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Frontend Coding Standards (TypeScript/React)

### File Organization

#### Directory Structure
```
frontend/
├── app/                    # Next.js App Router
│   ├── (routes)/          # Route groups
│   ├── api/               # API routes
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Homepage
├── components/            # Reusable components
│   ├── ui/               # Base UI components
│   ├── features/         # Feature-specific components
│   ├── layout/           # Layout components
│   └── forms/            # Form components
├── lib/                  # Utility libraries
│   ├── utils.ts          # General utilities
│   ├── constants.ts      # Application constants
│   ├── types.ts          # Type definitions
│   └── validations.ts    # Validation schemas
├── hooks/                # Custom React hooks
├── styles/               # CSS modules and global styles
└── public/               # Static assets
```

#### File Naming Conventions
```typescript
// Components: PascalCase
UserProfile.tsx
ChatbotInterface.tsx
PaymentForm.tsx

// Utilities: camelCase
formatCurrency.ts
validateEmail.ts
apiClient.ts

// Constants: UPPER_SNAKE_CASE
API_ENDPOINTS.ts
ERROR_MESSAGES.ts

// Types: PascalCase with descriptive names
UserTypes.ts
ApiTypes.ts
ComponentTypes.ts
```

### TypeScript Standards

#### Type Definitions
```typescript
// Use interfaces for object shapes
interface User {
  readonly id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
  createdAt: Date;
  updatedAt?: Date;
}

// Use type aliases for unions and complex types
type ApiResponse<T> = {
  data: T;
  error: string | null;
  loading: boolean;
};

// Use enums for constants with semantic meaning
enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest'
}

// Use generic types for reusable components
interface ApiHookResult<T> {
  data: T | null;
  error: Error | null;
  loading: boolean;
  refetch: () => Promise<void>;
}
```

#### Function Signatures
```typescript
// Use explicit return types for public functions
function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

// Use async/await with proper error handling
async function fetchUserProfile(userId: string): Promise<User> {
  try {
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
}

// Use proper typing for event handlers
function handleSubmit(event: React.FormEvent<HTMLFormElement>): void {
  event.preventDefault();
  // Handle form submission
}
```

### React Component Standards

#### Component Structure
```typescript
// Use functional components with TypeScript
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
  className?: string;
}

export function UserProfile({ 
  userId, 
  onUpdate, 
  className 
}: UserProfileProps): JSX.Element {
  // Hooks at the top
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Effects after state
  useEffect(() => {
    fetchUserProfile(userId)
      .then(setUser)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [userId]);
  
  // Event handlers
  const handleUpdate = useCallback((updatedUser: User) => {
    setUser(updatedUser);
    onUpdate?.(updatedUser);
  }, [onUpdate]);
  
  // Early returns for loading/error states
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!user) return <NotFound />;
  
  // Main render
  return (
    <div className={cn('user-profile', className)}>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
      <UserActions user={user} onUpdate={handleUpdate} />
    </div>
  );
}
```

#### Custom Hooks
```typescript
// Custom hooks for reusable logic
function useApi<T>(url: string): ApiHookResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(true);
  
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [url]);
  
  useEffect(() => {
    fetchData();
  }, [fetchData]);
  
  return { data, error, loading, refetch: fetchData };
}
```

### Styling Standards

#### Tailwind CSS Usage
```typescript
// Use consistent spacing and sizing
<div className="p-4 m-2 w-full max-w-md">
  <h1 className="text-2xl font-bold text-gray-900 mb-4">
    Title
  </h1>
  <p className="text-gray-600 leading-relaxed">
    Content
  </p>
</div>

// Use semantic color names
<button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
  Submit
</button>

// Use responsive design
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>
```

#### CSS Modules (when needed)
```css
/* components/UserProfile/UserProfile.module.css */
.container {
  @apply p-6 bg-white rounded-lg shadow-md;
}

.title {
  @apply text-xl font-semibold text-gray-900 mb-4;
}

.content {
  @apply text-gray-600 leading-relaxed;
}

/* Use BEM-like naming for complex components */
.userProfile__avatar {
  @apply w-16 h-16 rounded-full object-cover;
}

.userProfile__avatar--large {
  @apply w-24 h-24;
}
```

## Backend Coding Standards (Python)

### File Organization

#### Directory Structure
```
backend/agent/my_adk_agent/
├── __init__.py
├── agent.py              # Main agent class
├── config/               # Configuration management
│   ├── __init__.py
│   ├── settings.py       # Application settings
│   └── constants.py      # Application constants
├── services/             # Service layer
│   ├── __init__.py
│   ├── base_service.py   # Base service class
│   ├── supabase_service.py
│   ├── stripe_service.py
│   └── gemini_service.py
├── models/               # Data models
│   ├── __init__.py
│   ├── user.py
│   ├── conversation.py
│   └── payment.py
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── validators.py
│   ├── formatters.py
│   └── helpers.py
├── tools/                # ADK tools
│   ├── __init__.py
│   └── custom_tools.py
└── tests/                # Test files
    ├── __init__.py
    ├── conftest.py
    ├── test_agent.py
    └── test_services.py
```

#### File Naming Conventions
```python
# Modules: snake_case
user_service.py
payment_processor.py
email_validator.py

# Classes: PascalCase
class UserService:
class PaymentProcessor:
class EmailValidator:

# Functions and variables: snake_case
def process_payment():
def validate_email():
user_data = {}
```

### Python Code Standards

#### Class Definitions
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    """User data model with validation."""
    id: str
    name: str
    email: str
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Validate user data after initialization."""
        if not self.email or '@' not in self.email:
            raise ValueError("Invalid email address")
        
        if self.role not in ['admin', 'user', 'guest']:
            raise ValueError("Invalid user role")

class BaseService(ABC):
    """Abstract base class for all services."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize service with configuration."""
        self.config = config
        self._client = None
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service connections."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up service resources."""
        pass
    
    def _validate_config(self, required_keys: List[str]) -> None:
        """Validate required configuration keys."""
        missing_keys = [key for key in required_keys if key not in self.config]
        if missing_keys:
            raise ValueError(f"Missing configuration keys: {missing_keys}")
```

#### Function Definitions
```python
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

async def process_user_inquiry(
    inquiry: str,
    user_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a user inquiry and generate appropriate response.
    
    Args:
        inquiry: The user's inquiry text
        user_id: Unique identifier for the user
        context: Optional context information
    
    Returns:
        Dictionary containing response and metadata
    
    Raises:
        ValueError: If inquiry is empty or user_id is invalid
        ServiceError: If external service call fails
    """
    # Input validation
    if not inquiry.strip():
        raise ValueError("Inquiry cannot be empty")
    
    if not user_id:
        raise ValueError("User ID is required")
    
    try:
        # Log the inquiry (without sensitive data)
        logger.info(f"Processing inquiry for user {user_id[:8]}...")
        
        # Process the inquiry
        response_data = await _generate_response(inquiry, context)
        
        # Add metadata
        result = {
            'response': response_data['text'],
            'intent': response_data['intent'],
            'confidence': response_data['confidence'],
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully processed inquiry for user {user_id[:8]}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing inquiry for user {user_id[:8]}: {str(e)}")
        raise ServiceError(f"Failed to process inquiry: {str(e)}") from e

def _generate_response(
    inquiry: str, 
    context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Private helper function for response generation."""
    # Implementation details
    pass
```

#### Error Handling
```python
class ServiceError(Exception):
    """Base exception for service-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.utcnow()

class ValidationError(ServiceError):
    """Exception for validation errors."""
    pass

class ExternalServiceError(ServiceError):
    """Exception for external service failures."""
    pass

# Usage in service methods
async def create_user(self, user_data: Dict[str, Any]) -> User:
    """Create a new user with proper error handling."""
    try:
        # Validate input
        if not user_data.get('email'):
            raise ValidationError("Email is required")
        
        # Call external service
        result = await self._supabase_client.create_user(user_data)
        
        if result.get('error'):
            raise ExternalServiceError(
                f"Failed to create user: {result['error']}",
                error_code="USER_CREATION_FAILED"
            )
        
        return User(**result['data'])
        
    except ValidationError:
        raise  # Re-raise validation errors
    except ExternalServiceError:
        raise  # Re-raise service errors
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise ServiceError("Internal error occurred") from e
```

### Async/Await Patterns
```python
import asyncio
from typing import List, Coroutine, Any

class AsyncServiceManager:
    """Manage multiple async services."""
    
    def __init__(self) -> None:
        self.services: List[BaseService] = []
    
    async def initialize_all(self) -> None:
        """Initialize all services concurrently."""
        tasks = [service.initialize() for service in self.services]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def process_batch(
        self, 
        requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process multiple requests concurrently."""
        tasks = [self._process_single_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Request {i} failed: {str(result)}")
                processed_results.append({
                    'error': str(result),
                    'request_id': requests[i].get('id')
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_single_request(
        self, 
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single request."""
        # Implementation
        pass
```

## Database and API Standards

### Database Patterns

#### Repository Pattern
```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseRepository(ABC):
    """Abstract base repository."""
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Get record by ID."""
        pass
    
    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing record."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete record by ID."""
        pass

class UserRepository(BaseRepository):
    """User repository implementation."""
    
    def __init__(self, supabase_client) -> None:
        self.client = supabase_client
        self.table = 'users'
    
    async def create(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        # Validate required fields
        required_fields = ['email', 'name']
        missing_fields = [f for f in required_fields if f not in user_data]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
        
        # Add timestamps
        user_data['created_at'] = datetime.utcnow().isoformat()
        
        # Insert into database
        result = self.client.table(self.table).insert(user_data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise ExternalServiceError("Failed to create user")
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address."""
        result = self.client.table(self.table).select("*").eq("email", email).execute()
        
        if result.data:
            return result.data[0]
        return None
```

### API Design Standards

#### RESTful API Patterns
```python
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional

# Request/Response models
class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    role: str = 'user'

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: str
    updated_at: Optional[str] = None

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None

# API Router
router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Create a new user.
    
    - **name**: User's full name
    - **email**: User's email address (must be unique)
    - **role**: User role (admin, user, guest)
    """
    try:
        user = await user_service.create_user(user_data.dict())
        return UserResponse(**user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by ID."""
    user = await user_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(**user)

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """List users with pagination."""
    users = await user_service.list_users(skip=skip, limit=limit)
    return [UserResponse(**user) for user in users]
```

## Security Standards

### Input Validation
```python
from pydantic import BaseModel, validator, EmailStr
import re

class UserInput(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        
        # Remove potentially dangerous characters
        if re.search(r'[<>"\']', v):
            raise ValueError('Name contains invalid characters')
        
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is None:
            return v
        
        # Basic phone validation
        phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Invalid phone number format')
        
        return v

# SQL Injection Prevention
async def get_user_by_email_safe(email: str) -> Optional[Dict[str, Any]]:
    """Safe database query using parameterized queries."""
    # Using Supabase client (automatically parameterized)
    result = supabase.table('users').select('*').eq('email', email).execute()
    
    # If using raw SQL, always use parameters
    # query = "SELECT * FROM users WHERE email = %s"
    # result = await db.fetch_one(query, email)
    
    return result.data[0] if result.data else None
```

### Authentication and Authorization
```python
from functools import wraps
from typing import Callable, Any
import jwt

def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication."""
    @wraps(f)
    async def decorated_function(*args, **kwargs) -> Any:
        token = get_auth_token()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Add user context to kwargs
            kwargs['current_user_id'] = user_id
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return await f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role: str) -> Callable:
    """Decorator to require specific role."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        async def decorated_function(*args, **kwargs) -> Any:
            current_user_id = kwargs.get('current_user_id')
            
            if not current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user = await get_user(current_user_id)
            
            if not user or user.get('role') != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Usage
@router.delete("/{user_id}")
@require_auth
@require_role('admin')
async def delete_user(user_id: str, current_user_id: str) -> Dict[str, str]:
    """Delete user (admin only)."""
    await user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}
```

## Testing Standards

### Unit Test Structure
```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from my_adk_agent.services.user_service import UserService

class TestUserService:
    """Test suite for UserService."""
    
    @pytest.fixture
    def user_service(self):
        """Create UserService instance for testing."""
        config = {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test-key'
        }
        return UserService(config)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'user'
        }
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, sample_user_data):
        """Test successful user creation."""
        # Arrange
        expected_user = {'id': '123', **sample_user_data}
        
        with patch.object(user_service, '_supabase_client') as mock_client:
            mock_client.table.return_value.insert.return_value.execute.return_value = {
                'data': [expected_user],
                'error': None
            }
            
            # Act
            result = await user_service.create_user(sample_user_data)
            
            # Assert
            assert result['id'] == '123'
            assert result['email'] == sample_user_data['email']
            mock_client.table.assert_called_with('users')
    
    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, user_service):
        """Test user creation with invalid data."""
        # Arrange
        invalid_data = {'name': 'Test User'}  # Missing email
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Email is required"):
            await user_service.create_user(invalid_data)
    
    @pytest.mark.asyncio
    async def test_create_user_external_service_error(self, user_service, sample_user_data):
        """Test handling of external service errors."""
        # Arrange
        with patch.object(user_service, '_supabase_client') as mock_client:
            mock_client.table.return_value.insert.return_value.execute.return_value = {
                'data': None,
                'error': 'Database connection failed'
            }
            
            # Act & Assert
            with pytest.raises(ExternalServiceError, match="Failed to create user"):
                await user_service.create_user(sample_user_data)
```

### Integration Test Structure
```typescript
// frontend/tests/integration/user-management.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { UserManagement } from '../../components/UserManagement';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json([
      { id: '1', name: 'John Doe', email: 'john@example.com', role: 'user' },
      { id: '2', name: 'Jane Smith', email: 'jane@example.com', role: 'admin' }
    ]));
  }),
  
  rest.post('/api/users', (req, res, ctx) => {
    return res(ctx.json({
      id: '3',
      name: 'New User',
      email: 'new@example.com',
      role: 'user'
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('User Management Integration', () => {
  it('should display users and allow creation', async () => {
    render(<UserManagement />);
    
    // Wait for users to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
    
    // Create new user
    fireEvent.click(screen.getByText('Add User'));
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'New User' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'new@example.com' } });
    fireEvent.click(screen.getByText('Save'));
    
    // Verify new user appears
    await waitFor(() => {
      expect(screen.getByText('New User')).toBeInTheDocument();
    });
  });
});
```

## Documentation Standards

### Code Documentation
```python
def process_payment(
    amount: float,
    currency: str,
    payment_method: str,
    customer_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a payment transaction.
    
    This function handles payment processing through the configured payment
    provider (Stripe). It validates the payment data, creates a payment intent,
    and returns the result.
    
    Args:
        amount: Payment amount in the smallest currency unit (e.g., cents for USD)
        currency: Three-letter ISO currency code (e.g., 'USD', 'EUR')
        payment_method: Payment method identifier from the payment provider
        customer_id: Unique identifier for the customer
        metadata: Optional additional data to attach to the payment
    
    Returns:
        Dictionary containing payment result with the following keys:
        - 'id': Payment transaction ID
        - 'status': Payment status ('succeeded', 'failed', 'pending')
        - 'amount': Processed amount
        - 'currency': Currency used
        - 'created_at': Transaction timestamp
    
    Raises:
        ValidationError: If payment data is invalid
        PaymentError: If payment processing fails
        ExternalServiceError: If payment provider is unavailable
    
    Example:
        >>> result = process_payment(
        ...     amount=2000,  # $20.00
        ...     currency='USD',
        ...     payment_method='pm_card_visa',
        ...     customer_id='cus_123456789'
        ... )
        >>> print(result['status'])
        'succeeded'
    
    Note:
        This function requires valid Stripe API credentials to be configured
        in the application settings.
    """
    # Implementation here
    pass
```

### API Documentation
```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

class PaymentRequest(BaseModel):
    """
    Payment request model.
    
    Attributes:
        amount: Payment amount in cents (e.g., 2000 for $20.00)
        currency: ISO currency code (default: USD)
        payment_method: Stripe payment method ID
        customer_id: Customer identifier
        description: Optional payment description
    """
    amount: int
    currency: str = "USD"
    payment_method: str
    customer_id: str
    description: Optional[str] = None

@router.post("/payments", status_code=status.HTTP_201_CREATED)
async def create_payment(payment: PaymentRequest) -> Dict[str, Any]:
    """
    Create a new payment.
    
    Creates a payment intent with the specified amount and payment method.
    The payment will be processed immediately if the payment method allows it.
    
    **Request Body:**
    - `amount`: Payment amount in cents (minimum: 50)
    - `currency`: Three-letter ISO currency code
    - `payment_method`: Valid Stripe payment method ID
    - `customer_id`: Existing customer ID
    - `description`: Optional payment description
    
    **Response:**
    - `201 Created`: Payment created successfully
    - `400 Bad Request`: Invalid payment data
    - `404 Not Found`: Customer not found
    - `500 Internal Server Error`: Payment processing failed
    
    **Example Request:**
    ```json
    {
        "amount": 2000,
        "currency": "USD",
        "payment_method": "pm_card_visa",
        "customer_id": "cus_123456789",
        "description": "Monthly subscription"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "id": "pi_1234567890",
        "status": "succeeded",
        "amount": 2000,
        "currency": "USD",
        "created_at": "2025-01-28T10:00:00Z"
    }
    ```
    """
    # Implementation here
    pass
```

## Performance Standards

### Frontend Performance
```typescript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }: { data: ComplexData }) => {
  const processedData = useMemo(() => {
    return processComplexData(data);
  }, [data]);
  
  return <div>{/* Render processed data */}</div>;
});

// Use useCallback for event handlers
const UserList = ({ users, onUserUpdate }: UserListProps) => {
  const handleUserClick = useCallback((userId: string) => {
    onUserUpdate(userId);
  }, [onUserUpdate]);
  
  return (
    <div>
      {users.map(user => (
        <UserItem 
          key={user.id} 
          user={user} 
          onClick={handleUserClick}
        />
      ))}
    </div>
  );
};

// Lazy load components
const LazyDashboard = lazy(() => import('./Dashboard'));
const LazySettings = lazy(() => import('./Settings'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<LazyDashboard />} />
        <Route path="/settings" element={<LazySettings />} />
      </Routes>
    </Suspense>
  );
}
```

### Backend Performance
```python
import asyncio
from functools import lru_cache
from typing import List, Dict, Any

class PerformantService:
    """Service with performance optimizations."""
    
    def __init__(self):
        self._cache = {}
        self._connection_pool = None
    
    @lru_cache(maxsize=128)
    def get_cached_config(self, key: str) -> Any:
        """Cache configuration values."""
        return self._load_config(key)
    
    async def batch_process(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process items in batches for better performance."""
        batch_size = 10
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                self._process_item(item) for item in batch
            ])
            results.extend(batch_results)
        
        return results
    
    async def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single item."""
        # Use connection pooling for database operations
        async with self._connection_pool.acquire() as conn:
            result = await conn.fetch_one("SELECT * FROM table WHERE id = $1", item['id'])
            return result
```

## Code Review Standards

### Review Checklist

#### Functionality
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error handling is appropriate
- [ ] Performance is acceptable

#### Code Quality
- [ ] Code is readable and maintainable
- [ ] Follows established patterns
- [ ] No code duplication
- [ ] Proper naming conventions

#### Security
- [ ] Input validation present
- [ ] No security vulnerabilities
- [ ] Authentication/authorization correct
- [ ] No sensitive data exposed

#### Testing
- [ ] Unit tests included
- [ ] Tests cover edge cases
- [ ] Integration tests pass
- [ ] Performance tests pass

#### Documentation
- [ ] Code is properly documented
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] Comments explain complex logic

### Review Process
1. **Automated Checks**: CI/CD pipeline validates code
2. **Self Review**: Author reviews their own changes
3. **Peer Review**: Team member conducts thorough review
4. **Testing**: Deploy to development environment
5. **Approval**: Reviewer approves or requests changes

## Conclusion

These coding standards ensure:

- **Consistency**: Uniform code style across the project
- **Quality**: High-quality, maintainable code
- **Security**: Secure coding practices
- **Performance**: Optimized and efficient code
- **Testability**: Easy to test and debug
- **Documentation**: Well-documented codebase

Following these standards will result in a robust, maintainable, and scalable application that can be easily understood and extended by any developer or AI agent working on the project.