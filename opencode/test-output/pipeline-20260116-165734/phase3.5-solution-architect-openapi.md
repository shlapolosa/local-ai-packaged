{
  "skill": "openapi", 
  "task_name": "Appointment Scheduling API",
  "endpoints": [
    {
      "method": "GET", 
      "path": "/slots"
    },
    {
      "method": "POST", 
      "path": "/appointments"
    },
    {
      "method": "GET", 
      "path": "/appointments/{id}"
    },
    {
      "method": "DELETE", 
      "path": "/appointments/{id}"
    }
  ],
  "schemas": [
    {
      "name": "Slot",
      "description": "Search result for available slots"
    },
    {
      "name": "Appointment",
      "description": "New or updated appointment data"
    },
    {
      "name": "Error",
      "description": "API error response object"
    }
  ],
  "context": {
    "clinic_name": "Healthcare Clinic",
    "purpose": "Online appointment booking system",
    "current_state": "85% of appointments booked via phone with 8-minute average call time and 35% abandonment rate",
    "business_objives": "Reduce call volume by 40% through online self-scheduling"
  },
  "constraints": {
    "timeframe": "8 months",
    "budget": "$250,000"
  },
  "integration_options": [
    "FHIR APIs via Epic EHR"
  ],
  "compliance_requirements": ["HIPAA"]
}
