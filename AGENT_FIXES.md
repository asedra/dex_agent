# Agent Registration and Filtering Fixes

This document describes the fixes implemented for issues DX-84 and DX-88.

## 📋 Issues Fixed

### DX-84: Agent Registration Validation
**Problem**: Agent registration accepts incomplete data without validation.
**Solution**: Added comprehensive validation to `AgentRegister` schema.

### DX-88: Agent Filtering and Pagination
**Problem**: Status filtering and pagination not working properly.
**Solution**: Implemented proper filtering and pagination in database layer and API endpoints.

## 🔧 Changes Made

### 1. Schema Validation (DX-84)

**File**: `/apps/backend/app/schemas/agent.py`

- Made `ip`, `os`, and `version` required fields in `AgentRegister`
- Added comprehensive validators:
  - `validate_ip_address()`: Validates IPv4 and IPv6 formats
  - `validate_hostname()`: Validates hostname format
  - `validate_os()`: Ensures OS field is not empty
  - `validate_version()`: Ensures version field is not empty

**Before**:
```python
class AgentRegister(BaseModel):
    hostname: str
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
```

**After**:
```python
class AgentRegister(BaseModel):
    hostname: str = Field(..., min_length=1, max_length=255)
    ip: str = Field(..., description="IP address is required")
    os: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., min_length=1, max_length=50)
    # ... with validators
```

### 2. Database Layer Enhancement (DX-88)

**Files**: 
- `/apps/backend/app/core/database_postgresql.py`
- `/apps/backend/app/core/database.py`

Enhanced `get_agents()` method to support:
- Status filtering
- Limit/offset pagination
- Ordering options
- Count queries for pagination metadata

**New Method Signature**:
```python
def get_agents(
    self, 
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: str = 'updated_at',
    order_desc: bool = True
) -> List[Dict[str, Any]]
```

Added `get_agents_count()` method for pagination support.

### 3. API Endpoint Enhancement (DX-88)

**File**: `/apps/backend/app/api/v1/agents.py`

**Enhanced GET `/api/v1/agents`**:
- Added query parameters: `status`, `limit`, `offset`, `order_by`, `order_desc`, `include_total`
- Added input validation
- Returns detailed response with pagination metadata
- Maintains backward compatibility

**Added GET `/api/v1/agents/list`**:
- Simple endpoint returning just the agents array
- Supports filtering and pagination
- Provides backward compatibility for existing integrations

**New Response Format** (GET `/api/v1/agents`):
```json
{
    "agents": [...],
    "count": 10,
    "total_count": 50,
    "has_more": true,
    "filters": {
        "status": "online",
        "limit": 10,
        "offset": 0,
        "order_by": "updated_at",
        "order_desc": true
    }
}
```

## 🧪 Testing

Created comprehensive test script: `test_agent_fixes.py`

### DX-84 Tests:
- Missing required fields (IP, OS, version)
- Invalid IP address formats
- Empty hostname
- Valid registration with all fields

### DX-88 Tests:
- Status filtering (`?status=online`, `?status=offline`)
- Pagination (`?limit=5`, `?limit=2&offset=1`)
- Combined filtering and pagination
- Response format validation

## 📚 API Usage Examples

### Basic Agent List (Backward Compatible)
```bash
GET /api/v1/agents/list
```

### Filtered Agent List
```bash
GET /api/v1/agents?status=online&limit=10&include_total=true
```

### Paginated Results
```bash
GET /api/v1/agents?limit=5&offset=10&order_by=hostname&order_desc=false
```

### Agent Registration (Now with Validation)
```bash
POST /api/v1/agents/register
Content-Type: application/json

{
    "hostname": "WIN-SERVER-01",
    "ip": "192.168.1.100",
    "os": "Windows Server 2022",
    "version": "10.0.20348",
    "tags": ["production", "database"]
}
```

## 🔒 Security Enhancements

- **SQL Injection Protection**: Whitelisted `order_by` fields
- **Input Validation**: All query parameters validated
- **Rate Limiting**: Implemented reasonable limits (max 1000 results per request)
- **Data Sanitization**: IP addresses and hostnames validated with regex

## 🔄 Backward Compatibility

- Existing API calls to `/api/v1/agents` will work but return new format
- Added `/api/v1/agents/list` for simple array response
- All filtering/pagination parameters are optional
- Default behavior preserved when no parameters provided

## ✅ Validation Rules

### IP Address
- Must be valid IPv4 (e.g., `192.168.1.1`) or IPv6 format
- Cannot be empty or whitespace-only

### Hostname
- Must contain only alphanumeric characters, hyphens, and dots
- Cannot be empty
- Max length: 255 characters

### Operating System
- Cannot be empty or whitespace-only
- Max length: 100 characters

### Version
- Cannot be empty or whitespace-only
- Max length: 50 characters

### Status Filter
- Valid values: `online`, `offline`, `warning`, `error`

### Pagination
- `limit`: 1-1000 (default: no limit)
- `offset`: 0+ (default: 0)

### Ordering
- Valid `order_by` fields: `id`, `hostname`, `ip`, `os`, `version`, `status`, `last_seen`, `created_at`, `updated_at`
- `order_desc`: true/false (default: true)

## 🔄 Migration Notes

1. **Agent Registration**: Existing agents will continue to work, but new registrations require IP, OS, and version
2. **API Clients**: Should handle new response format or use `/list` endpoint
3. **Database**: Both PostgreSQL and SQLite implementations updated
4. **Testing**: Run `python test_agent_fixes.py` to verify all fixes