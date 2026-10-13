"""Stage 2 — syntax specification in, concrete invocations and their environments out.

v1 does this with roughly 715 lines of nested combinatorial Python across `ir/string.py`,
`ir/environment.py`, `ir/contents.py`, and `ir/mixin.py`. Here an LLM is told what the
input is, what to produce, and what format to produce it in — and nothing about how.
Whether it can enumerate a combinatorial space at all is the question being asked, so a
model that stops early, repeats itself, or runs out of room is measured, not corrected.

The one thing supplied beyond the specification is the DSL's value-expansion table. The
specification names types (`Glob`, `Signal`); the values those types stand for live in
v1's DSL runtime. Without them no invocation string could match v1's, and the comparison
would measure a missing input rather than the model. That is input material, like the man
page in stage 1 — not a hint about method.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI

from .. import llm, metrics_db, prompting, telemetry, v1
from ..errors import V1AccessError
from ..harness import invocation as harness_invocation
from ..telemetry import (
    DecodingParams,
    RunManifest,
    TelemetryRecord,
    ValidationReport,
)

STAGE = "generate"
COMPONENT = "llm_pipeline"
CONDITION = "plain"

# v1's own CLI defaults (`cli/__init__.py`), verified by reading them rather than assumed.
# Note that `--max-arity` defaults to 1, not 2: task 002's draft said 2, and the paper's
# "two-flag limit" is `--max-count`, a different knob. Whatever is used here must be used
# on the v1 side of any comparison, which is why all four are recorded in the manifest.
V1_DEFAULT_MAX_ARITY = 1
V1_DEFAULT_MAX_COUNT = 4
V1_DEFAULT_STDIN = "simple"
V1_DEFAULT_CONTENT = "simple"
V1_DEFAULT_SKIP: str | None = None  # v1's `--skip` has no default: nothing is skipped
# What v1's bare `--skip` means (`cli/__init__.py:10`, `const=DEFAULT_SKIP`).
V1_SKIP_CONST = "--version,--help,--interactive"

DEFAULT_MAX_TURNS = 12

INVOCATIONS_SUFFIX = ".invocations.txt"
CONFIGS_SUFFIX = ".configs.json"
RAW_CONFIGS_SUFFIX = ".configs.raw.json"

# Stage 2 returns a long enumeration, so it gets its own output cap: the model's maximum per
# turn (gpt-4o: 16,384). At v2's global default (4,096 per turn, 4 turns) `cat` at v1's bound
# was cut off by the cap rather than finished by the model (seen from the console, 2026-10-13).
GENERATE_MAX_TOKENS = 16_384

# What each `arg_type` does on disk, read from v1's `prepare_env` implementations
# (ir/environment.py:56-240, commit d8032407). Stated to the model because v1's schema names
# the types and says nothing about what they mean (task 011 §3, "the fourth instance").
ARG_TYPES = (
    '`"no_env"` (a value with nothing on disk: a flag with no value, a number, a word), '
    '`"file"` (a regular file is created with the given `content`), '
    '`"directory_empty"` (an empty directory is created), '
    '`"directory_nonempty"` (a directory with files in it is created), '
    '`"nonexistent"` (the path is absent; `parent_exists` says whether its parent directory '
    "exists), "
    '`"already"` (the path must already exist and nothing is created; v1 uses it only for '
    "`.` and `..`)"
)


def _config_examples() -> str:
    """Two real v1 configurations, frozen in `prompts/generate/v1_examples.json`."""
    path = prompting.prompts_root() / STAGE / "v1_examples.json"
    payload = json.loads(path.read_text())
    # One object per line, exactly as the output must be written: a pretty-printed example
    # was copied as a multi-line layout by the model, which the line parser rejects.
    return "\n".join(
        json.dumps(example, separators=(", ", ": ")) for example in payload["examples"]
    )



@dataclass(frozen=True)
class ParsedOutput:
    """What survived parsing the model's JSON Lines, and what did not."""

    invocations: list[str]
    configs: list[dict[str, Any]]
    line_count: int
    unparseable_lines: list[str]
    malformed_objects: int
    """True when the objects spanned lines and were recovered as a stream: content usable,
    format not followed."""
    stream_decoded: bool = False

    @property
    def parsed(self) -> int:
        return len(self.configs)


