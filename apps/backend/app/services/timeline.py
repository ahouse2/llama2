"""Timeline analytics built atop the metadata fragments."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from ..config import settings
from ..database import get_session


class TimelineService:
    def summarize(self) -> List[Dict[str, List[str]]]:
        with get_session() as session:
            fragments = session.list_metadata_fragments(fragment_type="dates")
            documents = {doc.id: doc for doc in session.list_documents()}
        grouped: Dict[str, List[str]] = defaultdict(list)
        for fragment in fragments:
            document = documents.get(fragment.document_id)
            if not document:
                continue
            grouped[fragment.fragment_value].append(document.external_id)
        timeline = [
            {"date": date, "documents": sorted(set(doc_ids))}
            for date, doc_ids in grouped.items()
        ]
        timeline.sort(key=lambda item: item["date"])
        settings.timeline_export_path.write_text("date,documents\n", encoding="utf-8")
        with settings.timeline_export_path.open("a", encoding="utf-8") as handle:
            for entry in timeline:
                handle.write(f"{entry['date']}," + ";".join(entry["documents"]) + "\n")
        return timeline


timeline_service = TimelineService()
