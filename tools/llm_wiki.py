#!/usr/bin/env python3
"""Register wiki repositories and expose their skills globally to Codex."""

from __future__ import annotations

import argparse
import configparser
import os
import re
import sys
from pathlib import Path


SKILLS = ("wiki-write", "wiki-update", "wiki-search")
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def default_config_path() -> Path:
    value = os.environ.get("LLM_WIKI_CONFIG", "~/.config/llm-wiki/config.ini")
    return Path(value).expanduser()


def default_skill_home() -> Path:
    value = os.environ.get("LLM_WIKI_SKILL_HOME", "~/.agents/skills")
    return Path(value).expanduser()


def load_config(path: Path) -> configparser.ConfigParser:
    config = configparser.ConfigParser(interpolation=None)
    if path.exists():
        config.read(path, encoding="utf-8")
    if "llm-wiki" not in config:
        config["llm-wiki"] = {}
    return config


def save_config(config: configparser.ConfigParser, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        config.write(handle)
    temporary.replace(path)


def validate_name(name: str) -> None:
    if not NAME_PATTERN.fullmatch(name):
        raise ValueError("Repository name must contain only letters, numbers, '-' or '_'.")


def repository_sections(config: configparser.ConfigParser) -> list[str]:
    return [section for section in config.sections() if section.startswith("repo:")]


def repository_name(section: str) -> str:
    return section.split(":", 1)[1]


def install_skills(root: Path, skill_home: Path, replace: bool) -> None:
    source_home = root / ".agents" / "skills"
    skill_home.mkdir(parents=True, exist_ok=True)

    for skill in SKILLS:
        source = source_home / skill
        destination = skill_home / skill
        if not (source / "SKILL.md").is_file():
            raise FileNotFoundError(f"Missing skill: {source / 'SKILL.md'}")

        if destination.is_symlink():
            if destination.resolve() == source.resolve():
                print(f"skill ok: {destination}")
                continue
            if replace:
                destination.unlink()
            else:
                print(f"skill kept: {destination} -> {destination.resolve()}")
                continue
        elif destination.exists():
            raise FileExistsError(
                f"Cannot replace non-symlink skill directory: {destination}"
            )

        destination.symlink_to(source, target_is_directory=True)
        print(f"skill linked: {destination} -> {source}")


def command_install(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).expanduser().resolve()
    name = args.name or root.name
    validate_name(name)

    if not (root / "AGENTS.md").is_file():
        raise FileNotFoundError(f"Not an LLM Wiki root: {root}")

    config_path = Path(args.config).expanduser()
    skill_home = Path(args.skill_home).expanduser()
    config = load_config(config_path)
    section = f"repo:{name}"
    config[section] = {
        "path": str(root),
        "kind": args.kind,
        "writable": str(not args.read_only).lower(),
    }

    if args.default or not config["llm-wiki"].get("default"):
        config["llm-wiki"]["default"] = name

    save_config(config, config_path)
    install_skills(root, skill_home, args.replace_skills)
    print(f"repository registered: {name} -> {root}")
    print(f"config: {config_path}")
    return 0


def command_list(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config).expanduser())
    default = config["llm-wiki"].get("default", "")
    for section in repository_sections(config):
        name = repository_name(section)
        marker = "*" if name == default else " "
        values = config[section]
        print(
            f"{marker} {name}\t{values.get('kind', 'unspecified')}\t"
            f"writable={values.get('writable', 'true')}\t{values.get('path', '')}"
        )
    return 0


def command_resolve(args: argparse.Namespace) -> int:
    config_path = Path(args.config).expanduser()
    config = load_config(config_path)
    name = args.name or config["llm-wiki"].get("default")
    if not name:
        raise KeyError(f"No default wiki configured in {config_path}")
    section = f"repo:{name}"
    if section not in config:
        raise KeyError(f"Unknown wiki repository: {name}")
    root = Path(config[section]["path"]).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Wiki repository is unavailable: {root}")
    print(root)
    return 0


def command_set_default(args: argparse.Namespace) -> int:
    config_path = Path(args.config).expanduser()
    config = load_config(config_path)
    section = f"repo:{args.name}"
    if section not in config:
        raise KeyError(f"Unknown wiki repository: {args.name}")
    config["llm-wiki"]["default"] = args.name
    save_config(config, config_path)
    print(f"default repository: {args.name}")
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    config_path = Path(args.config).expanduser()
    skill_home = Path(args.skill_home).expanduser()
    config = load_config(config_path)
    failures: list[str] = []

    default = config["llm-wiki"].get("default")
    if not default:
        failures.append("default repository is not configured")
    elif f"repo:{default}" not in config:
        failures.append(f"default repository is missing: {default}")

    for section in repository_sections(config):
        root = Path(config[section].get("path", "")).expanduser()
        if not root.is_dir():
            failures.append(f"repository path is unavailable: {root}")

    for skill in SKILLS:
        path = skill_home / skill / "SKILL.md"
        if not path.is_file():
            failures.append(f"global skill is unavailable: {path}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(f"OK: config {config_path}")
    print(f"OK: {len(repository_sections(config))} repository/repositories")
    print(f"OK: {len(SKILLS)} global skills")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(default_config_path()))
    parser.add_argument("--skill-home", default=str(default_skill_home()))
    subparsers = parser.add_subparsers(dest="command", required=True)

    install = subparsers.add_parser("install", help="register a wiki and link skills")
    install.add_argument("--repo-root", default=".")
    install.add_argument("--name")
    install.add_argument("--kind", choices=("personal", "team", "template"), default="personal")
    install.add_argument("--read-only", action="store_true")
    install.add_argument("--default", action="store_true")
    install.add_argument("--replace-skills", action="store_true")
    install.set_defaults(handler=command_install)

    list_command = subparsers.add_parser("list", help="list configured wikis")
    list_command.set_defaults(handler=command_list)

    resolve = subparsers.add_parser("resolve", help="print a configured wiki path")
    resolve.add_argument("name", nargs="?")
    resolve.set_defaults(handler=command_resolve)

    set_default = subparsers.add_parser("set-default", help="select the default wiki")
    set_default.add_argument("name")
    set_default.set_defaults(handler=command_set_default)

    doctor = subparsers.add_parser("doctor", help="validate configuration and skills")
    doctor.set_defaults(handler=command_doctor)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except (FileExistsError, FileNotFoundError, KeyError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
