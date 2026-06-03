"""
LinkedIn Profile Schemas

Pydantic models for LinkedIn profile data validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List
import re


class ExperienceEntry(BaseModel):
    """Work experience entry."""
    company: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1)
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    
    @field_validator('company')
    @classmethod
    def validate_company(cls, v):
        """Validate company name."""
        if not v:
            raise ValueError("Company cannot be empty")
        
        # Reject if contains noise indicators
        v_lower = v.lower()
        noise_indicators = ['#', '@', 'thanks', 'comment', 'followers', 'connections', 'people also viewed']
        for indicator in noise_indicators:
            if indicator in v_lower:
                raise ValueError(f"Company contains noise indicator: {indicator}")
        
        # Reject if too long (likely scraped multiple entries)
        if len(v) > 100:
            raise ValueError("Company name too long (>100 chars)")
        
        return v.strip()
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        """Validate role name."""
        if not v:
            raise ValueError("Role cannot be empty")
        
        # Reject noise
        v_lower = v.lower()
        if '#' in v or '@' in v:
            raise ValueError("Role contains noise characters")
        
        return v.strip()


class EducationEntry(BaseModel):
    """Education entry."""
    institution: str = Field(..., min_length=1, max_length=150)
    degree: str = Field(default="")
    year: str = Field(default="")
    
    @field_validator('institution')
    @classmethod
    def validate_institution(cls, v):
        """Validate institution name."""
        if not v:
            raise ValueError("Institution cannot be empty")
        
        # Reject if contains noise indicators
        v_lower = v.lower()
        noise_indicators = [
            '#', '@', 'thanks', 'comment', 'followers', 'connections',
            'people also viewed', 'big thanks', 'grateful', 'excited to announce'
        ]
        for indicator in noise_indicators:
            if indicator in v_lower:
                raise ValueError(f"Institution contains noise indicator: {indicator}")
        
        # Reject if contains multiple unrelated entries
        if '|' in v or v.count('\n') > 2:
            raise ValueError("Institution contains multiple entries")
        
        return v.strip()


class LinkedInProfile(BaseModel):
    """Complete LinkedIn profile."""
    name: str = Field(..., min_length=1)
    headline: str = Field(default="")
    location: str = Field(default="")
    experience: List[ExperienceEntry] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    
    @field_validator('location')
    @classmethod
    def validate_location(cls, v):
        """Validate location format."""
        if not v:
            return v
        
        v = v.strip()
        
        # Location should match: "City, State, Country" or "City, Country"
        # Reject if it looks like a headline (too long or descriptive)
        if len(v) > 100:
            raise ValueError("Location too long (likely not a location)")
        
        # Check if it looks like a proper location
        # Should have comma(s) and proper capitalization
        if ',' not in v:
            # Single word locations are rare but valid (e.g., "London")
            # Allow if short
            if len(v) > 30:
                raise ValueError("Location format invalid (missing comma)")
        
        return v
    
    @field_validator('headline')
    @classmethod
    def validate_headline(cls, v):
        """Validate headline."""
        if not v:
            return v
        
        v = v.strip()
        
        # Headline should be a professional summary
        # Reject if it looks like a location
        if re.match(r'^[A-Z][a-z]+,\s*[A-Z]', v):
            raise ValueError("Headline looks like a location")
        
        # Reject noise
        if '#' in v or '@' in v:
            raise ValueError("Headline contains noise characters")
        
        return v
