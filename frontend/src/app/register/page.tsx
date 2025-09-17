import { RegisterForm } from "@/components/auth/register-form"
import { Heart } from "lucide-react"
import Link from "next/link"

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href="/" className="inline-flex items-center space-x-2 mb-8">
            <Heart className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">IBS Wellness</span>
          </Link>
          <h2 className="text-3xl font-bold text-gray-900">Join us today</h2>
          <p className="mt-2 text-gray-600">
            Create your account and start your wellness journey
          </p>
        </div>

        <RegisterForm />
      </div>
    </div>
  )
}