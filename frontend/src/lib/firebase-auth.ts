import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  sendPasswordResetEmail,
  sendEmailVerification,
  updateProfile,
  User as FirebaseUser,
  AuthError
} from 'firebase/auth';
import { auth } from './firebase';

export interface FirebaseAuthService {
  signIn: (email: string, password: string) => Promise<FirebaseUser>;
  signUp: (email: string, password: string, displayName?: string) => Promise<FirebaseUser>;
  signOut: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  sendVerificationEmail: (user: FirebaseUser) => Promise<void>;
  updateUserProfile: (user: FirebaseUser, profile: { displayName?: string; photoURL?: string }) => Promise<void>;
}

class FirebaseAuthServiceImpl implements FirebaseAuthService {
  async signIn(email: string, password: string): Promise<FirebaseUser> {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return userCredential.user;
    } catch (error) {
      const authError = error as AuthError;
      throw new Error(this.getErrorMessage(authError.code));
    }
  }

  async signUp(email: string, password: string, displayName?: string): Promise<FirebaseUser> {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      
      // Update display name if provided
      if (displayName) {
        await updateProfile(user, { displayName });
      }
      
      // Send email verification
      await sendEmailVerification(user);
      
      return user;
    } catch (error) {
      const authError = error as AuthError;
      throw new Error(this.getErrorMessage(authError.code));
    }
  }

  async signOut(): Promise<void> {
    try {
      await signOut(auth);
    } catch (error) {
      const authError = error as AuthError;
      throw new Error(this.getErrorMessage(authError.code));
    }
  }

  async resetPassword(email: string): Promise<void> {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (error) {
      const authError = error as AuthError;
      throw new Error(this.getErrorMessage(authError.code));
    }
  }

  async sendVerificationEmail(user: FirebaseUser): Promise<void> {
    try {
      await sendEmailVerification(user);
    } catch (error) {
      const authError = error as AuthError;
      throw new Error(this.getErrorMessage(authError.code));
    }
  }

  async updateUserProfile(user: FirebaseUser, profile: { displayName?: string; photoURL?: string }): Promise<void> {
    try {
      await updateProfile(user, profile);
    } catch (error) {
      const authError = error as AuthError;
      throw new Error(this.getErrorMessage(authError.code));
    }
  }

  private getErrorMessage(errorCode: string): string {
    switch (errorCode) {
      case 'auth/user-not-found':
        return 'No user found with this email address.';
      case 'auth/wrong-password':
        return 'Incorrect password.';
      case 'auth/email-already-in-use':
        return 'An account with this email already exists.';
      case 'auth/weak-password':
        return 'Password should be at least 6 characters.';
      case 'auth/invalid-email':
        return 'Invalid email address.';
      case 'auth/user-disabled':
        return 'This account has been disabled.';
      case 'auth/too-many-requests':
        return 'Too many failed attempts. Please try again later.';
      case 'auth/network-request-failed':
        return 'Network error. Please check your connection.';
      default:
        return 'An error occurred during authentication.';
    }
  }
}

export const firebaseAuthService = new FirebaseAuthServiceImpl();
export { auth };