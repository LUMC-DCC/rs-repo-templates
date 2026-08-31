"""Extract a readable question reference from a DSW Knowledge Model export.

The DSW ``.km`` export is an event log. This script reconstructs the latest
entity state and writes a compact JSON reference that is easier to inspect and
map to the template context contract.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

MISC = Path(__file__).resolve().parent
DEFAULT_INPUT_PATH = MISC / "lumc_rsmp_1.0.2.km"
DEFAULT_OUTPUT_PATH = MISC / "lumc_rsmp_1.0.2.questions.json"
ZERO_UUID = "00000000-0000-0000-0000-000000000000"


def apply_event_fields(entity: dict[str, Any], content: dict[str, Any]) -> None:
    """Apply DSW event content to an entity snapshot.

    Parameters
    ----------
    entity : dict
        Mutable entity snapshot.
    content : dict
        Event content from the DSW Knowledge Model export.
    """
    for key, value in content.items():
        if key == "eventType":
            continue

        if isinstance(value, dict) and "changed" in value:
            if value.get("changed"):
                entity[key] = value.get("value")
            continue

        entity[key] = value


def entity_kind(event_type: str) -> str:
    """Return the DSW entity kind named by an event type.

    Parameters
    ----------
    event_type : str
        DSW event type, such as ``AddQuestionEvent``.

    Returns
    -------
    str
        Entity kind, such as ``Question``.
    """
    return event_type.removeprefix("Add").removeprefix("Edit").removesuffix("Event")


def reconstruct_entities(km: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reconstruct current entities from a DSW Knowledge Model event log.

    Parameters
    ----------
    km : dict
        Parsed DSW Knowledge Model export.

    Returns
    -------
    dict[str, dict]
        Entity UUIDs mapped to reconstructed entity snapshots.
    """
    entities: dict[str, dict[str, Any]] = {}

    for package in km["packages"]:
        for event in package["events"]:
            content = event["content"]
            event_type = content.get("eventType", "")
            uuid = event["entityUuid"]

            if event_type.startswith("Add"):
                entity = entities.setdefault(uuid, {})
                entity["uuid"] = uuid
                entity["kind"] = entity_kind(event_type)
                entity["parent_uuid"] = event.get("parentUuid")
                apply_event_fields(entity, content)
            elif event_type.startswith("Edit"):
                entity = entities.setdefault(uuid, {"uuid": uuid})
                entity.setdefault("kind", entity_kind(event_type))
                apply_event_fields(entity, content)
            elif event_type == "MoveQuestionEvent":
                entities.setdefault(uuid, {"uuid": uuid})["parent_uuid"] = event.get(
                    "parentUuid"
                )

    return entities


def ordered_entities(
    uuids: list[str],
    entities: dict[str, dict[str, Any]],
    kind: str | None = None,
) -> list[dict[str, Any]]:
    """Resolve UUIDs to entity snapshots while preserving order.

    Parameters
    ----------
    uuids : list[str]
        Entity UUIDs in DSW order.
    entities : dict[str, dict]
        Reconstructed entities.
    kind : str, optional
        Required entity kind.

    Returns
    -------
    list[dict]
        Resolved entities.
    """
    resolved = []
    for uuid in uuids:
        entity = entities.get(uuid)
        if not entity:
            continue
        if kind and entity.get("kind") != kind:
            continue
        resolved.append(entity)
    return resolved


