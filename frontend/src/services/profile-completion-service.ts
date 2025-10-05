interface ProfileSection {
  id: string;
  name: string;
  endpoint: string;
}

interface ProfileCompletionResult {
  completedSections: string[];
  totalSections: number;
  completionPercentage: number;
  sectionStatus: { [key: string]: boolean };
}

class ProfileCompletionService {
  private readonly profileSections: ProfileSection[] = [
    {
      id: 'basic-info',
      name: 'Basic Information',
      endpoint: '/api/v1/profile/basic-info'
    },
    {
      id: 'medical-history',
      name: 'Medical History',
      endpoint: '/api/v1/profile/medical-history'
    },
    {
      id: 'dietary-preferences',
      name: 'Dietary Preferences',
      endpoint: '/api/v1/profile/dietary-preferences'
    },
    {
      id: 'lifestyle-factors',
      name: 'Lifestyle Factors',
      endpoint: '/api/v1/profile/lifestyle-factors'
    },
    {
      id: 'goals-preferences',
      name: 'Goals & Preferences',
      endpoint: '/api/v1/profile/goals-preferences'
    }
  ];

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  private getBaseUrl(): string {
    return process.env['NEXT_PUBLIC_API_URL'] || 'http://localhost:8000';
  }

  async checkProfileCompletion(): Promise<ProfileCompletionResult> {
    try {
      const headers = this.getAuthHeaders();
      const baseUrl = this.getBaseUrl();

      // Check each profile section
      const sectionChecks = await Promise.all(
        this.profileSections.map(async (section) => {
          try {
            const response = await fetch(`${baseUrl}${section.endpoint}`, {
              credentials: 'include',
              headers
            });
            return {
              sectionId: section.id,
              completed: response.ok
            };
          } catch (error) {
            console.error(`Error checking ${section.name}:`, error);
            return {
              sectionId: section.id,
              completed: false
            };
          }
        })
      );

      // Process results
      const completedSections: string[] = [];
      const sectionStatus: { [key: string]: boolean } = {};

      sectionChecks.forEach(({ sectionId, completed }) => {
        sectionStatus[sectionId] = completed;
        if (completed) {
          completedSections.push(sectionId);
        }
      });

      const completionPercentage = Math.round(
        (completedSections.length / this.profileSections.length) * 100
      );

      return {
        completedSections,
        totalSections: this.profileSections.length,
        completionPercentage,
        sectionStatus
      };
    } catch (error) {
      console.error('Error checking profile completion:', error);
      
      // Return default values on error
      return {
        completedSections: [],
        totalSections: this.profileSections.length,
        completionPercentage: 0,
        sectionStatus: {}
      };
    }
  }

  getProfileSections(): ProfileSection[] {
    return [...this.profileSections];
  }

  getSectionById(id: string): ProfileSection | undefined {
    return this.profileSections.find(section => section.id === id);
  }
}

export const profileCompletionService = new ProfileCompletionService();
export type { ProfileCompletionResult, ProfileSection };