from typing import Dict, Any, List
from .base_agent import BaseAgent
try:
    from db.database import JobDatabase
except Exception:
    JobDatabase = None
import ast, json
class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Matcher",
            instructions="Match candidate profiles to job descriptions using skills overlap and heuristics.",
        )
    async def run(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Always return dict:
        {
          "matches": [
            {"student": ..., "organization": ..., "job": ..., "score": "85%"}
          ]
        }
        """
        if not messages:
            return {"matches": []}

        raw = messages[-1].get("content", "")
        payload = None

        # Parse string → dict
        try:
            payload = json.loads(raw)
        except Exception:
            try:
                payload = ast.literal_eval(raw)
            except Exception:
                payload = {"text": raw}

        matches = []

        # Case 1: Student profile + organizations
        if isinstance(payload, dict) and "profile" in payload and "organizations" in payload:
            profile = payload["profile"]
            organizations = payload["organizations"]

            skills = [s.strip().lower() for s in profile.get("skills", "").split(",") if s.strip()]
            for org in organizations:
                for job in org.get("jobs", []):
                    jd_skills = [s.strip().lower() for s in job.get("skills", "").split(",") if s.strip()]
                    if not jd_skills:
                        continue
                    score = len(set(skills) & set(jd_skills)) / max(1, len(jd_skills))
                    matches.append({
                        "student": profile.get("name", "Unknown"),
                        "organization": org.get("org_name", "Unknown"),
                        "job": job.get("title", "Unknown"),
                        "score": f"{int(score*100)}%"
                    })
            return {"matches": matches}

        # Case 2: Resume pipeline (extracted_info)
        if isinstance(payload, dict):
            extracted = payload.get("extracted_info", {})
            skills = extracted.get("skills", [])
            if isinstance(skills, str):
                skills = [s.strip().lower() for s in skills.split(",") if s.strip()]

            if JobDatabase and skills:
                try:
                    db = JobDatabase()
                    for skill in skills:
                        rows = db.search_jobs(skill, experience_level="")
                        for r in rows:
                            matches.append({
                                "student": extracted.get("name", "Unknown"),
                                "organization": r.get("company", "Unknown"),
                                "job": r.get("title", "Unknown"),
                                "score": "50%"
                            })
                except Exception:
                    pass

        return {"matches": matches}
