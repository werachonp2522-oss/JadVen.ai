// Central API URL — reads from NEXT_PUBLIC_API_URL env variable
// In development (.env.local):    NEXT_PUBLIC_API_URL=http://localhost:8000
// In production (.env.production): NEXT_PUBLIC_API_URL=http://10.0.100.147:8000

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
export default API_URL;
