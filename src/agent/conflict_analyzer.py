"""
Conflict Analyzer - Uses Gemini AI to detect interaction effects

Asks the LLM: "Given these two experiments, will they interfere?"
Returns analysis and recommendations.
"""

import os
import json
from typing import List, Tuple, Optional
import google.generativeai as genai

from src.models.experiment import Experiment
from src.knowledge.product_config import get_all_surfaces, get_all_metrics
from src.knowledge import deep_product_kb
from src.knowledge import interaction_patterns


class ConflictAnalyzer:
    """
    Uses Google Gemini to analyze whether experiments will interact.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError(
                "GEMINI_API_KEY not set. Set it as environment variable or pass as argument."
            )
        genai.configure(api_key=key)
        # Try latest Gemini models first, fall back to others
        try:
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        except:
            try:
                self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
            except:
                try:
                    self.model = genai.GenerativeModel("gemini-2.0-flash")
                except:
                    self.model = genai.GenerativeModel("gemini-pro")
    
    def analyze_conflicts(
        self,
        new_experiment: Experiment,
        existing_experiments: List[Experiment]
    ) -> dict:
        """
        Analyze if a new experiment conflicts with existing ones.
        
        Args:
            new_experiment: The experiment user wants to schedule
            existing_experiments: Experiments already scheduled
        
        Returns:
            {
                "has_conflicts": bool,
                "analysis": str,  # Human-readable explanation
                "recommendation": str,
                "confidence": float,  # 0.0-1.0
                "problematic_experiments": [exp.id],
            }
        """
        
        if not existing_experiments:
            return {
                "has_conflicts": False,
                "analysis": "No existing experiments in this period.",
                "recommendation": "Safe to schedule.",
                "confidence": 1.0,
                "problematic_experiments": [],
            }
        
        try:
            # Build the prompt for Gemini
            prompt = self._build_analysis_prompt(new_experiment, existing_experiments)
            
            # Call Gemini
            print("  [Calling Gemini for conflict analysis...]")
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            print(f"  [Gemini response received]")
            
            # Parse the response
            result = self._parse_gemini_response(analysis_text, existing_experiments)
            
            return result
        except Exception as e:
            print(f"  [Warning: Gemini analysis failed: {str(e)}]")
            # Fallback: simple conflict detection
            return {
                "has_conflicts": False,
                "analysis": f"Could not perform AI analysis ({str(e)}), but no date overlap conflicts detected.",
                "recommendation": "Proceed with caution - consider manual review.",
                "confidence": 0.3,
                "problematic_experiments": [],
            }
    
    def _build_analysis_prompt(
        self,
        new_experiment: Experiment,
        existing_experiments: List[Experiment]
    ) -> str:
        """Build the prompt to send to Gemini"""
        
        existing_str = "\n".join([
            f"- {exp.name} ({exp.start_date} to {exp.end_date})\n"
            f"  Surfaces: {', '.join(exp.surfaces)}\n"
            f"  Metrics: {', '.join(exp.metrics)}\n"
            f"  Description: {exp.description}"
            for exp in existing_experiments
        ])
        
        # Format the deep product knowledge
        platform_info = f"""
PLATFORM OVERVIEW:
Name: {deep_product_kb.PLATFORM['name']}
Description: {deep_product_kb.PLATFORM['description']}

FUNNEL FLOW:
1. DISCOVERY → Entry point where users explore
2. EXPLORATION → Users browse products
3. CONSIDERATION → Users evaluate products
4. PURCHASE → Transaction completion
5. POST-PURCHASE → Retention and loyalty

SURFACE DEFINITIONS:
"""
        for surface_name, surface_data in deep_product_kb.SURFACES.items():
            platform_info += f"\n- {surface_name.upper()}: {surface_data['description']}\n"
            platform_info += f"  Role: {surface_data['role']}\n"
            platform_info += f"  Funnel Stage: {surface_data['funnel_stage']}\n"
            platform_info += f"  Primary Metrics: {', '.join(surface_data['primary_metrics_affected'])}\n"
        
        # Format metric relationships
        metric_info = "METRIC RELATIONSHIPS:\n"
        for rel_name, rel_data in deep_product_kb.METRIC_RELATIONSHIPS.items():
            metric_info += f"- {rel_name}: {rel_data['relationship']} ({rel_data['note']})\n"
        
        prompt = f"""You are an experimentation expert analyzing product experiments for conflicts.

{platform_info}

{metric_info}

YOUR TASK:
1. Infer what CAUSAL MECHANISM each experiment targets (e.g., friction reduction, clarity improvement, urgency, trust)
2. Determine if mechanisms INTERFERE with each other on overlapping surfaces/metrics
3. Consider: Do different mechanisms compete for user attention? Do they measure the same outcome?

IMPORTANT: Overlap in dates/surfaces alone does NOT mean conflict!
Only flag as conflict if experiments will actually interfere with MEASUREMENT or RESULTS.

NEW EXPERIMENT:
Name: {new_experiment.name}
Start: {new_experiment.start_date}, End: {new_experiment.end_date}
Surfaces: {', '.join(new_experiment.surfaces)}
Metrics: {', '.join(new_experiment.metrics)}
Hypothesis: {new_experiment.hypothesis}
Description: {new_experiment.description}

EXISTING EXPERIMENTS (scheduled for overlapping period):
{existing_str}

ANALYSIS REQUIRED:
1. What MECHANISM does the new experiment target? (e.g., friction reduction, clarity, urgency, trust, discovery, upsell)
2. For each existing experiment: does its mechanism interfere with the new experiment?
3. Are they measuring the same outcome?
4. Final verdict: conflict or safe?

RESPOND IN THIS EXACT FORMAT:
[MECHANISM] <inferred mechanism for new experiment>
[CONFLICT] YES or NO
[INTERFERES_WITH] experiment_name_1, experiment_name_2 (or NONE)
[REASON] One sentence explaining why (or "No interference identified")
[RECOMMENDATION] What should the user do?
[CONFIDENCE] 0.0 to 1.0
[DETAILS] 2-3 sentences of detailed analysis"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str, existing_experiments: List[Experiment]) -> dict:
        """Parse Gemini's response into structured data"""
        
        lines = response_text.strip().split('\n')
        result = {
            "has_conflicts": False,
            "analysis": "",
            "recommendation": "",
            "confidence": 0.5,
            "mechanism": "",
            "problematic_experiments": [],
            "raw_response": response_text,
        }
        
        for line in lines:
            if line.startswith("[MECHANISM]"):
                result["mechanism"] = line.split("]", 1)[1].strip()
            elif line.startswith("[CONFLICT]"):
                result["has_conflicts"] = "YES" in line
            elif line.startswith("[INTERFERES_WITH]"):
                interferes_with = line.split("]", 1)[1].strip()
                if interferes_with != "NONE":
                    # Try to match experiment names
                    for exp in existing_experiments:
                        if exp.name.lower() in interferes_with.lower():
                            result["problematic_experiments"].append(exp.id)
            elif line.startswith("[REASON]"):
                result["analysis"] = line.split("]", 1)[1].strip()
            elif line.startswith("[RECOMMENDATION]"):
                result["recommendation"] = line.split("]", 1)[1].strip()
            elif line.startswith("[CONFIDENCE]"):
                try:
                    conf_str = line.split("]", 1)[1].strip()
                    result["confidence"] = float(conf_str)
                except (ValueError, IndexError):
                    pass
            elif line.startswith("[DETAILS]"):
                details = line.split("]", 1)[1].strip()
                result["analysis"] = f"{result['analysis']}\n{details}".strip()
        
        return result
