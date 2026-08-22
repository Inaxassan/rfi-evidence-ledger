"""Command-line interface for one bounded offline RFI evidence run."""

from __future__ import annotations

import argparse
from pathlib import Path

from .artifacts import write_artifacts
from .intake import IntakeError, load_bundle, load_task
from .runner import run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one bounded offline RFI Evidence Ledger evaluation task.")
    parser.add_argument("--task", required=True, type=Path, help="Path to a strict JSON task manifest.")
    parser.add_argument("--output", type=Path, default=Path("artifacts"), help="Directory for local dossier and receipt artifacts.")
    args = parser.parse_args(argv)
    try:
        task = load_task(args.task)
        bundle_path = Path(task.bundle_path)
        if not bundle_path.is_absolute():
            bundle_path = Path.cwd() / bundle_path
        documents = load_bundle(bundle_path)
        outcome = run(task, documents)
        paths = write_artifacts(outcome, args.output)
    except (OSError, IntakeError, ValueError) as error:
        parser.error(str(error))
        return 2
    print(f"terminal_state={outcome.terminal_state.value}")
    print(f"dossier={paths['dossier']}")
    print(f"receipt={paths['receipt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
