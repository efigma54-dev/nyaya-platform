
import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import AsyncSessionLocal
from app.models.legal import Act, Section, Judgment, Rule, Notification
from sqlalchemy import select, func
from sqlalchemy.exc import ProgrammingError


async def validate_corpus():
    """Validate the entire legal corpus and generate validation.json."""
    async with AsyncSessionLocal() as db:
        # Count acts
        result = await db.execute(select(func.count(Act.id)))
        act_count = result.scalar()
        
        # Count sections
        result = await db.execute(select(func.count(Section.id)))
        section_count = result.scalar()
        
        # Count judgments
        judgment_count = 0
        try:
            result = await db.execute(select(func.count(Judgment.id)))
            judgment_count = result.scalar()
        except ProgrammingError:
            await db.rollback()
        
        # Count rules
        rule_count = 0
        try:
            result = await db.execute(select(func.count(Rule.id)))
            rule_count = result.scalar()
        except ProgrammingError:
            await db.rollback()
        
        # Count notifications
        notification_count = 0
        try:
            result = await db.execute(select(func.count(Notification.id)))
            notification_count = result.scalar()
        except ProgrammingError:
            await db.rollback()
        
        # Find sections without qdrant_id
        result = await db.execute(select(Section).where(Section.qdrant_id.is_(None)))
        sections_without_vectors = result.scalars().all()
        
        # Find acts without sections
        result = await db.execute(select(Act))
        acts = result.scalars().all()
        acts_without_sections = []
        for act in acts:
            # Load sections
            await db.refresh(act, ["sections"])
            if not act.sections:
                acts_without_sections.append(act.id)
        
        # Find duplicates (sections with same act_id and section_number)
        duplicates = []
        result = await db.execute(
            select(Section.act_id, Section.section_number, func.count(Section.id).label("count"))
            .group_by(Section.act_id, Section.section_number)
            .having(func.count(Section.id) > 1)
        )
        for row in result:
            duplicates.append({
                "act_id": row.act_id,
                "section_number": row.section_number,
                "count": row.count
            })
        
        validation_report = {
            "acts": act_count,
            "sections": section_count,
            "judgments": judgment_count,
            "rules": rule_count,
            "notifications": notification_count,
            "vectors": {
                "total_sections": section_count,
                "sections_without_vectors": len(sections_without_vectors),
                "sections_with_vectors": section_count - len(sections_without_vectors)
            },
            "duplicates": duplicates,
            "embedding_failures": [s.id for s in sections_without_vectors],
            "missing_metadata": {
                "acts_without_sections": acts_without_sections
            },
            "orphan_vectors": [],  # Would need to check Qdrant
            "orphan_database_rows": []
        }
        
        # Save report
        output_path = Path(__file__).resolve().parents[2] / "validation.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Generated validation report at {output_path}")
        print("\nValidation Summary:")
        print(f"  Acts: {act_count}")
        print(f"  Sections: {section_count}")
        print(f"  Judgments: {judgment_count}")
        print(f"  Rules: {rule_count}")
        print(f"  Notifications: {notification_count}")
        print(f"  Sections without vectors: {len(sections_without_vectors)}")
        print(f"  Duplicate sections: {len(duplicates)}")
        
        return validation_report


if __name__ == "__main__":
    asyncio.run(validate_corpus())
