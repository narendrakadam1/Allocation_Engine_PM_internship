from typing import Dict, Any
from .base_agent import BaseAgent
from .extractor_agent import ExtractorAgent
from .analyzer_agent import AnalyzerAgent
from .matcher_agent import MatcherAgent
from .screener_agent import ScreenerAgent
from .recommender_agent import RecommenderAgent


class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            instructions="""Coordinate the recruitment workflow and delegate tasks to specialized agents.
            Ensure proper flow of information between extraction, analysis, matching, screening, and recommendation phases.
            Maintain context and aggregate results from each stage.""",
        )
        self._setup_agents()

    def _setup_agents(self):
        """Initialize all specialized agents"""
        self.extractor = ExtractorAgent()
        self.analyzer = AnalyzerAgent()
        self.matcher = MatcherAgent()
        self.screener = ScreenerAgent()
        self.recommender = RecommenderAgent()
    
    def process_resume(self, resume_path):
            """Existing resume processing (already works in your pipeline)."""
            return self.run(resume_path)

    def process_profile(self, student_profile, organizations):
        """Match a student profile (no resume) to org jobs."""
        skills = student_profile.get("skills", "").split(",")
        matches = []
        for org in organizations:
            for job in org.get("jobs", []):
                jd_skills = job["skills"].split(",")
                score = len(set(skills) & set(jd_skills)) / max(1, len(jd_skills))
                matches.append({
                    "student": student_profile["name"],
                    "organization": org["org_name"],
                    "job": job["title"],
                    "score": f"{score:.0%}"
                })
        best = max(matches, key=lambda x: float(x["score"].strip("%")), default=None)
        return best


    async def run(self, messages: list) -> Dict[str, Any]:
        """Process a single message through the agent"""
        prompt = messages[-1]["content"]
        response = self._query_ollama(prompt)
        return self._parse_json_safely(response)

    async def process_application(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow orchestrator for processing job applications"""
        print("🎯 Orchestrator: Starting application process")

        workflow_context = {
            "resume_data": resume_data,
            "status": "initiated",
            "current_stage": "extraction",
        }

        try:
            # Extract resume information
            extracted_data = await self.extractor.run(
                [{"role": "user", "content": str(resume_data)}]
            )
            workflow_context.update(
                {"extracted_data": extracted_data, "current_stage": "analysis"}
            )

            # Analyze candidate profile
            analysis_results = await self.analyzer.run(
                [{"role": "user", "content": str(extracted_data)}]
            )
            workflow_context.update(
                {"analysis_results": analysis_results, "current_stage": "matching"}
            )

            # Match with jobs
            job_matches = await self.matcher.run(
                [{"role": "user", "content": str(analysis_results)}]
            )
            workflow_context.update(
                {"job_matches": job_matches, "current_stage": "screening"}
            )

            # Screen candidate
            screening_results = await self.screener.run(
                [{"role": "user", "content": str(workflow_context)}]
            )
            workflow_context.update(
                {
                    "screening_results": screening_results,
                    "current_stage": "recommendation",
                }
            )

            # Generate recommendations
            final_recommendation = await self.recommender.run(
                [{"role": "user", "content": str(workflow_context)}]
            )
            workflow_context.update(
                {"final_recommendation": final_recommendation, "status": "completed"}
            )

            return workflow_context

        except Exception as e:
            workflow_context.update({"status": "failed", "error": str(e)})
            raise


# ---------------------------------------------------------------------------
# Synchronous wrapper for the async OrchestratorAgent
# Adds a stable, simple interface: Orchestrator.process_resume(path)
# and Orchestrator.process_profile(profile, orgs)
import asyncio
from typing import List, Dict, Any

class Orchestrator:
    """
    Lightweight synchronous wrapper around OrchestratorAgent.
    It attempts to call the async agent.run(...) via asyncio.run.
    If that fails it falls back to a simple skills-overlap heuristic for process_profile.
    """
    def __init__(self):
        try:
            # OrchestratorAgent is the async class already defined earlier in this module
            self.agent = OrchestratorAgent()
        except Exception:
            self.agent = None

    def process_resume(self, resume_path: str) -> Dict[str, Any]:
        """Process a resume file (path) through the async orchestrator. Returns a dict result."""
        messages = [{"role": "user", "content": str({"file_path": resume_path})}]
        if self.agent is not None:
            try:
                return asyncio.run(self.agent.run(messages))
            except Exception as e:
                return {"status": "failed", "error": f"OrchestratorAgent.run failed: {e}"}
        else:
            return {"status": "failed", "error": "OrchestratorAgent not available"}

    def process_profile(self, student_profile: Dict[str, Any], organizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Guarantee return: {"matches": [ ... ]}
        """
        results = []

        if self.agent is not None:
            try:
                messages = [{"role": "user", "content": str({"profile": student_profile, "organizations": organizations})}]
                res = asyncio.run(self.agent.run(messages))
                if isinstance(res, dict) and "matches" in res:
                    return res
                if isinstance(res, dict):
                    return {"matches": [res]}
            except Exception:
                pass

        # Heuristic fallback
        skills = [s.strip().lower() for s in student_profile.get("skills", "").split(",") if s.strip()]
        for org in organizations:
            for job in org.get("jobs", []):
                jd_skills = [s.strip().lower() for s in job.get("skills", "").split(",") if s.strip()]
                score = len(set(skills) & set(jd_skills)) / max(1, len(jd_skills))
                results.append({
                    "student": student_profile.get("name"),
                    "organization": org.get("org_name"),
                    "job": job.get("title"),
                    "score": f"{int(score*100)}%"
                })
        return {"matches": results}
