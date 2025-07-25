'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  HeartIcon, 
  ShieldCheckIcon, 
  ChatBubbleLeftRightIcon,
  UserGroupIcon 
} from '@heroicons/react/24/outline';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <HeartIcon className="h-8 w-8 text-teal-600" />
            <h1 className="text-2xl font-bold text-gray-900">Cogitto</h1>
            <span className="text-sm text-teal-600 font-medium">AI Medication Assistant</span>
          </div>
          <div className="space-x-4">
            <Link href="/login">
              <Button variant="outline">Login</Button>
            </Link>
            <Link href="/register">
              <Button variant="medical">Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Your Personal AI
            <span className="text-teal-600"> Medication Assistant</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Get intelligent, personalized medication guidance powered by real FDA data. 
            Track your medications, check interactions, and chat with an AI that understands your health needs.
          </p>
          <div className="space-x-4">
            <Link href="/register">
              <Button size="xl" variant="medical">
                Start Your Health Journey
              </Button>
            </Link>
            <Link href="/demo">
              <Button size="xl" variant="outline">
                Try Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
          Intelligent Healthcare at Your Fingertips
        </h2>
        
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="mx-auto w-12 h-12 bg-teal-100 rounded-lg flex items-center justify-center mb-4">
                <HeartIcon className="h-6 w-6 text-teal-600" />
              </div>
              <CardTitle>Real FDA Data</CardTitle>
              <CardDescription>
                25+ real medications from FDA Orange Book with accurate information
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="mx-auto w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <ChatBubbleLeftRightIcon className="h-6 w-6 text-blue-600" />
              </div>
              <CardTitle>AI Conversations</CardTitle>
              <CardDescription>
                Chat with GPT-4 enhanced with pharmaceutical knowledge
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="mx-auto w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <ShieldCheckIcon className="h-6 w-6 text-green-600" />
              </div>
              <CardTitle>Safety First</CardTitle>
              <CardDescription>
                Drug interaction checking and safety warnings included
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="text-center hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="mx-auto w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <UserGroupIcon className="h-6 w-6 text-purple-600" />
              </div>
              <CardTitle>Personal Tracking</CardTitle>
              <CardDescription>
                Track your medications with dosage, notes, and reminders
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-teal-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Take Control of Your Medications?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of users who trust Cogitto for their medication management
          </p>
          <Link href="/register">
            <Button size="xl" variant="secondary">
              Create Your Free Account
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <HeartIcon className="h-6 w-6 text-teal-400" />
            <span className="text-xl font-bold">Cogitto</span>
          </div>
          <p className="text-gray-400">
            Professional medication assistance powered by AI and real FDA data
          </p>
        </div>
      </footer>
    </div>
  );
}
