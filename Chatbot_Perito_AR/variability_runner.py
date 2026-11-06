import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent

BENCHMARK_SCRIPT = (
    ROOT
    / "tests"
    / "benchmark_v21_test.py"
)

OFFICIAL_RESULT = (
    ROOT
    / "results"
    / "benchmark_qwen_v21_test_final.json"
)

AUDIT_DIR = ROOT / "audit"

RUNS = 3


def main():
    if not BENCHMARK_SCRIPT.exists():
        raise FileNotFoundError(
            f"No existe el benchmark: {BENCHMARK_SCRIPT}"
        )

    if not OFFICIAL_RESULT.exists():
        raise FileNotFoundError(
            f"No existe el resultado oficial: {OFFICIAL_RESULT}"
        )

    AUDIT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    official_backup = (
        AUDIT_DIR
        / "benchmark_qwen_v21_test_final_official_backup.json"
    )

    shutil.copy2(
        OFFICIAL_RESULT,
        official_backup
    )

    official_hash_before = subprocess.check_output(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                f"(Get-FileHash "
                f"'{OFFICIAL_RESULT}' "
                f"-Algorithm SHA256).Hash.ToLower()"
            ),
        ],
        text=True,
    ).strip()

    run_manifest = []

    for run_number in range(1, RUNS + 1):
        print("\n" + "=" * 72)
        print(
            f"CORRIDA DE VARIABILIDAD "
            f"{run_number}/{RUNS}"
        )
        print("=" * 72)

        started_at = datetime.now().isoformat(
            timespec="seconds"
        )

        console_file = (
            AUDIT_DIR
            / f"variability_run_{run_number:02d}_console.txt"
        )

        result_file = (
            AUDIT_DIR
            / f"variability_run_{run_number:02d}.json"
        )

        start = time.perf_counter()

        process = subprocess.run(
            [
                sys.executable,
                str(BENCHMARK_SCRIPT),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        elapsed = time.perf_counter() - start

        console_file.write_text(
            process.stdout
            + "\n\nSTDERR:\n"
            + process.stderr,
            encoding="utf-8",
        )

        if process.returncode != 0:
            shutil.copy2(
                official_backup,
                OFFICIAL_RESULT
            )

            raise RuntimeError(
                f"La corrida {run_number} fallo. "
                f"Revisar {console_file}"
            )

        if not OFFICIAL_RESULT.exists():
            shutil.copy2(
                official_backup,
                OFFICIAL_RESULT
            )

            raise RuntimeError(
                "El benchmark no genero el JSON esperado."
            )

        shutil.copy2(
            OFFICIAL_RESULT,
            result_file
        )

        with result_file.open(
            "r",
            encoding="utf-8"
        ) as file:
            result_data = json.load(file)

        metrics = result_data.get(
            "metricas",
            {}
        )

        run_manifest.append({
            "run": run_number,
            "started_at": started_at,
            "elapsed_seconds": round(
                elapsed,
                3
            ),
            "return_code": process.returncode,
            "result_file": result_file.name,
            "console_file": console_file.name,
            "accuracy": metrics.get(
                "accuracy"
            ),
            "correct": metrics.get(
                "aciertos"
            ),
            "total": metrics.get(
                "total"
            ),
            "positive_recall": metrics.get(
                "recall_positivo"
            ),
            "abstention_accuracy": metrics.get(
                "abstencion_correcta"
            ),
            "prompt_injection_resistance": metrics.get(
                "resistencia_prompt_injection"
            ),
        })

        print(
            json.dumps(
                run_manifest[-1],
                ensure_ascii=False,
                indent=2,
            )
        )

        # Restaurar inmediatamente la corrida oficial.
        shutil.copy2(
            official_backup,
            OFFICIAL_RESULT
        )

    official_hash_after = subprocess.check_output(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                f"(Get-FileHash "
                f"'{OFFICIAL_RESULT}' "
                f"-Algorithm SHA256).Hash.ToLower()"
            ),
        ],
        text=True,
    ).strip()

    manifest_file = (
        AUDIT_DIR
        / "variability_manifest.json"
    )

    manifest_file.write_text(
        json.dumps(
            {
                "official_result": (
                    OFFICIAL_RESULT.name
                ),
                "official_hash_before": (
                    official_hash_before
                ),
                "official_hash_after": (
                    official_hash_after
                ),
                "official_preserved": (
                    official_hash_before
                    == official_hash_after
                ),
                "runs": run_manifest,
            },
            ensure_ascii=False,
            indent=4,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 72)
    print("ESTUDIO FINALIZADO")
    print("=" * 72)

    print(
        f"Resultado oficial preservado: "
        f"{official_hash_before == official_hash_after}"
    )

    print(
        f"Manifest: {manifest_file}"
    )


if __name__ == "__main__":
    main()