def build_child_index(
    entities: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Build entities grouped by parent UUID.

    Parameters
    ----------
    entities : dict[str, dict]
        Reconstructed entities.

    Returns
    -------
    dict[str, list[dict]]
        Child entities grouped by parent UUID.
    """
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity in entities.values():
        parent_uuid = entity.get("parent_uuid")
        if parent_uuid:
            children[parent_uuid].append(entity)
    return children


def compact_entity(entity: dict[str, Any]) -> dict[str, Any]:
    """Return stable public fields for an entity reference.

    Parameters
    ----------
    entity : dict
        Reconstructed DSW entity.

    Returns
    -------
    dict
        Compact entity representation.
    """
    keys = [
        "uuid",
        "kind",
        "title",
        "text",
        "questionType",
        "valueType",
        "label",
        "advice",
        "requiredPhaseUuid",
        "tagUuids",
    ]
    return {key: entity[key] for key in keys if entity.get(key) not in (None, [], "")}


def summarize_question(
    question: dict[str, Any],
    entities: dict[str, dict[str, Any]],
    children: dict[str, list[dict[str, Any]]],
    path: list[str] | None = None,
) -> dict[str, Any]:
    """Build a readable summary for one question.

    Parameters
    ----------
    question : dict
        Reconstructed question entity.
    entities : dict[str, dict]
        Reconstructed entities.
    children : dict[str, list[dict]]
        Entity children grouped by parent UUID.
    path : list[str], optional
        Human-readable parent path.

    Returns
    -------
    dict
        Question summary.
    """
    title = question.get("title") or "<untitled>"
    question_path = [*(path or []), title]

    answer_uuids = question.get("answerUuids") or [
        child["uuid"]
        for child in children.get(question["uuid"], [])
        if child.get("kind") == "Answer"
    ]
    choice_uuids = question.get("choiceUuids") or [
        child["uuid"]
        for child in children.get(question["uuid"], [])
        if child.get("kind") == "Choice"
    ]
    item_template_uuids = question.get("itemTemplateQuestionUuids") or [
        child["uuid"]
        for child in children.get(question["uuid"], [])
        if child.get("kind") == "Question"
    ]

    answers = []
    for answer in ordered_entities(answer_uuids, entities, "Answer"):
        follow_up_uuids = answer.get("followUpUuids") or [
            child["uuid"]
            for child in children.get(answer["uuid"], [])
            if child.get("kind") == "Question"
        ]
        answer_summary = compact_entity(answer)
        if follow_up_uuids:
            answer_summary["follow_up_questions"] = [
                summarize_question(follow_up, entities, children, question_path)
                for follow_up in ordered_entities(follow_up_uuids, entities, "Question")
            ]
        answers.append(answer_summary)

    summary = compact_entity(question)
    summary["path"] = question_path

    choices = [
        compact_entity(choice)
        for choice in ordered_entities(choice_uuids, entities, "Choice")
    ]
    if choices:
        summary["choices"] = choices

    if answers:
        summary["answers"] = answers

    item_template_questions = [
        summarize_question(item_question, entities, children, question_path)
        for item_question in ordered_entities(item_template_uuids, entities, "Question")
    ]
    if item_template_questions:
        summary["item_template_questions"] = item_template_questions

    return summary


def summarize_chapters(entities: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Build ordered chapter summaries with nested question summaries.

    Parameters
    ----------
    entities : dict[str, dict]
        Reconstructed DSW entities.

    Returns
    -------
    list[dict]
        Chapter summaries.
    """
    children = build_child_index(entities)
    chapters = [
        entity
        for entity in entities.values()
        if entity.get("kind") == "Chapter"
        and entity.get("parent_uuid") in {None, ZERO_UUID}
    ]

    summaries = []
    for chapter in chapters:
        question_uuids = chapter.get("questionUuids") or [
            child["uuid"]
            for child in children.get(chapter["uuid"], [])
            if child.get("kind") == "Question"
        ]
        chapter_summary = compact_entity(chapter)
        chapter_summary["questions"] = [
            summarize_question(
                question, entities, children, [chapter.get("title") or "<untitled>"]
            )
            for question in ordered_entities(question_uuids, entities, "Question")
        ]
        summaries.append(chapter_summary)

    return summaries


def flatten_questions(chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten nested chapter summaries into a question index.

    Parameters
    ----------
    chapters : list[dict]
        Nested chapter summaries.

    Returns
    -------
    list[dict]
        Compact question records with stable paths and option labels.
    """
    questions = []

    def visit(question: dict[str, Any]) -> None:
        """Append one question and visit nested question records."""
        record = {
            "uuid": question["uuid"],
            "title": question.get("title"),
            "path": question.get("path", []),
            "question_type": question.get("questionType"),
        }
        if question.get("text"):
            record["text"] = question["text"]
        if question.get("valueType"):
            record["value_type"] = question["valueType"]
        if question.get("choices"):
            record["choices"] = [
                choice.get("label")
                for choice in question["choices"]
                if choice.get("label")
            ]
        if question.get("answers"):
            record["answers"] = [
                answer.get("label")
                for answer in question["answers"]
                if answer.get("label")
            ]
        if question.get("item_template_questions"):
            record["item_template_questions"] = [
                {
                    "uuid": item_question["uuid"],
                    "title": item_question.get("title"),
                    "question_type": item_question.get("questionType"),
                    "value_type": item_question.get("valueType"),
                }
                for item_question in question["item_template_questions"]
            ]

        questions.append(record)

        for answer in question.get("answers", []):
            for follow_up in answer.get("follow_up_questions", []):
                visit(follow_up)
        for item_question in question.get("item_template_questions", []):
            visit(item_question)

    for chapter in chapters:
        for question in chapter.get("questions", []):
            visit(question)

    return questions


def build_reference(km: dict[str, Any], source_path: Path) -> dict[str, Any]:
    """Build a question reference from a parsed KM export.

    Parameters
    ----------
    km : dict
        Parsed DSW Knowledge Model export.
    source_path : pathlib.Path
        Source KM path.

    Returns
    -------
    dict
        JSON-serializable question reference.
    """
    entities = reconstruct_entities(km)
    chapters = summarize_chapters(entities)
    questions = flatten_questions(chapters)

    return {
        "source": source_path.name,
        "id": km.get("id"),
        "km_id": km.get("kmId"),
        "name": km.get("name"),
        "version": km.get("version"),
        "metamodel_version": km.get("metamodelVersion"),
        "package_count": len(km.get("packages", [])),
        "event_count": sum(
            len(package.get("events", [])) for package in km.get("packages", [])
        ),
        "question_count": len(questions),
        "chapters": chapters,
        "questions": questions,
    }


def load_km(path: Path) -> dict[str, Any]:
    """Load a DSW Knowledge Model export.

    Parameters
    ----------
    path : pathlib.Path
        Path to the ``.km`` JSON export.

    Returns
    -------
    dict
        Parsed Knowledge Model.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def write_reference(reference: dict[str, Any], path: Path) -> None:
    """Write a reconstructed question reference.

    Parameters
    ----------
    reference : dict
        Reconstructed question reference.
    path : pathlib.Path
        Destination JSON path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(reference, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    reference = build_reference(load_km(args.input), args.input)
    write_reference(reference, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
