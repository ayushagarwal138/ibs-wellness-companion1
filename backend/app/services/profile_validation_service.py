"""
Profile validation service for comprehensive data handling and validation.
"""

import logging
from typing import Dict, List, Any, Tuple
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, GenderEnum, IBSTypeEnum
from app.schemas.profile import ProfileValidationResponse, ProfileCompletionStatus

logger = logging.getLogger(__name__)


class ProfileValidationService:
    """Service for comprehensive profile validation and data handling."""

    def __init__(self):
        self.required_fields = {
            "basic_info": [
                "first_name",
                "last_name",
                "email",
                "date_of_birth",
                "gender",
            ],
            "medical_history": ["ibs_type", "diagnosis_date"],
            "dietary_preferences": [],  # No required fields for dietary preferences
            "lifestyle_factors": [],  # No required fields for lifestyle factors
            "goals_preferences": ["primary_goals"],
        }

        self.field_weights = {
            "basic_info": {
                "first_name": 5,
                "last_name": 5,
                "email": 5,
                "phone_number": 3,
                "date_of_birth": 8,
                "gender": 5,
                "height_cm": 4,
                "weight_kg": 4,
                "emergency_contact_name": 2,
                "emergency_contact_phone": 2,
            },
            "medical_history": {
                "ibs_type": 15,
                "diagnosis_date": 10,
                "severity_level": 8,
                "known_triggers": 6,
                "common_symptoms": 6,
                "symptom_patterns": 4,
                "current_medications": 5,
                "allergies": 4,
                "other_conditions": 3,
                "medical_notes": 2,
            },
            "dietary_preferences": {
                "dietary_restrictions": 4,
                "food_allergies": 5,
                "preferred_cuisines": 2,
                "meal_frequency": 3,
                "water_intake_goal": 2,
                "special_diets": 3,
                "trigger_foods": 6,
                "safe_foods": 4,
            },
            "lifestyle_factors": {
                "exercise_frequency": 4,
                "sleep_quality": 5,
                "stress_level": 5,
                "work_schedule": 2,
                "smoking_status": 3,
                "alcohol_consumption": 3,
            },
            "goals_preferences": {
                "primary_goals": 8,
                "preferred_treatments": 4,
                "communication_preferences": 2,
                "notification_preferences": 2,
                "privacy_settings": 2,
            },
        }

    async def validate_profile_update(
        self, update_data: Dict[str, Any], current_user: User, db: AsyncSession
    ) -> ProfileValidationResponse:
        """
        Validate profile update data comprehensively.

        Args:
            update_data: The profile update data
            current_user: Current user object
            db: Database session

        Returns:
            ProfileValidationResponse with validation results
        """
        errors = {}
        warnings = {}
        suggestions = []

        try:
            # Validate basic information
            if "basic_info" in update_data or any(
                field in update_data
                for field in [
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "date_of_birth",
                    "gender",
                    "height_cm",
                    "weight_kg",
                ]
            ):
                basic_errors, basic_warnings = await self._validate_basic_info(
                    update_data, current_user, db
                )
                if basic_errors:
                    errors["basic_info"] = basic_errors
                if basic_warnings:
                    warnings["basic_info"] = basic_warnings

            # Validate medical history
            if "medical_history" in update_data or any(
                field in update_data
                for field in ["ibs_type", "diagnosis_date", "medical_notes"]
            ):
                medical_errors, medical_warnings = await self._validate_medical_history(
                    update_data, current_user
                )
                if medical_errors:
                    errors["medical_history"] = medical_errors
                if medical_warnings:
                    warnings["medical_history"] = medical_warnings

            # Validate dietary preferences
            if "dietary_preferences" in update_data:
                dietary_errors, dietary_warnings = self._validate_dietary_preferences(
                    update_data["dietary_preferences"]
                )
                if dietary_errors:
                    errors["dietary_preferences"] = dietary_errors
                if dietary_warnings:
                    warnings["dietary_preferences"] = dietary_warnings

            # Validate lifestyle factors
            if "lifestyle_factors" in update_data:
                lifestyle_errors, lifestyle_warnings = self._validate_lifestyle_factors(
                    update_data["lifestyle_factors"]
                )
                if lifestyle_errors:
                    errors["lifestyle_factors"] = lifestyle_errors
                if lifestyle_warnings:
                    warnings["lifestyle_factors"] = lifestyle_warnings

            # Generate suggestions
            suggestions = self._generate_suggestions(update_data, current_user)

            return ProfileValidationResponse(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
            )

        except Exception as e:
            logger.error(f"Error validating profile update: {e}")
            return ProfileValidationResponse(
                valid=False,
                errors={"general": [f"Validation error: {str(e)}"]},
                warnings={},
                suggestions=[],
            )

    async def _validate_basic_info(
        self, update_data: Dict[str, Any], current_user: User, db: AsyncSession
    ) -> Tuple[List[str], List[str]]:
        """Validate basic information fields."""
        errors = []
        warnings = []

        # Email uniqueness check
        if "email" in update_data and update_data["email"] != current_user.email:
            from app.services.user_service import UserService

            user_service = UserService()
            existing_user = await user_service.get_user_by_email(
                db, update_data["email"]
            )
            if existing_user and existing_user.id != current_user.id:
                errors.append("Email address is already in use")

        # Age validation
        if "date_of_birth" in update_data:
            dob = update_data["date_of_birth"]
            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    errors.append("Invalid date of birth format")
                    return errors, warnings

            if dob:
                today = date.today()
                age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )
                if age < 13:
                    errors.append("User must be at least 13 years old")
                elif age > 100:
                    warnings.append("Please verify the date of birth")

        # BMI validation
        height = update_data.get("height_cm") or current_user.height_cm
        weight = update_data.get("weight_kg") or current_user.weight_kg

        if height and weight:
            bmi = weight / ((height / 100) ** 2)
            if bmi < 15 or bmi > 50:
                warnings.append(
                    "BMI appears to be outside normal range. Please verify height and weight."
                )

        return errors, warnings

    async def _validate_medical_history(
        self, update_data: Dict[str, Any], current_user: User
    ) -> Tuple[List[str], List[str]]:
        """Validate medical history fields."""
        errors = []
        warnings = []

        # IBS type validation
        if "ibs_type" in update_data:
            ibs_type = update_data["ibs_type"]
            if isinstance(ibs_type, str):
                # Convert frontend format to backend enum
                ibs_mapping = {
                    "ibs-d": IBSTypeEnum.IBS_D,
                    "ibs-c": IBSTypeEnum.IBS_C,
                    "ibs-m": IBSTypeEnum.IBS_M,
                    "ibs-u": IBSTypeEnum.IBS_U,
                }
                if ibs_type.lower() in ibs_mapping:
                    update_data["ibs_type"] = ibs_mapping[ibs_type.lower()]
                elif ibs_type.upper() not in [e.value for e in IBSTypeEnum]:
                    errors.append("Invalid IBS type specified")

        # Diagnosis date validation
        if "diagnosis_date" in update_data:
            diag_date = update_data["diagnosis_date"]
            if isinstance(diag_date, str):
                try:
                    diag_date = datetime.strptime(diag_date, "%Y-%m-%d").date()
                except ValueError:
                    errors.append("Invalid diagnosis date format")
                    return errors, warnings

            if diag_date and diag_date > date.today():
                errors.append("Diagnosis date cannot be in the future")

            # Check if diagnosis date is reasonable with age
            if current_user.date_of_birth and diag_date:
                age_at_diagnosis = diag_date.year - current_user.date_of_birth.year
                if age_at_diagnosis < 5:
                    warnings.append("IBS diagnosis at very young age is uncommon")

        return errors, warnings

    def _validate_dietary_preferences(
        self, dietary_data: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Validate dietary preferences."""
        errors = []
        warnings = []

        # Validate meal frequency
        if "meal_frequency" in dietary_data:
            freq = dietary_data["meal_frequency"]
            if freq and (freq < 1 or freq > 10):
                errors.append("Meal frequency must be between 1 and 10 meals per day")

        # Validate water intake
        if "water_intake_goal" in dietary_data:
            water = dietary_data["water_intake_goal"]
            if water and (water < 0.5 or water > 8):
                warnings.append(
                    "Water intake goal seems unusual. Recommended range is 1.5-3 liters per day."
                )

        return errors, warnings

    def _validate_lifestyle_factors(
        self, lifestyle_data: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Validate lifestyle factors."""
        errors = []
        warnings = []

        # Validate rating scales
        for field in ["sleep_quality", "stress_level"]:
            if field in lifestyle_data:
                value = lifestyle_data[field]
                if value and (value < 1 or value > 10):
                    errors.append(
                        f'{field.replace("_", " ").title()} must be between 1 and 10'
                    )

        return errors, warnings

    def _generate_suggestions(
        self, update_data: Dict[str, Any], current_user: User
    ) -> List[str]:
        """Generate helpful suggestions for profile completion."""
        suggestions = []

        # Basic info suggestions
        if not current_user.height_cm or not current_user.weight_kg:
            suggestions.append(
                "Adding height and weight helps provide more accurate health insights"
            )

        if not current_user.emergency_contact_name:
            suggestions.append(
                "Consider adding emergency contact information for safety"
            )

        # Medical history suggestions
        if not current_user.ibs_type:
            suggestions.append(
                "Specifying your IBS type helps personalize recommendations"
            )

        if not current_user.diagnosis_date:
            suggestions.append("Adding diagnosis date helps track your health journey")

        # General suggestions
        if not current_user.medical_notes:
            suggestions.append(
                "Medical notes can help healthcare providers understand your condition better"
            )

        return suggestions

    def calculate_profile_completion(self, user: User) -> ProfileCompletionStatus:
        """Calculate profile completion status."""
        section_scores = {}
        total_weight = 0
        total_score = 0
        missing_required = []

        # Calculate completion for each section
        for section, fields in self.field_weights.items():
            section_weight = sum(fields.values())
            section_score = 0

            for field, weight in fields.items():
                value = getattr(user, field, None)
                if value is not None and value != "" and value != []:
                    section_score += weight
                elif field in self.required_fields.get(section, []):
                    missing_required.append(f"{section}.{field}")

            section_percentage = (
                (section_score / section_weight) * 100 if section_weight > 0 else 0
            )
            section_scores[section] = round(section_percentage, 1)

            total_weight += section_weight
            total_score += section_score

        overall_completion = (
            (total_score / total_weight) * 100 if total_weight > 0 else 0
        )

        # Generate recommendations
        recommendations = []
        if overall_completion < 50:
            recommendations.append(
                "Complete basic information to unlock personalized features"
            )
        if "medical_history.ibs_type" in missing_required:
            recommendations.append("Add IBS type for better symptom tracking")
        if overall_completion < 80:
            recommendations.append(
                "Complete more sections for comprehensive health insights"
            )

        return ProfileCompletionStatus(
            overall_completion=round(overall_completion, 1),
            section_completion=section_scores,
            missing_required_fields=missing_required,
            recommended_next_steps=recommendations,
        )

    def transform_frontend_to_backend(
        self, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform frontend data format to backend format."""
        transformed = {}

        # Handle gender transformation
        if "gender" in update_data:
            gender_mapping = {
                "male": GenderEnum.MALE,
                "female": GenderEnum.FEMALE,
                "other": GenderEnum.OTHER,
                "prefer_not_to_say": GenderEnum.PREFER_NOT_TO_SAY,
            }
            gender_value = update_data["gender"]
            if isinstance(gender_value, str) and gender_value.lower() in gender_mapping:
                transformed["gender"] = gender_mapping[gender_value.lower()]
            else:
                transformed["gender"] = gender_value

        # Handle IBS type transformation
        if "ibs_type" in update_data:
            ibs_mapping = {
                "ibs-d": IBSTypeEnum.IBS_D,
                "ibs-c": IBSTypeEnum.IBS_C,
                "ibs-m": IBSTypeEnum.IBS_M,
                "ibs-u": IBSTypeEnum.IBS_U,
            }
            ibs_value = update_data["ibs_type"]
            if isinstance(ibs_value, str) and ibs_value.lower() in ibs_mapping:
                transformed["ibs_type"] = ibs_mapping[ibs_value.lower()]
            else:
                transformed["ibs_type"] = ibs_value

        # Copy other fields directly
        for key, value in update_data.items():
            if key not in ["gender", "ibs_type"]:
                transformed[key] = value

        return transformed

    def transform_backend_to_frontend(
        self, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform backend data format to frontend format."""
        transformed = {}

        # Handle gender transformation
        if "gender" in user_data and user_data["gender"]:
            gender_mapping = {
                GenderEnum.MALE: "male",
                GenderEnum.FEMALE: "female",
                GenderEnum.OTHER: "other",
                GenderEnum.PREFER_NOT_TO_SAY: "prefer_not_to_say",
            }
            transformed["gender"] = gender_mapping.get(
                user_data["gender"], user_data["gender"]
            )

        # Handle IBS type transformation
        if "ibs_type" in user_data and user_data["ibs_type"]:
            ibs_mapping = {
                IBSTypeEnum.IBS_D: "ibs-d",
                IBSTypeEnum.IBS_C: "ibs-c",
                IBSTypeEnum.IBS_M: "ibs-m",
                IBSTypeEnum.IBS_U: "ibs-u",
            }
            transformed["ibs_type"] = ibs_mapping.get(
                user_data["ibs_type"], user_data["ibs_type"]
            )

        # Copy other fields directly
        for key, value in user_data.items():
            if key not in ["gender", "ibs_type"]:
                transformed[key] = value

        return transformed