def parse_jsonl(text: str) -> ParsedOutput:
    """Read one JSON object per line, keeping a count of everything discarded.

    A truncated final line is simply unparseable and lands in `unparseable_lines`; the
    stage records that rather than trying to repair it, because a repaired line would be
    partly our output and partly the model's.
    """
    invocations: list[str] = []
    configs: list[dict[str, Any]] = []
    unparseable: list[str] = []
    malformed = 0
    # Code fences are asked against and still appear; they carry nothing, so they are dropped
    # before parsing rather than counted as unparseable lines.
    text = "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("```")
    )
    lines = [line for line in text.splitlines() if line.strip()]

    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            unparseable.append(line)
            continue

        if not isinstance(entry, dict) or "invocation" not in entry or "config" not in entry:
            malformed += 1
            continue

        invocations.append(str(entry["invocation"]))
        configs.append(entry["config"])

    # A model that lays objects out over several lines defeats the line parser even though
    # every object is complete. Decode the text as a stream of consecutive objects instead,
    # and say so in the record: the format was not followed, but the content is usable.
    stream_decoded = False
    if not configs and unparseable:
        decoder = json.JSONDecoder()
        position = 0
        recovered: list[Any] = []
        while position < len(text):
            while position < len(text) and text[position] in " \t\r\n,[]":
                position += 1
            if position >= len(text):
                break
            try:
                entry, end = decoder.raw_decode(text, position)
            except json.JSONDecodeError:
                break
            recovered.append(entry)
            position = end
        usable = [
            e for e in recovered if isinstance(e, dict) and "invocation" in e and "config" in e
        ]
        if usable:
            stream_decoded = True
            unparseable = []
            malformed = len(recovered) - len(usable)
            for entry in usable:
                invocations.append(str(entry["invocation"]))
                configs.append(entry["config"])

    return ParsedOutput(
        invocations=invocations,
        configs=configs,
        line_count=len(lines),
        unparseable_lines=unparseable[:20],
        malformed_objects=malformed,
        stream_decoded=stream_decoded,
    )


def compare_invocations(
    produced: list[str],
    reference: v1.ReferenceInvocations,
    *,
    command: str,
    bounds: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Set-diff the model's invocation strings against `caruca generate CMD`.

    The comparison itself lives in `harness/invocation.py`, which owns every stage-2
    measurement decision (the equivalence relation, the injectivity guard, the argv and
    literal figures reported alongside). The stage calls it so that each run still carries
    its own comparison inline in the manifest, rather than the number existing only after a
    separate scoring pass.
    """
    return harness_invocation.compare_invocation_sets(
        produced, reference, command=command, bounds=bounds
    )


def load_specification(command: str, spec_path: Path | None) -> tuple[str, str]:
    """The syntax specification text, and a note of where it came from."""
    if spec_path is None:
        return v1.syntax_spec(command), str(v1.syntax_spec_path(command))
    if not spec_path.is_file():
        raise V1AccessError(f"syntax specification not found at {spec_path}.")
    return spec_path.read_text(), str(spec_path)


@dataclass(frozen=True)
class GenerateResult:
    """Everything a caller needs from one configuration-generation run."""

    run_id: str
    run_dir: Path
    status: str
    invocations_path: Path | None
    configs_path: Path | None
    records: list[TelemetryRecord]
    manifest: RunManifest
    validation: ValidationReport | None

    @property
    def succeeded(self) -> bool:
        return self.status == "ok"


def run(
    command: str,
    *,
    model: str,
    temperature: float,
    seed: int | None = llm.DEFAULT_SEED,
    max_tokens: int = llm.DEFAULT_MAX_TOKENS,
    max_turns: int = DEFAULT_MAX_TURNS,
    spec_path: Path | None = None,
    max_arity: int = V1_DEFAULT_MAX_ARITY,
    max_count: int = V1_DEFAULT_MAX_COUNT,
    stdin_variation: str = V1_DEFAULT_STDIN,
    content_variation: str = V1_DEFAULT_CONTENT,
    skip_flags: str | None = V1_DEFAULT_SKIP,
    compare: bool = True,
    compare_timeout: int = 300,
    out_root: Path = metrics_db.DEFAULT_RUNS_ROOT,
    db_path: Path = metrics_db.DEFAULT_DB_PATH,
    log_conversation: bool = False,
    provider: str | None = None,
    client: OpenAI | None = None,
    progress: Callable[[dict[str, Any]], None] | None = None,
) -> GenerateResult:
    """Ask a model to enumerate a command's invocations, then measure what came back.

    `progress` receives one event per model turn (`kind: "turn"`, with the turn index, tokens,
    cost, seconds, the lines returned so far and whether another turn follows) and one per
    slow phase after the model (`kind: "phase"`). For showing activity; it changes nothing.
    """
    slug = v1.slug(command)

    active_client = client or llm.build_client()
    specification, spec_source = load_specification(command, spec_path)
    probe_values = v1.probe_values()
    config_schema = v1.command_config_schema()
    variation_values = v1.content_variation_values()

    prompt = prompting.build(
        STAGE,
        {
            "command": command,
            "syntax_spec": specification,
            "probe_values": json.dumps(probe_values, indent=1),
            "config_schema": json.dumps(config_schema, indent=1),
            "max_arity": str(max_arity),
            "max_count": str(max_count),
            "stdin_variation": stdin_variation,
            "content_variation": content_variation,
            "stdin_values": ", ".join(variation_values.get(stdin_variation, [])) or "(none)",
            "content_values": ", ".join(variation_values.get(content_variation, [])) or "(none)",
            "skip_flags": skip_flags or "(none)",
            "config_examples": _config_examples(),
            "arg_types": ARG_TYPES,
        },
    )

    out_root.mkdir(parents=True, exist_ok=True)
    run_dir = telemetry.create_run_directory(out_root, slug)

    responses = llm.complete_series(
        prompt.as_messages(),
        model=model,
        temperature=temperature,
        seed=seed,
        max_tokens=max_tokens,
        max_turns=max_turns,
        provider=provider,
        exhaust_instruction=llm.EXHAUST_INSTRUCTION,
        client=active_client,
        on_turn=(
            None
            if progress is None
            else lambda index, response, nxt: progress(
                {
                    "kind": "turn",
                    "turn": index + 1,
                    "max_turns": max_turns,
                    "prompt_tokens": response.prompt_tokens,
                    "completion_tokens": response.completion_tokens,
                    "cost_usd": response.cost_usd,
                    "seconds": response.wall_clock_seconds,
                    "lines": sum(1 for line in response.text.splitlines() if line.strip()),
                    "finish_reason": response.finish_reason,
                    "continues": nxt is not None,
                    "why": (
                        "cut off by the token cap"
                        if response.finish_reason == "length"
                        else "asked once whether anything is missing"
                        if nxt is not None
                        else "the model says it is done"
                    ),
                }
            )
        ),
    )

    if log_conversation:
        messages: list[dict[str, Any]] = list(prompt.as_messages())
        for index, response in enumerate(responses):
            messages.append(response.message)
            if index < len(responses) - 1:
                messages.append({"role": "user", "content": llm.CONTINUE_INSTRUCTION})
        telemetry.append_conversation(run_dir, messages)

    combined = "\n".join(
        stripped
        for stripped in (llm.strip_sentinel(response.text) for response in responses)
        if stripped.strip()
    )
    parsed = parse_jsonl(combined)
    truncated = responses[-1].finish_reason == "length"
    self_terminated = llm.declares_complete(responses[-1].text)

    invocations_path: Path | None = None
    configs_path: Path | None = None
    validation: ValidationReport | None = None
    status = "failed"
    failure_reason: str | None = None

    if not parsed.configs:
        failure_reason = (
            f"no usable output: {parsed.line_count} line(s) returned, none of them a "
            "JSON object carrying both `invocation` and `config`"
        )
    else:
        invocations_path = run_dir.file(f"{slug}{INVOCATIONS_SUFFIX}")
        invocations_path.write_text("\n".join(parsed.invocations) + "\n")

        configs_path = run_dir.file(f"{slug}{CONFIGS_SUFFIX}")
        configs_path.write_text(json.dumps(parsed.configs, indent=1) + "\n")

        if progress is not None:
            progress(
                {
                    "kind": "phase",
                    "message": f"checking {len(parsed.configs)} configurations with v1's own model",
                }
            )
        outcome = v1.validate_configs(configs_path)
        if outcome.passed and outcome.normalized is not None:
            # The file v1 would have written: every entry re-emitted through v1's own model
            # (computed fields present, defaults filled, bookkeeping in v1's form). The
            # model's own text is kept beside it, so what the model wrote stays inspectable.
            run_dir.file(f"{slug}{RAW_CONFIGS_SUFFIX}").write_text(
                json.dumps(parsed.configs, indent=1) + "\n"
            )
            configs_path.write_text(json.dumps(outcome.normalized, indent=1) + "\n")
        validation = ValidationReport(
            passed=outcome.passed,
            available=outcome.available,
            error=outcome.error,
            traceback=outcome.traceback,
            elements=outcome.count,
        )
        if outcome.passed:
            status = "ok"
        elif not outcome.available:
            failure_reason = f"validation unavailable: {outcome.error}"
        else:
            index = outcome.invalid_index
            where = "" if index is None else f" (first failure at entry {index})"
            failure_reason = f"v1 rejected the generated configs{where}: {outcome.error}"

    comparison: dict[str, Any] = {"available": False, "error": "comparison not requested"}
    if compare:
        if progress is not None:
            progress(
                {
                    "kind": "phase",
                    "message": "comparing against v1's own enumeration (runs v1's generate)",
                }
            )
        # Same bounds on both sides, or the diff measures the bounds instead of the model.
        reference = v1.reference_invocations(
            command,
            max_arity=max_arity,
            max_count=max_count,
            skip=skip_flags,
            timeout=compare_timeout,
        )
        comparison = compare_invocations(
            parsed.invocations,
            reference,
            command=command,
            bounds={
                "max_arity": max_arity,
                "max_count": max_count,
                "skip": skip_flags,
                "stdin_variation": stdin_variation,
                "content_variation": content_variation,
            },
        )

    decoding = DecodingParams(temperature=temperature, max_tokens=max_tokens)
    records = [
        TelemetryRecord(
            run_id=run_dir.run_id,
            command=command,
            component=COMPONENT,
            condition=CONDITION,
            stage=STAGE,
            model_id=response.model_reported,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            cost_usd=response.cost_usd,
            wall_clock_seconds=response.wall_clock_seconds,
            seed=seed,
            prompt_hash=prompt.prompt_hash,
            timestamp=run_dir.timestamp,
            decoding_params=decoding,
            turn=turn,
        )
        for turn, response in enumerate(responses)
    ]

    manifest = RunManifest(
        run_id=run_dir.run_id,
        timestamp=run_dir.timestamp,
        command=command,
        component=COMPONENT,
        condition=CONDITION,
        stage=STAGE,
        status=status,
        failure_reason=failure_reason,
        model_requested=responses[0].model_requested,
        model_reported=responses[0].model_reported,
        provider=responses[0].provider,
        seed=seed,
        seed_honored=seed is not None and llm.seed_is_honored(model),
        decoding_params=decoding,
        response_format="jsonl",
        prompt_hash=prompt.prompt_hash,
        prompt_files=[f"prompts/{STAGE}/system.md", f"prompts/{STAGE}/user.md"],
        prompt_system=prompt.system,
        prompt_user=prompt.user,
        raw_response=combined,
        finish_reason=responses[-1].finish_reason,
        output_truncated=truncated,
        turns=len(responses),
        output_paths=[str(path) for path in (invocations_path, configs_path) if path],
        validation=validation,
        checks={
            "parse": {
                "lines_returned": parsed.line_count,
                "objects_parsed": parsed.parsed,
                "unparseable_lines": len(parsed.unparseable_lines),
                "unparseable_sample": parsed.unparseable_lines,
                "malformed_objects": parsed.malformed_objects,
                # A run that hit the turn cap while still truncated did not finish
                # enumerating. Distinguishing that from a model that simply stopped is
                # what separates "the cap bound" from "the model bound".
                "stream_decoded": parsed.stream_decoded,
                "hit_turn_cap_while_truncated": truncated and len(responses) >= max_turns,
                # Recorded because this stage nudges a self-terminated model for more (see
                # `llm.complete_series`); a result from it is partly measuring the nudge.
                "continuation_policy": "exhaust",
                "turns_used": len(responses),
                "model_declared_complete": self_terminated,
                "hit_turn_cap_while_incomplete": (
                    not self_terminated and not truncated and len(responses) >= max_turns
                ),
            },
            "invocation_comparison": comparison,
        },
        prompt_tokens=sum(response.prompt_tokens for response in responses),
        completion_tokens=sum(response.completion_tokens for response in responses),
        cost_usd=sum(response.cost_usd for response in responses),
        wall_clock_seconds=sum(response.wall_clock_seconds for response in responses),
        inputs={
            "spec_source": spec_source,
            "caruca_v1_root": str(v1.v1_root()),
            "max_arity": max_arity,
            "max_count": max_count,
            "stdin_variation": stdin_variation,
            "content_variation": content_variation,
            "skip_flags": skip_flags,
            "max_turns": max_turns,
            "replaces_v1_modules": [
                "ir/string.py",
                "ir/environment.py",
                "ir/contents.py",
                "ir/mixin.py",
            ],
        },
    )

    for record in records:
        telemetry.write_sidecar(run_dir, f"{slug}.turn-{record.turn:02d}", record)
        metrics_db.append_run(
            record,
            run_dir=run_dir.path,
            validation_passed=None if validation is None else validation.passed,
            db_path=db_path,
        )
    telemetry.write_manifest(run_dir, manifest)

    return GenerateResult(
        run_id=run_dir.run_id,
        run_dir=run_dir.path,
        status=status,
        invocations_path=invocations_path,
        configs_path=configs_path,
        records=records,
        manifest=manifest,
        validation=validation,
    )
