'use client';

import React, { useState } from 'react';
import { 
  Play, 
  Database, 
  Users, 
  Calendar, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  Download,
  Upload,
  RefreshCw
} from 'lucide-react';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';

interface TestUser {
  id: string;
  name: string;
  email: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  ibsType: 'IBS-D' | 'IBS-C' | 'IBS-M' | 'IBS-U';
  diagnosisDate: string;
  severity: 'mild' | 'moderate' | 'severe';
}

interface TestSymptom {
  id: string;
  userId: string;
  date: string;
  time: string;
  severity: number;
  symptoms: string[];
  triggers: string[];
  duration: number;
  notes: string;
}

interface TestDietEntry {
  id: string;
  userId: string;
  date: string;
  meal: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  foods: string[];
  reactions: { food: string; severity: number; symptoms: string[] }[];
  notes: string;
}

interface TestMedication {
  id: string;
  userId: string;
  name: string;
  dosage: string;
  frequency: string;
  startDate: string;
  endDate: string;
  effectiveness: number;
  sideEffects: string[];
}

interface TestScenario {
  id: string;
  name: string;
  description: string;
  users: TestUser[];
  symptoms: TestSymptom[];
  dietEntries: TestDietEntry[];
  medications: TestMedication[];
  expectedOutcomes: {
    severityPrediction: number;
    flareupRisk: number;
    topTriggers: string[];
    recommendations: string[];
  };
}

// Sample test data generators
class TestDataGenerator {
  static generateUser(overrides: Partial<TestUser> = {}): TestUser {
    const names = ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown'];
    const genders: TestUser['gender'][] = ['male', 'female', 'other'];
    const ibsTypes: TestUser['ibsType'][] = ['IBS-D', 'IBS-C', 'IBS-M', 'IBS-U'];
    const severities: TestUser['severity'][] = ['mild', 'moderate', 'severe'];
    
    const nameIndex = Math.floor(Math.random() * names.length);
    const genderIndex = Math.floor(Math.random() * genders.length);
    const ibsIndex = Math.floor(Math.random() * ibsTypes.length);
    const severityIndex = Math.floor(Math.random() * severities.length);
    
    const diagnosisDateObj = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000 * 5);
    const diagnosisDate = diagnosisDateObj.toISOString().substring(0, 10);
    
