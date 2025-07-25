import React from 'react';
import { Alert } from '@/components/ui/alert';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export function SafetyDisclaimer() {
  return (
    <div className="p-4 bg-gradient-to-r from-blue-50 to-teal-50">
      <Alert variant="info" className="border-blue-200">
        <ExclamationTriangleIcon className="h-4 w-4" />
        <div className="ml-2">
          <p className="text-sm font-semibold text-blue-900">Medical Information Disclaimer</p>
          <p className="text-sm text-blue-800 mt-1 font-medium">
            Cogitto provides educational information only. Always consult your healthcare provider for medical advice, 
            diagnosis, or treatment decisions.
          </p>
        </div>
      </Alert>
    </div>
  );
}
