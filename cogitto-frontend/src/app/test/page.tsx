'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function TestPage() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Cogitto UI Test</h1>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Healthcare Button</CardTitle>
            <CardDescription>Test our medical-themed buttons</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="medical" className="w-full">Medical Action</Button>
            <Button variant="success" className="w-full">Success</Button>
            <Button variant="warning" className="w-full">Warning</Button>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Card Component</CardTitle>
            <CardDescription>Beautiful card design for healthcare UI</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              This card will be used for displaying medications, chat messages, and user information.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