    return {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: names[nameIndex] || 'Test User',
      email: `test${Math.floor(Math.random() * 1000)}@example.com`,
      age: Math.floor(Math.random() * 50) + 20,
      gender: genders[genderIndex] || 'other',
      ibsType: ibsTypes[ibsIndex] || 'IBS-M',
      diagnosisDate,
      severity: severities[severityIndex] || 'moderate',
      ...overrides
    };
  }

  static generateSymptoms(userId: string, count: number = 30): TestSymptom[] {
    const symptoms: TestSymptom[] = [];
    const symptomTypes = [
      'Abdominal pain', 'Bloating', 'Gas', 'Diarrhea', 'Constipation', 
      'Cramping', 'Nausea', 'Urgency', 'Fatigue'
    ];
    const triggers = [
      'Stress', 'Dairy', 'Gluten', 'Spicy food', 'Caffeine', 'Alcohol', 
      'Lack of sleep', 'Exercise', 'Travel'
    ];

    for (let i = 0; i < count; i++) {
      const dateObj = new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000);
      const date = dateObj.toISOString().substring(0, 10);
      const time = `${Math.floor(Math.random() * 24).toString().padStart(2, '0')}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`;
      
      symptoms.push({
        id: `symptom_${userId}_${i}`,
        userId,
        date,
        time,
        severity: Math.floor(Math.random() * 10) + 1,
        symptoms: [symptomTypes[Math.floor(Math.random() * symptomTypes.length)] || 'Unknown'],
        triggers: Math.random() > 0.5 ? [triggers[Math.floor(Math.random() * triggers.length)] || 'Unknown'] : [],
        duration: Math.floor(Math.random() * 480) + 30, // 30 minutes to 8 hours
        notes: Math.random() > 0.7 ? 'Additional notes about this episode' : ''
      });
    }

    return symptoms.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }

  static generateDietEntries(userId: string, count: number = 90): TestDietEntry[] {
    const entries: TestDietEntry[] = [];
    const foods = [
      'Rice', 'Chicken', 'Salmon', 'Broccoli', 'Carrots', 'Bread', 'Pasta', 
      'Milk', 'Cheese', 'Yogurt', 'Apples', 'Bananas', 'Beans', 'Nuts', 
      'Chocolate', 'Coffee', 'Tea', 'Spicy curry', 'Pizza', 'Salad'
    ];
    const meals: TestDietEntry['meal'][] = ['breakfast', 'lunch', 'dinner', 'snack'];

    for (let i = 0; i < count; i++) {
      const date = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000);
      const dateString = date.toISOString().substring(0, 10);
      const mealFoods = foods.slice(0, Math.floor(Math.random() * 5) + 1);
      const selectedMeal = meals[Math.floor(Math.random() * meals.length)] || 'snack';
      const reactionFoods = mealFoods.slice(0, Math.floor(Math.random() * 2));
      
      entries.push({
        id: `diet_${Date.now()}_${i}`,
        userId,
        date: dateString, // Now guaranteed to be a string
        meal: selectedMeal,
        foods: mealFoods.length > 0 ? mealFoods : ['Rice'],
        reactions: reactionFoods.map(food => {
          const reactionSymptoms = ['Bloating', 'Gas', 'Cramping'].slice(0, Math.floor(Math.random() * 3) + 1);
          return {
            food,
            severity: Math.floor(Math.random() * 8) + 1,
            symptoms: reactionSymptoms.length > 0 ? reactionSymptoms : ['Bloating']
          };
        }),
        notes: `Generated diet entry ${i + 1}`
      });
    }

    return entries.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  }

  static generateMedications(userId: string, count: number = 5): TestMedication[] {
    const medications = [
      'Loperamide', 'Dicyclomine', 'Rifaximin', 'Lubiprostone', 
      'Eluxadoline', 'Alosetron', 'Linaclotide', 'Plecanatide'
    ];
    const frequencies = ['Once daily', 'Twice daily', 'Three times daily', 'As needed', 'With meals'];
    const sideEffects = ['Nausea', 'Dizziness', 'Headache', 'Constipation', 'Diarrhea', 'Fatigue'];
    const entries: TestMedication[] = [];

    for (let i = 0; i < count; i++) {
       const startDateObj = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000);
       const startDate = startDateObj.toISOString().substring(0, 10);
       const endDateObj = new Date(startDateObj.getTime() + Math.random() * 180 * 24 * 60 * 60 * 1000);
       const endDate = endDateObj.toISOString().substring(0, 10);
       
       entries.push({
         id: `medication_${userId}_${i}`,
         userId,
         name: medications[Math.floor(Math.random() * medications.length)] || 'Unknown Medication',
         dosage: `${Math.floor(Math.random() * 50) + 5}mg`,
         frequency: frequencies[Math.floor(Math.random() * frequencies.length)] || 'As needed',
         startDate,
         endDate,
         effectiveness: Math.floor(Math.random() * 10) + 1,
         sideEffects: Math.random() > 0.6 ? 
           [sideEffects[Math.floor(Math.random() * sideEffects.length)] || 'None'] : []
       });
     }

    return entries;
  }

  static generateTestScenario(name: string, description: string): TestScenario {
    const users = Array.from({ length: 3 }, () => TestDataGenerator.generateUser());
    const symptoms = users.flatMap(user => TestDataGenerator.generateSymptoms(user.id, 20));
    const dietEntries = users.flatMap(user => TestDataGenerator.generateDietEntries(user.id, 60));
    const medications = users.flatMap(user => TestDataGenerator.generateMedications(user.id, 3));
    
    const topTriggers = ['Stress', 'Dairy', 'Gluten'].slice(0, Math.floor(Math.random() * 3) + 1);
    const recommendations = [
      'Reduce dairy intake',
      'Practice stress management',
      'Increase fiber gradually',
      'Consider elimination diet'
    ].slice(0, Math.floor(Math.random() * 4) + 1);

    return {
      id: `scenario_${Date.now()}`,
      name,
      description,
      users,
      symptoms,
      dietEntries,
      medications,
      expectedOutcomes: {
        severityPrediction: Math.random() * 10,
        flareupRisk: Math.random() * 100,
        topTriggers: topTriggers.length > 0 ? topTriggers : ['Stress'],
        recommendations: recommendations.length > 0 ? recommendations : ['Practice stress management']
      }
    };
  }
}

