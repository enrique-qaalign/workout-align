# Frontend React Skeleton

This directory provides a barebones React application scaffold to build a richer dashboard for the Reliability Engineer for Health platform.  
It is **not** compiled in this environment because external package installation is disabled. To develop the UI locally:

1. Ensure you have Node.js and npm installed.
2. Navigate into this directory:

```bash
cd frontend-react
```

3. Install dependencies:

```bash
npm install
```

4. Start the development server:

```bash
npm start
```

The app will be served on `http://localhost:3000` and will proxy API requests to `http://localhost:8000` if you configure a proxy in `package.json`.  

## Overview

The skeleton includes a basic `App` component that demonstrates how to authenticate a user, fetch meal templates and render a placeholder chart. You can extend it to visualise rolling averages, configure meal rotations, log workouts and more.