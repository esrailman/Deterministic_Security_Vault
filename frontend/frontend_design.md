# Frontend Design Document - Deterministic Security Vault (Sprint 3)

## Overview
This document outlines the design structure and user flow for the frontend of the Deterministic Security Vault. The goal of Sprint 3 is to establish a consistent visual identity and clear navigation structure.

## visual Identity
- **Theme**: Clean, modern, trustworthy (Security/Enterprise focus).
- **Color Palette**:
  - Primary: Deep Blue (`#003366`) - Headers, primary buttons.
  - Secondary: Teal/Cyan (`#00A8E8`) - Accents, highlights.
  - Background: Light Gray (`#F4F4F9`) - Main body background.
  - Text: Dark Gray (`#333333`) - Main text.
  - Alert/Error: Red (`#D32F2F`).
  - Success: Green (`#388E3C`).

## Global Layout
Every page will share a common structure:
1.  **Header**:
    *   Logo/Title: "Deterministic Security Vault"
    *   Navigation: Links to "Home", "Upload", "Verify", "Audit".
2.  **Main Content Area**: Centered container for the specific page content.
3.  **Footer**: Copyright info, simple links.

## Page Structures

### 1. Home (index.html)
*   **Purpose**: Welcome screen and quick access to main features.
*   **Components**:
    *   Hero section with a welcome message.
    *   Cards linking to Upload, Verify, and Audit.

### 2. Upload Page (upload.html)
*   **Purpose**: Allow users to "register" a file.
*   **Components**:
    *   Page Title: "Secure File Upload"
    *   Form:
        *   File Input area (Click to select or drag & drop style).
        *   Description input (optional).
        *   "Upload & Register" button (Primary color).
    *   Feedback Area: Shows success message and generated ID/Hash (mocked).

### 3. Verify Page (verify.html)
*   **Purpose**: Check if a file is intact.
*   **Components**:
    *   Page Title: "File Integrity Verification"
    *   Form:
        *   File Input (to verify a local file) OR ID/Hash Input.
        *   "Verify Integrity" button.
    *   Result Area:
        *   Success State: Green checkmark, "File is valid".
        *   Failure State: Red warning, "Tampering detected".

### 4. Audit Page (audit.html)
*   **Purpose**: List history of actions/records.
*   **Components**:
    *   Page Title: "System Audit Log"
    *   Data Table:
        *   Columns: Timestamp, Event Type (Upload/Verify), File Name, Status.
        *   Mock rows of data.

## User Flow
1.  User lands on **Home**.
2.  User navigates to **Upload** -> Selects file -> Clicks Upload -> Sees Success.
3.  User navigates to **Verify** -> Selects same file -> Clicks Verify -> Sees "Valid".
4.  User checks **Audit** -> Sees the recent upload and verify events in the list.