// Predefined test scenarios
const predefinedScenarios: Omit<TestScenario, 'id' | 'users' | 'symptoms' | 'dietEntries' | 'medications'>[] = [
  {
    name: 'High Stress Period',
    description: 'Simulates users during high-stress periods with increased symptom severity',
    expectedOutcomes: {
      severityPrediction: 7.5,
      flareupRisk: 85,
      topTriggers: ['Stress', 'Lack of sleep', 'Irregular eating'],
      recommendations: ['Stress management techniques', 'Regular sleep schedule', 'Consistent meal times']
    }
  },
  {
    name: 'Dietary Trigger Discovery',
    description: 'Tests the system\'s ability to identify food triggers through elimination patterns',
    expectedOutcomes: {
      severityPrediction: 5.2,
      flareupRisk: 45,
      topTriggers: ['Dairy', 'Gluten', 'High-fat foods'],
      recommendations: ['Elimination diet trial', 'Food diary maintenance', 'Gradual reintroduction']
    }
  },
  {
    name: 'Medication Effectiveness',
    description: 'Evaluates how well the system tracks medication effectiveness and side effects',
    expectedOutcomes: {
      severityPrediction: 4.1,
      flareupRisk: 30,
      topTriggers: ['Medication timing', 'Dosage consistency'],
      recommendations: ['Medication adherence tracking', 'Timing optimization', 'Side effect monitoring']
    }
  },
  {
    name: 'Seasonal Patterns',
    description: 'Tests detection of seasonal or cyclical symptom patterns',
    expectedOutcomes: {
      severityPrediction: 6.0,
      flareupRisk: 60,
      topTriggers: ['Weather changes', 'Seasonal foods', 'Activity level changes'],
      recommendations: ['Seasonal preparation', 'Activity adjustment', 'Preventive measures']
    }
  }
];

