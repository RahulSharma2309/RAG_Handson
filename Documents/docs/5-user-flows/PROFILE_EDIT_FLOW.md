# Profile View & Edit Flow - Request Journey

This document explains the realistic, market-standard flow when a user views and updates their profile details.

## Architecture Overview

```
Frontend (React) → API Gateway → User Service
```

## Complete Profile Flow

### Step 1: User Opens Profile (Frontend)

- **Route**: `/profile`
- **Component**: `frontend/src/components/Profile.js`
- **Protected Route**: Requires authentication (JWT in localStorage)

On page load, the frontend fetches the profile by the Auth `userId`:

- **Request**: `GET /api/users/by-userid/{userId}`
- **Headers**: `Authorization: Bearer {token}`

### Step 2: User Clicks “Edit Profile”

- The UI switches into edit mode (purely frontend state).
- Inputs are pre-filled with existing values.

### Step 3: Frontend Sends Update Request (PATCH semantics)

In a realistic profile edit flow, updates are **partial**: you only send fields that the user is editing.

- **Request**: `PATCH /api/users/{profileId}`
- **Destination**: API Gateway (http://localhost:5000)
- **Headers**: `Authorization: Bearer {token}`
- **Payload** (example):

```json
{
  "FirstName": "John",
  "LastName": "Doe",
  "PhoneNumber": "+1234567890",
  "Address": "123 Main St"
}
```

Notes:
- `profileId` is the **User Service profile** id (not the Auth `userId`).
- `UpdateUserProfileRequest` has PATCH semantics: all fields optional.

### Step 4: User Service Validation & Update

- Validates field constraints (max lengths, phone format)
- Checks phone uniqueness (cannot be used by another profile)
- Applies updates and returns the updated profile

**Response**:
- `200 OK` on success
- `404 Not Found` if profile doesn’t exist
- `409 Conflict` if phone number already exists

### Step 5: Frontend Updates UI

- Shows a success message
- Exits edit mode
- Renders updated fields

## Why PATCH (and not PUT)?

Enterprise-grade APIs typically use:
- **PUT**: replace the full resource (requires sending the full object)
- **PATCH**: update only specific fields (better UX and avoids accidental field resets)

This project uses PATCH for profile updates for safer, more realistic behavior.

