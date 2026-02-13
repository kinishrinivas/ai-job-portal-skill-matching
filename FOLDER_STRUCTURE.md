# Project Folder Structure

This document explains the folder structure of our AI Job Portal project.

## Complete Structure

```
ai-job-portal-skill-matching/
│
├── README.md                 ← Project documentation
│
├── backend/                  ← Flask API server
│   ├── models/              ← Database models (User, Job, Application)
│   │   └── __init__.py
│   ├── routes/              ← API endpoints
│   │   └── __init__.py
│   ├── utils/               ← Helper functions (AI, matching, validation)
│   │   └── __init__.py
│   └── uploads/             ← Resume files storage
│
└── frontend/                ← React application
    ├── public/              ← Static files
    ├── src/                 ← React source code
    │   ├── components/     ← Reusable UI components
    │   ├── pages/          ← Page components
    │   ├── services/       ← API calling functions
    │   └── utils/          ← Helper functions
```

## What's Next?

We will create files step by step:
1. Backend configuration and database setup
2. User authentication
3. Resume upload and AI skill extraction
4. Job posting features
5. Matching algorithm
6. Frontend pages

Each file will be explained line by line!
