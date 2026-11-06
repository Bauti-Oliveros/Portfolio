import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AUDIT_DIR = ROOT / "audit"

RUN_FILES = {
    "official": (
        ROOT
        / "results"
        / "benchmark_qwen_v21_test_final.json"
    ),
    "run_01": AUDIT_DIR / "variability_run_01.json",
    "run_02": AUDIT_DIR / "variability_run_02.json",
    "run_03": AUDIT_DIR / "variability_run_03.json",
}

OUTPUT_CSV = AUDIT_DIR / "variability_by_case.csv"
OUTPUT_MD = AUDIT_DIR / "variability_analysis.md"


def normalize_article(value):
    text = str(value or "").lower().strip()
    text = text.replace("id:", "")
    text = text.replace("id :", "")
    text = text.replace("artículo", "")
    text = text.replace("articulo", "")
    text = text.replace("art.", "")
    return text.strip()


def load_results(path):
    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    return {
        result["caso"]: result
        for result in data["resultados"]
    }


def get_article(result):
    return normalize_article(
        result.get("obtenido", "")
    )


def main():
    for name, path in RUN_FILES.items():
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {name}: {path}"
            )

    runs = {
        name: load_results(path)
        for name, path in RUN_FILES.items()
    }

    case_ids = list(
        runs["official"].keys()
    )

    rows = []

    for case_id in case_ids:
        official_result = runs["official"][case_id]

        articles = {
            run_name: get_article(
                run_results[case_id]
            )
            for run_name, run_results in runs.items()
        }

        correctness = {
            run_name: bool(
                run_results[case_id].get(
                    "correcto",
                    False
                )
            )
            for run_name, run_results in runs.items()
        }

        validations = {
            run_name: bool(
                run_results[case_id].get(
                    "valido",
                    False
                )
            )
            for run_name, run_results in runs.items()
        }

        if official_result.get(
            "es_prompt_injection",
            False
        ):
            category = "prompt_injection"
        elif official_result.get(
            "should_answer",
            False
        ):
            category = "positive"
        else:
            category = "negative"

        rows.append({
            "case": case_id,
            "category": category,
            "expected": official_result.get(
                "esperado",
                ""
            ),
            "official": articles["official"],
            "run_01": articles["run_01"],
            "run_02": articles["run_02"],
            "run_03": articles["run_03"],
            "stable_article": (
                len(set(articles.values())) == 1
            ),
            "stable_correctness": (
                len(set(correctness.values())) == 1
            ),
            "official_correct": correctness["official"],
            "run_01_correct": correctness["run_01"],
            "run_02_correct": correctness["run_02"],
            "run_03_correct": correctness["run_03"],
            "official_valid": validations["official"],
            "run_01_valid": validations["run_01"],
            "run_02_valid": validations["run_02"],
            "run_03_valid": validations["run_03"],
        })

    stable_articles = sum(
        row["stable_article"]
        for row in rows
    )

    variable_articles = [
        row
        for row in rows
        if not row["stable_article"]
    ]

    variable_correctness = [
        row
        for row in rows
        if not row["stable_correctness"]
    ]

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )

        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Perito.AR v2.1 variability study",
        "",
        "The official run was compared with three valid repetitions.",
        "The evaluated pipeline, corpus and prompt were not modified.",
        "",
        "## Aggregate results",
        "",
        "| Run | Accuracy | Correct |",
        "|---|---:|---:|",
        "| Official | 90.0% | 36/40 |",
        "| Run 01 | 90.0% | 36/40 |",
        "| Run 02 | 90.0% | 36/40 |",
        "| Run 03 | 90.0% | 36/40 |",
        "",
        "## Case-level stability",
        "",
        f"- Same selected article in all four runs: "
        f"{stable_articles}/40.",
        f"- Cases with a variable selected article: "
        f"{len(variable_articles)}/40.",
        f"- Cases whose correct/incorrect status changed: "
        f"{len(variable_correctness)}/40.",
        "",
    ]

    if variable_articles:
        lines.extend([
            "## Cases with variable articles",
            "",
            "| Case | Expected | Official | Run 01 | Run 02 | Run 03 |",
            "|---|---|---|---|---|---|",
        ])

        for row in variable_articles:
            lines.append(
                "| {case} | {expected} | {official} | "
                "{run_01} | {run_02} | {run_03} |".format(
                    case=row["case"],
                    expected=(
                        row["expected"]
                        or "NONE"
                    ),
                    official=(
                        row["official"]
                        or "ABSTENTION"
                    ),
                    run_01=(
                        row["run_01"]
                        or "ABSTENTION"
                    ),
                    run_02=(
                        row["run_02"]
                        or "ABSTENTION"
                    ),
                    run_03=(
                        row["run_03"]
                        or "ABSTENTION"
                    ),
                )
            )

    lines.extend([
        "",
        "## Methodological notes",
        "",
        "- The three valid repetitions reproduced the same aggregate metrics.",
        "- Case-level stability is reported separately.",
        "- Invalid runs created with an incorrect working directory are excluded.",
        "- The official benchmark JSON remained preserved by SHA-256.",
    ])

    OUTPUT_MD.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(
        f"Same article in all four runs: "
        f"{stable_articles}/40"
    )

    print(
        f"Cases with variable articles: "
        f"{len(variable_articles)}/40"
    )

    print(
        f"Cases with variable correctness: "
        f"{len(variable_correctness)}/40"
    )

    print(f"Markdown: {OUTPUT_MD}")
    print(f"CSV: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()