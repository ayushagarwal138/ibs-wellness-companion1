"""
IBS Recommendation Engine

Advanced recommendation system for generating personalized dietary plans,
lifestyle modifications, and evidence-based health suggestions for IBS management.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RecommendationType(str, Enum):
    """Types of recommendations."""
    DIETARY = "dietary"
    LIFESTYLE = "lifestyle"
    MEDICAL = "medical"
    BEHAVIORAL = "behavioral"
    SUPPLEMENT = "supplement"


class PriorityLevel(str, Enum):
    """Priority levels for recommendations."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    """Individual recommendation structure."""
    id: str
    type: RecommendationType
    title: str
    description: str
    rationale: str
    priority: PriorityLevel
    evidence_level: str
    scientific_references: List[str]
    implementation_steps: List[str]
    expected_timeline: str
    monitoring_metrics: List[str]
    contraindications: List[str]
    personalization_factors: Dict[str, Any]


class IBSRecommendationEngine:
    """
    Comprehensive recommendation engine for IBS management.
    
    Generates personalized recommendations based on:
    - User health profile and symptoms
    - IBS risk assessment results
    - Dietary patterns and preferences
    - Lifestyle factors
    - Medical history
    - Evidence-based guidelines
    """
    
    def __init__(self):
        self.dietary_database = self._initialize_dietary_database()
        self.lifestyle_database = self._initialize_lifestyle_database()
        self.supplement_database = self._initialize_supplement_database()
        self.evidence_database = self._initialize_evidence_database()
        
    def generate_comprehensive_recommendations(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> Dict[str, List[Recommendation]]:
        """
        Generate comprehensive personalized recommendations.
        
        Args:
            user_data: User health and profile data
            risk_assessment: IBS risk assessment results
            
        Returns:
            Categorized recommendations with evidence and implementation guidance
        """
        try:
            recommendations = {
                'immediate_actions': [],
                'dietary_plan': [],
                'lifestyle_modifications': [],
                'medical_consultations': [],
                'behavioral_interventions': [],
                'supplement_suggestions': [],
                'monitoring_plan': []
            }
            
            # Generate immediate actions for high-risk users
            if risk_assessment.get('risk_level') in ['high', 'severe']:
                recommendations['immediate_actions'] = self._generate_immediate_actions(
                    user_data, risk_assessment
                )
            
            # Generate dietary recommendations
            recommendations['dietary_plan'] = self._generate_dietary_recommendations(
                user_data, risk_assessment
            )
            
            # Generate lifestyle modifications
            recommendations['lifestyle_modifications'] = self._generate_lifestyle_recommendations(
                user_data, risk_assessment
            )
            
            # Generate medical consultation recommendations
            recommendations['medical_consultations'] = self._generate_medical_recommendations(
                user_data, risk_assessment
            )
            
            # Generate behavioral interventions
            recommendations['behavioral_interventions'] = self._generate_behavioral_recommendations(
                user_data, risk_assessment
            )
            
            # Generate supplement suggestions
            recommendations['supplement_suggestions'] = self._generate_supplement_recommendations(
                user_data, risk_assessment
            )
            
            # Generate monitoring plan
            recommendations['monitoring_plan'] = self._generate_monitoring_recommendations(
                user_data, risk_assessment
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._get_fallback_recommendations()
    
    def _generate_immediate_actions(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate immediate action recommendations for high-risk users."""
        actions = []
        
        # Severe symptom management
        if risk_assessment.get('risk_level') == 'severe':
            actions.append(Recommendation(
                id="immediate_medical_attention",
                type=RecommendationType.MEDICAL,
                title="Seek Immediate Medical Attention",
                description="Your symptoms indicate severe IBS that requires immediate medical evaluation.",
                rationale="Severe IBS symptoms can significantly impact quality of life and may indicate complications.",
                priority=PriorityLevel.CRITICAL,
                evidence_level="Grade A",
                scientific_references=[
                    "Ford AC, et al. Gastroenterology. 2020;158(5):1262-1273",
                    "Lacy BE, et al. Gastroenterology. 2021;160(4):1262-1286"
                ],
                implementation_steps=[
                    "Contact your gastroenterologist within 24-48 hours",
                    "Document current symptoms and severity",
                    "Prepare list of current medications",
                    "Consider emergency care if symptoms worsen"
                ],
                expected_timeline="Within 24-48 hours",
                monitoring_metrics=["Symptom severity", "Pain levels", "Bowel movement frequency"],
                contraindications=[],
                personalization_factors={"severity_level": risk_assessment.get('risk_level')}
            ))
        
        # Stress management for high stress levels
        symptoms = user_data.get('symptoms', {})
        if symptoms.get('stress_level', 0) >= 8:
            actions.append(Recommendation(
                id="immediate_stress_management",
                type=RecommendationType.BEHAVIORAL,
                title="Implement Immediate Stress Reduction",
                description="High stress levels are significantly impacting your IBS symptoms.",
                rationale="Stress is a major trigger for IBS symptoms and can worsen flare-ups.",
                priority=PriorityLevel.HIGH,
                evidence_level="Grade A",
                scientific_references=[
                    "Qin HY, et al. World J Gastroenterol. 2014;20(27):8886-8897",
                    "Fadgyas-Stanculete M, et al. World J Gastroenterol. 2014;20(2):359-364"
                ],
                implementation_steps=[
                    "Practice deep breathing exercises (5-10 minutes, 3x daily)",
                    "Try progressive muscle relaxation",
                    "Consider meditation apps (Headspace, Calm)",
                    "Limit stressful activities where possible"
                ],
                expected_timeline="Start immediately, effects within 1-2 weeks",
                monitoring_metrics=["Daily stress levels (1-10 scale)", "Symptom frequency"],
                contraindications=[],
                personalization_factors={"stress_level": symptoms.get('stress_level')}
            ))
        
        return actions
    
    def _generate_dietary_recommendations(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate personalized dietary recommendations."""
        dietary_recs = []
        
        profile = user_data.get('profile', {})
        symptoms = user_data.get('symptoms', {})
        dietary_patterns = user_data.get('dietary_patterns', {})
        
        # Low FODMAP diet recommendation
        if dietary_patterns.get('fodmap_adherence', 0) < 0.6:
            dietary_recs.append(Recommendation(
                id="low_fodmap_diet",
                type=RecommendationType.DIETARY,
                title="Implement Low FODMAP Diet",
                description="A structured low FODMAP diet can significantly reduce IBS symptoms.",
                rationale="Low FODMAP diet is the most evidence-based dietary intervention for IBS.",
                priority=PriorityLevel.HIGH,
                evidence_level="Grade A",
                scientific_references=[
                    "Halmos EP, et al. Gastroenterology. 2014;146(1):67-75",
                    "Staudacher HM, et al. Gastroenterology. 2017;153(4):936-947"
                ],
                implementation_steps=[
                    "Phase 1: Eliminate high FODMAP foods for 2-6 weeks",
                    "Phase 2: Systematically reintroduce FODMAP groups",
                    "Phase 3: Personalize diet based on tolerance",
                    "Work with registered dietitian familiar with FODMAP diet"
                ],
                expected_timeline="Initial improvement in 2-4 weeks",
                monitoring_metrics=["Symptom severity", "Bowel movement frequency", "Bloating levels"],
                contraindications=["Eating disorders", "Severe malnutrition"],
                personalization_factors={
                    "ibs_type": profile.get('ibs_type'),
                    "current_adherence": dietary_patterns.get('fodmap_adherence')
                }
            ))
        
        # Fiber modification based on IBS type
        ibs_type = profile.get('ibs_type', 'IBS_U')
        if ibs_type == 'IBS_C':  # Constipation-predominant
            dietary_recs.append(Recommendation(
                id="increase_soluble_fiber",
                type=RecommendationType.DIETARY,
                title="Increase Soluble Fiber Intake",
                description="Gradually increase soluble fiber to improve constipation symptoms.",
                rationale="Soluble fiber can help regulate bowel movements in IBS-C without worsening symptoms.",
                priority=PriorityLevel.MEDIUM,
                evidence_level="Grade B",
                scientific_references=[
                    "Eswaran S, et al. Gastroenterology. 2013;144(5):903-911",
                    "Moayyedi P, et al. BMJ. 2014;348:g2267"
                ],
                implementation_steps=[
                    "Start with 5g additional soluble fiber daily",
                    "Increase by 5g weekly until reaching 25-35g total daily",
                    "Focus on oats, psyllium, apples, carrots",
                    "Increase water intake proportionally"
                ],
                expected_timeline="Improvement in 2-4 weeks",
                monitoring_metrics=["Bowel movement frequency", "Stool consistency", "Abdominal pain"],
                contraindications=["Bowel obstruction", "Severe gastroparesis"],
                personalization_factors={"ibs_type": ibs_type, "current_fiber_intake": dietary_patterns.get('fiber_intake', 25)}
            ))
        
        elif ibs_type == 'IBS_D':  # Diarrhea-predominant
            dietary_recs.append(Recommendation(
                id="reduce_insoluble_fiber",
                type=RecommendationType.DIETARY,
                title="Moderate Insoluble Fiber Intake",
                description="Reduce insoluble fiber to help manage diarrhea symptoms.",
                rationale="Insoluble fiber can worsen diarrhea in IBS-D patients.",
                priority=PriorityLevel.MEDIUM,
                evidence_level="Grade B",
                scientific_references=[
                    "Eswaran S, et al. Gastroenterology. 2013;144(5):903-911",
                    "Chey WD, et al. Am J Gastroenterol. 2015;110(3):393-411"
                ],
                implementation_steps=[
                    "Limit raw vegetables and fruits with skins",
                    "Choose refined grains over whole grains initially",
                    "Cook vegetables thoroughly",
                    "Focus on soluble fiber sources instead"
                ],
                expected_timeline="Improvement in 1-2 weeks",
                monitoring_metrics=["Stool frequency", "Stool consistency", "Urgency episodes"],
                contraindications=["Severe constipation history"],
                personalization_factors={"ibs_type": ibs_type}
            ))
        
        # Hydration recommendations
        if dietary_patterns.get('hydration_level', 2) < 2.5:
            dietary_recs.append(Recommendation(
                id="increase_hydration",
                type=RecommendationType.DIETARY,
                title="Optimize Hydration",
                description="Adequate hydration is essential for digestive health and IBS management.",
                rationale="Proper hydration helps maintain healthy bowel function and can reduce constipation.",
                priority=PriorityLevel.MEDIUM,
                evidence_level="Grade C",
                scientific_references=[
                    "Anti M, et al. Eur J Clin Nutr. 1998;52(4):239-244"
                ],
                implementation_steps=[
                    "Aim for 8-10 glasses of water daily",
                    "Drink water between meals, not during",
                    "Monitor urine color as hydration indicator",
                    "Limit dehydrating beverages (alcohol, excessive caffeine)"
                ],
                expected_timeline="Benefits within 1 week",
                monitoring_metrics=["Daily water intake", "Urine color", "Constipation frequency"],
                contraindications=["Heart failure", "Kidney disease"],
                personalization_factors={"current_hydration": dietary_patterns.get('hydration_level')}
            ))
        
        return dietary_recs
    
    def _generate_lifestyle_recommendations(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate lifestyle modification recommendations."""
        lifestyle_recs = []
        
        lifestyle = user_data.get('lifestyle', {})
        symptoms = user_data.get('symptoms', {})
        
        # Exercise recommendations
        exercise_freq = lifestyle.get('exercise_frequency', 0)
        if exercise_freq < 3:
            lifestyle_recs.append(Recommendation(
                id="regular_exercise",
                type=RecommendationType.LIFESTYLE,
                title="Establish Regular Exercise Routine",
                description="Regular moderate exercise can significantly improve IBS symptoms.",
                rationale="Exercise helps regulate bowel function, reduces stress, and improves overall gut health.",
                priority=PriorityLevel.HIGH,
                evidence_level="Grade B",
                scientific_references=[
                    "Johannesson E, et al. Am J Gastroenterol. 2011;106(5):915-922",
                    "Daley AJ, et al. Sports Med. 2008;38(2):129-145"
                ],
                implementation_steps=[
                    "Start with 15-20 minutes of walking daily",
                    "Gradually increase to 30 minutes, 5 days per week",
                    "Include yoga or stretching 2-3 times per week",
                    "Avoid high-intensity exercise during flare-ups"
                ],
                expected_timeline="Improvement in 4-6 weeks",
                monitoring_metrics=["Exercise frequency", "Symptom severity", "Stress levels"],
                contraindications=["Severe cardiac conditions", "Active inflammatory conditions"],
                personalization_factors={"current_frequency": exercise_freq}
            ))
        
        # Sleep hygiene
        sleep_quality = symptoms.get('sleep_quality', 5)
        if sleep_quality <= 5:
            lifestyle_recs.append(Recommendation(
                id="improve_sleep_hygiene",
                type=RecommendationType.LIFESTYLE,
                title="Optimize Sleep Quality",
                description="Poor sleep can worsen IBS symptoms and increase stress levels.",
                rationale="Sleep disturbances are common in IBS and can perpetuate symptom cycles.",
                priority=PriorityLevel.HIGH,
                evidence_level="Grade B",
                scientific_references=[
                    "Orr WC, et al. Clin Gastroenterol Hepatol. 2014;12(11):1946-1954",
                    "Patel A, et al. Dig Dis Sci. 2016;61(5):1320-1329"
                ],
                implementation_steps=[
                    "Establish consistent sleep schedule (same bedtime/wake time)",
                    "Create relaxing bedtime routine",
                    "Limit screen time 1 hour before bed",
                    "Keep bedroom cool, dark, and quiet",
                    "Avoid large meals 3 hours before bedtime"
                ],
                expected_timeline="Improvement in 2-4 weeks",
                monitoring_metrics=["Sleep quality score", "Sleep duration", "Morning fatigue"],
                contraindications=[],
                personalization_factors={"current_sleep_quality": sleep_quality}
            ))
        
        # Stress management
        stress_level = symptoms.get('stress_level', 5)
        if stress_level >= 6:
            lifestyle_recs.append(Recommendation(
                id="comprehensive_stress_management",
                type=RecommendationType.BEHAVIORAL,
                title="Implement Comprehensive Stress Management",
                description="Chronic stress is a major trigger for IBS symptoms and requires systematic management.",
                rationale="The gut-brain axis means stress directly impacts digestive function in IBS patients.",
                priority=PriorityLevel.HIGH,
                evidence_level="Grade A",
                scientific_references=[
                    "Keefer L, et al. Gastroenterology. 2022;162(1):289-299",
                    "Ford AC, et al. Clin Gastroenterol Hepatol. 2014;12(10):1701-1711"
                ],
                implementation_steps=[
                    "Practice daily mindfulness meditation (10-20 minutes)",
                    "Learn progressive muscle relaxation techniques",
                    "Consider cognitive behavioral therapy (CBT)",
                    "Join stress management classes or support groups",
                    "Identify and address major stressors"
                ],
                expected_timeline="Initial benefits in 2-3 weeks, full benefits in 8-12 weeks",
                monitoring_metrics=["Daily stress levels", "Symptom frequency", "Anxiety scores"],
                contraindications=["Severe psychiatric conditions requiring immediate treatment"],
                personalization_factors={"stress_level": stress_level}
            ))
        
        return lifestyle_recs
    
    def _generate_medical_recommendations(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate medical consultation and treatment recommendations."""
        medical_recs = []
        
        risk_level = risk_assessment.get('risk_level', 'moderate')
        medical_history = user_data.get('medical_history', {})
        
        # Gastroenterologist consultation for high-risk patients
        if risk_level in ['high', 'severe']:
            medical_recs.append(Recommendation(
                id="gastroenterologist_consultation",
                type=RecommendationType.MEDICAL,
                title="Gastroenterologist Consultation",
                description="Your risk assessment indicates need for specialized gastroenterology care.",
                rationale="High-risk IBS patients benefit from specialized medical management and monitoring.",
                priority=PriorityLevel.HIGH,
                evidence_level="Grade A",
                scientific_references=[
                    "Ford AC, et al. Lancet. 2020;396(10263):1675-1688",
                    "Lacy BE, et al. Gastroenterology. 2021;160(4):1262-1286"
                ],
                implementation_steps=[
                    "Request referral from primary care physician",
                    "Prepare symptom diary for consultation",
                    "Compile list of current medications and supplements",
                    "Prepare questions about treatment options"
                ],
                expected_timeline="Schedule within 2-4 weeks",
                monitoring_metrics=["Symptom improvement", "Quality of life scores"],
                contraindications=[],
                personalization_factors={"risk_level": risk_level}
            ))
        
        # Medication review
        medication_adherence = medical_history.get('medication_adherence', 0.8)
        if medication_adherence < 0.7:
            medical_recs.append(Recommendation(
                id="medication_review",
                type=RecommendationType.MEDICAL,
                title="Comprehensive Medication Review",
                description="Poor medication adherence may be impacting your symptom control.",
                rationale="Optimal medication management is crucial for IBS symptom control.",
                priority=PriorityLevel.MEDIUM,
                evidence_level="Grade B",
                scientific_references=[
                    "Chey WD, et al. Am J Gastroenterol. 2015;110(3):393-411"
                ],
                implementation_steps=[
                    "Schedule appointment with prescribing physician",
                    "Discuss barriers to medication adherence",
                    "Review side effects and effectiveness",
                    "Consider medication timing optimization",
                    "Explore alternative formulations if needed"
                ],
                expected_timeline="Within 2 weeks",
                monitoring_metrics=["Medication adherence rate", "Symptom control"],
                contraindications=[],
                personalization_factors={"adherence_rate": medication_adherence}
            ))
        
        return medical_recs
    
    def _generate_behavioral_recommendations(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate behavioral intervention recommendations."""
        behavioral_recs = []
        
        symptoms = user_data.get('symptoms', {})
        risk_level = risk_assessment.get('risk_level', 'moderate')
        
        # Gut-directed hypnotherapy for moderate to high risk
        if risk_level in ['moderate', 'high', 'severe']:
            behavioral_recs.append(Recommendation(
                id="gut_directed_hypnotherapy",
                type=RecommendationType.BEHAVIORAL,
                title="Gut-Directed Hypnotherapy",
                description="Specialized hypnotherapy can significantly improve IBS symptoms and quality of life.",
                rationale="Gut-directed hypnotherapy has strong evidence for IBS symptom improvement.",
                priority=PriorityLevel.MEDIUM,
                evidence_level="Grade A",
                scientific_references=[
                    "Ford AC, et al. Am J Gastroenterol. 2014;109(9):1350-1365",
                    "Schaefert R, et al. Psychosom Med. 2014;76(2):128-138"
                ],
                implementation_steps=[
                    "Find certified gut-directed hypnotherapist",
                    "Commit to 7-12 weekly sessions",
                    "Practice self-hypnosis techniques daily",
                    "Track symptom changes throughout treatment"
                ],
                expected_timeline="Improvement typically seen after 6-8 sessions",
                monitoring_metrics=["IBS symptom severity", "Quality of life scores", "Anxiety levels"],
                contraindications=["Severe psychiatric conditions", "Active psychosis"],
                personalization_factors={"risk_level": risk_level}
            ))
        
        # Cognitive Behavioral Therapy
        if symptoms.get('stress_level', 5) >= 7 or symptoms.get('mood_score', 5) <= 4:
            behavioral_recs.append(Recommendation(
                id="cognitive_behavioral_therapy",
                type=RecommendationType.BEHAVIORAL,
                title="Cognitive Behavioral Therapy (CBT)",
                description="CBT can help manage the psychological aspects of IBS and improve coping strategies.",
                rationale="CBT addresses the gut-brain connection and helps develop effective coping mechanisms.",
                priority=PriorityLevel.MEDIUM,
                evidence_level="Grade A",
                scientific_references=[
                    "Lackner JM, et al. Gastroenterology. 2018;155(1):47-57",
                    "Ford AC, et al. Clin Gastroenterol Hepatol. 2014;12(10):1701-1711"
                ],
                implementation_steps=[
                    "Find therapist specializing in chronic illness/IBS",
                    "Attend weekly sessions for 8-12 weeks",
                    "Practice cognitive restructuring techniques",
                    "Implement behavioral coping strategies"
                ],
                expected_timeline="Significant improvement in 8-12 weeks",
                monitoring_metrics=["Stress levels", "Coping ability", "Symptom severity"],
                contraindications=["Severe depression requiring immediate intervention"],
                personalization_factors={
                    "stress_level": symptoms.get('stress_level'),
                    "mood_score": symptoms.get('mood_score')
                }
            ))
        
        return behavioral_recs
    
    def _generate_supplement_recommendations(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate evidence-based supplement recommendations."""
        supplement_recs = []
        
        profile = user_data.get('profile', {})
        symptoms = user_data.get('symptoms', {})
        
        # Probiotics
        supplement_recs.append(Recommendation(
            id="targeted_probiotics",
            type=RecommendationType.SUPPLEMENT,
            title="Targeted Probiotic Supplementation",
            description="Specific probiotic strains can help restore gut microbiome balance and reduce IBS symptoms.",
            rationale="Certain probiotic strains have demonstrated efficacy in clinical trials for IBS.",
            priority=PriorityLevel.MEDIUM,
            evidence_level="Grade B",
            scientific_references=[
                "Ford AC, et al. Am J Gastroenterol. 2018;113(4):506-518",
                "Tiequn B, et al. J Gastroenterol Hepatol. 2015;30(1):9-17"
            ],
            implementation_steps=[
                "Choose multi-strain probiotic with Lactobacillus and Bifidobacterium",
                "Start with lower dose and gradually increase",
                "Take consistently for at least 4 weeks",
                "Monitor symptom changes"
            ],
            expected_timeline="Initial benefits in 2-4 weeks",
            monitoring_metrics=["Bloating", "Bowel movement regularity", "Overall symptom severity"],
            contraindications=["Immunocompromised state", "Severe acute pancreatitis"],
            personalization_factors={"ibs_type": profile.get('ibs_type')}
        ))
        
        # Peppermint oil for pain management
        if symptoms.get('abdominal_pain', 0) >= 6:
            supplement_recs.append(Recommendation(
                id="peppermint_oil",
                type=RecommendationType.SUPPLEMENT,
                title="Enteric-Coated Peppermint Oil",
                description="Peppermint oil can provide natural antispasmodic effects for abdominal pain.",
                rationale="Peppermint oil has antispasmodic properties that can reduce IBS-related abdominal pain.",
                priority=PriorityLevel.MEDIUM,
                evidence_level="Grade A",
                scientific_references=[
                    "Khanna R, et al. J Clin Gastroenterol. 2014;48(6):505-512",
                    "Alammar N, et al. BMC Complement Altern Med. 2019;19(1):11"
                ],
                implementation_steps=[
                    "Use enteric-coated capsules (0.2-0.4ml, 3 times daily)",
                    "Take 30-60 minutes before meals",
                    "Start with lower dose to assess tolerance",
                    "Continue for 2-8 weeks as needed"
                ],
                expected_timeline="Pain relief within 1-2 weeks",
                monitoring_metrics=["Abdominal pain intensity", "Pain frequency"],
                contraindications=["GERD", "Hiatal hernia", "Gallstones"],
                personalization_factors={"pain_level": symptoms.get('abdominal_pain')}
            ))
        
        return supplement_recs
    
    def _generate_monitoring_recommendations(
        self, 
        user_data: Dict[str, Any], 
        risk_assessment: Dict[str, Any]
    ) -> List[Recommendation]:
        """Generate monitoring and tracking recommendations."""
        monitoring_recs = []
        
        # Symptom tracking
        monitoring_recs.append(Recommendation(
            id="comprehensive_symptom_tracking",
            type=RecommendationType.BEHAVIORAL,
            title="Comprehensive Symptom and Trigger Tracking",
            description="Systematic tracking helps identify patterns and triggers for personalized management.",
            rationale="Detailed tracking enables identification of personal triggers and treatment effectiveness.",
            priority=PriorityLevel.HIGH,
            evidence_level="Grade B",
            scientific_references=[
                "Halpert A, et al. Clin Gastroenterol Hepatol. 2007;5(10):1175-1183"
            ],
            implementation_steps=[
                "Track daily symptoms, severity, and duration",
                "Record food intake and timing",
                "Monitor stress levels and sleep quality",
                "Note medication timing and effectiveness",
                "Use mobile app or diary for consistency"
            ],
            expected_timeline="Patterns emerge after 2-4 weeks of tracking",
            monitoring_metrics=["Tracking consistency", "Pattern identification"],
            contraindications=["Obsessive-compulsive tendencies that might worsen with tracking"],
            personalization_factors={"risk_level": risk_assessment.get('risk_level')}
        ))
        
        return monitoring_recs
    
    def _initialize_dietary_database(self) -> Dict[str, Any]:
        """Initialize dietary recommendations database."""
        return {
            "low_fodmap_foods": [
                "Rice", "Quinoa", "Oats", "Potatoes", "Carrots", "Spinach",
                "Bell peppers", "Tomatoes", "Chicken", "Fish", "Eggs",
                "Lactose-free dairy", "Oranges", "Grapes", "Strawberries"
            ],
            "high_fodmap_foods": [
                "Wheat", "Rye", "Onions", "Garlic", "Apples", "Pears",
                "Milk", "Yogurt", "Beans", "Lentils", "Cashews", "Pistachios"
            ],
            "soluble_fiber_sources": [
                "Oats", "Psyllium husk", "Apples", "Carrots", "Sweet potatoes",
                "Flaxseeds", "Chia seeds"
            ],
            "trigger_foods_common": [
                "Spicy foods", "Fatty foods", "Alcohol", "Caffeine",
                "Artificial sweeteners", "Processed foods"
            ]
        }
    
    def _initialize_lifestyle_database(self) -> Dict[str, Any]:
        """Initialize lifestyle recommendations database."""
        return {
            "exercise_types": {
                "low_impact": ["Walking", "Swimming", "Yoga", "Tai Chi"],
                "moderate": ["Cycling", "Dancing", "Light jogging"],
                "strength": ["Resistance bands", "Light weights", "Bodyweight exercises"]
            },
            "stress_management": [
                "Deep breathing", "Progressive muscle relaxation", "Meditation",
                "Mindfulness", "Journaling", "Nature walks"
            ],
            "sleep_hygiene": [
                "Consistent sleep schedule", "Cool bedroom temperature",
                "Dark environment", "No screens before bed", "Relaxation routine"
            ]
        }
    
    def _initialize_supplement_database(self) -> Dict[str, Any]:
        """Initialize supplement recommendations database."""
        return {
            "probiotics": {
                "strains": ["Lactobacillus plantarum", "Bifidobacterium infantis",
                          "Lactobacillus acidophilus", "Bifidobacterium lactis"],
                "dosage": "10^9 to 10^11 CFU daily",
                "duration": "4-8 weeks minimum"
            },
            "digestive_aids": {
                "peppermint_oil": "0.2-0.4ml, 3 times daily",
                "digestive_enzymes": "With meals as needed",
                "fiber_supplements": "Start low, increase gradually"
            }
        }
    
    def _initialize_evidence_database(self) -> Dict[str, Any]:
        """Initialize evidence-based recommendations database."""
        return {
            "grade_a_evidence": [
                "Low FODMAP diet", "Peppermint oil", "Gut-directed hypnotherapy",
                "Cognitive behavioral therapy", "Certain probiotics"
            ],
            "grade_b_evidence": [
                "Regular exercise", "Stress management", "Sleep hygiene",
                "Fiber modification", "Dietary counseling"
            ],
            "grade_c_evidence": [
                "Hydration optimization", "Meal timing", "Portion control"
            ]
        }
    
    def _get_fallback_recommendations(self) -> Dict[str, List[Recommendation]]:
        """Return basic recommendations when errors occur."""
        return {
            'immediate_actions': [],
            'dietary_plan': [
                Recommendation(
                    id="basic_dietary_advice",
                    type=RecommendationType.DIETARY,
                    title="Basic Dietary Management",
                    description="Follow general IBS dietary guidelines.",
                    rationale="Basic dietary modifications can help manage IBS symptoms.",
                    priority=PriorityLevel.MEDIUM,
                    evidence_level="Grade B",
                    scientific_references=["General IBS guidelines"],
                    implementation_steps=["Eat regular meals", "Stay hydrated", "Limit trigger foods"],
                    expected_timeline="2-4 weeks",
                    monitoring_metrics=["Symptom severity"],
                    contraindications=[],
                    personalization_factors={}
                )
            ],
            'lifestyle_modifications': [],
            'medical_consultations': [],
            'behavioral_interventions': [],
            'supplement_suggestions': [],
            'monitoring_plan': []
        }