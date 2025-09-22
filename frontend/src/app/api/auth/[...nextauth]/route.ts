import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import CredentialsProvider from 'next-auth/providers/credentials'
import { NextAuthOptions } from 'next-auth'

declare module 'next-auth' {
  interface Session {
    accessToken?: string
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    accessToken?: string
    refreshToken?: string
    user?: any
  }
}

const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env['GOOGLE_CLIENT_ID']!,
      clientSecret: process.env['GOOGLE_CLIENT_SECRET']!,
    }),
    GitHubProvider({
      clientId: process.env['GITHUB_CLIENT_ID']!,
      clientSecret: process.env['GITHUB_CLIENT_SECRET']!,
    }),
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL']}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: credentials.email,
              password: credentials.password,
            }),
          })

          if (!response.ok) {
            return null
          }

          const data = await response.json()
          
          return {
            id: data.user.id,
            email: data.user.email,
            name: `${data.user.first_name} ${data.user.last_name}`,
            image: data.user.avatar,
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
          }
        } catch (error) {
          console.error('Authentication error:', error)
          return null
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user, account }) {
      // Handle OAuth providers (Google, GitHub)
      if (account && user) {
        if (account.provider === 'google' || account.provider === 'github') {
          // Register or login OAuth user with backend
          try {
            const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL']}/api/v1/auth/oauth`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                provider: account.provider,
                provider_id: account.providerAccountId,
                email: user.email,
                name: user.name,
                image: user.image,
                access_token: account.access_token,
              }),
            })

            if (response.ok) {
              const data = await response.json()
              token.accessToken = data.access_token
              token.refreshToken = data.refresh_token
              token.user = data.user
            }
          } catch (error) {
            console.error('OAuth backend registration error:', error)
          }
        } else {
          // Handle credentials provider
          token.accessToken = (user as any).accessToken
          token.refreshToken = (user as any).refreshToken
        }
      }

      // Handle token refresh
      if (token.refreshToken && Date.now() > (token['exp'] as number) * 1000) {
        try {
          const response = await fetch(`${process.env['NEXT_PUBLIC_API_URL']}/api/v1/auth/refresh`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              refresh_token: token.refreshToken,
            }),
          })

          if (response.ok) {
            const data = await response.json()
            token.accessToken = data.access_token
            token.refreshToken = data.refresh_token
          }
        } catch (error) {
          console.error('Token refresh error:', error)
        }
      }

      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string
      if (session.user) {
        (session.user as any).id = token.sub as string
      }
      return session
    },
    async signIn({ user, account, profile }) {
      // Allow all sign-ins
      return true
    },
  },
  pages: {
    signIn: '/login',
  },
  session: {
    strategy: 'jwt',
  },
  secret: process.env.NEXTAUTH_SECRET,
}

const handler = NextAuth(authOptions)

export { handler as GET, handler as POST, authOptions }