export default function TestDataGeneratorComponent() {
  const [activeScenario, setActiveScenario] = useState<TestScenario | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [testResults, setTestResults] = useState<any[]>([]);
  const [generationProgress, setGenerationProgress] = useState(0);

  const generateScenario = async (scenarioTemplate: typeof predefinedScenarios[0]) => {
    setIsGenerating(true);
    setGenerationProgress(0);

    try {
      // Simulate progressive data generation
      const scenario = TestDataGenerator.generateTestScenario(
        scenarioTemplate.name,
        scenarioTemplate.description
      );
      
      // Update progress
      for (let i = 0; i <= 100; i += 10) {
        setGenerationProgress(i);
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      scenario.expectedOutcomes = scenarioTemplate.expectedOutcomes;
      setActiveScenario(scenario);
    } catch (error) {
      console.error('Error generating scenario:', error);
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
    }
  };

  const runMLTests = async () => {
    if (!activeScenario) return;

    setIsGenerating(true);
    try {
      // Simulate ML prediction testing
      const results = [];
      
      for (const user of activeScenario.users) {
        // Simulate API calls to ML endpoints
        const userSymptoms = activeScenario.symptoms.filter(s => s.userId === user.id);
        const userDiet = activeScenario.dietEntries.filter(d => d.userId === user.id);
        
        const result = {
          userId: user.id,
          userName: user.name,
          severityPrediction: Math.random() * 10,
          flareupRisk: Math.random() * 100,
          accuracy: Math.random() * 0.3 + 0.7, // 70-100% accuracy
          processingTime: Math.random() * 500 + 100, // 100-600ms
          dataPoints: userSymptoms.length + userDiet.length
        };
        
        results.push(result);
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      setTestResults(results);
    } catch (error) {
      console.error('Error running ML tests:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const exportTestData = () => {
    if (!activeScenario) return;
    
    const dataToExport = {
      scenario: activeScenario,
      testResults,
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ibs-test-data-${activeScenario.name.toLowerCase().replace(/\s+/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderScenarioOverview = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Test Users</p>
              <p className="text-2xl font-bold text-gray-900">
                {activeScenario?.users.length || 0}
              </p>
            </div>
            <Users className="text-blue-500" size={24} />
          </div>
        </div>
        
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Symptom Entries</p>
              <p className="text-2xl font-bold text-gray-900">
                {activeScenario?.symptoms.length || 0}
              </p>
            </div>
            <TrendingUp className="text-green-500" size={24} />
          </div>
        </div>
        
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Diet Entries</p>
              <p className="text-2xl font-bold text-gray-900">
                {activeScenario?.dietEntries.length || 0}
              </p>
            </div>
            <Database className="text-purple-500" size={24} />
          </div>
        </div>
        
        <div className="bg-white border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Medications</p>
              <p className="text-2xl font-bold text-gray-900">
                {activeScenario?.medications.length || 0}
              </p>
            </div>
            <Calendar className="text-orange-500" size={24} />
          </div>
        </div>
      </div>

      {activeScenario && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Scenario Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Test Users</h4>
              <div className="space-y-2">
                {activeScenario.users.map(user => (
                  <div key={user.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div>
                      <span className="font-medium">{user.name}</span>
                      <span className="text-sm text-gray-500 ml-2">({user.age}y, {user.gender})</span>
                    </div>
                    <Badge variant={user.severity === 'severe' ? 'destructive' : user.severity === 'moderate' ? 'default' : 'secondary'}>
                      {user.ibsType} - {user.severity}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Expected Outcomes</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Severity Prediction:</span>
                  <span className="font-medium">{activeScenario.expectedOutcomes.severityPrediction.toFixed(1)}/10</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Flare-up Risk:</span>
                  <span className="font-medium">{activeScenario.expectedOutcomes.flareupRisk.toFixed(0)}%</span>
                </div>
                <div>
                  <span className="text-sm text-gray-600">Top Triggers:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {activeScenario.expectedOutcomes.topTriggers.map(trigger => (
                      <Badge key={trigger} variant="outline" className="text-xs">
                        {trigger}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderTestResults = () => (
    <div className="space-y-6">
      {testResults.length > 0 ? (
        <>
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">ML Prediction Results</h3>
            <div className="space-y-4">
              {testResults.map(result => (
                <div key={result.userId} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{result.userName}</h4>
                    <Badge variant={result.accuracy > 0.9 ? 'default' : result.accuracy > 0.8 ? 'secondary' : 'destructive'}>
                      {(result.accuracy * 100).toFixed(1)}% accuracy
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Severity Prediction:</span>
                      <div className="font-medium">{result.severityPrediction.toFixed(1)}/10</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Flare-up Risk:</span>
                      <div className="font-medium">{result.flareupRisk.toFixed(0)}%</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Processing Time:</span>
                      <div className="font-medium">{result.processingTime.toFixed(0)}ms</div>
                    </div>
                    <div>
                      <span className="text-gray-500">Data Points:</span>
                      <div className="font-medium">{result.dataPoints}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="text-green-600" size={20} />
              <span className="font-medium text-green-800">Test Completed Successfully</span>
            </div>
            <p className="text-sm text-green-700 mt-2">
              All ML predictions completed with average accuracy of {((testResults.reduce((acc, r) => acc + r.accuracy, 0) / testResults.length) * 100).toFixed(1)}%
            </p>
          </div>
        </>
      ) : (
        <div className="text-center py-12">
          <Database className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-500">No test results yet. Run ML tests to see results.</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          IBS Test Data Generator
        </h1>
        <p className="text-gray-600">
          Generate realistic test data and validate ML prediction accuracy with sample scenarios.
        </p>
      </div>

      <Tabs defaultValue="scenarios" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="scenarios">Test Scenarios</TabsTrigger>
          <TabsTrigger value="overview">Data Overview</TabsTrigger>
          <TabsTrigger value="results">Test Results</TabsTrigger>
        </TabsList>

        <TabsContent value="scenarios">
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {predefinedScenarios.map((scenario, index) => (
                <div key={index} className="bg-white border rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {scenario.name}
                  </h3>
                  <p className="text-gray-600 mb-4">{scenario.description}</p>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Expected Severity:</span>
                      <span className="font-medium">{scenario.expectedOutcomes.severityPrediction}/10</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Flare-up Risk:</span>
                      <span className="font-medium">{scenario.expectedOutcomes.flareupRisk}%</span>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => generateScenario(scenario)}
                    disabled={isGenerating}
                    className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {isGenerating ? (
                      <>
                        <RefreshCw className="animate-spin" size={16} />
                        <span>Generating...</span>
                      </>
                    ) : (
                      <>
                        <Play size={16} />
                        <span>Generate Scenario</span>
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>

            {isGenerating && (
              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Generating Test Data...</h3>
                <Progress value={generationProgress} className="mb-2" />
                <p className="text-sm text-gray-600">{generationProgress}% complete</p>
              </div>
            )}

            {activeScenario && !isGenerating && (
              <div className="bg-white border rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Active Scenario: {activeScenario.name}</h3>
                  <div className="flex space-x-2">
                    <button
                      onClick={runMLTests}
                      className="bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 flex items-center space-x-2"
                    >
                      <Play size={16} />
                      <span>Run ML Tests</span>
                    </button>
                    <button
                      onClick={exportTestData}
                      className="bg-purple-500 text-white py-2 px-4 rounded-md hover:bg-purple-600 flex items-center space-x-2"
                    >
                      <Download size={16} />
                      <span>Export Data</span>
                    </button>
                  </div>
                </div>
                <p className="text-gray-600">{activeScenario.description}</p>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="overview">
          {renderScenarioOverview()}
        </TabsContent>

        <TabsContent value="results">
          {renderTestResults()}
        </TabsContent>
      </Tabs>
    </div>
  );
}