import { Metadata } from 'next';
import { ChatInterface } from '@/components/chat';

export const metadata: Metadata = {
  title: 'Chat - IBS Wellness Companion',
  description: 'Chat with your AI wellness assistant for personalized IBS support and recommendations.',
};

export default function ChatPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI Wellness Assistant
        </h1>
        <p className="text-gray-600">
          Get personalized IBS support, symptom assessments, and recommendations from your AI assistant.
        </p>
      </div>
      
      <ChatInterface className="mx-auto" />
      
      <div className="mt-6 text-sm text-gray-500 text-center">
        <p>
          Your conversations are private and secure. The AI assistant uses your health data 
          to provide personalized recommendations and insights.
        </p>
      </div>
    </div>
  );
}